import sys
import os
from pathlib import Path

# Add project root to path to import app modules
# This works both locally and on Streamlit Cloud
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from dotenv import load_dotenv

# Load environment variables
# Try .env first, then Streamlit secrets
env_path = ROOT / ".env"
if env_path.exists():
    load_dotenv(env_path)

from app.data_loader import load_restaurants_df
from app.filter_engine import filter_candidates
from app.llm_client import LLMClient
from app.config import get_settings
from app.prompting import build_recommendation_prompt

# Page configuration
st.set_page_config(
    page_title="Restaurant Recommender",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stButton>button {
        color: white;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
        height: 3em;
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
    }
    .recommendation-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .explanation-box {
        background: #f0f4ff;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🍽️ Restaurant Recommender")
    st.markdown("Find the perfect restaurant based on your preferences using AI-powered recommendations.")
    
    st.sidebar.header("Configuration")
    
    # Check API keys
    settings = get_settings()
    has_openrouter = bool(settings.openrouter_api_key)
    has_groq = bool(settings.groq_api_key)
    
    if has_openrouter:
        st.sidebar.success("✅ OpenRouter API key configured")
    else:
        st.sidebar.warning("⚠️ OpenRouter API key not configured")
    
    if has_groq:
        st.sidebar.success("✅ Groq API key configured")
    else:
        st.sidebar.warning("⚠️ Groq API key not configured")
    
    if not has_openrouter and not has_groq:
        st.sidebar.error("❌ No LLM API keys configured. Add OPENROUTER_API_KEY or GROQ_API_KEY to .env file")
    
    st.sidebar.markdown("---")
    
    # Get unique locations from dataset for suggestions
    try:
        df = load_restaurants_df()
        unique_locations = sorted(df['location'].unique().tolist())
        unique_cuisines = sorted(df['cuisine'].unique().tolist())
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        unique_locations = []
        unique_cuisines = []
    
    # Main form
    st.header("Your Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        location = st.selectbox(
            "Location *",
            options=unique_locations if unique_locations else ["Bellandur", "Indiranagar", "Koramangala"],
            index=0,
            help="Select your preferred location"
        )
        
        budget = st.selectbox(
            "Budget *",
            options=["low", "medium", "high"],
            index=1,
            help="Low: Up to Rs.800, Medium: Rs.801-2000, High: Above Rs.2000"
        )
    
    with col2:
        cuisine = st.selectbox(
            "Cuisine *",
            options=unique_cuisines if unique_cuisines else ["North Indian", "South Indian", "Chinese", "Italian", "American"],
            index=0,
            help="Select your preferred cuisine type"
        )
        
        min_rating = st.slider(
            "Minimum Rating *",
            min_value=0.0,
            max_value=5.0,
            value=4.0,
            step=0.1,
            help="Minimum rating for restaurants"
        )
    
    additional_preferences = st.text_input(
        "Additional Preferences (Optional)",
        placeholder="e.g., family-friendly, outdoor seating",
        max_chars=500,
        help="Any specific requirements or preferences"
    )
    
    top_n = st.selectbox(
        "Number of Recommendations *",
        options=[3, 4, 5],
        index=2,
        help="How many recommendations to show"
    )
    
    # Submit button
    submitted = st.button("Get Recommendations", type="primary")
    
    if submitted:
        if not location or not cuisine:
            st.error("Please fill in all required fields")
            return
        
        # Show loading spinner
        with st.spinner("Finding the best restaurants for you..."):
            try:
                # Load data
                df = load_restaurants_df()
                
                # Filter candidates
                from app.models import RecommendationRequest
                req = RecommendationRequest(
                    location=location,
                    budget=budget,
                    cuisine=cuisine,
                    min_rating=min_rating,
                    additional_preferences=additional_preferences or None,
                    top_n=top_n
                )
                
                filtered, fallback_applied, strategy = filter_candidates(df, req)
                candidate_limit = settings.max_candidates_for_llm
                candidate_df = filtered.head(candidate_limit)
                
                if candidate_df.empty:
                    st.error("No candidates found after filtering. Try adjusting your preferences.")
                    return
                
                # Prepare candidates for LLM
                candidates = [
                    {
                        "restaurant_name": row["restaurant_name"],
                        "location": row["location"],
                        "cuisine": row["cuisine"],
                        "rating": float(row["rating"]),
                        "estimated_cost": float(row["average_cost_for_two"]),
                    }
                    for _, row in candidate_df.iterrows()
                ]
                
                # Build prompt and get LLM ranking
                prompt = build_recommendation_prompt(req, candidates)
                llm_client = LLMClient(settings)
                
                try:
                    import asyncio
                    llm_data, llm_provider = asyncio.run(llm_client.rank_with_fallback(prompt))
                    
                    if not isinstance(llm_data, dict):
                        raise ValueError("LLM output is not a JSON object")
                    
                    raw_recommendations = llm_data.get("recommendations", [])
                    if not isinstance(raw_recommendations, list):
                        raise ValueError("'recommendations' is not a list")
                    
                    # Hallucination guard
                    candidate_names = {c["restaurant_name"] for c in candidates}
                    llm_recommendations = []
                    for rec in raw_recommendations:
                        if isinstance(rec, dict) and rec.get("restaurant_name") in candidate_names:
                            llm_recommendations.append(rec)
                    
                except Exception as exc:
                    st.warning(f"LLM ranking failed: {exc}. Using deterministic fallback.")
                    llm_provider = "none"
                    llm_recommendations = []
                
                # Fallback if no LLM recommendations
                if not llm_recommendations:
                    llm_recommendations = [
                        {
                            "restaurant_name": c["restaurant_name"],
                            "cuisine": c["cuisine"],
                            "rating": c["rating"],
                            "estimated_cost": c["estimated_cost"],
                            "explanation": (
                                f"Strong match for {location} with rating {c['rating']:.1f}; "
                                "selected by deterministic filters due to LLM unavailability."
                            ),
                        }
                        for c in candidates[: top_n]
                    ]
                
                # Display results
                st.success(f"Found {len(llm_recommendations)} recommendations!")
                
                # Show metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("LLM Provider", llm_provider)
                with col2:
                    st.metric("Fallback Applied", "Yes" if fallback_applied else "No")
                with col3:
                    st.metric("Strategy", strategy[:20] + "..." if len(strategy) > 20 else strategy)
                
                st.markdown("---")
                
                # Display recommendations
                for i, rec in enumerate(llm_recommendations[: top_n], 1):
                    st.markdown(f"""
                    <div class="recommendation-card">
                        <h3>#{i} {rec['restaurant_name']}</h3>
                        <p><strong>Cuisine:</strong> {rec['cuisine']}</p>
                        <p><strong>Rating:</strong> ⭐ {rec['rating']}</p>
                        <p><strong>Cost for Two:</strong> Rs.{rec['estimated_cost']:.0f}</p>
                        <div class="explanation-box">
                            <strong>Why this?</strong> {rec.get('explanation', 'No explanation available')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Optional: Show raw JSON
                with st.expander("View Raw Response"):
                    st.json({
                        "recommendations": llm_recommendations[: top_n],
                        "llm_provider_used": llm_provider,
                        "fallback_applied": fallback_applied,
                        "filter_strategy": strategy
                    })
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.exception(e)

if __name__ == "__main__":
    main()

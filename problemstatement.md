# Coding Prompt: AI-Powered Restaurant Recommendation System

Build an AI-assisted restaurant recommendation application inspired by Zomato.

## Goal
Create a system that accepts user dining preferences, filters a real restaurant dataset, and uses an LLM to return ranked recommendations with concise reasoning.

## Dataset
Use this dataset from Hugging Face:
`https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation`

At minimum, load and standardize these fields:
- `restaurant_name`
- `location`
- `cuisine`
- `average_cost_for_two` (or equivalent cost field)
- `rating`
- any additional useful metadata available

## Functional Requirements
1. **Input Collection**
   - Accept user preferences:
     - location (for example: Delhi, Bangalore)
     - budget (low, medium, high)
     - preferred cuisine(s)
     - minimum rating
     - optional free-text preferences (for example: family-friendly, quick service)

2. **Data Processing**
   - Clean and normalize dataset values.
   - Map budget categories to a cost range.
   - Filter candidates based on user inputs.
   - Handle missing or malformed fields gracefully.

3. **LLM Recommendation Layer**
   - Build a prompt that includes:
     - user preferences
     - top filtered candidate restaurants in structured form
   - Ask the LLM to:
     - rank restaurants from best to worst fit
     - provide a short reason for each recommendation
     - mention trade-offs when relevant
   - Prevent hallucinations by requiring the model to use only provided candidate data.

4. **Output**
   - Return top 3-5 recommendations.
   - Each recommendation must include:
     - restaurant name
     - cuisine
     - rating
     - estimated cost
     - LLM-generated explanation

## Non-Functional Requirements
- Write modular, readable code.
- Add basic error handling and input validation.
- Include clear setup/run instructions.
- Keep API keys/configuration outside source code (environment variables).

## Suggested Tech Stack (you may choose alternatives)
- Python (FastAPI/Flask + Pandas)
- or JavaScript/TypeScript (Node.js + Express)
- Any LLM provider (OpenAI, Azure OpenAI, etc.)

## Deliverables
1. Source code
2. `README.md` with:
   - setup instructions
   - how to run
   - sample request and response
3. One example prompt used for the LLM
4. A short note explaining filtering + ranking strategy

## Evaluation Criteria
- Correctness of filtering logic
- Quality and relevance of recommendations
- Clarity of explanations
- Robustness and code quality
- Ease of running the project
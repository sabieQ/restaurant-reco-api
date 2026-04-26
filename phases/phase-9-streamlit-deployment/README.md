# Phase 9 - Deployment using Streamlit (Optional)

This phase implements a single-process Python app using Streamlit for demos and stakeholder previews without requiring Node.js build or separate SPA host.

## Goals
- Create Streamlit app with preference widgets
- Load corpus, validate, filter, prompt, and recommend
- Render ranked cards with explanations
- Support secrets via Streamlit secrets or environment variables
- Deploy to Streamlit Community Cloud (free tier)

## Implementation

### Tech Stack
- **Framework**: Streamlit
- **Language**: Python 3.11
- **Deployment**: Streamlit Community Cloud (free tier) or Docker

### Features
- **Form Widgets**: st.selectbox for location, budget, cuisine, top_n; st.slider for rating; st.text_input for additional preferences
- **Loading States**: st.spinner while model runs
- **Results Display**: Styled cards with restaurant details and AI explanations
- **Metadata**: Shows LLM provider, fallback status, filter strategy
- **Raw JSON View**: Expandable section for API response
- **Empty States**: Clear error messages when no candidates found
- **Secrets Management**: Supports Streamlit secrets and environment variables

### Data Flow
1. User selects preferences via Streamlit widgets
2. Load dataset from Hugging Face
3. Filter candidates based on preferences
4. Build prompt and call LLM with fallback
5. Render ranked recommendations with explanations

## Run (PowerShell)

### Local
```powershell
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The app will open at [http://localhost:8501](http://localhost:8501)

### Streamlit Community Cloud
See `docs/streamlit-deploy.md` for detailed deployment instructions.

## Relationship to Phase 7-8
- **Complementary**: Phase 7 (HTTP API) + Phase 8 (Next.js) remain the primary product UI
- **Phase 9**: Ideal for course demos, stakeholder previews, and fast sharing without operating Vite + CORS + two deployables
- **Implementation**: Imports milestone1 directly (duplication of orchestration is acceptable for this use case)

## P0 Edge Cases Checked
1. Secrets never exposed to browser client
2. Empty states handled with clear messages
3. LLM fallback triggers deterministic ranking
4. Dataset load failures caught and displayed

## Outputs
- `phase-9-gate-evidence.md`
- `phases/phase-9-streamlit-deployment/app.py`
- `streamlit_app.py` (repo root entry point)
- `docs/streamlit-deploy.md`
- Updated `requirements.txt` with streamlit and nest-asyncio

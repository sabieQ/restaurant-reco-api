# Restaurant Recommendation API

Python 3.11 + FastAPI backend with Next.js frontend for AI-assisted restaurant recommendations using:
- OpenRouter free-first (`openrouter/free`)
- Groq free tier fallback

## Features
- Loads and normalizes Zomato dataset from Hugging Face.
- Filtering policy:
  - strict location
  - strict rating
  - semi-strict cuisine
  - flexible budget
- No-match fallback:
  - relax rating by 0.5
  - then widen cuisine
- LLM ranking + explanation with deterministic fallback if LLM calls fail.
- Modern Next.js frontend with TypeScript and Tailwind CSS.
- v1 API endpoints with structured logging.
- Deployed on Vercel (frontend) and Render (backend).

## Phase Execution Structure
- Each implementation phase is executed in its own folder under `phases/`.
- Phase 0 artifacts live at `phases/phase_0_alignment_scope_lock/`.
- See `phase-architecture.md` for complete phase documentation.

## Setup

### Backend
1. Create and activate a Python 3.11 virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy and configure environment variables:

```bash
copy .env.example .env
```

Populate at least one key:
- `OPENROUTER_API_KEY` (primary)
- `GROQ_API_KEY` (fallback)

### Frontend (Next.js)
1. Navigate to frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Configure local environment (optional - defaults to localhost:8000):
```bash
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > frontend\.env.local
```

## Run

### Backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Next.js)
```bash
cd frontend
npm run dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000)

## Deployment

See `docs/deployment.md` for complete deployment instructions for:
- **Backend**: Deploy FastAPI to Render
- **Frontend**: Deploy Next.js to Vercel
- **Environment Variables**: Configuration for both platforms
- **CORS Setup**: Allow frontend domain on backend

### API Endpoints (v1)
- `GET /health` - Health check with key configuration status
- `GET /api/v1/meta` - Metadata for form hints
- `POST /api/v1/recommendations` - Main recommendation endpoint
- `POST /recommend` - Legacy endpoint (redirects to v1)

### Sample request
```json
{
  "location": "Bellandur",
  "budget": "medium",
  "cuisine": "American",
  "min_rating": 4.0,
  "additional_preferences": "family-friendly",
  "top_n": 5
}
```

### Sample response
```json
{
  "recommendations": [
    {
      "restaurant_name": "Chili's American Grill & Bar",
      "cuisine": "American, Tex-Mex, Burger, BBQ",
      "rating": 4.6,
      "estimated_cost": 1800.0,
      "explanation": "Strong match for Bellandur with rating 4.6; selected by LLM ranking."
    }
  ],
  "llm_provider_used": "openrouter",
  "fallback_applied": false,
  "filter_strategy": "strict location + strict rating + semi-strict cuisine + flexible budget"
}
```

## Testing

### Run Filter Engine Tests
```bash
py -3.11 tests/test_filter_engine_standalone.py
```

### Run API Contract Tests
Start the backend first, then run:
```bash
py -3.11 tests/test_api_contract_standalone.py
```

## Limitations

- **Dataset**: Uses Zomato Indian restaurant dataset; location searches work best with Indian cities
- **LLM Rate Limits**: Free tier API keys may have rate limits
- **Cold Starts**: First request may be slower due to dataset loading
- **Candidate Cap**: Maximum 15 candidates sent to LLM for ranking (configurable via MAX_CANDIDATES_FOR_LLM)

## Cost and Latency Notes

See `docs/cost-latency-notes.md` for detailed information on:
- Candidate cap and its impact on costs
- Model selection recommendations
- When to raise load limits
- Caching strategies for repeated queries

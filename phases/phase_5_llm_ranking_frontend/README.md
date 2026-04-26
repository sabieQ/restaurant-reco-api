# Phase 5 - LLM Ranking, Explanation, and Frontend

This phase implements LLM-based ranking and explanation generation, along with a frontend web interface for the restaurant recommendation API.

## Goals
- Implement LLM ranking using OpenRouter (primary) and Groq (fallback)
- Generate personalized explanations for recommendations
- Create a modern frontend web interface
- Integrate frontend with backend API
- Test full end-to-end flow

## Architecture

### Backend Components
- `app/llm_client.py` - LLM API client with fallback logic
- `app/ranking_engine.py` - LLM-based ranking and explanation generation
- `app/main.py` - FastAPI endpoints

### Frontend Components
- `frontend/` - React-based web interface
- `frontend/src/` - React components
- `frontend/public/` - Static assets

## LLM Provider Configuration
- Primary: OpenRouter (openrouter/free model)
- Fallback: Groq (llama-3.1-8b-instant)
- Deterministic fallback if both LLMs fail

## Run (PowerShell)

### Backend
```powershell
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```powershell
cd frontend
npm install
npm start
```

## P0 Edge Cases Checked
1. Malformed LLM output is safely handled
2. Hallucination guard is active (restaurants must be in candidate list)
3. Primary provider downtime triggers fallback
4. Fallback provider failure triggers deterministic fallback

## Outputs
- `phase-5-gate-evidence.md`
- LLM ranking validation report
- Frontend application

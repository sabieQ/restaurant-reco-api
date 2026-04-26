# Phase 7 - Backend (HTTP API)

This phase implements a thin HTTP service that owns server-side secrets, dataset access, and orchestration.

## Goals
- Restructure API to v1 endpoints with stable JSON contract
- Add structured logging (counts, latency, token totals)
- Implement request size limits on free-text fields
- Configure CORS for frontend integration
- Maintain backward compatibility with legacy endpoints

## Implementation

### v1 Endpoints
- `POST /api/v1/recommendations` - Main recommendation endpoint
- `GET /health` - Health check with key configuration status
- `GET /api/v1/meta` - Metadata for form hints (max values, allowed options)

### Legacy Endpoints (Backward Compatibility)
- `POST /recommend` - Redirects to v1 endpoint

### Structured Logging
- JSON-formatted logs with timestamp, level, and message
- Tracks: request parameters, candidate counts, latency, LLM provider used
- No raw user notes in info-level logs

### CORS Configuration
- Allowed origins: `http://localhost:3000`, `http://127.0.0.1:3000`, `http://localhost:3001`
- All methods and headers allowed for development

### Request Validation
- Additional preferences max length: 500 characters
- Pydantic models enforce field constraints

## Run (PowerShell)

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Contract

### POST /api/v1/recommendations

**Request:**
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

**Response:**
```json
{
  "recommendations": [
    {
      "restaurant_name": "Chili's American Grill & Bar",
      "cuisine": "American, Tex-Mex, Burger, BBQ",
      "rating": 4.6,
      "estimated_cost": 1800.0,
      "explanation": "..."
    }
  ],
  "llm_provider_used": "openrouter",
  "fallback_applied": false,
  "filter_strategy": "strict location + strict rating + semi-strict cuisine + flexible budget"
}
```

### GET /api/v1/meta

**Response:**
```json
{
  "max_top_n": 5,
  "min_top_n": 3,
  "allowed_budget_levels": ["low", "medium", "high"],
  "rating_range": {"min": 0.0, "max": 5.0},
  "max_additional_preferences_length": 500
}
```

## P0 Edge Cases Checked
1. Response schema is enforced via Pydantic models
2. Exceptions are sanitized (no stack traces leaked)
3. Request size limits prevent abuse
4. Structured logging for observability

## Outputs
- `phase-7-gate-evidence.md`
- Updated `app/main.py` with v1 endpoints

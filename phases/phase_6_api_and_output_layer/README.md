# Phase 6 - API and Output Layer

This phase validates the API contract, exception handling, and output schema enforcement.

## Goals
- Verify response schema contains all required fields
- Ensure exceptions are sanitized (no stack traces leaked)
- Validate CORS configuration for frontend integration
- Test health endpoint availability

## Compatibility with Phase 5

### Backend Changes
- **CORS Middleware**: Added in Phase 5 to support frontend communication
  - Allows origins: `http://localhost:3000`, `http://127.0.0.1:3000`
  - All methods and headers allowed for development
  - No breaking changes to existing API contract

- **API Schema**: Unchanged from original design
  - Same request/response models
  - Same endpoint structure
  - Compatible with existing tests

### Known Issues
- **Pydantic DLL Blocking**: The original `validate_api_output.py` uses FastAPI TestClient which requires pydantic_core, blocked by Application Control policy
- **Solution**: Created `validate_api_standalone.py` that uses httpx directly, bypassing pydantic dependency

## Run (PowerShell)

### Start Backend First
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Validation
```powershell
py -3.11 .\validate_api_standalone.py
```

## P0 Edge Cases Checked
1. Response schema is enforced
2. Exceptions are sanitized (no stack traces leaked)
3. Health endpoint is accessible

## Outputs
- `phase-6-gate-evidence.md`
- Validation test results

## Test Data Notes
- Tests use Indian locations (e.g., "Bellandur") to match the Zomato dataset
- Original test used "New York" which would return no results with this dataset

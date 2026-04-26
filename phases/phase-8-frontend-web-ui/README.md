# Phase 8 - Frontend (Web UI)

This phase implements the primary user-facing surface with a preference form and results list using Next.js.

## Goals
- Create modern Next.js frontend with TypeScript
- Map form fields to v1 API JSON schema
- Display recommendations with name, cuisines, rating, estimated cost, AI explanation
- Implement clear empty-state semantics
- Add loading states, validation errors, disabled submit while pending
- Responsive design with Tailwind CSS

## Implementation

### Tech Stack
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React hooks (useState)

### Features
- **Form Fields**: Location, budget band, cuisines, minimum rating, additional text, top_n
- **API Integration**: Calls `POST /api/v1/recommendations`
- **Loading States**: Disabled submit button with loading text
- **Validation**: HTML5 validation + API error handling
- **Results Display**: Cards with restaurant details and AI explanations
- **Empty States**: Clear distinction between "no filter match" and "model returned no grounded picks"
- **Responsive**: Works on mobile, tablet, and desktop

### Data Flow
1. User fills form with preferences
2. Form data mapped to API JSON schema
3. POST request to `/api/v1/recommendations`
4. Display results or error messages
5. Show LLM provider used and fallback status

## Run (PowerShell)

### Backend First
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

The app will open at [http://localhost:3000](http://localhost:3000)

## P0 Edge Cases Checked
1. Form validation before submission
2. Loading states prevent duplicate submissions
3. Error messages displayed clearly
4. Empty states handled appropriately
5. API contract matches v1 schema

## Outputs
- `phase-8-gate-evidence.md`
- Next.js frontend in `frontend/` directory
- Updated main README with frontend setup instructions

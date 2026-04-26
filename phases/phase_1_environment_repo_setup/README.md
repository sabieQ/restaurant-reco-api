# Phase 1 - Environment and Repo Setup

This phase establishes a reproducible local environment with Python 3.11 and env-based secrets handling.

## Goals
- Pin runtime to Python 3.11.
- Create a project virtual environment.
- Install dependencies via `pip`.
- Configure secrets only through environment variables.

## Quick Start (PowerShell)

1) Verify Python 3.11:
```powershell
py -3.11 --version
```

2) Create virtual environment:
```powershell
py -3.11 -m venv .venv
```

3) Activate virtual environment:
```powershell
.\.venv\Scripts\Activate.ps1
```

4) Install dependencies:
```powershell
python -m pip install --upgrade pip
pip install -r ..\..\requirements.txt
```

5) Create env file:
```powershell
copy .env.example .env
```

6) Set API keys in `.env` (do not commit `.env`):
- `OPENROUTER_API_KEY`
- `GROQ_API_KEY`

## Validation
- Runtime pin check:
```powershell
python .\validate_runtime.py
```

- App import check:
```powershell
python -c "from app.main import app; print(app.title)"
```

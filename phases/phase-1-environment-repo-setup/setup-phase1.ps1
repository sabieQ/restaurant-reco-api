$ErrorActionPreference = "Stop"

Write-Host "Creating Python 3.11 virtual environment..."
py -3.11 -m venv .venv

Write-Host "Activating virtual environment..."
. .\.venv\Scripts\Activate.ps1

Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

Write-Host "Installing dependencies from root requirements..."
pip install -r ..\..\requirements.txt

Write-Host "Running runtime validation..."
python .\validate_runtime.py

Write-Host "Phase 1 setup complete."

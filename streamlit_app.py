import sys
from pathlib import Path

# Add phases directory to path
sys.path.insert(0, str(Path(__file__).parent / "phases" / "phase-9-streamlit-deployment"))

from app import main

if __name__ == "__main__":
    main()

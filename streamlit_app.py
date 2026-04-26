import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Import from phase-9 app
from phases.phase_9_streamlit_deployment.app import main

if __name__ == "__main__":
    main()

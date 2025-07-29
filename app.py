"""
MedExplain Main Application Entry Point
Run this file to start the Streamlit application
"""

import sys
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the Streamlit app
from medexplain.ui.streamlit_app import main

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Launcher script for the Excel Quotation Analyzer Streamlit application
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit application"""
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("🚀 Starting Excel Quotation Analyzer...")
    print("📂 Working directory:", os.getcwd())
    print("🌐 Opening web browser...")
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main() 
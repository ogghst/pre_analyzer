"""
PRE vs Analisi Profittabilita Cross-Comparator Launcher
Launch the specialized comparison application for PRE and Profittabilita files
"""

import sys
import os
import subprocess
import streamlit
from pathlib import Path

def get_app_path():
    """Get the path to the PRE-Profittabilita comparator app"""
    current_dir = Path(__file__).parent
    app_path = current_dir / "pre_profittabilita_comparator_app.py"
    return str(app_path)

def main():
    """Main launcher function"""
    app_path = get_app_path()
    
    if not os.path.exists(app_path):
        print(f"❌ Error: Application file not found at {app_path}")
        sys.exit(1)
    
    print("🔄 Launching PRE vs Analisi Profittabilita Cross-Comparator...")
    print(f"📁 App location: {app_path}")
    print("🌐 Opening in browser...")
    
    try:
        # Launch Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--theme.base", "light",
            "--theme.primaryColor", "#1f77b4",
            "--theme.backgroundColor", "#ffffff",
            "--theme.secondaryBackgroundColor", "#f0f2f6",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
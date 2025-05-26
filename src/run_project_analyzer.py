"""
Project Structure Analyzer Launcher
Simple launcher for the comprehensive project structure analysis tool
"""

import sys
import os
import subprocess

def main():
    """Launch the Project Structure Analyzer"""
    print("🏗️ Project Structure Analyzer")
    print("=" * 50)
    print("Launching comprehensive project analysis tool...")
    print("=" * 50)
    
    try:
        # Launch the Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "scope_of_supply_analyzer.py",
            "--server.headless", "false",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Project Structure Analyzer stopped by user")
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        print("\n🔧 Alternative launch methods:")
        print("   • streamlit run scope_of_supply_analyzer.py")
        print("   • python streamlit_app.py")

if __name__ == "__main__":
    main() 
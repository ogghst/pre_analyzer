#!/usr/bin/env python3
"""
Simple Unified Excel Analysis & Comparison Application Runner
Basic launcher for the integrated analysis and comparison tool
"""

import os
import sys
import subprocess


def main():
    """Simple main runner function"""
    print("🚀 Starting Unified Excel Analysis & Comparison Tool...")
    print("=" * 60)
    
    # Check if streamlit is available
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} found")
    except ImportError:
        print("❌ Error: Streamlit is not installed")
        print("Please install it using: pip install streamlit")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Get the current directory (should be src)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"📁 Working directory: {current_dir}")
    
    # Change to the script directory
    os.chdir(current_dir)
    
    # Check if the application file exists
    app_file = "scope_of_supply_analyzer.py"
    if not os.path.exists(app_file):
        print(f"❌ Error: {app_file} not found")
        print("Please make sure you're running this from the src directory.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print(f"✅ Found {app_file}")
    print(f"📊 Launching application...")
    print(f"🌐 The application will open in your default web browser")
    print("⏹️  Press Ctrl+C to stop the application")
    print("=" * 60)
    
    try:
        # Simple streamlit run command - let streamlit handle port selection
        cmd = [sys.executable, "-m", "streamlit", "run", app_file]
        
        print("🚀 Starting Streamlit...")
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n⏹️  Application stopped by user")
        
    except FileNotFoundError:
        print("❌ Error: Python or Streamlit not found")
        print("Please make sure Python and Streamlit are installed:")
        print("  pip install streamlit")
        input("Press Enter to exit...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the 'src' directory")
        print("2. Install streamlit: pip install streamlit")
        print("3. Try running directly: streamlit run scope_of_supply_analyzer.py")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main() 
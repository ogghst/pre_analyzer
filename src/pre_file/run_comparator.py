#!/usr/bin/env python3
"""
Simple runner script for the PRE Comparator application
"""

import sys
import os
import subprocess

def check_streamlit_installation():
    """
    Check if streamlit is installed and determine the best way to run it
    Returns: (is_installed, command_to_use)
    """
    # Method 1: Try direct streamlit command
    try:
        result = subprocess.run(["streamlit", "--version"], 
                              capture_output=True, check=True, text=True)
        return True, ["streamlit"]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Method 2: Try python -m streamlit
    try:
        result = subprocess.run([sys.executable, "-m", "streamlit", "--version"], 
                              capture_output=True, check=True, text=True)
        return True, [sys.executable, "-m", "streamlit"]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Method 3: Check if streamlit is importable
    try:
        import streamlit
        # If importable but not runnable, suggest python -m streamlit
        return True, [sys.executable, "-m", "streamlit"]
    except ImportError:
        return False, None

def check_virtual_environment():
    """Check if we're in a virtual environment"""
    return (hasattr(sys, 'real_prefix') or 
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
            os.environ.get('VIRTUAL_ENV'))

def main():
    """Launch the PRE Comparator Streamlit application"""
    # Get the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the comparator app
    app_path = os.path.join(current_dir, "pre_comparator_app.py")
    
    # Check if the app file exists
    if not os.path.exists(app_path):
        print(f"❌ Error: Could not find {app_path}")
        sys.exit(1)
    
    print("🔍 Checking Streamlit installation...")
    
    # Check streamlit installation
    is_installed, streamlit_cmd = check_streamlit_installation()
    
    if not is_installed:
        print("❌ Error: Streamlit is not installed or not accessible")
        print("\n💡 Solutions:")
        
        # Check if we're in a virtual environment
        if check_virtual_environment():
            print("🔧 You're in a virtual environment. Try:")
            print("   pip install streamlit")
            print("   OR")
            print("   python -m pip install streamlit")
        else:
            print("🔧 Install Streamlit:")
            print("   pip install streamlit")
            print("   OR")
            print("   python -m pip install streamlit")
        
        print("\n🔄 Alternative: Run directly with:")
        print(f"   python -m streamlit run {os.path.basename(app_path)}")
        sys.exit(1)
    
    # Determine which command worked
    if streamlit_cmd == ["streamlit"]:
        print("✅ Found streamlit command")
    else:
        print("✅ Found streamlit via python module")
    
    print("🚀 Launching PRE File Comparator...")
    print(f"📁 App location: {app_path}")
    print("🌐 The app will open in your default browser")
    print("⏹️  Press Ctrl+C to stop the application")
    print("-" * 50)
    
    # Launch streamlit
    try:
        cmd = streamlit_cmd + ["run", app_path]
        subprocess.run(cmd, cwd=current_dir)
    except KeyboardInterrupt:
        print("\n👋 PRE Comparator stopped by user")
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        print(f"\n🔄 Try running manually:")
        print(f"   cd {current_dir}")
        print(f"   python -m streamlit run {os.path.basename(app_path)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
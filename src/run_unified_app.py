#!/usr/bin/env python3
"""
Unified Excel Analysis & Comparison Application Runner
Launches the integrated analysis and comparison tool
"""

import os
import sys
import subprocess
import socket
import time
from pathlib import Path


def get_project_root():
    """Get the project root directory"""
    return Path(__file__).parent


def is_port_available(port, host='127.0.0.1'):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)  # 1 second timeout
            result = sock.connect_ex((host, port))
            return result != 0  # Port is available if connection fails
    except Exception:
        return True  # Assume available if we can't test


def find_available_port(start_port=8501, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    return start_port  # Return the default port if nothing else works


def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import streamlit
        return True, streamlit.__version__
    except ImportError:
        return False, None


def main():
    """Main runner function"""
    print("🚀 Starting Unified Excel Analysis & Comparison Tool...")
    print("=" * 60)
    
    # Check dependencies first
    deps_ok, streamlit_version = check_dependencies()
    if not deps_ok:
        print("❌ Error: Streamlit is not installed")
        print("Please install it using: pip install streamlit")
        sys.exit(1)
    
    print(f"✅ Streamlit {streamlit_version} found")
    
    # Get project directory
    project_dir = get_project_root()
    print(f"📁 Working directory: {project_dir}")
    
    # Change to project directory
    os.chdir(project_dir)
    
    # Application file
    app_file = "scope_of_supply_analyzer.py"
    
    if not os.path.exists(app_file):
        print(f"❌ Error: {app_file} not found in {project_dir}")
        print("Please make sure you're running this script from the correct directory.")
        sys.exit(1)
    
    print(f"✅ Found {app_file}")
    
    # Find available port
    print("🔍 Checking for available port...")
    port = find_available_port(8501)
    
    if port != 8501:
        print(f"⚠️  Port 8501 may be in use, trying port {port}")
    else:
        print(f"✅ Using port {port}")
    
    print(f"📊 Launching {app_file}...")
    print(f"🌐 The application will open in your default web browser")
    print(f"📍 URL: http://localhost:{port}")
    print("⏹️  Press Ctrl+C to stop the application")
    print("=" * 60)
    
    try:
        # Launch streamlit app with improved error handling
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            app_file,
            "--server.port", str(port),
            "--server.headless", "false",
            "--server.runOnSave", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        print(f"🚀 Executing: streamlit run {app_file} --server.port {port}")
        
        # Try to run directly first (simpler approach)
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            if "Permission" in str(e) or "10013" in str(e):
                # Try a different port
                print(f"⚠️  Port {port} failed, trying port {port + 1}")
                cmd[cmd.index(str(port))] = str(port + 1)
                print(f"🔄 Retrying with port {port + 1}")
                subprocess.run(cmd, check=True)
            else:
                raise
            
    except KeyboardInterrupt:
        print("\n⏹️  Application stopped by user")
        
    except FileNotFoundError:
        print("❌ Error: Python or Streamlit not found in PATH")
        print("Please make sure Python and Streamlit are properly installed")
        print("Try: pip install streamlit")
        sys.exit(1)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching application:")
        if "Permission" in str(e) or "10013" in str(e):
            print("   This appears to be a permission or port conflict issue.")
            print("   Try the following solutions:")
            print("   1. Run as administrator")
            print("   2. Close other Streamlit applications")
            print("   3. Restart your computer")
            print("   4. Try running: streamlit run scope_of_supply_analyzer.py --server.port 8502")
        else:
            print(f"   {e}")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please check your Python environment and try again")
        print("You can also try running directly:")
        print("streamlit run scope_of_supply_analyzer.py")
        sys.exit(1)


if __name__ == "__main__":
    main() 
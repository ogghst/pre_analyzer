"""
Runner script for Analisi Profittabilita Comparator Application
Launches the Streamlit app with proper configuration and error handling
"""

import subprocess
import sys
import os
import time
from pathlib import Path


class ProfittabilitaComparatorRunner:
    """Runner class for the Analisi Profittabilita Comparator application"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.app_file = self.script_dir / "profittabilita_comparator_app.py"
        
    def check_streamlit_availability(self) -> bool:
        """Check if Streamlit is available"""
        try:
            import streamlit
            return True
        except ImportError:
            return False
    
    def run_with_streamlit_command(self) -> bool:
        """Try to run using streamlit command"""
        try:
            print("🚀 Launching Analisi Profittabilita Comparator with streamlit command...")
            cmd = ["streamlit", "run", str(self.app_file), "--server.address", "localhost", "--server.port", "8502"]
            
            # Change to the script directory
            os.chdir(self.script_dir)
            
            result = subprocess.run(cmd, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"❌ Failed to run with streamlit command: {e}")
            return False
    
    def run_with_python_module(self) -> bool:
        """Try to run using python -m streamlit"""
        try:
            print("🚀 Launching Analisi Profittabilita Comparator with python -m streamlit...")
            cmd = [sys.executable, "-m", "streamlit", "run", str(self.app_file), "--server.address", "localhost", "--server.port", "8502"]
            
            # Change to the script directory
            os.chdir(self.script_dir)
            
            result = subprocess.run(cmd, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"❌ Failed to run with python -m streamlit: {e}")
            return False
    
    def print_help_message(self):
        """Print helpful information for manual setup"""
        print("\n" + "="*60)
        print("🔧 MANUAL SETUP INSTRUCTIONS")
        print("="*60)
        print("\nIf the automatic launcher failed, you can run the comparator manually:")
        print("\n1. Open a terminal/command prompt")
        print(f"2. Navigate to: {self.script_dir}")
        print("3. Run one of these commands:")
        print(f"   • streamlit run profittabilita_comparator_app.py --server.port 8502")
        print(f"   • python -m streamlit run profittabilita_comparator_app.py --server.port 8502")
        print("\n4. Open your browser to: http://localhost:8502")
        print("\n" + "="*60)
        print("📋 REQUIREMENTS:")
        print("="*60)
        print("Make sure you have installed:")
        print("• streamlit")
        print("• pandas")
        print("• plotly")
        print("• openpyxl")
        print("\nInstall with: pip install streamlit pandas plotly openpyxl")
        print("="*60)
    
    def run(self):
        """Main run method that tries different approaches"""
        print("🔄 Analisi Profittabilita Comparator Launcher")
        print("="*50)
        
        # Check if the app file exists
        if not self.app_file.exists():
            print(f"❌ Error: App file not found at {self.app_file}")
            return False
        
        # Check if Streamlit is available
        if not self.check_streamlit_availability():
            print("❌ Error: Streamlit is not installed or not available")
            print("Install with: pip install streamlit")
            return False
        
        print(f"📁 Working directory: {self.script_dir}")
        print(f"📄 App file: {self.app_file.name}")
        print(f"🌐 Will launch on: http://localhost:8502")
        print()
        
        # Try different launch methods
        success = False
        
        # Method 1: Direct streamlit command
        if not success:
            success = self.run_with_streamlit_command()
        
        # Method 2: Python module approach
        if not success:
            success = self.run_with_python_module()
        
        # If all methods failed, provide help
        if not success:
            print("\n❌ All automatic launch methods failed!")
            self.print_help_message()
            return False
        
        return True


def main():
    """Main entry point"""
    try:
        runner = ProfittabilitaComparatorRunner()
        success = runner.run()
        
        if success:
            print("\n✅ Analisi Profittabilita Comparator launched successfully!")
        else:
            print("\n❌ Failed to launch Analisi Profittabilita Comparator automatically.")
            print("Please follow the manual instructions above.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Analisi Profittabilita Comparator launcher interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error occurred: {e}")
        print("Please try running the application manually.")


if __name__ == "__main__":
    main() 
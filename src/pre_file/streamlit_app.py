"""
Streamlit Application for Excel Analysis - Updated Architecture
Entry point that uses the refactored modular components
"""

import streamlit as st
import sys
import os

# Add the current directory to the path so we can import the refactored app
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import and run the refactored app
try:
    from streamlit_app_refactored import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    st.error(f"Failed to import refactored application: {e}")
    st.info("Please ensure all component files are properly installed.")
    
    # Fallback info
    st.markdown("""
    ## 📊 Excel Industrial Equipment Analyzer
    
    **Refactored Application Architecture**
    
    This application has been updated with a modular architecture:
    
    ### 🏗️ New Structure:
    - **`components/file_processor.py`**: Handles file upload and parsing
    - **`components/analyzers/`**: Separate analyzers for different file types
      - `base_analyzer.py`: Common functionality
      - `pre_analyzer.py`: PRE quotation analysis
      - `profittabilita_analyzer.py`: Analisi Profittabilita analysis
    - **`components/ui_components.py`**: Reusable UI elements
    - **`streamlit_app_refactored.py`**: Main application controller
    
    ### ✨ Key Improvements:
    - 🎯 **Dual Parser Support**: PRE files and Analisi Profittabilita files
    - 🧩 **Modular Design**: Better separation of responsibilities  
    - 📊 **Enhanced Visualizations**: Type-specific analysis views
    - 🔍 **Comprehensive Analysis**: 81+ fields for profitability files
    - 💾 **Smart Export**: File-type aware JSON export
    
    ### 🚀 Features by File Type:
    
    **PRE Quotation Files:**
    - Project parameters and customer info
    - Financial analysis with fees calculation  
    - Equipment vs installation breakdown
    - Traditional quotation views
    
    **Analisi Profittabilita Files:**
    - Complete 81-column field extraction
    - UTM time tracking analysis
    - Engineering and manufacturing workflows
    - Field activities and logistics
    - Profitability and margin analysis
    - Comprehensive field usage statistics
    
    **Please check the component files are properly installed.**
    """) 
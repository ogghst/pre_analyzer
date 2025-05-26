"""
Project Structure Analyzer Application
Main entry point for the comprehensive project structure analysis tool
"""

import streamlit as st
import sys
import os

# Add the current directory to the path so we can import the application
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import and run the unified application
try:
    from scope_of_supply_analyzer import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    st.error(f"Failed to import unified application: {e}")
    st.info("Please ensure all component files are properly installed.")
    
    # Fallback info with updated features
    st.markdown("""
    ## 🏗️ Project Structure Analyzer
    
    **Comprehensive Project Structure Analysis Tool**
    
    This application provides a unified solution for analysis, comparison, and cross-validation of industrial equipment files.
    
    ### 🎯 Available Operations:
    
    #### 📊 Single File Analysis
    - **Analyze PRE File**: Complete analysis of PRE quotation files with financial breakdowns
    - **Analyze Analisi Profittabilita**: Comprehensive profitability analysis with UTM, WBE, and cost elements
    
    #### 🔄 File Comparison
    - **Compare Two PRE Files**: Side-by-side comparison of quotation parameters and financial differences
    - **Compare Two Profittabilita Files**: Advanced comparison focusing on WBE, cost elements, UTM, and equipment types
    
    #### 🔗 Cross-File Analysis
    - **Cross-Compare PRE vs Profittabilita**: Advanced cross-validation between quotation and profitability data with WBE impact analysis
    
    ### ✨ Key Features:
    
    **Unified Interface:**
    - 🎯 **Operation Selection**: Choose between analysis and comparison modes
    - 📁 **Smart File Upload**: Automatic file type detection and processing
    - 🔄 **Reset Function**: Return to initial state and switch between operations
    - 📊 **Status Indicators**: Real-time feedback on file loading and processing status
    
    **Analysis Capabilities:**
    - 📈 **Financial Analysis**: Margin calculations and cost breakdowns
    - 🏗️ **Tree Structure**: Hierarchical visualization of data structure
    - 📋 **Field Analysis**: Usage statistics and completeness metrics
    - ⏱️ **UTM Time Tracking**: Manufacturing process analysis
    - 🏷️ **WBE Analysis**: Work Breakdown Element cost aggregation
    
    **Comparison Features:**
    - 🔍 **Difference Detection**: Configurable thresholds for change identification
    - 📊 **Visual Comparisons**: Side-by-side charts and tables
    - 💰 **Cost Impact Analysis**: Financial difference calculations
    - 📄 **Summary Reports**: Automated insights and recommendations
    - 🎯 **Specialized Views**: Type-specific comparison modes
    
    ### 🏗️ Architecture:
    
    **Modular Design:**
    - **`scope_of_supply_analyzer.py`**: Main unified application controller
    - **`components/file_processor.py`**: File upload and parsing logic
    - **`components/ui_components.py`**: Reusable UI elements and styling
    - **`components/analyzers/`**: Analysis and comparison engines
      - `pre_analyzer.py`: PRE quotation analysis
      - `profittabilita_analyzer.py`: Analisi Profittabilita analysis
      - `pre_comparator.py`: PRE file comparison
      - `profittabilita_comparator.py`: Profitability file comparison
    - **`parsers/`**: File format processors
      - `pre_file_parser.py`: PRE file parsing
      - `analisi_profittabilita_parser.py`: Profitability file parsing
    
    ### 🚀 Quick Start:
    
    **Option 1 - Python Runner:**
    ```bash
    cd src
    python run_unified_app.py
    ```
    
    **Option 2 - Windows Batch:**
    ```bash
    cd src
    run_unified_app.bat
    ```
    
    **Option 3 - Direct Launch:**
    ```bash
    cd src
    streamlit run scope_of_supply_analyzer.py
    ```
    
    ### 📋 Supported Files:
    
    - **PRE Quotation Files**: Standard quotation structure with project parameters
    - **Analisi Profittabilita Files**: 81+ column profitability analysis format
    - **Formats**: .xlsx, .xls, .xlsm Excel files
    
    ### 🔧 Operation Modes:
    
    1. **Select Operation**: Choose from 4 available operation modes
    2. **Upload Files**: Single file for analysis, dual files for comparison
    3. **Explore Results**: Navigate through analysis or comparison views
    4. **Export Data**: Download processed results (analysis mode)
    5. **Reset**: Start over with new operation or files
    
    **Please check that all component files are properly installed and try launching the application.**
    """) 
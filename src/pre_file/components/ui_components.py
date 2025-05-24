"""
UI Components
Reusable UI components for the Streamlit Excel Analyzer
"""

import streamlit as st
import json
from typing import Dict, Any, Optional, List
from .file_processor import FileType


def render_app_header():
    """Render the main application header"""
    st.title("📊 Excel Industrial Equipment Analyzer")
    st.markdown("### Interactive Analysis of PRE Quotations & Profitability Files")
    
    # Add description expander
    with st.expander("ℹ️ About this Application"):
        st.markdown("""
        **Multi-Parser Excel Analyzer** supports two types of industrial equipment files:
        
        🔹 **PRE Quotation Files**: Commercial quotations with pricing, parameters, and financial analysis  
        🔹 **Analisi Profittabilita Files**: Comprehensive cost analysis with 81+ fields including UTM, engineering, manufacturing, and field activities
        
        **Key Features:**
        - 🎯 **Auto-detection** of file types
        - 📊 **Interactive visualizations** with Plotly charts
        - 🔍 **Advanced filtering** and search capabilities
        - 💰 **Financial analysis** and profitability metrics
        - 📈 **Field usage analysis** for comprehensive data insights
        - 💾 **JSON export** of processed data
        """)


def render_navigation_sidebar(analyzer, current_view: str) -> Optional[str]:
    """
    Render navigation sidebar with file-specific analysis options
    
    Args:
        analyzer: Current analyzer instance
        current_view: Currently selected view
        
    Returns:
        Selected analysis view
    """
    st.sidebar.header("🧭 Navigation")
    
    if analyzer is None:
        st.sidebar.info("Upload and process a file to enable navigation.")
        return None
    
    # Get available views from analyzer
    analysis_views = analyzer.get_analysis_views()
    
    # Display file type info
    file_processor = st.session_state.get('file_processor')
    if file_processor and file_processor.is_data_loaded():
        file_info = file_processor.get_file_info()
        file_type = file_processor.get_current_file_type()
        
        if file_type == FileType.PRE_FILE:
            st.sidebar.success("📋 **PRE Quotation File**")
        elif file_type == FileType.ANALISI_PROFITTABILITA:
            st.sidebar.success("💹 **Analisi Profittabilita File**")
        
        st.sidebar.caption(f"File: {file_info.get('name', 'Unknown')}")
    
    # Navigation radio buttons
    selected_view = st.sidebar.radio(
        "Select Analysis View",
        analysis_views,
        index=analysis_views.index(current_view) if current_view in analysis_views else 0,
        key="navigation_radio"
    )
    
    return selected_view


def render_export_section(data: Dict[str, Any], file_type: Optional[FileType] = None):
    """
    Render export section in sidebar
    
    Args:
        data: Data to export
        file_type: Type of file being exported
    """
    st.sidebar.markdown("---")
    st.sidebar.header("💾 Export")
    
    if data:
        # Generate filename based on file type
        if file_type == FileType.PRE_FILE:
            filename = f"pre_quotation_{data.get('project', {}).get('id', 'export')}.json"
        elif file_type == FileType.ANALISI_PROFITTABILITA:
            filename = f"profittabilita_{data.get('project', {}).get('id', 'export')}.json"
        else:
            filename = "export_data.json"
        
        # Clean filename
        filename = filename.replace(' ', '_').replace('/', '_')
        
        # JSON export
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        st.sidebar.download_button(
            label="📄 Download JSON",
            data=json_str,
            file_name=filename,
            mime="application/json",
            help="Download the processed data as JSON file",
            use_container_width=True
        )
        
        # Display file stats
        with st.sidebar.expander("📊 Export Info"):
            st.write(f"**File size:** {len(json_str):,} characters")
            st.write(f"**Groups:** {len(data.get('product_groups', []))}")
            
            total_items = sum(
                len(cat.get('items', [])) 
                for group in data.get('product_groups', []) 
                for cat in group.get('categories', [])
            )
            st.write(f"**Total items:** {total_items}")
    else:
        st.sidebar.info("No data available for export.")


def render_debug_info():
    """Render debug information in sidebar"""
    with st.sidebar.expander("🔍 Debug Info"):
        # Session state info
        st.write("**Session State:**")
        if hasattr(st.session_state, 'file_processor'):
            processor = st.session_state.file_processor
            st.write(f"- Data loaded: {processor.is_data_loaded()}")
            if processor.is_data_loaded():
                file_info = processor.get_file_info()
                st.write(f"- File type: {file_info.get('type', 'Unknown')}")
                st.write(f"- File size: {file_info.get('size', 0):,} bytes")
        else:
            st.write("- No file processor in session")
        
        # Memory usage
        import sys
        st.write(f"**Memory:** {sys.getsizeof(st.session_state):,} bytes")


def render_error_message(error: str, details: Optional[str] = None):
    """
    Render formatted error message
    
    Args:
        error: Main error message
        details: Optional detailed error information
    """
    st.error(f"❌ {error}")
    
    if details:
        with st.expander("🔍 Error Details"):
            st.code(details, language="text")


def render_success_message(message: str, details: Optional[Dict[str, Any]] = None):
    """
    Render formatted success message
    
    Args:
        message: Success message
        details: Optional additional information to display
    """
    st.success(f"✅ {message}")
    
    if details:
        with st.expander("ℹ️ Details"):
            for key, value in details.items():
                st.write(f"**{key}:** {value}")


def render_info_box(title: str, content: str, icon: str = "ℹ️"):
    """
    Render formatted info box
    
    Args:
        title: Box title
        content: Box content
        icon: Icon to display
    """
    st.info(f"{icon} **{title}**\n\n{content}")


def render_warning_box(title: str, content: str):
    """
    Render formatted warning box
    
    Args:
        title: Warning title
        content: Warning content
    """
    st.warning(f"⚠️ **{title}**\n\n{content}")


def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app"""
    st.markdown("""
    <style>
        /* Main container styling */
        .main > div {
            padding-top: 2rem;
        }
        
        /* Metric boxes */
        .stMetric {
            border: 1px solid #e1e5f0;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        
        /* File upload area */
        .uploadedFile {
            border: 2px dashed #e1e5f0;
            border-radius: 0.5rem;
            padding: 2rem;
            text-align: center;
        }
        
        /* Navigation styling */
        .sidebar .stRadio > div {
            gap: 0.5rem;
        }
        
        /* Tree structure styling */
        .tree-item {
            margin-left: 20px;
            padding: 5px;
            border-left: 2px solid #e1e5f0;
        }
        
        .group-header {
            font-weight: bold;
            color: #1f77b4;
            font-size: 1.1em;
        }
        
        .category-header {
            font-weight: bold;
            color: #ff7f0e;
            margin-left: 10px;
        }
        
        .item-text {
            color: #2ca02c;
            margin-left: 20px;
            font-size: 0.9em;
        }
        
        /* Success/Error message styling */
        .success-box {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        
        .error-box {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        
        /* Chart container improvements */
        .plotly-chart {
            border: 1px solid #e1e5f0;
            border-radius: 0.5rem;
            padding: 0.5rem;
        }
        
        /* Dataframe styling */
        .dataframe {
            border: 1px solid #e1e5f0;
            border-radius: 0.5rem;
        }
        
        /* Sidebar improvements */
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 0.5rem;
            border: 1px solid #dee2e6;
            transition: all 0.2s;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #f8f9fa;
            border-radius: 0.5rem;
        }
        
        /* Footer styling */
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f8f9fa;
            color: #6c757d;
            text-align: center;
            padding: 10px;
            font-size: 12px;
        }
    </style>
    """, unsafe_allow_html=True)


def render_welcome_screen():
    """Render welcome screen when no data is loaded"""
    st.markdown("""
    ## 🚀 Welcome to Excel Industrial Equipment Analyzer
    
    This application supports **dual-parser analysis** for industrial equipment files.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📋 PRE Quotation Files
        - **Commercial quotations** with pricing analysis
        - **Project parameters** (DOC %, PM %, financial costs)
        - **Fee calculations** and grand totals
        - **Customer information** and currency handling
        - **Equipment vs Installation** cost breakdown
        """)
    
    with col2:
        st.markdown("""
        ### 💹 Analisi Profittabilita Files
        - **Comprehensive cost analysis** with 81+ fields
        - **UTM tracking** (Robot, LGV, Intra, Layout)
        - **Engineering fields** (UTE, BA, SW-PC, SW-PLC)
        - **Manufacturing & Testing** workflows
        - **Field activities** and logistics
        - **Margin analysis** and profitability metrics
        """)
    
    st.markdown("""
    ---
    ### 🎯 Key Features
    
    **📤 Smart File Detection**: Automatically detects file type based on content and filename patterns
    
    **📊 Rich Visualizations**: Interactive charts, treemaps, and profitability gauges
    
    **🔍 Advanced Analysis**: 
    - Hierarchical tree views of product structures
    - Financial breakdowns and margin analysis
    - UTM time tracking and cost analysis
    - Comprehensive field usage statistics
    
    **💾 Export Capabilities**: Download processed data as structured JSON
    
    ---
    
    **Getting Started:**
    1. 📁 Upload your Excel file using the sidebar
    2. 🚀 Click "Process File" to analyze the data
    3. 🧭 Use navigation to explore different analysis views
    4. 🔍 Apply filters and search to focus on specific data
    5. 💾 Export results for further analysis
    """)
    
    # Sample data structure
    with st.expander("📋 Supported File Formats"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**PRE Files:**")
            st.code("""
            - PRE_ONLY_OFFER*.xlsx
            - Contains quotation data
            - Groups with TXT- prefix
            - Commercial pricing focus
            """)
        
        with col2:
            st.markdown("**Profittabilita Files:**")
            st.code("""
            - *analisi*profittabilita*.xlsx
            - Contains cost analysis
            - Groups with TXT prefix
            - 81 columns of detailed data
            """)


def render_footer():
    """Render application footer"""
    st.markdown("""
    ---
    <div style='text-align: center; color: #6c757d; font-size: 12px; padding: 20px;'>
        📊 Excel Industrial Equipment Analyzer | Dual-Parser Support for PRE & Profittabilita Files
    </div>
    """, unsafe_allow_html=True) 
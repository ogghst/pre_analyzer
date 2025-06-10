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
    """Apply custom CSS styling to the Streamlit app with modern dark theme"""
    st.markdown("""
    <style>
        /* Global font size reduction for professional look */
        .main .block-container {
            font-size: 14px;
            line-height: 1.4;
        }
        
        /* Main container styling */
        .main > div {
            padding-top: 1.5rem;
        }
        
        /* Reduce font sizes across components */
        .stMarkdown, .stText, .stCaption {
            font-size: 13px !important;
        }
        
        /* Headers with smaller fonts */
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.3rem !important; }
        h4 { font-size: 1.1rem !important; }
        
        /* Metric boxes with dark theme */
        .stMetric {
            background-color: #1E1E1E;
            border: 1px solid #333;
            padding: 0.8rem;
            border-radius: 8px;
            margin: 0.4rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .stMetric label {
            font-size: 12px !important;
            color: #B0B0B0;
        }
        
        .stMetric div[data-testid="metric-container"] > div {
            font-size: 18px !important;
            color: #00D4FF;
        }
        
        /* File upload area */
        .uploadedFile {
            border: 2px dashed #333;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            background-color: #1A1A1A;
        }
        
        /* Navigation styling */
        .sidebar .stRadio > div {
            gap: 0.3rem;
        }
        
        .sidebar .stRadio label {
            font-size: 13px !important;
        }
        
        /* Tree structure styling with dark theme */
        .tree-item {
            margin-left: 15px;
            padding: 3px;
            border-left: 2px solid #333;
            font-size: 12px;
        }
        
        .group-header {
            font-weight: 600;
            color: #00D4FF;
            font-size: 14px !important;
        }
        
        .category-header {
            font-weight: 600;
            color: #FF6B6B;
            margin-left: 8px;
            font-size: 13px !important;
        }
        
        .item-text {
            color: #4ECDC4;
            margin-left: 15px;
            font-size: 12px !important;
        }
        
        /* Success/Error message styling for dark theme */
        .success-box {
            background-color: #1B4332;
            border: 1px solid #2D6A4F;
            color: #52B788;
            padding: 0.8rem;
            border-radius: 8px;
            margin: 0.8rem 0;
            font-size: 13px;
        }
        
        .error-box {
            background-color: #641220;
            border: 1px solid #A4161A;
            color: #FFB3BA;
            padding: 0.8rem;
            border-radius: 8px;
            margin: 0.8rem 0;
            font-size: 13px;
        }
        
        /* Chart container improvements */
        .plotly-chart {
            border: 1px solid #333;
            border-radius: 8px;
            padding: 0.5rem;
            background-color: #1A1A1A;
        }
        
        /* Dataframe styling for dark theme */
        .dataframe {
            border: 1px solid #333;
            border-radius: 8px;
            background-color: #1A1A1A;
            font-size: 12px !important;
        }
        
        /* Dataframe headers */
        .dataframe th {
            background-color: #2A2A2A !important;
            color: #FAFAFA !important;
            font-size: 12px !important;
            padding: 6px !important;
        }
        
        .dataframe td {
            background-color: #1A1A1A !important;
            color: #E0E0E0 !important;
            font-size: 11px !important;
            padding: 4px !important;
        }
        
        /* Button styling with modern dark theme */
        .stButton > button {
            border-radius: 8px;
            border: 1px solid #333;
            background-color: #2A2A2A;
            color: #FAFAFA;
            font-size: 13px !important;
            padding: 0.4rem 0.8rem;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            background-color: #00D4FF;
            color: #0E1117;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,212,255,0.3);
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #2A2A2A;
            border-radius: 8px;
            font-size: 14px !important;
        }
        
        /* Selectbox and input styling */
        .stSelectbox > div > div {
            background-color: #2A2A2A;
            border: 1px solid #333;
            border-radius: 6px;
            font-size: 13px !important;
        }
        
        .stTextInput > div > div > input {
            background-color: #2A2A2A;
            border: 1px solid #333;
            border-radius: 6px;
            color: #FAFAFA;
            font-size: 13px !important;
        }
        
        /* Progress bar styling */
        .stProgress > div > div > div {
            background-color: #00D4FF;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #2A2A2A;
            border-radius: 6px;
            font-size: 13px !important;
            padding: 6px 12px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #00D4FF;
            color: #0E1117;
        }
        
        /* Footer styling */
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #1A1A1A;
            color: #808080;
            text-align: center;
            padding: 8px;
            font-size: 11px;
            border-top: 1px solid #333;
        }
        
        /* Sidebar enhancements */
        .css-1d391kg {
            background-color: #1C1C1C;
        }
        
        /* Custom scrollbar for dark theme */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #1A1A1A;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #333;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #00D4FF;
        }
        
        /* Alert styling for dark theme */
        .stAlert {
            font-size: 13px !important;
        }
        
        /* Code block styling */
        .stCode {
            background-color: #1A1A1A !important;
            border: 1px solid #333 !important;
            font-size: 12px !important;
        }
        
        /* Table alternating row colors */
        .stDataFrame tbody tr:nth-child(even) {
            background-color: #1E1E1E !important;
        }
        
        .stDataFrame tbody tr:nth-child(odd) {
            background-color: #1A1A1A !important;
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
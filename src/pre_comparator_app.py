"""
PRE File Comparator Streamlit Application
Compare two PRE quotation files and show differences
"""

import streamlit as st
import traceback
import os
import tempfile
from typing import Optional, Tuple, Dict, Any

# Import components
from components.file_processor import FileType, FileProcessor
from components.ui_components import (
    render_app_header, 
    render_error_message,
    apply_custom_css,
    render_footer
)
from components.analyzers.pre_comparator import PreComparator

# Import parsers directly
from pre_file_parser import parse_excel_to_json


class PreComparatorApp:
    """Main application class for the PRE file comparator"""
    
    def __init__(self):
        self.comparator = None
        self.data1 = None
        self.data2 = None
        self.file1_name = None
        self.file2_name = None
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'comparison_view' not in st.session_state:
            st.session_state.comparison_view = "Project Comparison"
        if 'comparator_initialized' not in st.session_state:
            st.session_state.comparator_initialized = False
        if 'files_uploaded' not in st.session_state:
            st.session_state.files_uploaded = {'file1': None, 'file2': None}
    
    def process_pre_file(self, uploaded_file) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Process a single PRE file and return data and error message if any"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                temp_file_path = tmp_file.name
            
            try:
                # Parse the file
                data = parse_excel_to_json(temp_file_path)
                return data, None
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            return None, f"Error processing file: {str(e)}"
    
    def render_file_upload_section(self):
        """Render the file upload section for two PRE files"""
        st.sidebar.header("📁 Upload PRE Files")
        
        # File 1 upload
        st.sidebar.subheader("📄 First PRE File")
        uploaded_file1 = st.sidebar.file_uploader(
            "Choose first PRE file",
            type=['xlsx', 'xls', 'xlsm'],
            key="file1_uploader",
            help="Upload the first PRE quotation file for comparison"
        )
        
        # File 2 upload
        st.sidebar.subheader("📄 Second PRE File")
        uploaded_file2 = st.sidebar.file_uploader(
            "Choose second PRE file",
            type=['xlsx', 'xls', 'xlsm'],
            key="file2_uploader",
            help="Upload the second PRE quotation file for comparison"
        )
        
        # Process files
        data1, data2 = None, None
        file1_name, file2_name = None, None
        
        if uploaded_file1 is not None:
            file1_name = uploaded_file1.name
            with st.spinner(f"Processing {file1_name}..."):
                data1, error1 = self.process_pre_file(uploaded_file1)
                
                if data1 is not None:
                    st.sidebar.success(f"✅ {file1_name} loaded successfully")
                else:
                    st.sidebar.error(f"❌ Error processing {file1_name}: {error1}")
        
        if uploaded_file2 is not None:
            file2_name = uploaded_file2.name
            with st.spinner(f"Processing {file2_name}..."):
                data2, error2 = self.process_pre_file(uploaded_file2)
                
                if data2 is not None:
                    st.sidebar.success(f"✅ {file2_name} loaded successfully")
                else:
                    st.sidebar.error(f"❌ Error processing {file2_name}: {error2}")
        
        return data1, data2, file1_name, file2_name
    
    def render_comparison_navigation(self):
        """Render the comparison navigation menu"""
        if self.comparator is not None:
            st.sidebar.markdown("---")
            st.sidebar.header("🔍 Comparison Views")
            
            views = self.comparator.get_comparison_views()
            
            selected_view = st.sidebar.radio(
                "Select comparison view:",
                views,
                index=views.index(st.session_state.comparison_view) if st.session_state.comparison_view in views else 0,
                key="comparison_view_selector"
            )
            
            return selected_view
        
        return None
    
    def render_comparison_view(self, view_name: str):
        """
        Render the selected comparison view
        
        Args:
            view_name: Name of the comparison view to render
        """
        try:
            if view_name == "Project Comparison":
                self.comparator.display_project_comparison()
                
            elif view_name == "Financial Comparison":
                self.comparator.display_financial_comparison()
                
            elif view_name == "Groups Comparison":
                self.comparator.display_groups_comparison()
                
            elif view_name == "Categories Comparison":
                self.comparator.display_categories_comparison()
                
            elif view_name == "Items Comparison":
                self.comparator.display_items_comparison()
                
            elif view_name == "Summary Report":
                self.comparator.display_summary_report()
            
            else:
                st.error(f"Unknown comparison view: {view_name}")
                
        except Exception as e:
            render_error_message(
                f"Error displaying {view_name}",
                f"Exception: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            )
    
    def render_comparison_header(self):
        """Render header showing the files being compared"""
        if self.file1_name and self.file2_name:
            st.markdown("### 🔄 PRE File Comparison")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                st.info(f"**File 1:** {self.file1_name}")
            
            with col2:
                st.markdown("<div style='text-align: center; font-size: 24px;'>VS</div>", unsafe_allow_html=True)
            
            with col3:
                st.info(f"**File 2:** {self.file2_name}")
            
            st.markdown("---")
    
    def render_welcome_screen(self):
        """Render welcome screen when no files are loaded"""
        st.markdown("""
        # 🔄 PRE File Comparator
        
        Welcome to the PRE File Comparator! This tool allows you to compare two PRE quotation files and identify differences.
        
        ## 📋 How to use:
        
        1. **Upload Files**: Use the sidebar to upload two PRE quotation files (.xlsx, .xls, or .xlsm)
        2. **Compare**: Once both files are loaded, select different comparison views from the sidebar
        3. **Analyze**: Review the differences in project details, financial breakdowns, groups, categories, and items
        
        ## 🔍 Available Comparison Views:
        
        - **Project Comparison**: Side-by-side comparison of project parameters and totals
        - **Financial Comparison**: Detailed financial breakdown comparison with charts
        - **Groups Comparison**: Analysis of product groups differences
        - **Categories Comparison**: Category-level comparison with value filtering
        - **Items Comparison**: High-level items statistics comparison
        - **Summary Report**: Comprehensive comparison report with insights and recommendations
        
        ## 📊 Features:
        
        - ✅ Visual side-by-side comparisons
        - ✅ Interactive charts and graphs
        - ✅ Difference highlighting
        - ✅ Financial impact analysis
        - ✅ Automated insights and recommendations
        - ✅ Export capabilities
        
        **Get started by uploading your first PRE file in the sidebar!**
        """)
    
    def run(self):
        """Main application entry point"""
        # Configure Streamlit page
        st.set_page_config(
            page_title="PRE File Comparator",
            page_icon="🔄",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Apply custom styling
        apply_custom_css()
        
        # Initialize session state
        self.initialize_session_state()
        
        # Render main header
        render_app_header()
        
        # Sidebar: File upload and navigation
        with st.sidebar:
            # File upload section
            try:
                data1, data2, file1_name, file2_name = self.render_file_upload_section()
            except Exception as e:
                render_error_message(
                    "Error in file upload section",
                    f"Exception: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                )
                data1, data2, file1_name, file2_name = None, None, None, None
            
            # Update comparator if both files are available
            if data1 is not None and data2 is not None:
                try:
                    self.data1 = data1
                    self.data2 = data2
                    self.file1_name = file1_name or "File 1"
                    self.file2_name = file2_name or "File 2"
                    
                    # Create comparator
                    self.comparator = PreComparator(
                        data1, data2, 
                        self.file1_name, self.file2_name
                    )
                    st.session_state.comparator_initialized = True
                    
                except Exception as e:
                    render_error_message(
                        "Failed to initialize comparator",
                        f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                    )
                    self.comparator = None
                    st.session_state.comparator_initialized = False
            
            # Navigation (only if comparator is available)
            if self.comparator is not None:
                try:
                    selected_view = self.render_comparison_navigation()
                    
                    if selected_view and selected_view != st.session_state.comparison_view:
                        st.session_state.comparison_view = selected_view
                        st.rerun()
                    
                except Exception as e:
                    render_error_message(
                        "Error in navigation",
                        f"Exception: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                    )
            
            # Status section
            st.sidebar.markdown("---")
            st.sidebar.header("📊 Status")
            
            file1_status = "✅ Loaded" if data1 is not None else "❌ Not loaded"
            file2_status = "✅ Loaded" if data2 is not None else "❌ Not loaded"
            comparison_status = "✅ Ready" if self.comparator is not None else "❌ Not ready"
            
            st.sidebar.write(f"**File 1:** {file1_status}")
            st.sidebar.write(f"**File 2:** {file2_status}")
            st.sidebar.write(f"**Comparison:** {comparison_status}")
            
            if data1 is not None and data2 is not None:
                st.sidebar.success("🎉 Ready for comparison!")
            elif data1 is not None or data2 is not None:
                st.sidebar.warning("⚠️ Upload second file to start comparison")
            else:
                st.sidebar.info("ℹ️ Upload both files to begin")
        
        # Main content area
        if (self.comparator is not None and 
            self.data1 is not None and 
            self.data2 is not None and
            st.session_state.comparator_initialized):
            
            # Show comparison header
            self.render_comparison_header()
            
            # Render selected comparison view
            current_view = st.session_state.comparison_view
            self.render_comparison_view(current_view)
            
        else:
            # Welcome screen when files are not loaded
            self.render_welcome_screen()
        
        # Footer
        render_footer()


def main():
    """Application entry point"""
    try:
        app = PreComparatorApp()
        app.run()
    except Exception as e:
        st.error("Critical application error occurred.")
        with st.expander("🔍 Error Details"):
            st.error(f"Exception: {str(e)}")
            st.code(traceback.format_exc(), language="text")


if __name__ == "__main__":
    main() 
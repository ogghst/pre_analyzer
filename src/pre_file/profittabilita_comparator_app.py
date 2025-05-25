"""
Analisi Profittabilita Comparator Streamlit Application
Compare two Analisi Profittabilita files and show differences in WBE, cost elements, and types
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
from components.analyzers.profittabilita_comparator import ProfittabilitaComparator

# Import parsers directly
from analisi_profittabilita_parser import parse_analisi_profittabilita_to_json


class ProfittabilitaComparatorApp:
    """Main application class for the Analisi Profittabilita file comparator"""
    
    def __init__(self):
        self.comparator = None
        self.data1 = None
        self.data2 = None
        self.file1_name = None
        self.file2_name = None
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'profittabilita_comparison_view' not in st.session_state:
            st.session_state.profittabilita_comparison_view = "Project Comparison"
        if 'profittabilita_comparator_initialized' not in st.session_state:
            st.session_state.profittabilita_comparator_initialized = False
        if 'profittabilita_files_uploaded' not in st.session_state:
            st.session_state.profittabilita_files_uploaded = {'file1': None, 'file2': None}
    
    def process_profittabilita_file(self, uploaded_file) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Process a single Analisi Profittabilita file and return data and error message if any"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                temp_file_path = tmp_file.name
            
            try:
                # Parse the file
                data = parse_analisi_profittabilita_to_json(temp_file_path)
                return data, None
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            return None, f"Error processing file: {str(e)}"
    
    def render_file_upload_section(self):
        """Render the file upload section for two Analisi Profittabilita files"""
        st.sidebar.header("📁 Upload Analisi Profittabilita Files")
        
        # File 1 upload
        st.sidebar.subheader("📄 First Profittabilita File")
        uploaded_file1 = st.sidebar.file_uploader(
            "Choose first Analisi Profittabilita file",
            type=['xlsx', 'xls', 'xlsm'],
            key="profittabilita_file1_uploader",
            help="Upload the first Analisi Profittabilita file for comparison"
        )
        
        # File 2 upload
        st.sidebar.subheader("📄 Second Profittabilita File")
        uploaded_file2 = st.sidebar.file_uploader(
            "Choose second Analisi Profittabilita file",
            type=['xlsx', 'xls', 'xlsm'],
            key="profittabilita_file2_uploader",
            help="Upload the second Analisi Profittabilita file for comparison"
        )
        
        # Process files
        data1, data2 = None, None
        file1_name, file2_name = None, None
        
        if uploaded_file1 is not None:
            file1_name = uploaded_file1.name
            with st.spinner(f"Processing {file1_name}..."):
                data1, error1 = self.process_profittabilita_file(uploaded_file1)
                
                if data1 is not None:
                    st.sidebar.success(f"✅ {file1_name} loaded successfully")
                else:
                    st.sidebar.error(f"❌ Error processing {file1_name}: {error1}")
        
        if uploaded_file2 is not None:
            file2_name = uploaded_file2.name
            with st.spinner(f"Processing {file2_name}..."):
                data2, error2 = self.process_profittabilita_file(uploaded_file2)
                
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
                index=views.index(st.session_state.profittabilita_comparison_view) if st.session_state.profittabilita_comparison_view in views else 0,
                key="profittabilita_comparison_view_selector"
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
                
            elif view_name == "Profitability Comparison":
                self.comparator.display_profitability_comparison()
                
            elif view_name == "WBE Comparison":
                self.comparator.display_wbe_comparison()
                
            elif view_name == "Cost Elements Comparison":
                self.comparator.display_cost_elements_comparison()
                
            elif view_name == "UTM Comparison":
                self.comparator.display_utm_comparison()
                
            elif view_name == "Engineering Comparison":
                self.comparator.display_engineering_comparison()
                
            elif view_name == "Types Comparison":
                self.comparator.display_types_comparison()
                
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
            st.markdown("### 🔄 Analisi Profittabilita Comparison")
            
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
        # 🔄 Analisi Profittabilita Comparator
        
        Welcome to the Analisi Profittabilita Comparator! This tool allows you to compare two Analisi Profittabilita files and identify differences in WBE, cost elements, and equipment types.
        
        ## 📋 How to use:
        
        1. **Upload Files**: Use the sidebar to upload two Analisi Profittabilita files (.xlsx, .xls, or .xlsm)
        2. **Compare**: Once both files are loaded, select different comparison views from the sidebar
        3. **Analyze**: Review the differences in profitability, WBE elements, cost breakdowns, UTM components, and equipment types
        
        ## 🔍 Available Comparison Views:
        
        - **Project Comparison**: Side-by-side comparison of project parameters and financial totals
        - **Profitability Comparison**: Detailed profitability analysis with cost vs margin breakdown
        - **WBE Comparison**: Analysis of Work Breakdown Elements differences and costs
        - **Cost Elements Comparison**: Comprehensive breakdown of all cost components (Material, UTM, Engineering, etc.)
        - **UTM Comparison**: Focus on UTM time tracking differences (Robot, LGV, Intra, Layout)
        - **Engineering Comparison**: Engineering costs analysis (UTE, BA, Software components)
        - **Types Comparison**: Equipment and category types analysis
        - **Summary Report**: Comprehensive comparison report with insights and recommendations
        
        ## 📊 Key Features:
        
        - ✅ WBE (Work Breakdown Element) analysis and comparison
        - ✅ Detailed cost element breakdown (UTM, UTE, BA, Software, Manufacturing, etc.)
        - ✅ UTM time tracking analysis with visual comparisons
        - ✅ Equipment types and categories comparison
        - ✅ Financial impact analysis with margin calculations
        - ✅ Interactive charts and filtering capabilities
        - ✅ Automated insights and recommendations
        - ✅ Threshold-based difference highlighting
        
        ## 🎯 Focus Areas:
        
        This comparator specializes in highlighting differences in:
        - **WBE Elements**: Work breakdown structure analysis
        - **Cost Components**: UTM, UTE, Material, Engineering, Manufacturing costs
        - **Equipment Types**: Robot/AGV, Conveyor, Storage, Software, etc.
        - **Time Tracking**: UTM Robot, LGV, Intra, Layout hours and costs
        - **Engineering Elements**: UTE, BA, Software PC/PLC/LGV components
        
        **Get started by uploading your first Analisi Profittabilita file in the sidebar!**
        """)
    
    def run(self):
        """Main application entry point"""
        # Configure Streamlit page
        st.set_page_config(
            page_title="Analisi Profittabilita Comparator",
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
                    self.comparator = ProfittabilitaComparator(
                        data1, data2, 
                        self.file1_name, self.file2_name
                    )
                    st.session_state.profittabilita_comparator_initialized = True
                    
                except Exception as e:
                    render_error_message(
                        "Failed to initialize comparator",
                        f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                    )
                    self.comparator = None
                    st.session_state.profittabilita_comparator_initialized = False
            
            # Navigation (only if comparator is available)
            if self.comparator is not None:
                try:
                    selected_view = self.render_comparison_navigation()
                    
                    if selected_view and selected_view != st.session_state.profittabilita_comparison_view:
                        st.session_state.profittabilita_comparison_view = selected_view
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
            st.session_state.profittabilita_comparator_initialized):
            
            # Show comparison header
            self.render_comparison_header()
            
            # Render selected comparison view
            current_view = st.session_state.profittabilita_comparison_view
            self.render_comparison_view(current_view)
            
        else:
            # Welcome screen when files are not loaded
            self.render_welcome_screen()
        
        # Footer
        render_footer()


def main():
    """Application entry point"""
    try:
        app = ProfittabilitaComparatorApp()
        app.run()
    except Exception as e:
        st.error("Critical application error occurred.")
        with st.expander("🔍 Error Details"):
            st.error(f"Exception: {str(e)}")
            st.code(traceback.format_exc(), language="text")


if __name__ == "__main__":
    main() 
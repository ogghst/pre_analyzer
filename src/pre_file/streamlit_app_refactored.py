"""
Refactored Streamlit Application for Excel Analysis
Clean, modular architecture supporting both PRE and Analisi Profittabilita files
"""

import streamlit as st
import traceback
from typing import Optional

# Import components
from components.file_processor import render_file_upload_component, render_file_metrics, FileType
from components.ui_components import (
    render_app_header, 
    render_navigation_sidebar, 
    render_export_section,
    render_debug_info,
    render_error_message,
    apply_custom_css,
    render_welcome_screen,
    render_footer
)
from components.analyzers.pre_analyzer import PreAnalyzer
from components.analyzers.profittabilita_analyzer import ProfittabilitaAnalyzer


class ExcelAnalyzerApp:
    """Main application class for the refactored Excel analyzer"""
    
    def __init__(self):
        self.current_analyzer = None
        self.current_data = None
        self.current_file_type = None
        self.current_view = "Project Summary"
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'current_view' not in st.session_state:
            st.session_state.current_view = self.current_view
        if 'analyzer_initialized' not in st.session_state:
            st.session_state.analyzer_initialized = False
    
    def create_analyzer(self, data, file_type: FileType):
        """
        Create appropriate analyzer based on file type
        
        Args:
            data: Parsed data from file
            file_type: Type of file (PRE or Analisi Profittabilita)
            
        Returns:
            Analyzer instance
        """
        if file_type == FileType.PRE_FILE:
            return PreAnalyzer(data)
        elif file_type == FileType.ANALISI_PROFITTABILITA:
            return ProfittabilitaAnalyzer(data)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def render_analysis_view(self, analyzer, view_name: str):
        """
        Render the selected analysis view
        
        Args:
            analyzer: Current analyzer instance
            view_name: Name of the view to render
        """
        try:
            if view_name == "Project Summary":
                analyzer.display_project_summary()
                
            elif view_name == "Tree Structure":
                analyzer.display_tree_structure()
                
            elif view_name == "Groups Analysis":
                analyzer.display_groups_analysis()
                
            elif view_name == "Categories Analysis":
                analyzer.display_categories_analysis()
                
            elif view_name == "Items Analysis":
                analyzer.display_items_analysis()
                
            elif view_name == "Financial Analysis":
                # Only available for PRE files
                if hasattr(analyzer, 'display_financial_analysis'):
                    analyzer.display_financial_analysis()
                else:
                    st.warning("Financial Analysis is only available for PRE quotation files.")
                    
            elif view_name == "Profitability Analysis":
                # Only available for Analisi Profittabilita files
                if hasattr(analyzer, 'display_profitability_analysis'):
                    analyzer.display_profitability_analysis()
                else:
                    st.warning("Profitability Analysis is only available for Analisi Profittabilita files.")
                    
            elif view_name == "UTM Analysis":
                # Only available for Analisi Profittabilita files
                if hasattr(analyzer, 'display_utm_analysis'):
                    analyzer.display_utm_analysis()
                else:
                    st.warning("UTM Analysis is only available for Analisi Profittabilita files.")
                    
            elif view_name == "WBE Analysis":
                # Only available for Analisi Profittabilita files
                if hasattr(analyzer, 'display_wbe_analysis'):
                    analyzer.display_wbe_analysis()
                else:
                    st.warning("WBE Analysis is only available for Analisi Profittabilita files.")
                    
            elif view_name == "Field Analysis":
                # Only available for Analisi Profittabilita files
                if hasattr(analyzer, 'display_field_analysis'):
                    analyzer.display_field_analysis()
                else:
                    st.warning("Field Analysis is only available for Analisi Profittabilita files.")
            
            else:
                st.error(f"Unknown analysis view: {view_name}")
                
        except Exception as e:
            render_error_message(
                f"Error displaying {view_name}",
                f"Exception: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            )
    
    def run(self):
        """Main application entry point"""
        # Configure Streamlit page
        st.set_page_config(
            page_title="Excel Industrial Equipment Analyzer",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Apply custom styling
        apply_custom_css()
        
        # Initialize session state
        self.initialize_session_state()
        
        # Render main header
        render_app_header()
        
        # Sidebar: File upload and processing
        with st.sidebar:
            # File upload component
            try:
                data, file_type = render_file_upload_component()
            except Exception as e:
                render_error_message(
                    "Error in file upload component",
                    f"Exception: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                )
                data, file_type = None, None
            
            # Update current data and analyzer if new data is available
            if data is not None and file_type is not None:
                try:
                    self.current_data = data
                    self.current_file_type = file_type
                    self.current_analyzer = self.create_analyzer(data, file_type)
                    st.session_state.analyzer_initialized = True
                except Exception as e:
                    render_error_message(
                        "Failed to initialize analyzer",
                        f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                    )
                    self.current_analyzer = None
                    st.session_state.analyzer_initialized = False
            
            # Navigation (only if analyzer is available)
            if self.current_analyzer is not None:
                try:
                    selected_view = render_navigation_sidebar(
                        self.current_analyzer, 
                        st.session_state.current_view
                    )
                    
                    if selected_view != st.session_state.current_view:
                        st.session_state.current_view = selected_view
                        st.rerun()
                    
                    # Export section
                    render_export_section(self.current_data, self.current_file_type)
                    
                    # Debug information
                    render_debug_info()
                    
                except Exception as e:
                    render_error_message(
                        "Error in navigation",
                        f"Exception: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                    )
        
        # Main content area
        if (self.current_analyzer is not None and 
            self.current_data is not None and 
            st.session_state.analyzer_initialized):
            
            # Show file metrics at the top of main area
            render_file_metrics(self.current_data, self.current_file_type)
            
            # Add separator
            st.markdown("---")
            
            # Render selected analysis view
            current_view = st.session_state.current_view
            self.render_analysis_view(self.current_analyzer, current_view)
            
        else:
            # Welcome screen when no data is loaded
            render_welcome_screen()
        
        # Footer
        render_footer()


def main():
    """Application entry point"""
    try:
        app = ExcelAnalyzerApp()
        app.run()
    except Exception as e:
        st.error("Critical application error occurred.")
        with st.expander("🔍 Error Details"):
            st.error(f"Exception: {str(e)}")
            st.code(traceback.format_exc(), language="text")


if __name__ == "__main__":
    main() 
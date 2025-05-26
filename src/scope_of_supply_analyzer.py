"""
Project Structure Analyzer - Comprehensive Industrial Equipment Analysis
Supports PRE quotations, Analisi Profittabilita analysis, and cross-file comparisons
Provides unified interface for all project analysis and validation needs
"""

import streamlit as st
import traceback
import tempfile
import os
from typing import Optional, Tuple, Dict, Any
from enum import Enum

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
from components.analyzers.pre_comparator import PreComparator
from components.analyzers.profittabilita_comparator import ProfittabilitaComparator
from components.analyzers.pre_profittabilita_comparator import PreProfittabilitaComparator

# Import parsers
from parsers.pre_file_parser import parse_pre_to_json
from parsers.analisi_profittabilita_parser import parse_analisi_profittabilita_to_json


class OperationMode(Enum):
    """Enumeration of available operation modes"""
    ANALYZE_PRE = "analyze_pre"
    ANALYZE_PROFITTABILITA = "analyze_profittabilita"
    COMPARE_PRE = "compare_pre"
    COMPARE_PROFITTABILITA = "compare_profittabilita"
    CROSS_COMPARE_PRE_PROFITTABILITA = "cross_compare_pre_profittabilita"


class ProjectStructureAnalyzer:
    """Main application class for comprehensive project structure analysis"""
    
    def __init__(self):
        self.reset_state()
        
    def reset_state(self):
        """Reset all application state"""
        self.operation_mode = None
        self.current_analyzer = None
        self.current_comparator = None
        self.cross_comparator = None
        self.current_data = None
        self.current_file_type = None
        self.current_view = "Project Summary"
        
        # For comparison mode
        self.data1 = None
        self.data2 = None
        self.file1_name = None
        self.file2_name = None
        
        # For cross-comparison mode
        self.pre_data = None
        self.prof_data = None
        self.pre_file_name = None
        self.prof_file_name = None
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'operation_mode' not in st.session_state:
            st.session_state.operation_mode = None
        if 'current_view' not in st.session_state:
            st.session_state.current_view = self.current_view
        if 'analyzer_initialized' not in st.session_state:
            st.session_state.analyzer_initialized = False
        if 'comparator_initialized' not in st.session_state:
            st.session_state.comparator_initialized = False
        if 'comparison_view' not in st.session_state:
            st.session_state.comparison_view = "Project Comparison"
        if 'cross_comparator_initialized' not in st.session_state:
            st.session_state.cross_comparator_initialized = False
        if 'cross_comparison_view' not in st.session_state:
            st.session_state.cross_comparison_view = "Executive Summary"
    
    def render_operation_selector(self):
        """Render operation mode selector"""
        st.sidebar.header("🎯 Select Operation")
        
        operation_options = {
            "📊 Analyze PRE File": OperationMode.ANALYZE_PRE,
            "💹 Analyze Analisi Profittabilita": OperationMode.ANALYZE_PROFITTABILITA,
            "🔄 Compare Two PRE Files": OperationMode.COMPARE_PRE,
            "⚖️ Compare Two Profittabilita Files": OperationMode.COMPARE_PROFITTABILITA,
            "🔗 Cross-Compare PRE vs Profittabilita": OperationMode.CROSS_COMPARE_PRE_PROFITTABILITA
        }
        
        selected_operation = st.sidebar.radio(
            "Choose what you want to do:",
            list(operation_options.keys()),
            key="operation_selector",
            help="Select the type of analysis or comparison you want to perform"
        )
        
        return operation_options[selected_operation]
    
    def render_reset_button(self):
        """Render reset button to return to initial state"""
        st.sidebar.markdown("---")
        if st.sidebar.button("🔄 Reset Analysis", type="secondary", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            # Reset application state
            self.reset_state()
            st.rerun()
    
    def process_file(self, uploaded_file, file_type: FileType) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Process a single file based on its type with caching to avoid re-parsing"""
        try:
            # Create a unique key for this file based on name and size
            file_key = f"{uploaded_file.name}_{uploaded_file.size}_{file_type.value}"
            
            # Check if we already have this file parsed in session state
            if f"parsed_data_{file_key}" in st.session_state:
                return st.session_state[f"parsed_data_{file_key}"], None
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                temp_file_path = tmp_file.name
            
            try:
                # Parse based on file type
                if file_type == FileType.PRE_FILE:
                    data = parse_pre_to_json(temp_file_path)
                elif file_type == FileType.ANALISI_PROFITTABILITA:
                    data = parse_analisi_profittabilita_to_json(temp_file_path)
                else:
                    return None, f"Unsupported file type: {file_type}"
                
                # Cache the parsed data in session state
                st.session_state[f"parsed_data_{file_key}"] = data
                
                return data, None
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            return None, f"Error processing file: {str(e)}"
    
    def render_single_file_upload(self, file_type: FileType, title: str):
        """Render single file upload for analysis mode"""
        st.sidebar.subheader(title)
        
        file_extensions = ['xlsx', 'xls', 'xlsm']
        help_text = f"Upload a {file_type.value} file for analysis"
        
        uploaded_file = st.sidebar.file_uploader(
            f"Choose {file_type.value} file",
            type=file_extensions,
            key=f"single_file_uploader_{file_type.value}",
            help=help_text
        )
        
        if uploaded_file is not None:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                data, error = self.process_file(uploaded_file, file_type)
                
                if data is not None:
                    st.sidebar.success(f"✅ {uploaded_file.name} loaded successfully")
                    return data, uploaded_file.name
                else:
                    st.sidebar.error(f"❌ Error processing {uploaded_file.name}: {error}")
        
        return None, None
    
    def render_dual_file_upload(self, file_type: FileType, title: str):
        """Render dual file upload for comparison mode"""
        st.sidebar.subheader(title)
        
        file_extensions = ['xlsx', 'xls', 'xlsm']
        
        # File 1 upload
        st.sidebar.write("**First File:**")
        uploaded_file1 = st.sidebar.file_uploader(
            f"Choose first {file_type.value} file",
            type=file_extensions,
            key=f"dual_file1_uploader_{file_type.value}",
            help=f"Upload the first {file_type.value} file for comparison"
        )
        
        # File 2 upload
        st.sidebar.write("**Second File:**")
        uploaded_file2 = st.sidebar.file_uploader(
            f"Choose second {file_type.value} file",
            type=file_extensions,
            key=f"dual_file2_uploader_{file_type.value}",
            help=f"Upload the second {file_type.value} file for comparison"
        )
        
        data1, data2 = None, None
        file1_name, file2_name = None, None
        
        if uploaded_file1 is not None:
            file1_name = uploaded_file1.name
            with st.spinner(f"Processing {file1_name}..."):
                data1, error1 = self.process_file(uploaded_file1, file_type)
                
                if data1 is not None:
                    st.sidebar.success(f"✅ {file1_name} loaded successfully")
                else:
                    st.sidebar.error(f"❌ Error processing {file1_name}: {error1}")
        
        if uploaded_file2 is not None:
            file2_name = uploaded_file2.name
            with st.spinner(f"Processing {file2_name}..."):
                data2, error2 = self.process_file(uploaded_file2, file_type)
                
                if data2 is not None:
                    st.sidebar.success(f"✅ {file2_name} loaded successfully")
                else:
                    st.sidebar.error(f"❌ Error processing {file2_name}: {error2}")
        
        return data1, data2, file1_name, file2_name
    
    def render_cross_comparison_upload(self):
        """Render cross-comparison file upload for PRE vs Profittabilita mode"""
        st.sidebar.subheader("🔗 Cross-File Comparison")
        st.sidebar.markdown("Upload one PRE file and one Analisi Profittabilita file for cross-analysis.")
        
        file_extensions = ['xlsx', 'xls', 'xlsm']
        
        # PRE file upload
        st.sidebar.write("**PRE Quotation File:**")
        uploaded_pre_file = st.sidebar.file_uploader(
            "Choose PRE file",
            type=file_extensions,
            key="cross_pre_file_uploader",
            help="Upload a PRE quotation file"
        )
        
        # Profittabilita file upload
        st.sidebar.write("**Analisi Profittabilita File:**")
        uploaded_prof_file = st.sidebar.file_uploader(
            "Choose Analisi Profittabilita file",
            type=file_extensions,
            key="cross_prof_file_uploader",
            help="Upload an Analisi Profittabilita file"
        )
        
        pre_data, prof_data = None, None
        pre_file_name, prof_file_name = None, None
        
        if uploaded_pre_file is not None:
            pre_file_name = uploaded_pre_file.name
            with st.spinner(f"Processing PRE file: {pre_file_name}..."):
                pre_data, error_pre = self.process_file(uploaded_pre_file, FileType.PRE_FILE)
                
                if pre_data is not None:
                    st.sidebar.success(f"✅ {pre_file_name} loaded successfully")
                else:
                    st.sidebar.error(f"❌ Error processing {pre_file_name}: {error_pre}")
        
        if uploaded_prof_file is not None:
            prof_file_name = uploaded_prof_file.name
            with st.spinner(f"Processing Profittabilita file: {prof_file_name}..."):
                prof_data, error_prof = self.process_file(uploaded_prof_file, FileType.ANALISI_PROFITTABILITA)
                
                if prof_data is not None:
                    st.sidebar.success(f"✅ {prof_file_name} loaded successfully")
                else:
                    st.sidebar.error(f"❌ Error processing {prof_file_name}: {error_prof}")
        
        return pre_data, prof_data, pre_file_name, prof_file_name
    
    def create_analyzer(self, data, file_type: FileType):
        """Create appropriate analyzer based on file type with caching"""
        # Create a unique key for this analyzer
        data_hash = hash(str(data.get('project', {}).get('id', '')) + str(len(data.get('product_groups', []))))
        analyzer_key = f"analyzer_{file_type.value}_{data_hash}"
        
        # Check if we already have this analyzer in session state
        if analyzer_key in st.session_state:
            return st.session_state[analyzer_key]
        
        # Create new analyzer
        if file_type == FileType.PRE_FILE:
            analyzer = PreAnalyzer(data)
        elif file_type == FileType.ANALISI_PROFITTABILITA:
            analyzer = ProfittabilitaAnalyzer(data)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Cache the analyzer
        st.session_state[analyzer_key] = analyzer
        return analyzer
    
    def create_comparator(self, data1, data2, file_type: FileType, name1: str, name2: str):
        """Create appropriate comparator based on file type with caching"""
        # Create a unique key for this comparator
        data1_hash = hash(str(data1.get('project', {}).get('id', '')) + str(len(data1.get('product_groups', []))))
        data2_hash = hash(str(data2.get('project', {}).get('id', '')) + str(len(data2.get('product_groups', []))))
        comparator_key = f"comparator_{file_type.value}_{data1_hash}_{data2_hash}"
        
        # Check if we already have this comparator in session state
        if comparator_key in st.session_state:
            return st.session_state[comparator_key]
        
        # Create new comparator
        if file_type == FileType.PRE_FILE:
            comparator = PreComparator(data1, data2, name1, name2)
        elif file_type == FileType.ANALISI_PROFITTABILITA:
            comparator = ProfittabilitaComparator(data1, data2, name1, name2)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Cache the comparator
        st.session_state[comparator_key] = comparator
        return comparator
    
    def create_cross_comparator(self, pre_data, prof_data, pre_name: str, prof_name: str):
        """Create cross-comparator for PRE vs Profittabilita analysis with caching"""
        # Create a unique key for this cross-comparator
        pre_hash = hash(str(pre_data.get('project', {}).get('id', '')) + str(len(pre_data.get('product_groups', []))))
        prof_hash = hash(str(prof_data.get('project', {}).get('id', '')) + str(len(prof_data.get('product_groups', []))))
        cross_comparator_key = f"cross_comparator_{pre_hash}_{prof_hash}"
        
        # Check if we already have this cross-comparator in session state
        if cross_comparator_key in st.session_state:
            return st.session_state[cross_comparator_key]
        
        # Create new cross-comparator
        cross_comparator = PreProfittabilitaComparator(pre_data, prof_data, pre_name, prof_name)
        
        # Cache the cross-comparator
        st.session_state[cross_comparator_key] = cross_comparator
        return cross_comparator
    
    def render_analysis_view(self, analyzer, view_name: str):
        """Render the selected analysis view"""
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
                if hasattr(analyzer, 'display_financial_analysis'):
                    analyzer.display_financial_analysis()
                else:
                    st.warning("Financial Analysis is only available for PRE quotation files.")
            elif view_name == "Profitability Analysis":
                if hasattr(analyzer, 'display_profitability_analysis'):
                    analyzer.display_profitability_analysis()
                else:
                    st.warning("Profitability Analysis is only available for Analisi Profittabilita files.")
            elif view_name == "UTM Analysis":
                if hasattr(analyzer, 'display_utm_analysis'):
                    analyzer.display_utm_analysis()
                else:
                    st.warning("UTM Analysis is only available for Analisi Profittabilita files.")
            elif view_name == "WBE Analysis":
                if hasattr(analyzer, 'display_wbe_analysis'):
                    analyzer.display_wbe_analysis()
                else:
                    st.warning("WBE Analysis is only available for Analisi Profittabilita files.")
            elif view_name == "Field Analysis":
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
    
    def render_comparison_view(self, comparator, view_name: str):
        """Render the selected comparison view"""
        try:
            if view_name == "Project Comparison":
                comparator.display_project_comparison()
            elif view_name == "Financial Comparison" or view_name == "Profitability Comparison":
                if hasattr(comparator, 'display_financial_comparison'):
                    comparator.display_financial_comparison()
                elif hasattr(comparator, 'display_profitability_comparison'):
                    comparator.display_profitability_comparison()
            elif view_name == "Groups Comparison":
                comparator.display_groups_comparison()
            elif view_name == "Categories Comparison":
                comparator.display_categories_comparison()
            elif view_name == "Items Comparison":
                comparator.display_items_comparison()
            elif view_name == "WBE Comparison":
                if hasattr(comparator, 'display_wbe_comparison'):
                    comparator.display_wbe_comparison()
                else:
                    st.warning("WBE Comparison is only available for Analisi Profittabilita files.")
            elif view_name == "Cost Elements Comparison":
                if hasattr(comparator, 'display_cost_elements_comparison'):
                    comparator.display_cost_elements_comparison()
                else:
                    st.warning("Cost Elements Comparison is only available for Analisi Profittabilita files.")
            elif view_name == "UTM Comparison":
                if hasattr(comparator, 'display_utm_comparison'):
                    comparator.display_utm_comparison()
                else:
                    st.warning("UTM Comparison is only available for Analisi Profittabilita files.")
            elif view_name == "Engineering Comparison":
                if hasattr(comparator, 'display_engineering_comparison'):
                    comparator.display_engineering_comparison()
                else:
                    st.warning("Engineering Comparison is only available for Analisi Profittabilita files.")
            elif view_name == "Types Comparison":
                if hasattr(comparator, 'display_types_comparison'):
                    comparator.display_types_comparison()
                else:
                    st.warning("Types Comparison is only available for Analisi Profittabilita files.")
            elif view_name == "Summary Report":
                comparator.display_summary_report()
            else:
                st.error(f"Unknown comparison view: {view_name}")
                
        except Exception as e:
            render_error_message(
                f"Error displaying {view_name}",
                f"Exception: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            )
    
    def render_comparison_header(self, file1_name: str, file2_name: str):
        """Render header showing the files being compared"""
        st.markdown("### 🔄 File Comparison")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.info(f"**File 1:** {file1_name}")
        
        with col2:
            st.markdown("<div style='text-align: center; font-size: 24px;'>VS</div>", unsafe_allow_html=True)
        
        with col3:
            st.info(f"**File 2:** {file2_name}")
        
        st.markdown("---")
    
    def render_cross_comparison_view(self, cross_comparator, view_name: str):
        """Render the selected cross-comparison view"""
        try:
            if view_name == "Executive Summary":
                cross_comparator.display_executive_summary()
                
            elif view_name == "Data Consistency Check":
                cross_comparator.display_data_consistency_check()
                
            elif view_name == "WBE Impact Analysis":
                cross_comparator.display_wbe_impact_analysis()
                
            elif view_name == "Pricelist Comparison":
                cross_comparator.display_pricelist_comparison()
                
            elif view_name == "Missing Items Analysis":
                cross_comparator.display_missing_items_analysis()
                
            elif view_name == "Financial Impact Assessment":
                self.display_financial_impact_assessment(cross_comparator)
                
            elif view_name == "Project Structure Analysis":
                self.display_project_structure_analysis(cross_comparator)
                
            elif view_name == "Detailed Item Comparison":
                cross_comparator.display_detailed_item_comparison()
            
            else:
                st.error(f"Unknown cross-comparison view: {view_name}")
                
        except Exception as e:
            render_error_message(
                f"Error displaying {view_name}",
                f"Exception: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            )
    
    def render_cross_comparison_header(self, pre_file_name: str, prof_file_name: str):
        """Render header showing the files being cross-compared"""
        st.markdown("### 🔗 PRE vs Analisi Profittabilita Cross-Comparison")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.info(f"**PRE File:** {pre_file_name}")
        
        with col2:
            st.markdown("<div style='text-align: center; font-size: 24px;'>⚡ VS ⚡</div>", unsafe_allow_html=True)
        
        with col3:
            st.info(f"**Profittabilita:** {prof_file_name}")
        
        st.markdown("---")
    
    def display_financial_impact_assessment(self, cross_comparator):
        """Display comprehensive financial impact assessment"""
        st.header("💰 Financial Impact Assessment")
        
        st.markdown("""
        This section provides a comprehensive financial impact analysis comparing
        the PRE quotation with the current Analisi Profittabilita structure.
        """)
        
        # Overall financial metrics
        pre_total = cross_comparator.pricelist_analysis['pre_total_listino']
        prof_total = cross_comparator.pricelist_analysis['prof_total_listino']
        diff_amount = cross_comparator.pricelist_analysis['listino_difference']
        diff_percentage = cross_comparator.pricelist_analysis['listino_difference_percentage']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("PRE Total Value", f"€{pre_total:,.2f}")
        
        with col2:
            st.metric("Prof Total Value", f"€{prof_total:,.2f}")
        
        with col3:
            st.metric("Absolute Difference", f"€{diff_amount:,.2f}")
        
        with col4:
            st.metric("Percentage Difference", f"{diff_percentage:+.2f}%")
        
        # Impact categories
        st.subheader("📊 Impact by Category")
        
        # Calculate impact by item status
        missing_in_prof_value = 0
        missing_in_pre_value = 0
        modified_items_impact = 0
        
        for comp in cross_comparator.item_comparisons:
            if comp.result_type.value == "missing_in_profittabilita" and comp.pre_item:
                item = comp.pre_item['item_data']
                missing_in_prof_value += cross_comparator._safe_float(
                    item.get('pricelist_total_price', 0)
                )
            elif comp.result_type.value == "missing_in_pre" and comp.prof_item:
                item = comp.prof_item['item_data']
                missing_in_pre_value += cross_comparator._safe_float(
                    item.get('pricelist_total', 0)
                )
            elif comp.result_type.value == "value_mismatch":
                if comp.pre_item and comp.prof_item:
                    pre_value = cross_comparator._safe_float(
                        comp.pre_item['item_data'].get('pricelist_total_price', 0)
                    )
                    prof_value = cross_comparator._safe_float(
                        comp.prof_item['item_data'].get('pricelist_total', 0)
                    )
                    modified_items_impact += abs(pre_value - prof_value)
        
        impact_data = {
            'Category': [
                'Items to Add to Prof',
                'Items to Remove from Prof', 
                'Modified Items Impact',
                'Net Financial Impact'
            ],
            'Value (€)': [
                missing_in_prof_value,
                -missing_in_pre_value,
                modified_items_impact,
                diff_amount
            ],
            'Description': [
                f"Value of {cross_comparator.pricelist_analysis['items_missing_in_prof']} items missing in Profittabilita",
                f"Value of {cross_comparator.pricelist_analysis['items_missing_in_pre']} items missing in PRE",
                f"Total value variance in {cross_comparator.pricelist_analysis['items_with_differences']} modified items",
                "Overall net impact on project value"
            ]
        }
        
        import pandas as pd
        df_impact = pd.DataFrame(impact_data)
        df_impact['Value (€) Formatted'] = df_impact['Value (€)'].apply(lambda x: f"€{x:,.2f}")
        
        # Display impact table
        display_df = df_impact[['Category', 'Value (€) Formatted', 'Description']].copy()
        display_df.columns = ['Impact Category', 'Financial Value', 'Description']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Visual representation
        col1, col2 = st.columns(2)
        
        with col1:
            # Impact breakdown pie chart
            import plotly.express as px
            
            positive_values = [max(0, x) for x in df_impact['Value (€)'].tolist()[:-1]]  # Exclude net impact
            positive_categories = [cat for cat, val in zip(df_impact['Category'].tolist()[:-1], df_impact['Value (€)'].tolist()[:-1]) if val > 0]
            
            if sum(positive_values) > 0:
                fig_pie = px.pie(
                    values=positive_values,
                    names=positive_categories,
                    title="Financial Impact Breakdown",
                    color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#45b7d1']
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Impact trend chart
            import plotly.graph_objects as go
            
            fig_bar = go.Figure()
            
            colors = ['red' if x < 0 else 'green' for x in df_impact['Value (€)'].tolist()]
            
            fig_bar.add_trace(go.Bar(
                x=df_impact['Category'],
                y=df_impact['Value (€)'],
                marker_color=colors,
                text=[f"€{x:,.0f}" for x in df_impact['Value (€)']],
                textposition='auto'
            ))
            
            fig_bar.update_layout(
                title="Financial Impact by Category",
                xaxis_title="Impact Category",
                yaxis_title="Value (€)",
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Risk assessment
        st.subheader("⚠️ Risk Assessment")
        
        risks = []
        
        if abs(diff_percentage) > 10:
            risks.append(f"🔴 High financial variance: {diff_percentage:.1f}% difference between PRE and Profittabilita")
        
        if missing_in_prof_value > pre_total * 0.05:  # More than 5% of total
            risks.append(f"🟡 Significant missing value in Profittabilita: €{missing_in_prof_value:,.2f}")
        
        if cross_comparator.pricelist_analysis['items_with_differences'] > len(cross_comparator.item_comparisons) * 0.1:
            risks.append(f"🟡 High number of item discrepancies: {cross_comparator.pricelist_analysis['items_with_differences']} items")
        
        high_impact_wbes = [w for w in cross_comparator.wbe_impacts if abs(w.margin_percentage_change) > 15]
        if high_impact_wbes:
            risks.append(f"🔴 Critical WBE margin impact: {len(high_impact_wbes)} WBEs with >15% margin change")
        
        if not risks:
            st.success("✅ Low financial risk identified. Values are well-aligned between files.")
        else:
            for risk in risks:
                st.warning(risk)
    
    def display_project_structure_analysis(self, cross_comparator):
        """Display project structure comparison analysis"""
        st.header("🏗️ Project Structure Analysis")
        
        st.markdown("""
        This analysis compares the overall project structure between the PRE quotation
        and the Analisi Profittabilita WBE organization.
        """)
        
        # Structure overview
        st.subheader("📊 Structure Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### PRE File Structure")
            pre_groups = len(cross_comparator.pre_product_groups)
            pre_categories = sum(len(group.get('categories', [])) for group in cross_comparator.pre_product_groups)
            pre_items = len(cross_comparator.pre_items_map)
            
            st.metric("Product Groups", pre_groups)
            st.metric("Categories", pre_categories)
            st.metric("Total Items", pre_items)
            
            # PRE group breakdown
            if cross_comparator.pre_product_groups:
                group_data = []
                for group in cross_comparator.pre_product_groups:
                    group_items = sum(len(cat.get('items', [])) for cat in group.get('categories', []))
                    group_data.append({
                        'Group': group.get('group_name', 'Unknown')[:20],
                        'Categories': len(group.get('categories', [])),
                        'Items': group_items
                    })
                
                import pandas as pd
                df_pre_groups = pd.DataFrame(group_data)
                st.dataframe(df_pre_groups, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### Analisi Profittabilita Structure")
            prof_groups = len(cross_comparator.prof_product_groups)
            prof_categories = sum(len(group.get('categories', [])) for group in cross_comparator.prof_product_groups)
            prof_items = len(cross_comparator.prof_items_map)
            prof_wbes = len(cross_comparator.wbe_map)
            
            st.metric("Product Groups", prof_groups)
            st.metric("Categories", prof_categories)
            st.metric("WBE Elements", prof_wbes)
            st.metric("Total Items", prof_items)
            
            # WBE breakdown
            if cross_comparator.wbe_map:
                wbe_data = []
                for wbe_id, wbe_info in cross_comparator.wbe_map.items():
                    wbe_data.append({
                        'WBE': wbe_id,
                        'Categories': len(wbe_info['categories']),
                        'Items': wbe_info['items_count'],
                        'Value (€)': f"€{wbe_info['total_listino']:,.0f}"
                    })
                
                df_wbes = pd.DataFrame(wbe_data)
                st.dataframe(df_wbes, use_container_width=True, hide_index=True)
        
        # Structure mapping analysis
        st.subheader("🔗 Structure Mapping Analysis")
        
        # Group-to-WBE mapping
        group_wbe_mapping = {}
        
        for comp in cross_comparator.item_comparisons:
            if comp.pre_item and comp.prof_item:
                pre_group = comp.pre_item.get('group_name', 'Unknown')
                wbe = comp.wbe
                
                if pre_group not in group_wbe_mapping:
                    group_wbe_mapping[pre_group] = {}
                
                if wbe:
                    if wbe not in group_wbe_mapping[pre_group]:
                        group_wbe_mapping[pre_group][wbe] = 0
                    group_wbe_mapping[pre_group][wbe] += 1
        
        if group_wbe_mapping:
            st.markdown("#### Group to WBE Mapping")
            
            mapping_data = []
            for group, wbe_counts in group_wbe_mapping.items():
                for wbe, count in wbe_counts.items():
                    mapping_data.append({
                        'PRE Group': group[:30],
                        'WBE': wbe,
                        'Common Items': count,
                        'Mapping Strength': 'Strong' if count > 5 else 'Medium' if count > 2 else 'Weak'
                    })
            
            df_mapping = pd.DataFrame(mapping_data)
            df_mapping = df_mapping.sort_values(['PRE Group', 'Common Items'], ascending=[True, False])
            
            st.dataframe(df_mapping, use_container_width=True, hide_index=True)
            
            # Visualization
            import plotly.express as px
            
            if len(df_mapping) > 0:
                fig_mapping = px.sunburst(
                    df_mapping,
                    path=['PRE Group', 'WBE'],
                    values='Common Items',
                    title="PRE Group to WBE Mapping Structure"
                )
                st.plotly_chart(fig_mapping, use_container_width=True)
        
        # Structure consistency analysis
        st.subheader("📈 Structure Consistency Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Coverage metric
            items_with_mapping = len([c for c in cross_comparator.item_comparisons 
                                    if c.result_type.value == "match" or c.result_type.value == "value_mismatch"])
            total_items = max(len(cross_comparator.pre_items_map), len(cross_comparator.prof_items_map))
            coverage = (items_with_mapping / total_items * 100) if total_items > 0 else 0
            
            st.metric("Structure Coverage", f"{coverage:.1f}%", "Items mapped between structures")
        
        with col2:
            # Consistency score
            perfect_matches = len([c for c in cross_comparator.item_comparisons if c.result_type.value == "match"])
            consistency = (perfect_matches / len(cross_comparator.item_comparisons) * 100) if cross_comparator.item_comparisons else 0
            
            st.metric("Data Consistency", f"{consistency:.1f}%", "Perfect data matches")
        
        with col3:
            # Complexity indicator
            avg_items_per_wbe = (sum(wbe['items_count'] for wbe in cross_comparator.wbe_map.values()) / 
                               len(cross_comparator.wbe_map)) if cross_comparator.wbe_map else 0
            
            complexity = "High" if avg_items_per_wbe > 20 else "Medium" if avg_items_per_wbe > 10 else "Low"
            st.metric("WBE Complexity", complexity, f"{avg_items_per_wbe:.1f} avg items/WBE")
    
    def render_welcome_screen_with_operations(self):
        """Render welcome screen with operation descriptions"""
        st.markdown("""
        # 🏗️ Project Structure Analyzer
        
        Welcome to the comprehensive project structure analysis tool for industrial equipment files!
        
        ## 🎯 Available Operations:
        
        ### 📊 Single File Analysis
        - **Analyze PRE File**: Detailed analysis of PRE quotation files with financial breakdowns
        - **Analyze Analisi Profittabilita**: Comprehensive profitability analysis with UTM, WBE, and cost elements
        
        ### 🔄 File Comparison
        - **Compare Two PRE Files**: Side-by-side comparison of quotation parameters and financial differences  
        - **Compare Two Profittabilita Files**: Advanced comparison focusing on WBE, cost elements, UTM, and equipment types
        
        ### 🔗 Cross-File Analysis
        - **Cross-Compare PRE vs Profittabilita**: Advanced cross-validation between quotation and profitability data with WBE impact analysis
        
        ## 🚀 Getting Started
        
        1. **Select an operation** from the sidebar
        2. **Upload your file(s)** based on the selected operation
        3. **Explore the analysis** using the navigation menu
        4. **Reset anytime** to start over with new files
        
        ## 📋 Supported File Types
        
        - **.xlsx, .xls, .xlsm** files
        - **PRE quotation files** with standard structure
        - **Analisi Profittabilita files** with 81+ column structure
        
        ## ✨ Key Features
        
        ### Analysis Mode:
        - 📈 **Financial Analysis** with margin calculations
        - 🏗️ **Tree Structure** visualization
        - 📊 **Groups & Categories** breakdown
        - ⏱️ **UTM Time Tracking** (Profittabilita files)
        - 🏷️ **WBE Work Breakdown** (Profittabilita files)
        - 📋 **Field Analysis** with usage statistics
        
        ### Comparison Mode:
        - 🔍 **Difference Detection** with configurable thresholds
        - 📊 **Visual Comparisons** with side-by-side charts
        - 💰 **Cost Impact Analysis** for all elements
        - 📄 **Summary Reports** with automated insights
        - 🎯 **Specialized Views** for different data types
        
        **Select an operation from the sidebar to begin!**
        """)
    
    def render_status_section(self, operation_mode: OperationMode):
        """Render status section in sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.header("📊 Status")
        
        if operation_mode in [OperationMode.ANALYZE_PRE, OperationMode.ANALYZE_PROFITTABILITA]:
            # Single file analysis status
            data_status = "✅ Loaded" if self.current_data is not None else "❌ Not loaded"
            analysis_status = "✅ Ready" if self.current_analyzer is not None else "❌ Not ready"
            
            st.sidebar.write(f"**File:** {data_status}")
            st.sidebar.write(f"**Analysis:** {analysis_status}")
            
            if self.current_data is not None:
                st.sidebar.success("🎉 Ready for analysis!")
            else:
                st.sidebar.info("ℹ️ Upload a file to begin analysis")
        
        elif operation_mode == OperationMode.CROSS_COMPARE_PRE_PROFITTABILITA:
            # Cross-comparison status
            pre_status = "✅ Loaded" if self.pre_data is not None else "❌ Not loaded"
            prof_status = "✅ Loaded" if self.prof_data is not None else "❌ Not loaded"
            cross_status = "✅ Ready" if self.cross_comparator is not None else "❌ Not ready"
            
            st.sidebar.write(f"**PRE File:** {pre_status}")
            st.sidebar.write(f"**Prof File:** {prof_status}")
            st.sidebar.write(f"**Cross-Analysis:** {cross_status}")
            
            if self.pre_data is not None and self.prof_data is not None:
                st.sidebar.success("🎉 Ready for cross-comparison!")
            elif self.pre_data is not None or self.prof_data is not None:
                st.sidebar.warning("⚠️ Upload both files to start cross-analysis")
            else:
                st.sidebar.info("ℹ️ Upload PRE and Profittabilita files")
        
        else:
            # Dual file comparison status
            file1_status = "✅ Loaded" if self.data1 is not None else "❌ Not loaded"
            file2_status = "✅ Loaded" if self.data2 is not None else "❌ Not loaded"
            comparison_status = "✅ Ready" if self.current_comparator is not None else "❌ Not ready"
            
            st.sidebar.write(f"**File 1:** {file1_status}")
            st.sidebar.write(f"**File 2:** {file2_status}")
            st.sidebar.write(f"**Comparison:** {comparison_status}")
            
            if self.data1 is not None and self.data2 is not None:
                st.sidebar.success("🎉 Ready for comparison!")
            elif self.data1 is not None or self.data2 is not None:
                st.sidebar.warning("⚠️ Upload second file to start comparison")
            else:
                st.sidebar.info("ℹ️ Upload both files to begin comparison")
    
    def run(self):
        """Main application entry point"""
        # Configure Streamlit page
        st.set_page_config(
            page_title="Project Structure Analyzer",
            page_icon="🏗️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Apply custom styling
        apply_custom_css()
        
        # Initialize session state
        self.initialize_session_state()
        
        # Render main header
        render_app_header()
        
        # Sidebar: Operation selection and file processing
        with st.sidebar:
            # Operation selector
            operation_mode = self.render_operation_selector()
            st.session_state.operation_mode = operation_mode
            
            st.sidebar.markdown("---")
            
            try:
                # Handle different operation modes
                if operation_mode == OperationMode.ANALYZE_PRE:
                    data, file_name = self.render_single_file_upload(FileType.PRE_FILE, "📊 PRE File Analysis")
                    if data is not None:
                        self.current_data = data
                        self.current_file_type = FileType.PRE_FILE
                        self.current_analyzer = self.create_analyzer(data, FileType.PRE_FILE)
                        st.session_state.analyzer_initialized = True
                
                elif operation_mode == OperationMode.ANALYZE_PROFITTABILITA:
                    data, file_name = self.render_single_file_upload(FileType.ANALISI_PROFITTABILITA, "💹 Profittabilita Analysis")
                    if data is not None:
                        self.current_data = data
                        self.current_file_type = FileType.ANALISI_PROFITTABILITA
                        self.current_analyzer = self.create_analyzer(data, FileType.ANALISI_PROFITTABILITA)
                        st.session_state.analyzer_initialized = True
                
                elif operation_mode == OperationMode.COMPARE_PRE:
                    data1, data2, file1_name, file2_name = self.render_dual_file_upload(FileType.PRE_FILE, "🔄 PRE Files Comparison")
                    if data1 is not None and data2 is not None:
                        self.data1 = data1
                        self.data2 = data2
                        self.file1_name = file1_name or "File 1"
                        self.file2_name = file2_name or "File 2"
                        self.current_comparator = self.create_comparator(data1, data2, FileType.PRE_FILE, self.file1_name, self.file2_name)
                        st.session_state.comparator_initialized = True
                
                elif operation_mode == OperationMode.COMPARE_PROFITTABILITA:
                    data1, data2, file1_name, file2_name = self.render_dual_file_upload(FileType.ANALISI_PROFITTABILITA, "⚖️ Profittabilita Comparison")
                    if data1 is not None and data2 is not None:
                        self.data1 = data1
                        self.data2 = data2
                        self.file1_name = file1_name or "File 1"
                        self.file2_name = file2_name or "File 2"
                        self.current_comparator = self.create_comparator(data1, data2, FileType.ANALISI_PROFITTABILITA, self.file1_name, self.file2_name)
                        st.session_state.comparator_initialized = True
                
                elif operation_mode == OperationMode.CROSS_COMPARE_PRE_PROFITTABILITA:
                    pre_data, prof_data, pre_file_name, prof_file_name = self.render_cross_comparison_upload()
                    if pre_data is not None and prof_data is not None:
                        self.pre_data = pre_data
                        self.prof_data = prof_data
                        self.pre_file_name = pre_file_name or "PRE File"
                        self.prof_file_name = prof_file_name or "Profittabilita File"
                        self.cross_comparator = self.create_cross_comparator(pre_data, prof_data, self.pre_file_name, self.prof_file_name)
                        st.session_state.cross_comparator_initialized = True
                
            except Exception as e:
                render_error_message(
                    "Error in file processing",
                    f"Exception: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                )
            
            # Navigation for analysis mode
            if self.current_analyzer is not None and operation_mode in [OperationMode.ANALYZE_PRE, OperationMode.ANALYZE_PROFITTABILITA]:
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
                    
                except Exception as e:
                    render_error_message(
                        "Error in navigation",
                        f"Exception: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                    )
            
            # Navigation for comparison mode
            elif self.current_comparator is not None and operation_mode in [OperationMode.COMPARE_PRE, OperationMode.COMPARE_PROFITTABILITA]:
                try:
                    st.sidebar.header("🔍 Comparison Views")
                    
                    views = self.current_comparator.get_comparison_views()
                    
                    selected_view = st.sidebar.radio(
                        "Select comparison view:",
                        views,
                        index=views.index(st.session_state.comparison_view) if st.session_state.comparison_view in views else 0,
                        key="comparison_view_selector"
                    )
                    
                    if selected_view != st.session_state.comparison_view:
                        st.session_state.comparison_view = selected_view
                        st.rerun()
                    
                except Exception as e:
                    render_error_message(
                        "Error in comparison navigation",
                        f"Exception: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                    )
            
            # Navigation for cross-comparison mode
            elif self.cross_comparator is not None and operation_mode == OperationMode.CROSS_COMPARE_PRE_PROFITTABILITA:
                try:
                    st.sidebar.header("🔗 Cross-Comparison Views")
                    
                    views = self.cross_comparator.get_comparison_views()
                    
                    selected_view = st.sidebar.radio(
                        "Select analysis view:",
                        views,
                        index=views.index(st.session_state.cross_comparison_view) if st.session_state.cross_comparison_view in views else 0,
                        key="cross_comparison_view_selector"
                    )
                    
                    if selected_view != st.session_state.cross_comparison_view:
                        st.session_state.cross_comparison_view = selected_view
                        st.rerun()
                    
                except Exception as e:
                    render_error_message(
                        "Error in cross-comparison navigation",
                        f"Exception: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                    )
            
            # Status section
            self.render_status_section(operation_mode)
            
            # Reset button
            self.render_reset_button()
            
            # Debug information
            render_debug_info()
        
        # Main content area
        if operation_mode in [OperationMode.ANALYZE_PRE, OperationMode.ANALYZE_PROFITTABILITA]:
            # Analysis mode
            if (self.current_analyzer is not None and 
                self.current_data is not None and 
                st.session_state.analyzer_initialized):
                
                # Show file metrics
                render_file_metrics(self.current_data, self.current_file_type)
                st.markdown("---")
                
                # Render selected analysis view
                current_view = st.session_state.current_view
                self.render_analysis_view(self.current_analyzer, current_view)
            else:
                # Welcome screen for analysis
                self.render_welcome_screen_with_operations()
        
        elif operation_mode in [OperationMode.COMPARE_PRE, OperationMode.COMPARE_PROFITTABILITA]:
            # Comparison mode
            if (self.current_comparator is not None and 
                self.data1 is not None and 
                self.data2 is not None and
                st.session_state.comparator_initialized):
                
                # Show comparison header
                self.render_comparison_header(self.file1_name, self.file2_name)
                
                # Render selected comparison view
                current_view = st.session_state.comparison_view
                self.render_comparison_view(self.current_comparator, current_view)
            else:
                # Welcome screen for comparison
                self.render_welcome_screen_with_operations()
        
        elif operation_mode == OperationMode.CROSS_COMPARE_PRE_PROFITTABILITA:
            # Cross-comparison mode
            if (self.cross_comparator is not None and 
                self.pre_data is not None and 
                self.prof_data is not None and
                st.session_state.cross_comparator_initialized):
                
                # Show cross-comparison header
                self.render_cross_comparison_header(self.pre_file_name, self.prof_file_name)
                
                # Render selected cross-comparison view
                current_view = st.session_state.cross_comparison_view
                self.render_cross_comparison_view(self.cross_comparator, current_view)
            else:
                # Welcome screen for cross-comparison
                self.render_welcome_screen_with_operations()
        
        else:
            # Default welcome screen
            self.render_welcome_screen_with_operations()
        
        # Footer
        render_footer()


def main():
    """Application entry point"""
    try:
        app = ProjectStructureAnalyzer()
        app.run()
    except Exception as e:
        st.error("Critical application error occurred.")
        with st.expander("🔍 Error Details"):
            st.error(f"Exception: {str(e)}")
            st.code(traceback.format_exc(), language="text")


if __name__ == "__main__":
    main() 
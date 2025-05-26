"""
PRE vs Analisi Profittabilita Cross-Comparator Streamlit Application
Compare PRE quotation files with Analisi Profittabilita elaborations
to validate data consistency and analyze WBE impact
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
from components.analyzers.pre_profittabilita_comparator import PreProfittabilitaComparator

# Import parsers directly
from parsers.pre_file_parser import parse_pre_to_json as parse_pre_file
from parsers.analisi_profittabilita_parser import parse_analisi_profittabilita_to_json as parse_prof_file


class PreProfittabilitaComparatorApp:
    """Main application class for the PRE vs Analisi Profittabilita cross-comparator"""
    
    def __init__(self):
        self.comparator = None
        self.pre_data = None
        self.prof_data = None
        self.pre_file_name = None
        self.prof_file_name = None
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'cross_comparison_view' not in st.session_state:
            st.session_state.cross_comparison_view = "Executive Summary"
        if 'cross_comparator_initialized' not in st.session_state:
            st.session_state.cross_comparator_initialized = False
        if 'cross_files_uploaded' not in st.session_state:
            st.session_state.cross_files_uploaded = {'pre_file': None, 'prof_file': None}
    
    def process_pre_file(self, uploaded_file) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Process a PRE file and return data and error message if any"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                temp_file_path = tmp_file.name
            
            try:
                # Parse the PRE file
                data = parse_pre_file(temp_file_path)
                return data, None
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            return None, f"Error processing PRE file: {str(e)}"
    
    def process_prof_file(self, uploaded_file) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Process an Analisi Profittabilita file and return data and error message if any"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                temp_file_path = tmp_file.name
            
            try:
                # Parse the Profittabilita file
                data = parse_prof_file(temp_file_path)
                return data, None
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            return None, f"Error processing Analisi Profittabilita file: {str(e)}"
    
    def render_file_upload_section(self):
        """Render the file upload section for PRE and Profittabilita files"""
        st.sidebar.header("📁 Upload Files for Cross-Comparison")
        
        st.sidebar.markdown("""
        Upload one PRE quotation file and one Analisi Profittabilita file 
        to analyze data consistency and WBE impact.
        """)
        
        # PRE file upload
        st.sidebar.subheader("📄 PRE Quotation File")
        uploaded_pre_file = st.sidebar.file_uploader(
            "Choose PRE file",
            type=['xlsx', 'xls', 'xlsm'],
            key="pre_file_uploader",
            help="Upload a PRE quotation file"
        )
        
        # Profittabilita file upload
        st.sidebar.subheader("📊 Analisi Profittabilita File")
        uploaded_prof_file = st.sidebar.file_uploader(
            "Choose Analisi Profittabilita file",
            type=['xlsx', 'xls', 'xlsm'],
            key="prof_file_uploader",
            help="Upload an Analisi Profittabilita file"
        )
        
        # Process files
        pre_data, prof_data = None, None
        pre_file_name, prof_file_name = None, None
        
        if uploaded_pre_file is not None:
            pre_file_name = uploaded_pre_file.name
            with st.spinner(f"Processing PRE file: {pre_file_name}..."):
                pre_data, error_pre = self.process_pre_file(uploaded_pre_file)
                
                if pre_data is not None:
                    st.sidebar.success(f"✅ {pre_file_name} loaded successfully")
                else:
                    st.sidebar.error(f"❌ Error processing {pre_file_name}: {error_pre}")
        
        if uploaded_prof_file is not None:
            prof_file_name = uploaded_prof_file.name
            with st.spinner(f"Processing Profittabilita file: {prof_file_name}..."):
                prof_data, error_prof = self.process_prof_file(uploaded_prof_file)
                
                if prof_data is not None:
                    st.sidebar.success(f"✅ {prof_file_name} loaded successfully")
                else:
                    st.sidebar.error(f"❌ Error processing {prof_file_name}: {error_prof}")
        
        return pre_data, prof_data, pre_file_name, prof_file_name
    
    def render_comparison_navigation(self):
        """Render the comparison navigation menu"""
        if self.comparator is not None:
            st.sidebar.markdown("---")
            st.sidebar.header("🔍 Cross-Comparison Views")
            
            views = self.comparator.get_comparison_views()
            
            selected_view = st.sidebar.radio(
                "Select analysis view:",
                views,
                index=views.index(st.session_state.cross_comparison_view) if st.session_state.cross_comparison_view in views else 0,
                key="cross_comparison_view_selector"
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
            if view_name == "Executive Summary":
                self.comparator.display_executive_summary()
                
            elif view_name == "Data Consistency Check":
                self.comparator.display_data_consistency_check()
                
            elif view_name == "WBE Impact Analysis":
                self.comparator.display_wbe_impact_analysis()
                
            elif view_name == "Pricelist Comparison":
                self.comparator.display_pricelist_comparison()
                
            elif view_name == "Missing Items Analysis":
                self.comparator.display_missing_items_analysis()
                
            elif view_name == "Financial Impact Assessment":
                self.display_financial_impact_assessment()
                
            elif view_name == "Project Structure Analysis":
                self.display_project_structure_analysis()
                
            elif view_name == "Detailed Item Comparison":
                self.comparator.display_detailed_item_comparison()
            
            else:
                st.error(f"Unknown comparison view: {view_name}")
                
        except Exception as e:
            render_error_message(
                f"Error displaying {view_name}",
                f"Exception: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            )
    
    def display_financial_impact_assessment(self):
        """Display comprehensive financial impact assessment"""
        st.header("💰 Financial Impact Assessment")
        
        st.markdown("""
        This section provides a comprehensive financial impact analysis comparing
        the PRE quotation with the current Analisi Profittabilita structure.
        """)
        
        # Overall financial metrics
        pre_total = self.comparator.pricelist_analysis['pre_total_listino']
        prof_total = self.comparator.pricelist_analysis['prof_total_listino']
        diff_amount = self.comparator.pricelist_analysis['listino_difference']
        diff_percentage = self.comparator.pricelist_analysis['listino_difference_percentage']
        
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
        
        for comp in self.comparator.item_comparisons:
            if comp.result_type.value == "missing_in_profittabilita" and comp.pre_item:
                item = comp.pre_item['item_data']
                missing_in_prof_value += self.comparator._safe_float(
                    item.get('pricelist_total_price', 0)
                )
            elif comp.result_type.value == "missing_in_pre" and comp.prof_item:
                item = comp.prof_item['item_data']
                missing_in_pre_value += self.comparator._safe_float(
                    item.get('pricelist_total', 0)
                )
            elif comp.result_type.value == "value_mismatch":
                if comp.pre_item and comp.prof_item:
                    pre_value = self.comparator._safe_float(
                        comp.pre_item['item_data'].get('pricelist_total_price', 0)
                    )
                    prof_value = self.comparator._safe_float(
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
                f"Value of {self.comparator.pricelist_analysis['items_missing_in_prof']} items missing in Profittabilita",
                f"Value of {self.comparator.pricelist_analysis['items_missing_in_pre']} items missing in PRE",
                f"Total value variance in {self.comparator.pricelist_analysis['items_with_differences']} modified items",
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
        
        if self.comparator.pricelist_analysis['items_with_differences'] > len(self.comparator.item_comparisons) * 0.1:
            risks.append(f"🟡 High number of item discrepancies: {self.comparator.pricelist_analysis['items_with_differences']} items")
        
        high_impact_wbes = [w for w in self.comparator.wbe_impacts if abs(w.margin_percentage_change) > 15]
        if high_impact_wbes:
            risks.append(f"🔴 Critical WBE margin impact: {len(high_impact_wbes)} WBEs with >15% margin change")
        
        if not risks:
            st.success("✅ Low financial risk identified. Values are well-aligned between files.")
        else:
            for risk in risks:
                st.warning(risk)
    
    def display_project_structure_analysis(self):
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
            pre_groups = len(self.comparator.pre_product_groups)
            pre_categories = sum(len(group.get('categories', [])) for group in self.comparator.pre_product_groups)
            pre_items = len(self.comparator.pre_items_map)
            
            st.metric("Product Groups", pre_groups)
            st.metric("Categories", pre_categories)
            st.metric("Total Items", pre_items)
            
            # PRE group breakdown
            if self.comparator.pre_product_groups:
                group_data = []
                for group in self.comparator.pre_product_groups:
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
            prof_groups = len(self.comparator.prof_product_groups)
            prof_categories = sum(len(group.get('categories', [])) for group in self.comparator.prof_product_groups)
            prof_items = len(self.comparator.prof_items_map)
            prof_wbes = len(self.comparator.wbe_map)
            
            st.metric("Product Groups", prof_groups)
            st.metric("Categories", prof_categories)
            st.metric("WBE Elements", prof_wbes)
            st.metric("Total Items", prof_items)
            
            # WBE breakdown
            if self.comparator.wbe_map:
                wbe_data = []
                for wbe_id, wbe_info in self.comparator.wbe_map.items():
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
        
        for comp in self.comparator.item_comparisons:
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
            items_with_mapping = len([c for c in self.comparator.item_comparisons 
                                    if c.result_type.value == "match" or c.result_type.value == "value_mismatch"])
            total_items = max(len(self.comparator.pre_items_map), len(self.comparator.prof_items_map))
            coverage = (items_with_mapping / total_items * 100) if total_items > 0 else 0
            
            st.metric("Structure Coverage", f"{coverage:.1f}%", "Items mapped between structures")
        
        with col2:
            # Consistency score
            perfect_matches = len([c for c in self.comparator.item_comparisons if c.result_type.value == "match"])
            consistency = (perfect_matches / len(self.comparator.item_comparisons) * 100) if self.comparator.item_comparisons else 0
            
            st.metric("Data Consistency", f"{consistency:.1f}%", "Perfect data matches")
        
        with col3:
            # Complexity indicator
            avg_items_per_wbe = (sum(wbe['items_count'] for wbe in self.comparator.wbe_map.values()) / 
                               len(self.comparator.wbe_map)) if self.comparator.wbe_map else 0
            
            complexity = "High" if avg_items_per_wbe > 20 else "Medium" if avg_items_per_wbe > 10 else "Low"
            st.metric("WBE Complexity", complexity, f"{avg_items_per_wbe:.1f} avg items/WBE")
    
    def render_comparison_header(self):
        """Render header showing the files being compared"""
        if self.pre_file_name and self.prof_file_name:
            st.markdown("### 🔄 PRE vs Analisi Profittabilita Cross-Comparison")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                st.info(f"**PRE File:** {self.pre_file_name}")
            
            with col2:
                st.markdown("<div style='text-align: center; font-size: 24px;'>⚡ VS ⚡</div>", unsafe_allow_html=True)
            
            with col3:
                st.info(f"**Profittabilita:** {self.prof_file_name}")
            
            st.markdown("---")
    
    def render_welcome_screen(self):
        """Render welcome screen when no files are loaded"""
        st.markdown("""
        # 🔄 PRE vs Analisi Profittabilita Cross-Comparator
        
        Welcome to the PRE vs Analisi Profittabilita Cross-Comparator! This specialized tool performs 
        comprehensive analysis between quotation files (PRE) and profitability elaborations (Analisi Profittabilita).
        
        ## 🎯 What this tool does:
        
        ### 1. **Data Consistency Validation** 📊
        - Verifies that all PRE information is correctly transferred to Analisi Profittabilita
        - Identifies missing or mismatched items between files
        - Validates pricing and quantity consistency
        
        ### 2. **WBE Impact Analysis** 🏗️
        - Shows how PRE changes affect Work Breakdown Elements (WBE)
        - Calculates margin impact for each WBE
        - Identifies high-risk WBEs requiring attention
        
        ### 3. **Financial Impact Assessment** 💰
        - Comprehensive financial comparison between files
        - Risk assessment based on variance thresholds
        - Project profitability impact analysis
        
        ### 4. **Project Structure Analysis** 🔗
        - Maps PRE product groups to WBE structure
        - Analyzes structural consistency and coverage
        - Provides recommendations for structure optimization
        
        ## 📋 How to use:
        
        1. **Upload Files**: Use the sidebar to upload one PRE file and one Analisi Profittabilita file
        2. **Analyze**: Once both files are loaded, explore different analysis views
        3. **Review**: Check data consistency, WBE impacts, and financial differences
        4. **Export**: Download detailed reports and CSV files for further analysis
        
        ## 🔍 Available Analysis Views:
        
        - **Executive Summary**: High-level overview with key metrics and recommendations
        - **Data Consistency Check**: Detailed item-by-item validation with issue identification
        - **WBE Impact Analysis**: Work Breakdown Element impact assessment
        - **Pricelist Comparison**: Financial comparison by product groups
        - **Missing Items Analysis**: Detailed analysis of items missing in either file
        - **Financial Impact Assessment**: Comprehensive financial risk analysis
        - **Project Structure Analysis**: Structure mapping and consistency metrics
        - **Detailed Item Comparison**: Granular item-by-item comparison with filtering
        
        ## 📈 Key Benefits:
        
        - **Quality Assurance**: Ensure data integrity between quotation and elaboration
        - **Risk Management**: Identify potential issues before project submission
        - **Decision Support**: Data-driven insights for project optimization
        - **Time Savings**: Automated comparison instead of manual checking
        - **Audit Trail**: Comprehensive documentation of differences and changes
        
        ---
        
        **Ready to start?** Upload your PRE and Analisi Profittabilita files using the sidebar! 📁
        """)
    
    def run(self):
        """Main application runner"""
        try:
            # Apply custom CSS
            apply_custom_css()
            
            # Initialize session state
            self.initialize_session_state()
            
            # Render custom header for cross-comparator
            st.title("🔄 PRE vs Analisi Profittabilita Cross-Comparator")
            st.markdown("### Comprehensive Cross-File Analysis & WBE Impact Assessment")
            
            # File upload section
            self.pre_data, self.prof_data, self.pre_file_name, self.prof_file_name = self.render_file_upload_section()
            
            # Check if both files are loaded
            if self.pre_data is not None and self.prof_data is not None:
                # Initialize comparator
                if not st.session_state.cross_comparator_initialized:
                    with st.spinner("Initializing cross-comparison analysis..."):
                        self.comparator = PreProfittabilitaComparator(
                            self.pre_data, 
                            self.prof_data,
                            self.pre_file_name,
                            self.prof_file_name
                        )
                        st.session_state.cross_comparator_initialized = True
                        st.sidebar.success("✅ Cross-comparison analysis ready!")
                
                # Render comparison header
                self.render_comparison_header()
                
                # Navigation and view rendering
                selected_view = self.render_comparison_navigation()
                if selected_view:
                    st.session_state.cross_comparison_view = selected_view
                    self.render_comparison_view(selected_view)
                
            elif self.pre_data is not None or self.prof_data is not None:
                # One file loaded, waiting for the other
                if self.pre_data is not None:
                    st.info("✅ PRE file loaded. Please upload an Analisi Profittabilita file to start comparison.")
                else:
                    st.info("✅ Analisi Profittabilita file loaded. Please upload a PRE file to start comparison.")
                
                # Reset comparator state
                st.session_state.cross_comparator_initialized = False
                self.comparator = None
                
            else:
                # No files loaded, show welcome screen
                self.render_welcome_screen()
                
                # Reset state
                st.session_state.cross_comparator_initialized = False
                self.comparator = None
            
            # Render footer
            render_footer()
            
        except Exception as e:
            render_error_message(
                "Application Error",
                f"An unexpected error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            )


def main():
    """Main entry point"""
    app = PreProfittabilitaComparatorApp()
    app.run()


if __name__ == "__main__":
    main() 
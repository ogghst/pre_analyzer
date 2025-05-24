"""
Streamlit Application for Excel to JSON Parser
Interactive web application for processing and visualizing industrial equipment quotations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import io
import traceback
from typing import Dict, List, Any
import numpy as np
import os

# Import our parser
from pre_file_parser import PreFileParser
from temp.validate_json_schema import validate_quotation_json

# Configure Streamlit page
st.set_page_config(
    page_title="Excel Quotation Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'selected_view' not in st.session_state:
    st.session_state.selected_view = "Project Summary"

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {

        border: 1px solid #e1e5f0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
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
    .sidebar .stRadio > div {
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

class QuotationAnalyzer:
    """Main application class for quotation analysis"""
    
    def __init__(self):
        self.data = None
        self.parser = None
        
    def load_and_process_file(self, uploaded_file) -> bool:
        """Load and process the uploaded Excel file"""
        try:
            # Save uploaded file temporarily
            temp_file = "temp_upload.xlsx"
            with open(temp_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process with parser
            self.parser = PreFileParser(temp_file)
            self.data = self.parser.parse()
            
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return True
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            with st.expander("🔍 Error Details"):
                st.error(traceback.format_exc())
            return False
    
    def display_project_summary(self):
        """Display project summary information"""
        if not self.data:
            st.error("No data available. Please upload and process a file first.")
            return
            
        project = self.data['project']
        totals = self.data['totals']
        
        st.header("📋 Project Summary")
        
        # Create columns for metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Project ID", project.get('id', 'N/A'))
            st.metric("Customer", project.get('customer', 'N/A'))
            
        with col2:
            currency = project.get('parameters', {}).get('currency', 'N/A')
            exchange_rate = project.get('parameters', {}).get('exchange_rate', 0)
            st.metric("Currency", currency)
            st.metric("Exchange Rate", f"{exchange_rate:.2f}")
            
        with col3:
            doc_perc = project.get('parameters', {}).get('doc_percentage', 0)
            pm_perc = project.get('parameters', {}).get('pm_percentage', 0)
            st.metric("DOC %", f"{doc_perc:.3%}")
            st.metric("PM %", f"{pm_perc:.3%}")
            
        with col4:
            st.metric("Product Groups", len(self.data.get('product_groups', [])))
            total_items = sum(len(cat.get('items', [])) for group in self.data.get('product_groups', []) for cat in group.get('categories', []))
            st.metric("Total Items", total_items)
        
        # Financial summary
        st.subheader("💰 Financial Summary")
        fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
        
        with fin_col1:
            st.metric("Equipment Total", f"€{totals.get('equipment_total', 0):,.2f}")
        with fin_col2:
            st.metric("Installation Total", f"€{totals.get('installation_total', 0):,.2f}")
        with fin_col3:
            fees_total = totals.get('doc_fee', 0) + totals.get('pm_fee', 0) + totals.get('warranty_fee', 0)
            st.metric("Fees Total", f"€{fees_total:,.2f}")
        with fin_col4:
            st.metric("Grand Total", f"€{totals.get('grand_total', 0):,.2f}")
    
    def display_tree_structure(self):
        """Display hierarchical tree structure"""
        if not self.data:
            st.error("No data available. Please upload and process a file first.")
            return
            
        st.header("🌳 Hierarchical Structure")
        
        product_groups = self.data.get('product_groups', [])
        if not product_groups:
            st.warning("No product groups found in the data.")
            return
        
        # Create expandable tree structure
        for group_idx, group in enumerate(product_groups):
            group_total = sum(cat.get('total_offer', 0) for cat in group.get('categories', []))
            
            with st.expander(f"🏗️ {group.get('group_id', 'Unknown')}: {group.get('group_name', 'Unnamed Group')} (€{group_total:,.2f})", expanded=False):
                
                categories = group.get('categories', [])
                if not categories:
                    st.info("No categories found in this group.")
                    continue
                
                for category in categories:
                    cat_total = category.get('total_offer', 0)
                    st.markdown(f"**📂 {category.get('category_id', 'Unknown')}: {category.get('category_name', 'Unnamed Category')}** (€{cat_total:,.2f})")
                    
                    # Show top items in this category
                    items = category.get('items', [])
                    items_with_value = [item for item in items if item.get('pricelist_total_price', 0) > 0]
                    
                    if items_with_value:
                        top_items = sorted(items_with_value, key=lambda x: x.get('pricelist_total_price', 0), reverse=True)
                        
                        for item in top_items:
                            description = item.get('description', 'No description')
                            price = item.get('pricelist_total_price', 0)
                            st.markdown(f"  • `{item.get('code', 'Unknown')}`: {description}... (€{price:,.2f})")
                    else:
                        st.markdown("  • *No items with value*")
                    
                    st.markdown("---")
    
    def display_groups_analysis(self):
        """Display groups analysis with charts"""
        if not self.data:
            st.error("No data available. Please upload and process a file first.")
            return
            
        st.header("📦 Product Groups Analysis")
        
        product_groups = self.data.get('product_groups', [])
        if not product_groups:
            st.warning("No product groups found in the data.")
            return
        
        # Prepare groups data
        groups_data = []
        for group in product_groups:
            group_total_offer = sum(cat.get('total_offer', 0) for cat in group.get('categories', []))
            group_total = sum(cat.get('total', 0) for cat in group.get('categories', []))
            total_items = sum(len(cat.get('items', [])) for cat in group.get('categories', []))
            
            groups_data.append({
                'Group ID': group.get('group_id', 'Unknown'),
                'Group Name': group.get('group_name', 'Unnamed'),
                'Categories': len(group.get('categories', [])),
                'Total Items': total_items,
                'Total Offer (€)': group_total_offer,
                'Total (€)': group_total,
                'Quantity': group.get('quantity', 1)
            })
        
        df_groups = pd.DataFrame(groups_data)
        
        if df_groups.empty:
            st.warning("No group data to display.")
            return
        
        # Display table
        st.subheader("📊 Groups Summary Table")
        st.dataframe(df_groups, use_container_width=True)
        
        # Create charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart of total offers by group
            fig_bar = px.bar(
                df_groups, 
                x='Group ID', 
                y='Total Offer (€)',
                title='Total Offer by Product Group',
                text='Total Offer (€)',
                color='Total Offer (€)',
                color_continuous_scale='Blues'
            )
            fig_bar.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
            fig_bar.update_layout(height=500)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Pie chart of total offer distribution
            fig_pie = px.pie(
                df_groups, 
                values='Total Offer (€)', 
                names='Group ID',
                title='Total Offer Distribution by Group'
            )
            fig_pie.update_layout(height=500)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Treemap visualization
        st.subheader("🗺️ Groups Treemap")
        fig_treemap = px.treemap(
            df_groups,
            path=['Group ID'],
            values='Total Offer (€)',
            title='Product Groups by Total Offer Value',
            color='Total Offer (€)',
            color_continuous_scale='RdYlBu'
        )
        fig_treemap.update_layout(height=600)
        st.plotly_chart(fig_treemap, use_container_width=True)
    
    def display_categories_analysis(self):
        """Display categories analysis with charts"""
        if not self.data:
            st.error("No data available. Please upload and process a file first.")
            return
            
        st.header("📂 Categories Analysis")
        
        # Prepare categories data
        categories_data = []
        for group in self.data.get('product_groups', []):
            for category in group.get('categories', []):
                categories_data.append({
                    'Group ID': group.get('group_id', 'Unknown'),
                    'Group Name': group.get('group_name', 'Unnamed'),
                    'Category ID': category.get('category_id', 'Unknown'),
                    'Category Name': category.get('category_name', 'Unnamed'),
                    'Items Count': len(category.get('items', [])),
                    'Subtotal Listino (€)': category.get('subtotal_listino', 0),
                    'Subtotal Codice (€)': category.get('subtotal_codice', 0),
                    'Total (€)': category.get('total', 0),
                    'Total Offer (€)': category.get('total_offer', 0)
                })
        
        df_categories = pd.DataFrame(categories_data)
        
        if df_categories.empty:
            st.warning("No category data to display.")
            return
        
        # Filter controls
        col1, col2 = st.columns(2)
        with col1:
            selected_groups = st.multiselect(
                "Filter by Groups",
                options=df_categories['Group ID'].unique(),
                default=df_categories['Group ID'].unique(),
                key="categories_group_filter"
            )
        
        with col2:
            min_value = st.number_input(
                "Minimum Total Offer (€)",
                min_value=0.0,
                value=0.0,
                step=1000.0,
                key="categories_min_value"
            )
        
        # Apply filters
        filtered_df = df_categories[
            (df_categories['Group ID'].isin(selected_groups)) &
            (df_categories['Total Offer (€)'] >= min_value)
        ]
        
        # Display filtered table
        st.subheader("📊 Categories Summary Table")
        st.dataframe(filtered_df, use_container_width=True)
        
        if len(filtered_df) > 0:
            # Top categories chart
            top_categories = filtered_df.nlargest(15, 'Total Offer (€)')
            
            fig_top = px.bar(
                top_categories,
                x='Total Offer (€)',
                y='Category ID',
                orientation='h',
                title=f'Top {len(top_categories)} Categories by Total Offer',
                text='Total Offer (€)',
                color='Total Offer (€)',
                color_continuous_scale='Viridis'
            )
            fig_top.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
            fig_top.update_layout(height=600)
            st.plotly_chart(fig_top, use_container_width=True)
            
            # Categories by group
            col1, col2 = st.columns(2)
            
            with col1:
                # Stacked bar chart by group
                fig_stacked = px.bar(
                    filtered_df,
                    x='Group ID',
                    y='Total Offer (€)',
                    color='Category ID',
                    title='Categories Total Offer by Group'
                )
                fig_stacked.update_layout(height=500)
                st.plotly_chart(fig_stacked, use_container_width=True)
            
            with col2:
                # Scatter plot: items count vs total offer
                fig_scatter = px.scatter(
                    filtered_df,
                    x='Items Count',
                    y='Total Offer (€)',
                    color='Group ID',
                    size='Total Offer (€)',
                    hover_data=['Category ID', 'Category Name'],
                    title='Items Count vs Total Offer'
                )
                fig_scatter.update_layout(height=500)
                st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.warning("No categories match the current filters.")
    
    def display_items_analysis(self):
        """Display items analysis with charts"""
        if not self.data:
            st.error("No data available. Please upload and process a file first.")
            return
            
        st.header("🔧 Items Analysis")
        
        # Prepare items data
        items_data = []
        for group in self.data.get('product_groups', []):
            for category in group.get('categories', []):
                for item in category.get('items', []):
                    items_data.append({
                        'Group ID': group.get('group_id', 'Unknown'),
                        'Group Name': group.get('group_name', 'Unnamed'),
                        'Category ID': category.get('category_id', 'Unknown'),
                        'Category Name': category.get('category_name', 'Unnamed'),
                        'Position': item.get('position', ''),
                        'Code': item.get('code', 'Unknown'),
                        'Description': item.get('description', 'No description')[:100] + ('...' if len(item.get('description', '')) > 100 else ''),
                        'Full Description': item.get('description', 'No description'),
                        'Quantity': item.get('quantity', 0),
                        'Unit Price (€)': item.get('pricelist_unit_price', 0),
                        'Total Price (€)': item.get('pricelist_total_price', 0),
                        'Unit Cost (€)': item.get('unit_cost', 0),
                        'Total Cost (€)': item.get('total_cost', 0)
                    })
        
        df_items = pd.DataFrame(items_data)
        
        if df_items.empty:
            st.warning("No item data to display.")
            return
        
        # Filter controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            unique_groups = df_items['Group ID'].unique()
            selected_groups = st.multiselect(
                "Filter by Groups",
                options=unique_groups,
                default=unique_groups[:min(5, len(unique_groups))],  # Limit initial selection
                key="items_group_filter"
            )
        
        with col2:
            min_total_price = st.number_input(
                "Minimum Total Price (€)",
                min_value=0.0,
                value=1000.0,
                step=100.0,
                key="items_min_price"
            )
        
        with col3:
            search_term = st.text_input(
                "Search in Description",
                value="",
                placeholder="Enter search term...",
                key="items_search"
            )
        
        # Apply filters
        filtered_items = df_items[
            (df_items['Group ID'].isin(selected_groups)) &
            (df_items['Total Price (€)'] >= min_total_price)
        ]
        
        if search_term:
            filtered_items = filtered_items[
                filtered_items['Full Description'].str.contains(search_term, case=False, na=False)
            ]
        
        # Display summary metrics
        if len(filtered_items) > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Filtered Items", len(filtered_items))
            with col2:
                st.metric("Total Value", f"€{filtered_items['Total Price (€)'].sum():,.2f}")
            with col3:
                st.metric("Average Price", f"€{filtered_items['Total Price (€)'].mean():,.2f}")
            with col4:
                st.metric("Max Price", f"€{filtered_items['Total Price (€)'].max():,.2f}")
            
            # Display top items table
            st.subheader("🔝 Top Items by Value")
            top_items = filtered_items.nlargest(20, 'Total Price (€)')
            
            # Create display table with shortened descriptions
            display_columns = ['Group ID', 'Category ID', 'Code', 'Description', 'Quantity', 'Unit Price (€)', 'Total Price (€)']
            st.dataframe(top_items[display_columns], use_container_width=True)
            
            # Charts
            if len(top_items) > 0:
                # Top items bar chart
                fig_items = px.bar(
                    top_items.head(15),
                    x='Total Price (€)',
                    y='Code',
                    orientation='h',
                    title='Top 15 Items by Total Price',
                    text='Total Price (€)',
                    color='Total Price (€)',
                    color_continuous_scale='Plasma'
                )
                fig_items.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
                fig_items.update_layout(height=600)
                st.plotly_chart(fig_items, use_container_width=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Price distribution histogram
                    fig_hist = px.histogram(
                        filtered_items,
                        x='Total Price (€)',
                        nbins=30,
                        title='Price Distribution',
                        labels={'count': 'Number of Items'}
                    )
                    fig_hist.update_layout(height=400)
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                with col2:
                    # Quantity vs Price scatter
                    sample_items = filtered_items.sample(min(500, len(filtered_items)))  # Sample for performance
                    fig_scatter = px.scatter(
                        sample_items,
                        x='Quantity',
                        y='Total Price (€)',
                        color='Group ID',
                        hover_data=['Code', 'Description'],
                        title='Quantity vs Total Price (Sample)'
                    )
                    fig_scatter.update_layout(height=400)
                    st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.warning("No items match the current filters. Please adjust your criteria.")
    
    def display_financial_analysis(self):
        """Display comprehensive financial analysis"""
        if not self.data:
            st.error("No data available. Please upload and process a file first.")
            return
            
        st.header("💰 Financial Analysis")
        
        totals = self.data.get('totals', {})
        
        # Financial breakdown
        financial_data = {
            'Category': ['Equipment', 'Installation', 'DOC Fee', 'PM Fee', 'Warranty Fee'],
            'Amount (€)': [
                totals.get('equipment_total', 0),
                totals.get('installation_total', 0), 
                totals.get('doc_fee', 0),
                totals.get('pm_fee', 0),
                totals.get('warranty_fee', 0)
            ]
        }
        
        df_financial = pd.DataFrame(financial_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Financial breakdown pie chart
            fig_pie = px.pie(
                df_financial,
                values='Amount (€)',
                names='Category',
                title='Financial Breakdown'
            )
            fig_pie.update_layout(height=500)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Financial breakdown waterfall chart
            fig_waterfall = go.Figure(go.Waterfall(
                name="Financial Flow",
                orientation="v",
                measure=["absolute", "relative", "relative", "relative", "relative", "total"],
                x=["Equipment", "Installation", "DOC Fee", "PM Fee", "Warranty Fee", "Grand Total"],
                textposition="outside",
                text=[f"€{x:,.0f}" for x in financial_data['Amount (€)']] + [f"€{totals.get('grand_total', 0):,.0f}"],
                y=[
                    totals.get('equipment_total', 0),
                    totals.get('installation_total', 0),
                    totals.get('doc_fee', 0),
                    totals.get('pm_fee', 0),
                    totals.get('warranty_fee', 0),
                    totals.get('grand_total', 0)
                ],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
            ))
            
            fig_waterfall.update_layout(
                title="Financial Waterfall Analysis",
                showlegend=False,
                height=500
            )
            st.plotly_chart(fig_waterfall, use_container_width=True)
        
        # Group-level financial analysis
        st.subheader("📊 Financial Analysis by Group")
        
        group_financial = []
        for group in self.data.get('product_groups', []):
            equipment_total = sum(cat.get('total_offer', 0) for cat in group.get('categories', []) 
                                if not cat.get('category_id', '').startswith('E'))
            installation_total = sum(cat.get('total_offer', 0) for cat in group.get('categories', []) 
                                   if cat.get('category_id', '').startswith('E'))
            
            group_name = group.get('group_name', 'Unnamed')
            if len(group_name) > 30:
                group_name = group_name[:30] + '...'
            
            group_financial.append({
                'Group ID': group.get('group_id', 'Unknown'),
                'Group Name': group_name,
                'Equipment (€)': equipment_total,
                'Installation (€)': installation_total,
                'Total (€)': equipment_total + installation_total
            })
        
        df_group_financial = pd.DataFrame(group_financial)
        
        if not df_group_financial.empty:
            # Stacked bar chart for group financial breakdown
            fig_stacked = px.bar(
                df_group_financial,
                x='Group ID',
                y=['Equipment (€)', 'Installation (€)'],
                title='Equipment vs Installation Costs by Group',
                barmode='stack'
            )
            fig_stacked.update_layout(height=600)
            st.plotly_chart(fig_stacked, use_container_width=True)
            
            # Financial summary table
            st.dataframe(df_group_financial, use_container_width=True)
        else:
            st.warning("No financial data to display.")

def main():
    """Main application function"""
    
    st.title("📊 Excel Quotation Analyzer")
    st.markdown("### Interactive Analysis of Industrial Equipment Quotations")
    
    # Initialize analyzer if not exists
    if st.session_state.analyzer is None:
        st.session_state.analyzer = QuotationAnalyzer()
    
    analyzer = st.session_state.analyzer
    
    # Sidebar for file upload and controls
    with st.sidebar:
        st.header("🔧 Controls")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Excel Quotation File",
            type=['xlsx', 'xls'],
            help="Upload a PRE_ONLY_OFFER format Excel file",
            key="file_uploader"
        )
        
        if uploaded_file is not None:
            st.success(f"File uploaded: {uploaded_file.name}")
            
            # Process file
            if st.button("🚀 Process File", type="primary", key="process_button"):
                with st.spinner("Processing Excel file..."):
                    if analyzer.load_and_process_file(uploaded_file):
                        st.success("✅ File processed successfully!")
                        st.session_state.data_loaded = True
                        st.session_state.analyzer = analyzer  # Update session state
                        st.rerun()  # Refresh to show navigation
                    else:
                        st.error("❌ Failed to process file")
                        st.session_state.data_loaded = False
        
        # Navigation - only show if data is loaded
        selected_analysis = None
        if st.session_state.data_loaded and analyzer.data:
            st.markdown("---")
            st.subheader("📋 Navigation")
            
            analysis_options = [
                "Project Summary",
                "Tree Structure", 
                "Groups Analysis",
                "Categories Analysis",
                "Items Analysis",
                "Financial Analysis"
            ]
            
            selected_analysis = st.radio(
                "Select Analysis View",
                analysis_options,
                index=analysis_options.index(st.session_state.selected_view),
                key="navigation_radio"
            )
            
            # Update session state
            if selected_analysis != st.session_state.selected_view:
                st.session_state.selected_view = selected_analysis
                st.rerun()
            
            # Export options
            st.markdown("---")
            st.subheader("💾 Export")
            
            if st.button("📄 Download JSON", key="download_json"):
                if analyzer.data:
                    json_str = json.dumps(analyzer.data, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="⬇️ Download JSON File",
                        data=json_str,
                        file_name="quotation_data.json",
                        mime="application/json",
                        key="download_button"
                    )
            
            # Debug info
            with st.expander("🔍 Debug Info"):
                st.write(f"Data loaded: {st.session_state.data_loaded}")
                st.write(f"Selected view: {st.session_state.selected_view}")
                st.write(f"Has data: {analyzer.data is not None}")
                if analyzer.data:
                    st.write(f"Product groups: {len(analyzer.data.get('product_groups', []))}")
    
    # Main content area
    if st.session_state.data_loaded and analyzer and analyzer.data:
        
        # Get current selection
        current_view = st.session_state.selected_view
        
        # Display selected analysis
        try:
            if current_view == "Project Summary":
                analyzer.display_project_summary()
                
            elif current_view == "Tree Structure":
                analyzer.display_tree_structure()
                
            elif current_view == "Groups Analysis":
                analyzer.display_groups_analysis()
                
            elif current_view == "Categories Analysis":
                analyzer.display_categories_analysis()
                
            elif current_view == "Items Analysis":
                analyzer.display_items_analysis()
                
            elif current_view == "Financial Analysis":
                analyzer.display_financial_analysis()
                
        except Exception as e:
            st.error(f"Error displaying {current_view}: {str(e)}")
            with st.expander("🔍 Error Details"):
                st.error(traceback.format_exc())
    
    else:
        # Welcome screen
        st.markdown("""
        ## 🚀 Welcome to Excel Quotation Analyzer
        
        This application helps you analyze industrial equipment quotations from Excel files.
        
        ### Features:
        - 📤 **Upload Excel Files**: Support for PRE_ONLY_OFFER format
        - 🌳 **Hierarchical View**: Interactive tree structure of groups, categories, and items
        - 📊 **Data Tables**: Detailed tabular views with filtering and search
        - 📈 **Visualizations**: Interactive charts and graphs using Plotly
        - 💰 **Financial Analysis**: Comprehensive cost breakdowns and analysis
        - 📄 **Export**: Download processed data as JSON
        
        ### Getting Started:
        1. Upload an Excel quotation file using the sidebar
        2. Click "Process File" to analyze the data
        3. Use the navigation menu to explore different views
        4. Filter and search data using the interactive controls
        
        ### Supported Data:
        - Project information and parameters
        - Product groups with hierarchical categories
        - Individual items with pricing and descriptions
        - Financial totals and fee calculations
        """)
        
        # Sample data info
        with st.expander("📋 Sample Data Structure"):
            st.json({
                "project": {
                    "id": "PRE_LSU2300105_NEW_04_QS",
                    "customer": "DrinkPAK II, LLC",
                    "parameters": {
                        "doc_percentage": 0.00632,
                        "pm_percentage": 0.02061,
                        "currency": "Euro"
                    }
                },
                "product_groups": [
                    {
                        "group_id": "TXT-71",
                        "group_name": "SMART DECISION MAKER",
                        "categories": [
                            {
                                "category_id": "SWZZ",
                                "category_name": "SDM - SOFTWARE",
                                "items": ["..."]
                            }
                        ]
                    }
                ],
                "totals": {
                    "equipment_total": 8492539.36,
                    "installation_total": 1273880.90,
                    "grand_total": 10029429.96
                }
            })

if __name__ == "__main__":
    main() 
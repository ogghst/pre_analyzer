"""
Unified Analyzer for Industrial Equipment Quotations
Automatically detects file type and provides comprehensive analysis widgets
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Union
import sys
import os
import decimal

# Import IndustrialQuotation model and ParserType enum
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from models.quotation_models import IndustrialQuotation, ParserType

# Import field constants
from ..field_constants import JsonFields, DisplayFields

# Import formatters
from utils.format import safe_format_number, safe_format_currency, safe_format_percentage


class UnifiedAnalyzer:
    """Unified analyzer that works directly with IndustrialQuotation objects"""
    
    def __init__(self, quotation: IndustrialQuotation, detected_file_type: str = None):
        self.quotation = quotation
        self.project = quotation.project
        self.product_groups = quotation.product_groups
        self.totals = quotation.totals
        self.detected_file_type = detected_file_type or self._detect_file_type()
        
    def _detect_file_type(self) -> str:
        """Infer file type from IndustrialQuotation parser_type attribute"""
        # Use parser type from the quotation model
        if hasattr(self.quotation, 'parser_type') and self.quotation.parser_type:
            if self.quotation.parser_type == ParserType.PRE_FILE_PARSER:
                return 'pre'
            elif self.quotation.parser_type == ParserType.ANALISI_PROFITTABILITA_PARSER:
                return 'analisi_profittabilita'
        
        # Default fallback if parser_type is not available or unrecognized
        return 'analisi_profittabilita'
    
    def get_analysis_views(self) -> List[str]:
        """Return list of available analysis views"""
        return [
            "Project Summary",
            "Tree Structure", 
            "Groups Analysis",
            "Categories Analysis",
            "Items Analysis",
            "Profitability Analysis",
            "UTM Analysis",
            "Financial Analysis",
            "Field Analysis"
        ]
    
    def display_project_summary(self):
        """Display unified project summary information"""
        st.header("📋 Project Summary")
        
        # Show file type detection info
        file_type_display = "PRE Quotation" if self.detected_file_type == 'pre' else "Analisi Profittabilita"
        st.info(f"🔍 **Detected File Type:** {file_type_display}")
        
        # Create columns for metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Project ID", self.project.id or 'N/A')
            st.metric("Project Name", self.project.customer or 'N/A')
            st.metric("Project Listino", self.project.listino or 'N/A')
            
        with col2:
            st.metric("Area Manager", self.project.sales_info.area_manager or 'N/A')
            st.metric("Author", self.project.sales_info.author or 'N/A')
            st.metric("Agent", self.project.sales_info.agent or 'N/A')
            
        with col3:
            st.metric("Groups", len(self.product_groups))
            st.metric("Categories", sum(len(group.categories) for group in self.product_groups))
            total_items = sum(len(category.items) for group in self.product_groups for category in group.categories)
            st.metric("Items", total_items)
            
        # Financial summary
        st.subheader("💰 Financial Summary")

        # Show extended layout with offer data
        fin_col1, fin_col2, fin_col3, fin_col4, fin_col5 = st.columns(5)
        
        with fin_col1:
            st.metric("Total Listino", safe_format_currency(self.totals.total_pricelist))
        with fin_col2:
            st.metric("Total Cost", safe_format_currency(self.totals.total_cost))
        with fin_col3:
            st.metric("Total Offer", safe_format_currency(self.totals.total_offer))
        with fin_col4:
            st.metric("Offer Margin", safe_format_currency(self.totals.offer_margin))
        with fin_col5:
            st.metric("Offer Margin %", safe_format_percentage(self.totals.offer_margin_percentage))
    
    def display_profitability_analysis(self):
        """Display comprehensive profitability analysis"""
        st.header("💹 Profitability Analysis")
        
        # Overall profitability metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # Profitability pie chart
            if self.detected_file_type == 'analisi_profittabilita':
                total_offer = getattr(self.totals, 'total_offer', 0) or 0
                total_cost = getattr(self.totals, 'total_cost', 0) or 0
                
                if total_offer > 0:
                    offer_margin = total_offer - total_cost
                    profit_data = {
                        DisplayFields.CATEGORY_NAME: ['Total Cost', 'Offer Margin'],
                        'Amount (€)': [total_cost, offer_margin],
                    }
                    title = 'Cost vs Offer Margin Distribution'
                    color_map = {'Total Cost': '#ff6b6b', 'Offer Margin': '#51cf66'}
                else:
                    total_pricelist = getattr(self.totals, 'total_pricelist', 0) or 0
                    listino_margin = total_pricelist - total_cost
                    profit_data = {
                        DisplayFields.CATEGORY_NAME: ['Total Cost', 'Listino Margin'],
                        'Amount (€)': [total_cost, listino_margin],
                    }
                    title = 'Cost vs Listino Margin Distribution'
                    color_map = {'Total Cost': '#ff6b6b', 'Listino Margin': '#51cf66'}
            else:
                # PRE file
                total_cost = getattr(self.totals, 'total_cost', 0) or 0
                offer_margin = getattr(self.totals, 'offer_margin', 0) or 0
                profit_data = {
                    DisplayFields.CATEGORY_NAME: ['Total Cost', 'Margin'],
                    'Amount (€)': [total_cost, offer_margin],
                }
                title = 'Cost vs Margin Distribution'
                color_map = {'Total Cost': '#ff6b6b', 'Margin': '#51cf66'}
            
            df_profit = pd.DataFrame(profit_data)
            
            fig_pie = px.pie(
                df_profit,
                values='Amount (€)',
                names=DisplayFields.CATEGORY_NAME,
                title=title,
                color=DisplayFields.CATEGORY_NAME,
                color_discrete_map=color_map
            )
            fig_pie.update_layout(height=500)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Category profitability chart
            category_data = []
            for group in self.product_groups:
                for category in group.categories:
                    cat_total = self._get_category_total(category)
                    
                    if self.detected_file_type == 'analisi_profittabilita':
                        cat_cost = getattr(category, 'cost_subtotal', 0) or 0
                        cat_revenue = getattr(category, 'offer_price', 0) or 0
                        if cat_revenue == 0:
                            cat_revenue = cat_total
                    else:
                        cat_cost = sum(getattr(item, 'total_cost', 0) or 0 for item in category.items)
                        cat_revenue = cat_total
                    
                    cat_margin = cat_revenue - cat_cost
                    try:
                        cat_margin_perc = (cat_margin / cat_revenue * 100) if cat_revenue > 0 else 0
                    except (ZeroDivisionError, decimal.DivisionUndefined, decimal.InvalidOperation):
                        cat_margin_perc = 0
                    
                    if cat_revenue > 0:
                        category_data.append({
                            'Category': category.category_id or 'Unknown',
                            'Revenue': cat_revenue,
                            'Cost': cat_cost,
                            'Margin %': cat_margin_perc
                        })
            
            df_categories = pd.DataFrame(category_data)
            
            if not df_categories.empty:
                # Top categories by revenue
                top_categories = df_categories.nlargest(10, 'Revenue')
                
                fig_category = px.bar(
                    top_categories,
                    x='Category',
                    y='Margin %',
                    title='Top 10 Categories by Margin %',
                    text='Margin %',
                    color='Margin %',
                    color_continuous_scale='RdYlGn'
                )
                fig_category.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig_category.update_layout(height=500)
                st.plotly_chart(fig_category, use_container_width=True)
        
        # Category-level profitability analysis
        st.subheader("📊 Profitability by Category")
        
        # Collect category-level data
        category_data = []
        for group in self.product_groups:
            for category in group.categories:
                cat_total = self._get_category_total(category)
                
                # Calculate cost based on file type
                if self.detected_file_type == 'analisi_profittabilita':
                    cat_cost = getattr(category, 'cost_subtotal', 0) or 0
                    cat_revenue = getattr(category, 'offer_price', 0) or 0
                    if cat_revenue == 0:
                        cat_revenue = cat_total
                else:
                    cat_cost = sum(getattr(item, 'total_cost', 0) or 0 for item in category.items)
                    cat_revenue = cat_total
                
                cat_margin = cat_revenue - cat_cost
                try:
                    cat_margin_perc = (cat_margin / cat_revenue * 100) if cat_revenue > 0 else 0
                except (ZeroDivisionError, decimal.DivisionUndefined, decimal.InvalidOperation):
                    cat_margin_perc = 0
                
                category_data.append({
                    'Category': category.category_id or 'Unknown',
                    'Group': group.group_id or 'Unknown',
                    'Revenue (€)': cat_revenue,
                    'Cost (€)': cat_cost,
                    'Margin (€)': cat_margin,
                    'Margin (%)': cat_margin_perc
                })
        
        df_categories = pd.DataFrame(category_data)
        
        if not df_categories.empty:
            # Category profitability table
            st.subheader("📋 Category Profitability Table")
            
            # Configure column formats
            column_config = {
                'Revenue (€)': st.column_config.NumberColumn(
                    "Revenue (€)",
                    format="€%.0f",
                    help="Total revenue for this category"
                ),
                "Cost (€)": st.column_config.NumberColumn(
                    "Cost (€)", 
                    format="€%.0f",
                    help="Total cost for this category"
                ),
                "Margin (€)": st.column_config.NumberColumn(
                    "Margin (€)",
                    format="€%.0f", 
                    help="Profit margin for this category"
                ),
                "Margin (%)": st.column_config.NumberColumn(
                    "Margin (%)",
                    format="%.2f%%",
                    help="Profit margin percentage"
                )
            }
            
            st.dataframe(df_categories, use_container_width=True, column_config=column_config)
            
            # Category profitability chart
            fig_bar = go.Figure()
            
            fig_bar.add_trace(go.Bar(
                name='Revenue',
                x=df_categories['Category'],
                y=df_categories['Revenue (€)'],
                marker_color='#2E86AB'
            ))
            
            fig_bar.add_trace(go.Bar(
                name='Cost',
                x=df_categories['Category'],
                y=df_categories['Cost (€)'],
                marker_color='#A23B72'
            ))
            
            fig_bar.update_layout(
                title='Revenue vs Cost by Category',
                xaxis_title='Category',
                yaxis_title='Amount (€)',
                barmode='group',
                height=500
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("No category data available for profitability analysis.")
    
    def display_utm_analysis(self):
        """Display Cost Center Analysis - generalized for all cost centers"""
        st.header("💰 Cost Center Analysis")
        
        # Collect all cost center data from all items
        cost_center_data = []
        cost_center_fields = [
            ('UTM Robot', 'utm_robot', 'utm_robot_h'),
            ('UTM LGV', 'utm_lgv', 'utm_lgv_h'),
            ('UTM Intra', 'utm_intra', 'utm_intra_h'),
            ('UTM Layout', 'utm_layout', 'utm_layout_h'),
            ('PM Cost', 'pm_cost', 'pm_h'),
            ('Install', 'install', 'install_h'),
            ('After Sales', 'after_sales', 'after_sales_h'),
            ('Total Cost', 'total_cost', 'total_h')
        ]
        
        for group in self.product_groups:
            for category in group.categories:
                for item in category.items:
                    item_data = {
                        DisplayFields.GROUP_ID: group.group_id or 'Unknown',
                        DisplayFields.CATEGORY_ID: category.category_id or 'Unknown',
                        DisplayFields.ITEM_CODE: item.code or 'Unknown',
                        DisplayFields.ITEM_DESCRIPTION: self._truncate_text(item.description or '', 40),
                    }
                    
                    # Add all cost center fields
                    total_cost = 0
                    total_hours = 0
                    has_data = False
                    
                    for field_name, cost_field, hours_field in cost_center_fields:
                        cost_value = self._safe_float(getattr(item, cost_field, 0))
                        hours_value = self._safe_float(getattr(item, hours_field, 0))
                        
                        item_data[f'{field_name} (€)'] = cost_value
                        item_data[f'{field_name} Hours'] = hours_value
                        
                        if cost_value > 0 or hours_value > 0:
                            has_data = True
                        
                        total_cost += cost_value
                        total_hours += hours_value
                    
                    item_data['Total Cost (€)'] = total_cost
                    item_data['Total Hours'] = total_hours
                    
                    # Only include items with cost center data
                    if has_data:
                        cost_center_data.append(item_data)
        
        if cost_center_data:
            df_cost_center = pd.DataFrame(cost_center_data)
            
            # Cost center selection
            st.subheader("🎯 Select Cost Center for Analysis")
            
            # Get available cost centers
            available_cost_centers = []
            for field_name, _, _ in cost_center_fields:
                if df_cost_center[f'{field_name} (€)'].sum() > 0:
                    available_cost_centers.append(field_name)
            
            if available_cost_centers:
                selected_cost_center = st.selectbox(
                    "Select Cost Center",
                    options=available_cost_centers,
                    key="cost_center_selector"
                )
                
                # Filter data for selected cost center
                cost_col = f'{selected_cost_center} (€)'
                hours_col = f'{selected_cost_center} Hours'
                
                filtered_df = df_cost_center[df_cost_center[cost_col] > 0]
                
                if not filtered_df.empty:
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Items with Cost", len(filtered_df))
                    with col2:
                        st.metric("Total Cost", f"€{filtered_df[cost_col].sum():,.0f}")
                    with col3:
                        st.metric("Total Hours", f"{filtered_df[hours_col].sum():,.1f}")
                    with col4:
                        try:
                            avg_hourly = filtered_df[cost_col].sum() / filtered_df[hours_col].sum() if filtered_df[hours_col].sum() > 0 else 0
                        except (ZeroDivisionError, decimal.DivisionUndefined, decimal.InvalidOperation):
                            avg_hourly = 0
                        st.metric("Avg €/Hour", f"€{avg_hourly:.2f}")
                    
                    # Charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Cost distribution by category
                        category_costs = filtered_df.groupby(DisplayFields.CATEGORY_ID)[cost_col].sum().reset_index()
                        fig_category_pie = px.pie(
                            category_costs,
                            values=cost_col,
                            names=DisplayFields.CATEGORY_ID,
                            title=f'{selected_cost_center} Cost Distribution by Category'
                        )
                        fig_category_pie.update_layout(height=400)
                        st.plotly_chart(fig_category_pie, use_container_width=True)
                    
                    with col2:
                        # Top items by cost
                        top_items = filtered_df.nlargest(10, cost_col)
                        fig_top_items = px.bar(
                            top_items,
                            x=cost_col,
                            y=DisplayFields.ITEM_CODE,
                            orientation='h',
                            title=f'Top 10 Items by {selected_cost_center} Cost',
                            text=cost_col,
                            color=cost_col,
                            color_continuous_scale='Blues'
                        )
                        fig_top_items.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
                        fig_top_items.update_layout(height=400)
                        st.plotly_chart(fig_top_items, use_container_width=True)
                    
                    # Detailed table
                    st.subheader(f"📊 {selected_cost_center} Detailed Analysis")
                    
                    # Show top items with significant costs
                    significant_items = filtered_df[filtered_df[cost_col] > 100].nlargest(20, cost_col)
                    
                    if not significant_items.empty:
                        display_cols = [DisplayFields.CATEGORY_ID, DisplayFields.ITEM_CODE, DisplayFields.ITEM_DESCRIPTION, 
                                      cost_col, hours_col]
                        
                        # Configure column formats
                        cost_center_column_config = {
                            cost_col: st.column_config.NumberColumn(
                                f"{selected_cost_center} (€)",
                                format="€%.0f",
                                help=f"Cost for {selected_cost_center}"
                            ),
                            hours_col: st.column_config.NumberColumn(
                                f"{selected_cost_center} Hours",
                                format="%.1f",
                                help=f"Hours for {selected_cost_center}"
                            )
                        }
                        
                        st.dataframe(significant_items[display_cols], use_container_width=True, column_config=cost_center_column_config)
                    else:
                        st.info(f"No items with significant {selected_cost_center} costs found.")
                else:
                    st.info(f"No items with {selected_cost_center} costs found.")
            else:
                st.info("No cost center data available.")
        else:
            st.info("No cost center data found in the current dataset.")
    

    
    def display_financial_analysis(self):
        """Display comprehensive financial analysis similar to PRE Financial Analysis"""
        st.header("💼 Financial Analysis")
        
        # Calculate overall financial metrics
        total_revenue = 0
        total_cost = 0
        total_listino = 0
        total_offer = 0
        
        # Collect financial data by category
        financial_data = []
        
        for group in self.product_groups:
            for category in group.categories:
                cat_total = self._get_category_total(category)
                
                # Calculate costs and revenues based on file type
                if self.detected_file_type == 'analisi_profittabilita':
                    cat_cost = getattr(category, 'cost_subtotal', 0) or 0
                    cat_listino = getattr(category, 'pricelist_subtotal', 0) or 0
                    cat_offer = getattr(category, 'offer_price', 0) or 0
                    cat_revenue = cat_offer if cat_offer > 0 else cat_listino
                else:
                    cat_cost = sum(getattr(item, 'total_cost', 0) or 0 for item in category.items)
                    cat_listino = cat_total
                    cat_offer = 0
                    cat_revenue = cat_total
                
                total_revenue += cat_revenue
                total_cost += cat_cost
                total_listino += cat_listino
                total_offer += cat_offer
                
                cat_margin = cat_revenue - cat_cost
                try:
                    cat_margin_perc = (cat_margin / cat_revenue * 100) if cat_revenue > 0 else 0
                except (ZeroDivisionError, decimal.DivisionUndefined, decimal.InvalidOperation):
                    cat_margin_perc = 0
                
                financial_data.append({
                    'Group': group.group_id or 'Unknown',
                    'Category': category.category_id or 'Unknown',
                    'Revenue (€)': cat_revenue,
                    'Cost (€)': cat_cost,
                    'Margin (€)': cat_margin,
                    'Margin (%)': cat_margin_perc,
                    'Listino (€)': cat_listino,
                    'Offer (€)': cat_offer
                })
        
        # Overall financial summary
        st.subheader("📊 Overall Financial Summary")
        
        overall_margin = total_revenue - total_cost
        try:
            overall_margin_perc = (overall_margin / total_revenue * 100) if total_revenue > 0 else 0
        except (ZeroDivisionError, decimal.DivisionUndefined, decimal.InvalidOperation):
            overall_margin_perc = 0
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Revenue", f"€{total_revenue:,.0f}")
        with col2:
            st.metric("Total Cost", f"€{total_cost:,.0f}")
        with col3:
            st.metric("Total Margin", f"€{overall_margin:,.0f}")
        with col4:
            st.metric("Margin %", f"{overall_margin_perc:.2f}%")
        with col5:
            if total_listino > 0:
                discount_perc = ((total_listino - total_revenue) / total_listino * 100) if total_listino > 0 else 0
                st.metric("Discount %", f"{discount_perc:.2f}%")
        
        # Financial breakdown by category
        df_financial = pd.DataFrame(financial_data)
        
        if not df_financial.empty:
            st.subheader("💰 Financial Breakdown by Category")
            
            # Configure column formats
            financial_column_config = {
                'Revenue (€)': st.column_config.NumberColumn(
                    "Revenue (€)",
                    format="€%.0f",
                    help="Total revenue for this category"
                ),
                'Cost (€)': st.column_config.NumberColumn(
                    "Cost (€)",
                    format="€%.0f",
                    help="Total cost for this category"
                ),
                'Margin (€)': st.column_config.NumberColumn(
                    "Margin (€)",
                    format="€%.0f",
                    help="Profit margin for this category"
                ),
                'Margin (%)': st.column_config.NumberColumn(
                    "Margin (%)",
                    format="%.2f%%",
                    help="Profit margin percentage"
                ),
                'Listino (€)': st.column_config.NumberColumn(
                    "Listino (€)",
                    format="€%.0f",
                    help="Listino price for this category"
                ),
                'Offer (€)': st.column_config.NumberColumn(
                    "Offer (€)",
                    format="€%.0f",
                    help="Offer price for this category"
                )
            }
            
            st.dataframe(df_financial, use_container_width=True, column_config=financial_column_config)
            
            # Financial charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Revenue vs Cost waterfall chart
                fig_waterfall = go.Figure()
                
                # Add revenue bars
                fig_waterfall.add_trace(go.Bar(
                    name='Revenue',
                    x=df_financial['Category'],
                    y=df_financial['Revenue (€)'],
                    marker_color='#2E86AB'
                ))
                
                # Add cost bars
                fig_waterfall.add_trace(go.Bar(
                    name='Cost',
                    x=df_financial['Category'],
                    y=df_financial['Cost (€)'],
                    marker_color='#A23B72'
                ))
                
                fig_waterfall.update_layout(
                    title='Revenue vs Cost by Category',
                    xaxis_title='Category',
                    yaxis_title='Amount (€)',
                    barmode='group',
                    height=500
                )
                
                st.plotly_chart(fig_waterfall, use_container_width=True)
            
            with col2:
                # Margin analysis
                fig_margin = px.scatter(
                    df_financial,
                    x='Revenue (€)',
                    y='Margin (%)',
                    size='Margin (€)',
                    color='Group',
                    hover_data=['Category'],
                    title='Margin Analysis: Revenue vs Margin %'
                )
                fig_margin.update_layout(height=500)
                st.plotly_chart(fig_margin, use_container_width=True)
            
            # Top performers analysis
            st.subheader("🏆 Top Performers")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top categories by revenue
                top_revenue = df_financial.nlargest(10, 'Revenue (€)')
                fig_top_revenue = px.bar(
                    top_revenue,
                    x='Revenue (€)',
                    y='Category',
                    orientation='h',
                    title='Top 10 Categories by Revenue',
                    text='Revenue (€)',
                    color='Margin (%)',
                    color_continuous_scale='RdYlGn'
                )
                fig_top_revenue.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
                fig_top_revenue.update_layout(height=500)
                st.plotly_chart(fig_top_revenue, use_container_width=True)
            
            with col2:
                # Top categories by margin percentage
                top_margin = df_financial[df_financial['Revenue (€)'] > 1000].nlargest(10, 'Margin (%)')
                fig_top_margin = px.bar(
                    top_margin,
                    x='Margin (%)',
                    y='Category',
                    orientation='h',
                    title='Top 10 Categories by Margin %',
                    text='Margin (%)',
                    color='Margin (%)',
                    color_continuous_scale='RdYlGn'
                )
                fig_top_margin.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig_top_margin.update_layout(height=500)
                st.plotly_chart(fig_top_margin, use_container_width=True)
            
            # Risk analysis
            st.subheader("⚠️ Risk Analysis")
            
            # Categories with low margin
            low_margin = df_financial[df_financial['Margin (%)'] < 15]
            high_value_low_margin = low_margin[low_margin['Revenue (€)'] > 10000]
            
            if not high_value_low_margin.empty:
                st.warning("Categories with High Revenue but Low Margin (<15%):")
                risk_column_config = {
                    'Revenue (€)': st.column_config.NumberColumn(
                        "Revenue (€)",
                        format="€%.0f",
                        help="Revenue for this category"
                    ),
                    'Margin (%)': st.column_config.NumberColumn(
                        "Margin (%)",
                        format="%.2f%%",
                        help="Margin percentage"
                    )
                }
                st.dataframe(high_value_low_margin[['Category', 'Revenue (€)', 'Margin (%)']].head(10), 
                           use_container_width=True, column_config=risk_column_config)
            else:
                st.success("No high-value categories with concerning low margins found.")
        else:
            st.warning("No financial data available for analysis.")

    def display_field_analysis(self):
        """Display comprehensive field analysis"""
        st.header("🔍 Comprehensive Field Analysis")
        
        # Collect field usage statistics
        field_stats = {}
        total_items = 0
        
        # Analyze field usage
        for group in self.product_groups:
            for category in group.categories:
                for item in category.items:
                    total_items += 1
                    # Convert item to dict for field analysis
                    if hasattr(item, '__dict__'):
                        item_dict = item.__dict__
                    else:
                        item_dict = {}
                        
                    for field, value in item_dict.items():
                        if isinstance(value, (int, float)) and value != 0:
                            if field not in field_stats:
                                field_stats[field] = {'count': 0, 'sum': 0, 'max': 0}
                            field_stats[field]['count'] += 1
                            field_stats[field]['sum'] += value
                            field_stats[field]['max'] = max(field_stats[field]['max'], value)
        
        # Show field type detection
        st.info(f"🔍 **File Type:** {self.detected_file_type.replace('_', ' ').title()}")
        
        # Top fields analysis
        st.subheader("🔝 Most Used Fields")
        
        if field_stats:
            top_fields = sorted(field_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:15]
            
            top_fields_data = []
            for field, stats in top_fields:
                usage_perc = (stats['count'] / total_items * 100) if total_items > 0 else 0
                avg_value = stats['sum'] / stats['count'] if stats['count'] > 0 else 0
                
                top_fields_data.append({
                    'Field': field,
                    'Items with Data': stats['count'],
                    'Usage %': usage_perc,
                    'Total Value': stats['sum'],
                    'Average Value': avg_value,
                    'Max Value': stats['max']
                })
            
            df_top_fields = pd.DataFrame(top_fields_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Usage chart
                fig_top_usage = px.bar(
                    df_top_fields.head(10),
                    x='Usage %',
                    y='Field',
                    orientation='h',
                    title='Top 10 Fields by Usage',
                    text='Usage %',
                    color='Usage %',
                    color_continuous_scale='Blues'
                )
                fig_top_usage.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig_top_usage.update_layout(height=500)
                st.plotly_chart(fig_top_usage, use_container_width=True)
            
            with col2:
                # Value chart
                fig_top_value = px.bar(
                    df_top_fields.head(10),
                    x='Total Value',
                    y='Field',
                    orientation='h',
                    title='Top 10 Fields by Total Value',
                    text='Total Value',
                    color='Total Value',
                    color_continuous_scale='Reds'
                )
                fig_top_value.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
                fig_top_value.update_layout(height=500)
                st.plotly_chart(fig_top_value, use_container_width=True)
            
            # Detailed fields table
            field_analysis_column_config = {
                'Items with Data': st.column_config.NumberColumn(
                    "Items with Data",
                    format="localized",
                    help="Number of items that have data in this field"
                ),
                'Usage %': st.column_config.NumberColumn(
                    "Usage %",
                    format="%.2f%%",
                    help="Percentage of items using this field"
                ),
                'Total Value': st.column_config.NumberColumn(
                    "Total Value",
                    format="localized",
                    help="Sum of all values in this field"
                ),
                'Average Value': st.column_config.NumberColumn(
                    "Average Value",
                    format="localized",
                    help="Average value for this field"
                ),
                'Max Value': st.column_config.NumberColumn(
                    "Max Value",
                    format="localized",
                    help="Maximum value found in this field"
                )
            }
            
            st.dataframe(df_top_fields, use_container_width=True, column_config=field_analysis_column_config)
        else:
            st.info("No field data found for analysis.")
    
    def _count_items_with_data(self) -> int:
        """Count items that have non-zero values in any field"""
        count = 0
        for group in self.product_groups:
            for category in group.categories:
                for item in category.items:
                    # Convert item to dict for field analysis
                    if hasattr(item, '__dict__'):
                        item_dict = item.__dict__
                    else:
                        item_dict = {}
                    
                    has_data = any(
                        isinstance(value, (int, float)) and value != 0 
                        for value in item_dict.values()
                    )
                    if has_data:
                        count += 1
        return count
    
    # Implement helper methods for working with model objects
    def _get_group_total(self, group) -> float:
        """Get total value for a group based on file type"""
        if self.detected_file_type == 'analisi_profittabilita':
            return sum(getattr(cat, 'pricelist_subtotal', 0) or 0 for cat in group.categories)
        else:
            # PRE file
            return sum(getattr(item, 'pricelist_total_price', 0) or 0 for cat in group.categories for item in cat.items)
    
    def _get_category_total(self, category) -> float:
        """Get total value for a category based on file type"""
        if self.detected_file_type == 'analisi_profittabilita':
            return getattr(category, 'pricelist_subtotal', 0) or 0
        else:
            # PRE file
            return sum(getattr(item, 'pricelist_total_price', 0) or 0 for item in category.items)
    
    def _get_item_price(self, item) -> float:
        """Get item price based on file type"""
        if self.detected_file_type == 'analisi_profittabilita':
            return getattr(item, 'pricelist_total_price', 0) or 0
        else:
            # PRE file
            return getattr(item, 'pricelist_total_price', 0) or 0
    
    def _get_item_unit_price(self, item) -> float:
        """Get unit price for an item based on file type"""
        return getattr(item, 'pricelist_unit_price', 0) or 0
    
    def _get_category_specific_fields(self, category) -> Dict[str, Any]:
        """Get category-specific fields based on file type"""
        if self.detected_file_type == 'analisi_profittabilita':
            return {
                'Subtotal Listino (€)': getattr(category, 'pricelist_subtotal', 0) or 0,
                'Subtotal Costo (€)': getattr(category, 'cost_subtotal', 0) or 0,
                'Total Cost (€)': getattr(category, 'total_cost', 0) or 0,
                'WBE': getattr(category, 'wbe', '') or ''
            }
        else:
            # PRE file
            return {
                'Subtotal (€)': self._get_category_total(category),
                'Items Count': len(category.items)
            }
    
    def _get_item_specific_fields(self, item) -> Dict[str, Any]:
        """Get item-specific fields based on file type"""
        if self.detected_file_type == 'analisi_profittabilita':
            return {
                'Unit Cost (€)': getattr(item, 'unit_cost', 0) or 0,
                'Total Cost (€)': getattr(item, 'total_cost', 0) or 0,
                'UTM Robot': getattr(item, 'utm_robot', 0) or 0,
                'PM Cost': getattr(item, 'pm_cost', 0) or 0,
                'Install': getattr(item, 'install', 0) or 0,
                'After Sales': getattr(item, 'after_sales', 0) or 0
            }
        else:
            # PRE file
            return {
                'Unit Price (€)': getattr(item, 'pricelist_unit_price', 0) or 0,
                'Cost (€)': getattr(item, 'total_cost', 0) or 0,
                'Quantity': getattr(item, 'quantity', 0) or 0
            }
    
    def _truncate_text(self, text: str, max_length: int = 50) -> str:
        """Truncate text to specified maximum length"""
        if isinstance(text, str) and len(text) > max_length:
            return text[:max_length] + "..."
        return str(text) if text is not None else ""
    
    def _safe_float(self, value, default: float = 0.0) -> float:
        """Safely convert value to float"""
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError, decimal.DivisionUndefined, decimal.InvalidOperation):
            return default
    
    def display_tree_structure(self):
        """Display hierarchical tree structure"""
        st.header("🌳 Hierarchical Structure")
        
        if not self.product_groups:
            st.warning("No product groups found in the data.")
            return
        
        # Create expandable tree structure
        for group_idx, group in enumerate(self.product_groups):
            group_total = self._get_group_total(group)
            
            with st.expander(
                f"🏗️ {group.group_id or 'Unknown'}: {group.group_name or 'Unnamed Group'} (€{group_total:,.2f})", 
                expanded=False
            ):
                categories = group.categories
                if not categories:
                    st.info("No categories found in this group.")
                    continue
                
                for category in categories:
                    cat_total = self._get_category_total(category)
                    st.markdown(f"**📂 {category.category_id or 'Unknown'}: {category.category_name or 'Unnamed Category'}** (€{cat_total:,.2f})")
                    
                    # Show top items in this category
                    items = category.items
                    items_with_value = [item for item in items if self._get_item_price(item) > 0]
                    
                    if items_with_value:
                        top_items = sorted(items_with_value, key=lambda x: self._get_item_price(x), reverse=True)
                        
                        for item in top_items[:10]:  # Show top 10 items
                            description = item.description or 'No description'
                            if len(description) > 80:
                                description = description[:80] + "..."
                            price = self._get_item_price(item)
                            st.markdown(f"  • `{item.code or 'Unknown'}`: {description} (€{price:,.2f})")
                    else:
                        st.markdown("  • *No items with value*")
                    
                    st.markdown("---")

    def display_groups_analysis(self):
        """Display groups analysis with charts"""
        st.header("📦 Product Groups Analysis")
        
        if not self.product_groups:
            st.warning("No product groups found in the data.")
            return
        
        # Prepare groups data
        groups_data = []
        for group in self.product_groups:
            group_total = self._get_group_total(group)
            total_items = sum(len(cat.items) for cat in group.categories)
            
            # Calculate costs based on file type
            if self.detected_file_type == 'analisi_profittabilita':
                group_cost = sum(getattr(cat, 'cost_subtotal', 0) or 0 for cat in group.categories)
                group_revenue = sum(getattr(cat, 'offer_price', 0) or 0 for cat in group.categories)
                if group_revenue == 0:
                    group_revenue = group_total
            else:
                group_cost = sum(getattr(item, 'total_cost', 0) or 0 for cat in group.categories for item in cat.items)
                group_revenue = group_total
            
            group_margin = group_revenue - group_cost
            try:
                group_margin_perc = (group_margin / group_revenue * 100) if group_revenue > 0 else 0
            except (ZeroDivisionError, decimal.DivisionUndefined, decimal.InvalidOperation):
                group_margin_perc = 0
            
            groups_data.append({
                DisplayFields.GROUP_ID: group.group_id or 'Unknown',
                DisplayFields.GROUP_NAME: group.group_name or 'Unnamed',
                DisplayFields.CATEGORIES_COUNT: len(group.categories),
                DisplayFields.TOTAL_ITEMS: total_items,
                'Revenue (€)': group_revenue,
                'Cost (€)': group_cost,
                'Margin (€)': group_margin,
                'Margin (%)': group_margin_perc,
                DisplayFields.QUANTITY: getattr(group, 'quantity', 1) or 1
            })
        
        df_groups = pd.DataFrame(groups_data)
        
        if df_groups.empty:
            st.warning("No group data to display.")
            return
        
        # Display table
        st.subheader("📊 Groups Summary Table")
        
        # Configure column formats for groups table
        groups_column_config = {
            DisplayFields.CATEGORIES_COUNT: st.column_config.NumberColumn(
                "Categories",
                format="localized",
                help="Number of categories in this group"
            ),
            DisplayFields.TOTAL_ITEMS: st.column_config.NumberColumn(
                "Total Items",
                format="localized",
                help="Total number of items in this group"
            ),
            'Revenue (€)': st.column_config.NumberColumn(
                "Revenue (€)",
                format="€%.0f",
                help="Total revenue for this group"
            ),
            'Cost (€)': st.column_config.NumberColumn(
                "Cost (€)",
                format="€%.0f",
                help="Total cost for this group"
            ),
            'Margin (€)': st.column_config.NumberColumn(
                "Margin (€)",
                format="€%.0f",
                help="Profit margin for this group"
            ),
            'Margin (%)': st.column_config.NumberColumn(
                "Margin (%)",
                format="%.2f%%",
                help="Profit margin percentage"
            ),
            DisplayFields.QUANTITY: st.column_config.NumberColumn(
                "Quantity",
                format="localized",
                help="Quantity of this product group"
            )
        }
        
        st.dataframe(df_groups, use_container_width=True, column_config=groups_column_config)
        
        # Create charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue vs Cost chart
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                name='Revenue',
                x=df_groups[DisplayFields.GROUP_ID],
                y=df_groups['Revenue (€)'],
                marker_color='#2E86AB'
            ))
            fig_bar.add_trace(go.Bar(
                name='Cost',
                x=df_groups[DisplayFields.GROUP_ID],
                y=df_groups['Cost (€)'],
                marker_color='#A23B72'
            ))
            fig_bar.update_layout(
                title='Revenue vs Cost by Product Group',
                xaxis_title='Group',
                yaxis_title='Amount (€)',
                barmode='group',
                height=500
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Margin percentage chart
            fig_margin = px.bar(
                df_groups, 
                x=DisplayFields.GROUP_ID, 
                y='Margin (%)',
                title='Margin Percentage by Product Group',
                text='Margin (%)',
                color='Margin (%)',
                color_continuous_scale='RdYlGn'
            )
            fig_margin.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_margin.update_layout(height=500)
            st.plotly_chart(fig_margin, use_container_width=True)
        
        # Treemap visualization
        st.subheader("🗺️ Groups Treemap")
        fig_treemap = px.treemap(
            df_groups,
            path=[DisplayFields.GROUP_ID],
            values='Revenue (€)',
            title='Product Groups by Revenue',
            color='Margin (%)',
            color_continuous_scale='RdYlGn'
        )
        fig_treemap.update_layout(height=600)
        st.plotly_chart(fig_treemap, use_container_width=True)

    def display_categories_analysis(self):
        """Display categories analysis with charts"""
        st.header("📂 Categories Analysis")
        
        # Prepare categories data
        categories_data = []
        for group in self.product_groups:
            for category in group.categories:
                cat_total = self._get_category_total(category)
                
                # Calculate costs and revenues
                if self.detected_file_type == 'analisi_profittabilita':
                    cat_cost = getattr(category, 'cost_subtotal', 0) or 0
                    cat_revenue = getattr(category, 'offer_price', 0) or 0
                    if cat_revenue == 0:
                        cat_revenue = cat_total
                else:
                    cat_cost = sum(getattr(item, 'total_cost', 0) or 0 for item in category.items)
                    cat_revenue = cat_total
                
                cat_margin = cat_revenue - cat_cost
                try:
                    cat_margin_perc = (cat_margin / cat_revenue * 100) if cat_revenue > 0 else 0
                except (ZeroDivisionError, decimal.DivisionUndefined, decimal.InvalidOperation):
                    cat_margin_perc = 0
                
                categories_data.append({
                    DisplayFields.GROUP_ID: group.group_id or 'Unknown',
                    DisplayFields.GROUP_NAME: group.group_name or 'Unnamed',
                    DisplayFields.CATEGORY_ID: category.category_id or 'Unknown',
                    DisplayFields.CATEGORY_NAME: category.category_name or 'Unnamed',
                    DisplayFields.ITEMS_COUNT: len(category.items),
                    DisplayFields.TOTAL_EUR: cat_total,
                    'Revenue (€)': cat_revenue,
                    'Cost (€)': cat_cost,
                    'Margin (€)': cat_margin,
                    'Margin (%)': cat_margin_perc,
                    **self._get_category_specific_fields(category)
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
                options=df_categories[DisplayFields.GROUP_ID].unique(),
                default=df_categories[DisplayFields.GROUP_ID].unique(),
                key="categories_group_filter"
            )
        
        with col2:
            min_value = st.number_input(
                "Minimum Total Value (€)",
                min_value=0.0,
                value=0.0,
                step=1000.0,
                key="categories_min_value"
            )
        
        # Apply filters
        filtered_df = df_categories[
            (df_categories[DisplayFields.GROUP_ID].isin(selected_groups)) &
            (df_categories[DisplayFields.TOTAL_EUR] >= min_value)
        ]
        
        if filtered_df.empty:
            st.warning("No categories match the selected filters.")
            return
        
        # Display filtered data
        st.subheader("📊 Filtered Categories Table")
        
        # Configure column formats for categories table
        categories_column_config = {
            DisplayFields.ITEMS_COUNT: st.column_config.NumberColumn(
                "Items Count",
                format="localized",
                help="Number of items in this category"
            ),
            DisplayFields.TOTAL_EUR: st.column_config.NumberColumn(
                "Total (€)",
                format="€%.0f",
                help="Total value for this category"
            ),
            'Revenue (€)': st.column_config.NumberColumn(
                "Revenue (€)",
                format="€%.0f",
                help="Total revenue for this category"
            ),
            'Cost (€)': st.column_config.NumberColumn(
                "Cost (€)",
                format="€%.0f",
                help="Total cost for this category"
            ),
            'Margin (€)': st.column_config.NumberColumn(
                "Margin (€)",
                format="€%.0f",
                help="Profit margin for this category"
            ),
            'Margin (%)': st.column_config.NumberColumn(
                "Margin (%)",
                format="%.2f%%",
                help="Profit margin percentage"
            )
        }
        
        # Add specific fields configuration based on file type
        if self.detected_file_type == 'analisi_profittabilita':
            categories_column_config.update({
                'Subtotal Listino (€)': st.column_config.NumberColumn(
                    "Subtotal Listino (€)",
                    format="localized",
                    help="Subtotal from listino prices"
                ),
                'Subtotal Costo (€)': st.column_config.NumberColumn(
                    "Subtotal Costo (€)",
                    format="localized",
                    help="Subtotal of costs"
                ),
                'Total Cost (€)': st.column_config.NumberColumn(
                    "Total Cost (€)",
                    format="localized",
                    help="Total cost for this category"
                )
            })
        else:
            categories_column_config.update({
                'Subtotal (€)': st.column_config.NumberColumn(
                    "Subtotal (€)",
                    format="localized",
                    help="Category subtotal"
                )
            })
        
        st.dataframe(filtered_df, use_container_width=True, column_config=categories_column_config)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Top categories by value
            top_categories = filtered_df.nlargest(10, DisplayFields.TOTAL_EUR)
            fig_bar = px.bar(
                top_categories,
                x=DisplayFields.TOTAL_EUR,
                y=DisplayFields.CATEGORY_ID,
                orientation='h',
                title='Top 10 Categories by Value',
                text=DisplayFields.TOTAL_EUR,
                color=DisplayFields.TOTAL_EUR,
                color_continuous_scale='Viridis'
            )
            fig_bar.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
            fig_bar.update_layout(height=500)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Categories costs vs revenues scatter chart
            fig_scatter = px.scatter(
                filtered_df,
                x='Cost (€)',
                y='Revenue (€)',
                size='Revenue (€)',
                hover_data=[DisplayFields.CATEGORY_ID, DisplayFields.GROUP_ID],
                title='Categories: Cost vs Revenue',
                color=DisplayFields.GROUP_ID
            )
            fig_scatter.update_layout(height=500)
            st.plotly_chart(fig_scatter, use_container_width=True)

    def display_items_analysis(self):
        """Display items analysis with detailed breakdown"""
        st.header("📄 Items Analysis")
        
        # Prepare items data
        items_data = []
        for group in self.product_groups:
            for category in group.categories:
                for item in category.items:
                    item_price = self._get_item_price(item)
                    item_unit_price = self._get_item_unit_price(item)
                    
                    # Calculate revenues and costs for all items
                    if self.detected_file_type == 'analisi_profittabilita':
                        item_cost = getattr(item, 'total_cost', 0) or 0
                        item_revenue = getattr(item, 'offer_price', 0) or 0
                        if item_revenue == 0:
                            item_revenue = item_price
                    else:
                        item_cost = getattr(item, 'total_cost', 0) or 0
                        item_revenue = item_price
                    
                    items_data.append({
                        DisplayFields.CATEGORY_ID: category.category_id or 'Unknown',
                        DisplayFields.CATEGORY_NAME: category.category_name or 'Unnamed',
                        DisplayFields.ITEM_CODE: item.code or 'Unknown',
                        DisplayFields.ITEM_DESCRIPTION: self._truncate_text(item.description or '', 60),
                        DisplayFields.QUANTITY: getattr(item, 'quantity', 0) or 0,
                        DisplayFields.UNIT_PRICE: item_unit_price,
                        'Revenue (€)': item_revenue,
                        'Total Cost (€)': item_cost,
                        'UTM Robot (€)': getattr(item, 'utm_robot', 0) or 0,
                        'UTM LGV (€)': getattr(item, 'utm_lgv', 0) or 0,
                        'UTM Intra (€)': getattr(item, 'utm_intra', 0) or 0,
                        'UTM Layout (€)': getattr(item, 'utm_layout', 0) or 0,
                        'PM Cost (€)': getattr(item, 'pm_cost', 0) or 0,
                        'Install (€)': getattr(item, 'install', 0) or 0,
                        'After Sales (€)': getattr(item, 'after_sales', 0) or 0,
                        'Unit Cost (€)': getattr(item, 'unit_cost', 0) or 0,
                        **self._get_item_specific_fields(item)
                    })
        
        df_items = pd.DataFrame(items_data)
        
        if df_items.empty:
            st.warning("No items data to display.")
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Items", len(df_items))
        with col2:
            items_with_value = df_items[df_items['Revenue (€)'] > 0]
            st.metric("Items with Revenue", len(items_with_value))
        with col3:
            total_value = df_items['Revenue (€)'].sum()
            st.metric("Total Revenue", f"€{total_value:,.2f}")
        with col4:
            avg_value = df_items[df_items['Revenue (€)'] > 0]['Revenue (€)'].mean()
            st.metric("Average Item Revenue", f"€{avg_value:,.2f}" if not pd.isna(avg_value) else "€0.00")
        
        # Filter controls
        st.subheader("🔍 Filter Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_categories = st.multiselect(
                "Filter by Categories",
                options=df_items[DisplayFields.CATEGORY_ID].unique(),
                default=df_items[DisplayFields.CATEGORY_ID].unique(),
                key="items_category_filter"
            )
        
        with col2:
            min_value = st.number_input(
                "Minimum Item Revenue (€)",
                min_value=0.0,
                value=0.0,
                step=100.0,
                help="Filter items by minimum revenue value",
                key="items_min_value"
            )
        
        with col3:
            top_n = st.number_input(
                "Show Top N Items",
                min_value=10,
                max_value=1000,
                value=50,
                step=10,
                key="items_top_n"
            )
        
        # Apply filters
        filtered_df = df_items[
            (df_items[DisplayFields.CATEGORY_ID].isin(selected_categories)) &
            (df_items['Revenue (€)'] >= min_value)
        ].nlargest(top_n, 'Revenue (€)')
        
        if filtered_df.empty:
            st.warning("No items match the selected filters.")
            return
        
        # Display filtered data
        st.subheader("📊 Top Items Table")
        
        # Configure column formats for items table
        items_column_config = {
            DisplayFields.QUANTITY: st.column_config.NumberColumn(
                "Quantity",
                format="localized",
                help="Quantity of this item"
            ),
            DisplayFields.UNIT_PRICE: st.column_config.NumberColumn(
                "Unit Price (€)",
                format="€%.2f",
                help="Unit price for this item"
            ),
            'Revenue (€)': st.column_config.NumberColumn(
                "Revenue (€)",
                format="€%.0f",
                help="Total revenue for this item"
            ),
            'Total Cost (€)': st.column_config.NumberColumn(
                "Total Cost (€)",
                format="€%.0f",
                help="Total cost for this item"
            ),
            'UTM Robot (€)': st.column_config.NumberColumn(
                "UTM Robot (€)",
                format="€%.0f",
                help="Robot engineering costs"
            ),
            'UTM LGV (€)': st.column_config.NumberColumn(
                "UTM LGV (€)",
                format="€%.0f",
                help="LGV engineering costs"
            ),
            'UTM Intra (€)': st.column_config.NumberColumn(
                "UTM Intra (€)",
                format="€%.0f",
                help="Intralogistics engineering costs"
            ),
            'UTM Layout (€)': st.column_config.NumberColumn(
                "UTM Layout (€)",
                format="€%.0f",
                help="Layout engineering costs"
            ),
            'PM Cost (€)': st.column_config.NumberColumn(
                "PM Cost (€)",
                format="€%.0f",
                help="Project management costs"
            ),
            'Install (€)': st.column_config.NumberColumn(
                "Install (€)",
                format="€%.0f",
                help="Installation costs"
            ),
            'After Sales (€)': st.column_config.NumberColumn(
                "After Sales (€)",
                format="€%.0f",
                help="After sales service costs"
            ),
            'Unit Cost (€)': st.column_config.NumberColumn(
                "Unit Cost (€)",
                format="€%.2f",
                help="Unit cost for this item"
            )
        }
        
        # Add specific fields configuration based on file type
        if self.detected_file_type == 'analisi_profittabilita':
            items_column_config.update({
                'Unit Cost (€)': st.column_config.NumberColumn(
                    "Unit Cost (€)",
                    format="localized",
                    help="Unit cost for this item"
                ),
                'Total Cost (€)': st.column_config.NumberColumn(
                    "Total Cost (€)",
                    format="localized",
                    help="Total cost for this item"
                ),
                'UTM Robot': st.column_config.NumberColumn(
                    "UTM Robot",
                    format="localized",
                    help="Robot engineering costs"
                ),
                'PM Cost': st.column_config.NumberColumn(
                    "PM Cost",
                    format="localized",
                    help="Project management costs"
                ),
                'Install': st.column_config.NumberColumn(
                    "Install",
                    format="localized",
                    help="Installation costs"
                ),
                'After Sales': st.column_config.NumberColumn(
                    "After Sales",
                    format="€%. 0f",
                    help="After sales service costs"
                )
            })
        else:
            items_column_config.update({
                'Cost (€)': st.column_config.NumberColumn(
                    "Cost (€)",
                    format="localized",
                    help="Cost for this item"
                )
            })
        
        st.dataframe(filtered_df, use_container_width=True, column_config=items_column_config)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Top items by revenue
            top_items = filtered_df.head(20)
            fig_bar = px.bar(
                top_items,
                x='Revenue (€)',
                y=DisplayFields.ITEM_CODE,
                orientation='h',
                title=f'Top 20 Items by Revenue',
                text='Revenue (€)',
                hover_data=[DisplayFields.ITEM_DESCRIPTION, DisplayFields.CATEGORY_ID],
                color=DisplayFields.CATEGORY_ID
            )
            fig_bar.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
            fig_bar.update_layout(height=600)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Revenue distribution by category
            category_totals = filtered_df.groupby(DisplayFields.CATEGORY_ID)['Revenue (€)'].sum().reset_index()
            fig_pie = px.pie(
                category_totals,
                values='Revenue (€)',
                names=DisplayFields.CATEGORY_ID,
                title='Revenue Distribution by Category (Filtered Items)'
            )
            fig_pie.update_layout(height=600)
            st.plotly_chart(fig_pie, use_container_width=True) 
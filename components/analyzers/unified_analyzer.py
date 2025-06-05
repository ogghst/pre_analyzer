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

# Import IndustrialQuotation model and ParserType enum
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from models.quotation_models import IndustrialQuotation, ParserType

# Import field constants
from ..field_constants import JsonFields, DisplayFields


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
            "WBE Analysis",
            "Field Analysis"
        ]
    
    def display_project_summary(self):
        """Display unified project summary information"""
        st.header("📋 Project Summary")
        
        # Show file type detection info
        file_type_display = "PRE Quotation" if self.detected_file_type == 'pre' else "Analisi Profittabilita"
        st.info(f"🔍 **Detected File Type:** {file_type_display}")
        
        # Create columns for metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Project ID", self.project.id or 'N/A')
            if self.detected_file_type == 'analisi_profittabilita':
                listino = getattr(self.project, 'listino', None)
                st.metric("Listino", listino or 'N/A')
            
        with col2:
            currency = self.project.parameters.currency if self.project.parameters else 'EUR'
            exchange_rate = self.project.parameters.exchange_rate if self.project.parameters else 1.0
            st.metric("Currency", currency)
            st.metric("Exchange Rate", f"{exchange_rate:.2f}")
            
        with col3:
            st.metric("Product Groups", len(self.product_groups))
            total_items = sum(len(category.items) for group in self.product_groups for category in group.categories)
            st.metric("Total Items", total_items)
            
        with col4:
            # Show appropriate margin based on file type
            if self.detected_file_type == 'analisi_profittabilita':
                total_offer = getattr(self.totals, 'total_offer', 0) or 0
                if total_offer > 0:
                    offer_margin_perc = getattr(self.totals, 'offer_margin_percentage', 0) or 0
                    st.metric("Offer Margin %", f"{offer_margin_perc:.2f}%")
                else:
                    margin_perc = getattr(self.totals, 'margin_percentage', 0) or 0
                    st.metric("Listino Margin %", f"{margin_perc:.2f}%")
            else:
                margin_perc = getattr(self.totals, 'margin_percentage', 0) or 0
                st.metric("Margin %", f"{margin_perc:.2f}%")
            
            items_with_data = self._count_items_with_data()
            st.metric("Items with Data", items_with_data)
        
        # Financial summary
        st.subheader("💰 Financial Summary")
        
        # Determine layout based on file type and available data
        if self.detected_file_type == 'analisi_profittabilita':
            total_offer = getattr(self.totals, 'total_offer', 0) or 0
            
            if total_offer > 0:
                # Show extended layout with offer data
                fin_col1, fin_col2, fin_col3, fin_col4, fin_col5 = st.columns(5)
                
                with fin_col1:
                    total_pricelist = getattr(self.totals, 'total_pricelist', 0) or 0
                    st.metric("Total Listino", f"€{total_pricelist:,.2f}")
                with fin_col2:
                    total_cost = getattr(self.totals, 'total_cost', 0) or 0
                    st.metric("Total Cost", f"€{total_cost:,.2f}")
                with fin_col3:
                    st.metric("Total Offer (VA21)", f"€{total_offer:,.2f}")
                with fin_col4:
                    offer_margin = getattr(self.totals, 'offer_margin', 0) or 0
                    st.metric("Offer Margin", f"€{offer_margin:,.2f}")
                with fin_col5:
                    offer_margin_perc = getattr(self.totals, 'offer_margin_percentage', 0) or 0
                    st.metric("Offer Margin %", f"{offer_margin_perc:.2f}%", delta=f"{offer_margin_perc - 20:.1f}%")
            else:
                # Show basic layout without offer data
                fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
                
                with fin_col1:
                    total_pricelist = getattr(self.totals, 'total_pricelist', 0) or 0
                    st.metric("Total Listino", f"€{total_pricelist:,.2f}")
                with fin_col2:
                    total_cost = getattr(self.totals, 'total_cost', 0) or 0
                    st.metric("Total Cost", f"€{total_cost:,.2f}")
                with fin_col3:
                    margin = total_pricelist - total_cost
                    st.metric("Listino Margin", f"€{margin:,.2f}")
                with fin_col4:
                    margin_perc = (margin / total_pricelist * 100) if total_pricelist > 0 else 0
                    st.metric("Listino Margin %", f"{margin_perc:.2f}%", delta=f"{margin_perc - 20:.1f}%")
        else:
            # PRE file layout
            fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
            
            with fin_col1:
                total_pricelist = getattr(self.totals, 'total_pricelist', 0) or 0
                st.metric("Total Amount", f"€{total_pricelist:,.2f}")
            with fin_col2:
                total_cost = getattr(self.totals, 'total_cost', 0) or 0
                st.metric("Total Cost", f"€{total_cost:,.2f}")
            with fin_col3:
                offer_margin = getattr(self.totals, 'offer_margin', 0) or 0
                st.metric("Margin", f"€{offer_margin:,.2f}")
            with fin_col4:
                offer_margin_perc = getattr(self.totals, 'offer_margin_percentage', 0) or 0
                st.metric("Margin %", f"{offer_margin_perc:.2f}%", delta=f"{offer_margin_perc - 20:.1f}%")
    
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
            # Margin gauge chart
            if self.detected_file_type == 'analisi_profittabilita':
                margin_perc = getattr(self.totals, 'offer_margin_percentage', 0) or 0
            else:
                margin_perc = getattr(self.totals, 'offer_margin_percentage', 0) or 0
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=margin_perc,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Margin Percentage"},
                delta={'reference': 25, 'position': "top"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 15], 'color': "lightgray"},
                        {'range': [15, 25], 'color': "yellow"},
                        {'range': [25, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig_gauge.update_layout(height=500)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Group-level profitability analysis
        st.subheader("📊 Profitability by Group")
        
        # Collect group-level data
        group_data = []
        for group in self.product_groups:
            group_total = self._get_group_total(group)
            
            # Calculate cost based on file type
            if self.detected_file_type == 'analisi_profittabilita':
                group_cost = sum(getattr(cat, 'cost_subtotal', 0) or 0 for cat in group.categories)
            else:
                group_cost = sum(getattr(item, 'total_cost', 0) or 0 for cat in group.categories for item in cat.items)
            
            group_margin = group_total - group_cost
            group_margin_perc = (group_margin / group_total * 100) if group_total > 0 else 0
            
            group_data.append({
                'Group': group.group_id or 'Unknown',
                'Total (€)': group_total,
                'Cost (€)': group_cost,
                'Margin (€)': group_margin,
                'Margin (%)': group_margin_perc
            })
        
        df_groups = pd.DataFrame(group_data)
        
        if not df_groups.empty:
            # Group profitability table
            st.subheader("📋 Group Profitability Table")
            st.dataframe(df_groups, use_container_width=True)
            
            # Group profitability chart
            fig_bar = go.Figure()
            
            fig_bar.add_trace(go.Bar(
                name='Total',
                x=df_groups['Group'],
                y=df_groups['Total (€)'],
                marker_color='#3498db'
            ))
            
            fig_bar.add_trace(go.Bar(
                name='Cost',
                x=df_groups['Group'],
                y=df_groups['Cost (€)'],
                marker_color='#e74c3c'
            ))
            
            fig_bar.update_layout(
                title='Total vs Cost by Group',
                xaxis_title='Group',
                yaxis_title='Amount (€)',
                barmode='group',
                height=500
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("No group data available for profitability analysis.")
    
    def display_utm_analysis(self):
        """Display UTM (time tracking) analysis - primarily for Analisi Profittabilita"""
        st.header("⏱️ UTM & Time Analysis")
        
        if self.detected_file_type != 'analisi_profittabilita':
            st.warning("UTM Analysis is primarily designed for Analisi Profittabilita files. Limited data may be available for PRE files.")
        
        # Collect UTM data from all items
        utm_data = []
        for group in self.product_groups:
            for category in group.categories:
                for item in category.items:
                    # UTM fields (mainly in Analisi Profittabilita)
                    utm_robot = self._safe_float(getattr(item, 'utm_robot', 0))
                    utm_robot_h = self._safe_float(getattr(item, 'utm_robot_h', 0))
                    utm_lgv = self._safe_float(getattr(item, 'utm_lgv', 0))
                    utm_lgv_h = self._safe_float(getattr(item, 'utm_lgv_h', 0))
                    utm_intra = self._safe_float(getattr(item, 'utm_intra', 0))
                    utm_intra_h = self._safe_float(getattr(item, 'utm_intra_h', 0))
                    utm_layout = self._safe_float(getattr(item, 'utm_layout', 0))
                    utm_layout_h = self._safe_float(getattr(item, 'utm_layout_h', 0))
                    
                    # PM and other time fields
                    pm_cost = self._safe_float(getattr(item, 'pm_cost', 0))
                    pm_h = self._safe_float(getattr(item, 'pm_h', 0))
                    
                    # Only include items with UTM data
                    total_utm_value = utm_robot + utm_lgv + utm_intra + utm_layout
                    total_utm_hours = utm_robot_h + utm_lgv_h + utm_intra_h + utm_layout_h + pm_h
                    
                    if total_utm_value > 0 or total_utm_hours > 0:
                        utm_data.append({
                            DisplayFields.GROUP_ID: group.group_id or 'Unknown',
                            DisplayFields.CATEGORY_ID: category.category_id or 'Unknown',
                            DisplayFields.ITEM_CODE: item.code or 'Unknown',
                            DisplayFields.ITEM_DESCRIPTION: self._truncate_text(item.description or '', 40),
                            'UTM Robot': utm_robot,
                            'UTM Robot Hours': utm_robot_h,
                            'UTM LGV': utm_lgv,
                            'UTM LGV Hours': utm_lgv_h,
                            'UTM Intra': utm_intra,
                            'UTM Intra Hours': utm_intra_h,
                            'UTM Layout': utm_layout,
                            'UTM Layout Hours': utm_layout_h,
                            'PM Cost': pm_cost,
                            'PM Hours': pm_h,
                            'Total UTM Value': total_utm_value,
                            'Total Hours': total_utm_hours
                        })
        
        if utm_data:
            df_utm = pd.DataFrame(utm_data)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Items with UTM", len(df_utm))
            with col2:
                st.metric("Total UTM Value", f"€{df_utm['Total UTM Value'].sum():,.2f}")
            with col3:
                st.metric("Total Hours", f"{df_utm['Total Hours'].sum():,.1f}")
            with col4:
                avg_hourly = df_utm['Total UTM Value'].sum() / df_utm['Total Hours'].sum() if df_utm['Total Hours'].sum() > 0 else 0
                st.metric("Avg €/Hour", f"€{avg_hourly:.2f}")
            
            # UTM breakdown charts
            col1, col2 = st.columns(2)
            
            with col1:
                # UTM values by type
                utm_summary = {
                    'UTM Type': ['Robot', 'LGV', 'Intra', 'Layout', 'PM'],
                    'Total Value (€)': [
                        df_utm['UTM Robot'].sum(),
                        df_utm['UTM LGV'].sum(),
                        df_utm['UTM Intra'].sum(),
                        df_utm['UTM Layout'].sum(),
                        df_utm['PM Cost'].sum()
                    ]
                }
                df_utm_summary = pd.DataFrame(utm_summary)
                df_utm_summary = df_utm_summary[df_utm_summary['Total Value (€)'] > 0]
                
                if not df_utm_summary.empty:
                    fig_utm_pie = px.pie(
                        df_utm_summary,
                        values='Total Value (€)',
                        names='UTM Type',
                        title='UTM Value Distribution by Type'
                    )
                    fig_utm_pie.update_layout(height=400)
                    st.plotly_chart(fig_utm_pie, use_container_width=True)
            
            with col2:
                # Hours by type
                hours_summary = {
                    'UTM Type': ['Robot', 'LGV', 'Intra', 'Layout', 'PM'],
                    'Total Hours': [
                        df_utm['UTM Robot Hours'].sum(),
                        df_utm['UTM LGV Hours'].sum(),
                        df_utm['UTM Intra Hours'].sum(),
                        df_utm['UTM Layout Hours'].sum(),
                        df_utm['PM Hours'].sum()
                    ]
                }
                df_hours_summary = pd.DataFrame(hours_summary)
                df_hours_summary = df_hours_summary[df_hours_summary['Total Hours'] > 0]
                
                if not df_hours_summary.empty:
                    fig_hours_bar = px.bar(
                        df_hours_summary,
                        x='UTM Type',
                        y='Total Hours',
                        title='Total Hours by UTM Type',
                        color='Total Hours',
                        color_continuous_scale='Blues'
                    )
                    fig_hours_bar.update_layout(height=400)
                    st.plotly_chart(fig_hours_bar, use_container_width=True)
            
            # Detailed UTM table
            st.subheader("📊 UTM Detailed Analysis")
            
            # Filter for items with significant UTM values
            significant_utm = df_utm[df_utm['Total UTM Value'] > 100].nlargest(20, 'Total UTM Value')
            
            if not significant_utm.empty:
                display_cols = [DisplayFields.GROUP_ID, DisplayFields.ITEM_CODE, DisplayFields.ITEM_DESCRIPTION, 
                              'Total UTM Value', 'Total Hours', 'UTM Robot', 'UTM LGV', 'PM Cost']
                st.dataframe(significant_utm[display_cols], use_container_width=True)
            else:
                st.info("No significant UTM values found in the data.")
        else:
            st.info("No UTM data found in the current dataset.")
    
    def display_wbe_analysis(self):
        """Display WBE (Work Breakdown Element) analysis - primarily for Analisi Profittabilita"""
        st.header("🏗️ WBE Analysis")
        
        if self.detected_file_type != 'analisi_profittabilita':
            st.warning("WBE Analysis is primarily designed for Analisi Profittabilita files. Limited data may be available for PRE files.")
        
        # Collect WBE data from all categories
        wbe_data = {}
        wbe_categories = {}
        
        for group in self.product_groups:
            for category in group.categories:
                wbe = getattr(category, 'wbe', '') or ''
                wbe = wbe.strip()
                if wbe and wbe != '':
                    if wbe not in wbe_data:
                        wbe_data[wbe] = {
                            'categories': [],
                            'total_listino': 0,
                            'total_costo': 0,
                            'total_offer': 0,
                            'items': []
                        }
                        wbe_categories[wbe] = []
                    
                    # Add category to WBE
                    wbe_categories[wbe].append({
                        'group_id': group.group_id or 'Unknown',
                        'group_name': group.group_name or 'Unnamed',
                        'category_id': category.category_id or 'Unknown',
                        'category_name': category.category_name or 'Unnamed',
                        'category': category
                    })
                    
                    # Aggregate financials
                    if self.detected_file_type == 'analisi_profittabilita':
                        cat_listino = self._safe_float(getattr(category, 'pricelist_subtotal', 0))
                        cat_costo = self._safe_float(getattr(category, 'cost_subtotal', 0))
                        cat_offer = self._safe_float(getattr(category, 'offer_price', 0))
                    else:
                        # PRE file
                        cat_listino = self._get_category_total(category)
                        cat_costo = sum(self._safe_float(getattr(item, 'total_cost', 0)) for item in category.items)
                        cat_offer = 0
                    
                    wbe_data[wbe]['total_listino'] += cat_listino
                    wbe_data[wbe]['total_costo'] += cat_costo
                    wbe_data[wbe]['total_offer'] += cat_offer
                    
                    # Collect items for detailed analysis
                    for item in category.items:
                        item_dict = {
                            'group_id': group.group_id or 'Unknown',
                            'category_id': category.category_id or 'Unknown',
                            'code': item.code,
                            'description': item.description,
                            'quantity': getattr(item, 'quantity', 0),
                            'unit_cost': getattr(item, 'unit_cost', 0),
                            'total_cost': getattr(item, 'total_cost', 0)
                        }
                        wbe_data[wbe]['items'].append(item_dict)
        
        if not wbe_data:
            st.warning("No WBE data found in the current dataset.")
            return
        
        # WBE selection
        st.subheader("🎯 Select WBE for Analysis")
        
        # Create WBE summary for selection
        wbe_summary = []
        for wbe, data in wbe_data.items():
            margin = data['total_listino'] - data['total_costo']
            margin_perc = (margin / data['total_listino'] * 100) if data['total_listino'] > 0 else 0
            
            wbe_summary.append({
                DisplayFields.WBE: wbe,
                DisplayFields.CATEGORIES: len(wbe_categories[wbe]),
                DisplayFields.ITEMS: len(data['items']),
                DisplayFields.LISTINO_EUR: data['total_listino'],
                DisplayFields.COSTO_EUR: data['total_costo'],
                DisplayFields.MARGIN_EUR: margin,
                DisplayFields.MARGIN_PERCENT: margin_perc
            })
        
        df_wbe_summary = pd.DataFrame(wbe_summary)
        
        # Display WBE summary table
        st.dataframe(df_wbe_summary, use_container_width=True)
        
        # WBE selection dropdown
        selected_wbe = st.selectbox(
            "Select WBE for Detailed Analysis",
            options=list(wbe_data.keys()),
            format_func=lambda x: f"{x} (€{wbe_data[x]['total_listino']:,.0f})",
            key="unified_wbe_selector"
        )
        
        if selected_wbe:
            self._display_detailed_wbe_analysis(selected_wbe, wbe_data[selected_wbe], wbe_categories[selected_wbe])
    
    def _display_detailed_wbe_analysis(self, wbe_name: str, wbe_data: Dict[str, Any], wbe_categories: List[Dict[str, Any]]):
        """Display detailed analysis for selected WBE"""
        st.markdown("---")
        st.subheader(f"📊 Detailed Analysis: {wbe_name}")
        
        # Financial overview
        total_listino = wbe_data['total_listino']
        total_costo = wbe_data['total_costo']
        total_offer = wbe_data.get('total_offer', 0)
        margin = total_listino - total_costo
        margin_perc = (margin / total_listino * 100) if total_listino > 0 else 0
        
        # Key metrics
        if total_offer > 0 and self.detected_file_type == 'analisi_profittabilita':
            offer_margin = total_offer - total_costo
            offer_margin_perc = (1 - (total_costo / total_offer)) * 100 if total_offer > 0 else 0
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Total Listino", f"€{total_listino:,.2f}")
            with col2:
                st.metric("Total Cost", f"€{total_costo:,.2f}")
            with col3:
                st.metric("Total Offer (VA21)", f"€{total_offer:,.2f}")
            with col4:
                st.metric("Offer Margin", f"€{offer_margin:,.2f}")
            with col5:
                st.metric("Offer Margin %", f"{offer_margin_perc:.2f}%", delta=f"{offer_margin_perc - 20:.1f}%")
        else:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Listino", f"€{total_listino:,.2f}")
            with col2:
                st.metric("Total Cost", f"€{total_costo:,.2f}")
            with col3:
                st.metric("Margin", f"€{margin:,.2f}")
            with col4:
                st.metric("Margin %", f"{margin_perc:.2f}%", delta=f"{margin_perc - 20:.1f}%")
        
        # Categories within WBE
        st.subheader("📂 Categories in this WBE")
        
        cat_data = []
        for cat_info in wbe_categories:
            category = cat_info['category']
            
            if self.detected_file_type == 'analisi_profittabilita':
                cat_listino = self._safe_float(getattr(category, 'pricelist_subtotal', 0))
                cat_costo = self._safe_float(getattr(category, 'cost_subtotal', 0))
                cat_offer = self._safe_float(getattr(category, 'offer_price', 0))
            else:
                cat_listino = self._get_category_total(category)
                cat_costo = sum(self._safe_float(getattr(item, 'total_cost', 0)) for item in category.items)
                cat_offer = 0
            
            cat_margin = cat_listino - cat_costo
            cat_margin_perc = (cat_margin / cat_listino * 100) if cat_listino > 0 else 0
            
            cat_data.append({
                'Group': cat_info['group_id'],
                'Category': cat_info['category_id'],
                'Name': self._truncate_text(cat_info['category_name'], 30),
                'Items': len(category.items),
                'Listino (€)': cat_listino,
                'Cost (€)': cat_costo,
                'Offer (€)': cat_offer,
                'Margin (€)': cat_margin,
                'Margin %': cat_margin_perc
            })
        
        df_categories = pd.DataFrame(cat_data)
        
        if not df_categories.empty:
            st.dataframe(df_categories, use_container_width=True)
    
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
            st.dataframe(df_top_fields, use_container_width=True)
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
    
    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float"""
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _truncate_text(self, text: str, max_length: int = 50) -> str:
        """Truncate text to maximum length"""
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

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
            
            groups_data.append({
                DisplayFields.GROUP_ID: group.group_id or 'Unknown',
                DisplayFields.GROUP_NAME: group.group_name or 'Unnamed',
                DisplayFields.CATEGORIES_COUNT: len(group.categories),
                DisplayFields.TOTAL_ITEMS: total_items,
                DisplayFields.TOTAL_EUR: group_total,
                DisplayFields.QUANTITY: getattr(group, 'quantity', 1) or 1
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
            # Bar chart of total values by group
            fig_bar = px.bar(
                df_groups, 
                x=DisplayFields.GROUP_ID, 
                y=DisplayFields.TOTAL_EUR,
                title='Total Value by Product Group',
                text=DisplayFields.TOTAL_EUR,
                color=DisplayFields.TOTAL_EUR,
                color_continuous_scale='Blues'
            )
            fig_bar.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
            fig_bar.update_layout(height=500)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Pie chart of total value distribution
            fig_pie = px.pie(
                df_groups, 
                values=DisplayFields.TOTAL_EUR, 
                names=DisplayFields.GROUP_ID,
                title='Total Value Distribution by Group'
            )
            fig_pie.update_layout(height=500)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Treemap visualization
        st.subheader("🗺️ Groups Treemap")
        fig_treemap = px.treemap(
            df_groups,
            path=[DisplayFields.GROUP_ID],
            values=DisplayFields.TOTAL_EUR,
            title='Product Groups by Total Value',
            color=DisplayFields.TOTAL_EUR,
            color_continuous_scale='RdYlBu'
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
                categories_data.append({
                    DisplayFields.GROUP_ID: group.group_id or 'Unknown',
                    DisplayFields.GROUP_NAME: group.group_name or 'Unnamed',
                    DisplayFields.CATEGORY_ID: category.category_id or 'Unknown',
                    DisplayFields.CATEGORY_NAME: category.category_name or 'Unnamed',
                    DisplayFields.ITEMS_COUNT: len(category.items),
                    DisplayFields.TOTAL_EUR: cat_total,
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
        st.dataframe(filtered_df, use_container_width=True)
        
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
            # Categories by items count
            fig_scatter = px.scatter(
                filtered_df,
                x=DisplayFields.ITEMS_COUNT,
                y=DisplayFields.TOTAL_EUR,
                size=DisplayFields.TOTAL_EUR,
                hover_data=[DisplayFields.CATEGORY_ID, DisplayFields.GROUP_ID],
                title='Categories: Items Count vs Total Value',
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
                    
                    items_data.append({
                        DisplayFields.GROUP_ID: group.group_id or 'Unknown',
                        DisplayFields.GROUP_NAME: group.group_name or 'Unnamed',
                        DisplayFields.CATEGORY_ID: category.category_id or 'Unknown',
                        DisplayFields.CATEGORY_NAME: category.category_name or 'Unnamed',
                        DisplayFields.ITEM_CODE: item.code or 'Unknown',
                        DisplayFields.ITEM_DESCRIPTION: self._truncate_text(item.description or '', 60),
                        DisplayFields.QUANTITY: getattr(item, 'quantity', 0) or 0,
                        DisplayFields.UNIT_PRICE_EUR: item_unit_price,
                        DisplayFields.TOTAL_EUR: item_price,
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
            items_with_value = df_items[df_items[DisplayFields.TOTAL_EUR] > 0]
            st.metric("Items with Value", len(items_with_value))
        with col3:
            total_value = df_items[DisplayFields.TOTAL_EUR].sum()
            st.metric("Total Value", f"€{total_value:,.2f}")
        with col4:
            avg_value = df_items[df_items[DisplayFields.TOTAL_EUR] > 0][DisplayFields.TOTAL_EUR].mean()
            st.metric("Average Item Value", f"€{avg_value:,.2f}" if not pd.isna(avg_value) else "€0.00")
        
        # Filter controls
        st.subheader("🔍 Filter Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_groups = st.multiselect(
                "Filter by Groups",
                options=df_items[DisplayFields.GROUP_ID].unique(),
                default=df_items[DisplayFields.GROUP_ID].unique(),
                key="items_group_filter"
            )
        
        with col2:
            min_value = st.number_input(
                "Minimum Item Value (€)",
                min_value=0.0,
                value=0.0,
                step=100.0,
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
            (df_items[DisplayFields.GROUP_ID].isin(selected_groups)) &
            (df_items[DisplayFields.TOTAL_EUR] >= min_value)
        ].nlargest(top_n, DisplayFields.TOTAL_EUR)
        
        if filtered_df.empty:
            st.warning("No items match the selected filters.")
            return
        
        # Display filtered data
        st.subheader("📊 Top Items Table")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Top items by value
            top_items = filtered_df.head(20)
            fig_bar = px.bar(
                top_items,
                x=DisplayFields.TOTAL_EUR,
                y=DisplayFields.ITEM_CODE,
                orientation='h',
                title=f'Top 20 Items by Value',
                text=DisplayFields.TOTAL_EUR,
                hover_data=[DisplayFields.ITEM_DESCRIPTION, DisplayFields.GROUP_ID],
                color=DisplayFields.GROUP_ID
            )
            fig_bar.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
            fig_bar.update_layout(height=600)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Value distribution by group
            group_totals = filtered_df.groupby(DisplayFields.GROUP_ID)[DisplayFields.TOTAL_EUR].sum().reset_index()
            fig_pie = px.pie(
                group_totals,
                values=DisplayFields.TOTAL_EUR,
                names=DisplayFields.GROUP_ID,
                title='Value Distribution by Group (Filtered Items)'
            )
            fig_pie.update_layout(height=600)
            st.plotly_chart(fig_pie, use_container_width=True) 
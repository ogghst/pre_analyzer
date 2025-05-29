"""
Analisi Profittabilita Analyzer
Specific analyzer for analisi profittabilita files with comprehensive field analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any
from .base_analyzer import BaseAnalyzer

# Import field constants
from ..field_constants import JsonFields, DisplayFields


class ProfittabilitaAnalyzer(BaseAnalyzer):
    """Analyzer specifically for Analisi Profittabilita files"""
    
    def get_analysis_views(self) -> List[str]:
        """Return list of available analysis views for Analisi Profittabilita files"""
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
        """Display Analisi Profittabilita-specific project summary information"""
        st.header("📋 Analisi Profittabilita Summary")
        
        # Create columns for metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Project ID", self.project.get(JsonFields.ID, 'N/A'))
            st.metric("Listino", self.project.get(JsonFields.LISTINO, 'N/A'))
            
        with col2:
            currency = self.project.get(JsonFields.PARAMETERS, {}).get(JsonFields.CURRENCY, 'EUR')
            exchange_rate = self.project.get(JsonFields.PARAMETERS, {}).get(JsonFields.EXCHANGE_RATE, 1.0)
            st.metric("Currency", currency)
            st.metric("Exchange Rate", f"{exchange_rate:.2f}")
            
        with col3:
            st.metric("Product Groups", len(self.product_groups))
            total_items = sum(len(cat.get(JsonFields.ITEMS, [])) for group in self.product_groups for cat in group.get(JsonFields.CATEGORIES, []))
            st.metric("Total Items", total_items)
            
        with col4:
            # Show offer margin percentage if available, otherwise listino margin
            total_offer = self.totals.get(JsonFields.TOTAL_OFFER, 0)
            if total_offer > 0:
                offer_margin_perc = self.totals.get(JsonFields.OFFER_MARGIN_PERCENTAGE, 0)
                st.metric("Offer Margin %", f"{offer_margin_perc:.2f}%")
            else:
                margin_perc = self.totals.get(JsonFields.MARGIN_PERCENTAGE, 0)
                st.metric("Listino Margin %", f"{margin_perc:.2f}%")
            # Count items with data
            items_with_data = self._count_items_with_data()
            st.metric("Items with Data", items_with_data)
        
        # Financial summary - enhanced with VA21 offer prices
        st.subheader("💰 Profitability Summary")
        
        # Determine layout based on whether we have offer data
        total_offer = self.totals.get(JsonFields.TOTAL_OFFER, 0)
        
        if total_offer > 0:
            # Show extended layout with offer data
            fin_col1, fin_col2, fin_col3, fin_col4, fin_col5 = st.columns(5)
            
            with fin_col1:
                st.metric("Total Listino", f"€{self.totals.get(JsonFields.TOTAL_LISTINO, 0):,.2f}")
            with fin_col2:
                st.metric("Total Cost", f"€{self.totals.get(JsonFields.TOTAL_COSTO, 0):,.2f}")
            with fin_col3:
                st.metric("Total Offer (VA21)", f"€{total_offer:,.2f}")
            with fin_col4:
                offer_margin = self.totals.get(JsonFields.OFFER_MARGIN, 0)
                st.metric("Offer Margin", f"€{offer_margin:,.2f}")
            with fin_col5:
                offer_margin_perc = self.totals.get(JsonFields.OFFER_MARGIN_PERCENTAGE, 0)
                delta_color = "normal" if offer_margin_perc > 20 else "inverse"
                st.metric("Offer Margin %", f"{offer_margin_perc:.2f}%", delta=f"{offer_margin_perc - 20:.1f}%")
        else:
            # Show basic layout without offer data
            fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
        
        with fin_col1:
            st.metric("Total Listino", f"€{self.totals.get(JsonFields.TOTAL_LISTINO, 0):,.2f}")
        with fin_col2:
                st.metric("Total Cost", f"€{self.totals.get(JsonFields.TOTAL_COSTO, 0):,.2f}")
        with fin_col3:
            margin = self.totals.get(JsonFields.MARGIN, 0)
            st.metric("Listino Margin", f"€{margin:,.2f}")
        with fin_col4:
            margin_perc = self.totals.get(JsonFields.MARGIN_PERCENTAGE, 0)
            delta_color = "normal" if margin_perc > 20 else "inverse"
            st.metric("Listino Margin %", f"{margin_perc:.2f}%", delta=f"{margin_perc - 20:.1f}%")
    
    def display_profitability_analysis(self):
        """Display comprehensive profitability analysis"""
        st.header("💹 Profitability Analysis")
        
        # Overall profitability metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # Profitability pie chart - use offer-based margin when available
            total_offer = self.totals.get(JsonFields.TOTAL_OFFER, 0)
            total_costo = self.totals.get(JsonFields.TOTAL_COSTO, 0)
            
            if total_offer > 0:
                # Use offer-based margin
                offer_margin = total_offer - total_costo
                profit_data = {
                    DisplayFields.CATEGORY_NAME: ['Total Costo', 'Offer Margin'],
                    'Amount (€)': [total_costo, offer_margin],
                    'Color': ['#ff6b6b', '#51cf66']
                }
                title = 'Cost vs Offer Margin Distribution'
                color_map = {'Total Costo': '#ff6b6b', 'Offer Margin': '#51cf66'}
            else:
                # Fall back to listino-based margin
                listino_margin = self.totals.get(JsonFields.MARGIN, 0)
                profit_data = {
                    DisplayFields.CATEGORY_NAME: ['Total Costo', 'Listino Margin'],
                    'Amount (€)': [total_costo, listino_margin],
                    'Color': ['#ff6b6b', '#51cf66']
                }
                title = 'Cost vs Listino Margin Distribution'
                color_map = {'Total Costo': '#ff6b6b', 'Listino Margin': '#51cf66'}
            
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
            margin_perc = self.totals.get(JsonFields.MARGIN_PERCENTAGE, 0)
            
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
        
        # WBE-level profitability analysis
        st.subheader("📊 Profitability by WBE")
        
        # Collect WBE-level data
        wbe_data = []
        for group in self.product_groups:
            for category in group.get(JsonFields.CATEGORIES, []):
                wbe_code = category.get(JsonFields.WBE, 'Unknown')
                listino_price = category.get(JsonFields.PRICELIST_SUBTOTAL, 0)
                offer_price = category.get(JsonFields.OFFER_PRICE, 0)
                cost = category.get(JsonFields.COST_SUBTOTAL, 0)
                
                # Calculate margin - only use offer price, no fallback to listino
                if offer_price > 0:
                    # Use offer price for margin calculation
                    margin_amount = offer_price - cost
                    margin_percentage = (1 - (cost / offer_price)) * 100 if offer_price > 0 else 0
                else:
                    # No offer price available - set margin to None/0
                    margin_amount = 0
                    margin_percentage = 0
                
                wbe_data.append({
                    'WBE': wbe_code,
                    'Listino (€)': listino_price,
                    'Offer (€)': offer_price if offer_price > 0 else None,
                    'Cost (€)': cost,
                    'Margin (€)': margin_amount if offer_price > 0 else None,
                    'Margin (%)': margin_percentage if offer_price > 0 else None
                })
        
        df_wbe = pd.DataFrame(wbe_data)
        
        if not df_wbe.empty:
            # Sort by margin amount descending for better visualization
            df_wbe_sorted = df_wbe.sort_values('Margin (€)', ascending=False)
            
            # 1. WBE Profitability Table
            st.subheader("📋 WBE Profitability Table")
            
            # Format the dataframe for display
            df_display = df_wbe_sorted.copy()
            for col in ['Listino (€)', 'Offer (€)', 'Cost (€)', 'Margin (€)']:
                if col in df_display.columns:
                    df_display[col] = df_display[col].apply(lambda x: f"€{x:,.2f}" if pd.notna(x) and x != 0 else "-")
            df_display['Margin (%)'] = df_display['Margin (%)'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "-")
            
            st.dataframe(df_display, use_container_width=True)
            
            # 2. Bar Chart: Offer Price vs Cost by WBE
            st.subheader("📊 Offer Price vs Cost by WBE")
            
            # Filter out WBEs without offer prices for this chart
            df_with_offers = df_wbe_sorted[df_wbe_sorted['Offer (€)'].notna() & (df_wbe_sorted['Offer (€)'] > 0)].copy()
            
            if not df_with_offers.empty:
                fig_bar = go.Figure()
                
                fig_bar.add_trace(go.Bar(
                    name='Offer Price',
                    x=df_with_offers['WBE'],
                    y=df_with_offers['Offer (€)'],
                    marker_color='#3498db',
                    text=df_with_offers['Offer (€)'].apply(lambda x: f"€{x:,.0f}"),
                    textposition='outside'
                ))
                
                fig_bar.add_trace(go.Bar(
                    name='Cost',
                    x=df_with_offers['WBE'],
                    y=df_with_offers['Cost (€)'],
                    marker_color='#e74c3c',
                    text=df_with_offers['Cost (€)'].apply(lambda x: f"€{x:,.0f}"),
                    textposition='outside'
                ))
                
                fig_bar.update_layout(
                    title='Offer Price vs Cost by WBE',
                    xaxis_title='WBE Code',
                    yaxis_title='Amount (€)',
                    barmode='group',
                    height=600,
                    xaxis={'tickangle': 45}
                )
                
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No WBEs with offer prices available for comparison chart.")
            
            # 3. Pie Chart: Margin Distribution by WBE
            st.subheader("🥧 Margin Distribution by WBE")
            
            # Filter WBEs with positive margins AND offer prices, sort by WBE name
            df_positive_margin = df_wbe[
                (df_wbe['Margin (€)'].notna()) & 
                (df_wbe['Margin (€)'] > 0) &
                (df_wbe['Offer (€)'].notna())
            ].copy().sort_values('WBE')
            
            if not df_positive_margin.empty:
                fig_margin_pie = px.pie(
                    df_positive_margin,
                    values='Margin (€)',
                    names='WBE',
                    title='Margin Distribution by WBE (Sorted by WBE Name - Offer-based only)',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_margin_pie.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Margin: €%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
                )
                fig_margin_pie.update_layout(height=600)
                st.plotly_chart(fig_margin_pie, use_container_width=True)
            else:
                st.warning("No WBEs with positive offer-based margins found.")
            
            # 4. Pie Chart: Cost Distribution by WBE
            st.subheader("🥧 Cost Distribution by WBE")
            
            # Filter WBEs with costs and sort by WBE name instead of cost
            df_with_costs = df_wbe[df_wbe['Cost (€)'] > 0].copy().sort_values('WBE')
            
            if not df_with_costs.empty:
                fig_cost_pie = px.pie(
                    df_with_costs,
                    values='Cost (€)',
                    names='WBE',
                    title='Cost Distribution by WBE (Sorted by WBE Name)',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_cost_pie.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Cost: €%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
                )
                fig_cost_pie.update_layout(height=600)
                st.plotly_chart(fig_cost_pie, use_container_width=True)
            else:
                st.warning("No WBEs with costs found.")
        else:
            st.warning("No WBE data available for profitability analysis.")
    
    def display_utm_analysis(self):
        """Display UTM (time tracking) analysis"""
        st.header("⏱️ UTM & Time Analysis")
        
        # Collect UTM data from all items
        utm_data = []
        for group in self.product_groups:
            for category in group.get(JsonFields.CATEGORIES, []):
                for item in category.get(JsonFields.ITEMS, []):
                    # UTM fields
                    utm_robot = self._safe_float(item.get(JsonFields.UTM_ROBOT, 0))
                    utm_robot_h = self._safe_float(item.get(JsonFields.UTM_ROBOT_H, 0))
                    utm_lgv = self._safe_float(item.get(JsonFields.UTM_LGV, 0))
                    utm_lgv_h = self._safe_float(item.get(JsonFields.UTM_LGV_H, 0))
                    utm_intra = self._safe_float(item.get(JsonFields.UTM_INTRA, 0))
                    utm_intra_h = self._safe_float(item.get(JsonFields.UTM_INTRA_H, 0))
                    utm_layout = self._safe_float(item.get(JsonFields.UTM_LAYOUT, 0))
                    utm_layout_h = self._safe_float(item.get(JsonFields.UTM_LAYOUT_H, 0))
                    
                    # PM and other time fields
                    pm_cost = self._safe_float(item.get(JsonFields.PM_COST, 0))
                    pm_h = self._safe_float(item.get(JsonFields.PM_H, 0))
                    
                    # Only include items with UTM data
                    total_utm_value = utm_robot + utm_lgv + utm_intra + utm_layout
                    total_utm_hours = utm_robot_h + utm_lgv_h + utm_intra_h + utm_layout_h + pm_h
                    
                    if total_utm_value > 0 or total_utm_hours > 0:
                        utm_data.append({
                            DisplayFields.GROUP_ID: group.get(JsonFields.GROUP_ID, 'Unknown'),
                            DisplayFields.CATEGORY_ID: category.get(JsonFields.CATEGORY_ID, 'Unknown'),
                            DisplayFields.ITEM_CODE: item.get(JsonFields.CODE, 'Unknown'),
                            DisplayFields.ITEM_DESCRIPTION: self._truncate_text(item.get(JsonFields.DESCRIPTION, ''), 40),
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
        """Display WBE (Work Breakdown Element) analysis with cost composition"""
        st.header("🏗️ WBE Analysis")
        
        # Collect WBE data from all categories
        wbe_data = {}
        wbe_categories = {}
        
        for group in self.product_groups:
            for category in group.get(JsonFields.CATEGORIES, []):
                wbe = category.get(JsonFields.WBE, '').strip()
                if wbe and wbe != '':
                    if wbe not in wbe_data:
                        wbe_data[wbe] = {
                            JsonFields.CATEGORIES: [],
                            'total_listino': 0,
                            'total_costo': 0,
                            'total_offer': 0,
                            JsonFields.ITEMS: []
                        }
                        wbe_categories[wbe] = []
                    
                    # Add category to WBE
                    wbe_categories[wbe].append({
                        JsonFields.GROUP_ID: group.get(JsonFields.GROUP_ID, 'Unknown'),
                        JsonFields.GROUP_NAME: group.get(JsonFields.GROUP_NAME, 'Unnamed'),
                        JsonFields.CATEGORY_ID: category.get(JsonFields.CATEGORY_ID, 'Unknown'),
                        JsonFields.CATEGORY_NAME: category.get(JsonFields.CATEGORY_NAME, 'Unnamed'),
                        'category': category
                    })
                    
                    # Aggregate financials including offer prices
                    cat_listino = self._safe_float(category.get(JsonFields.PRICELIST_SUBTOTAL, 0))
                    cat_costo = self._safe_float(category.get(JsonFields.COST_SUBTOTAL, 0))
                    cat_offer = self._safe_float(category.get(JsonFields.OFFER_PRICE, 0))
                    
                    wbe_data[wbe]['total_listino'] += cat_listino
                    wbe_data[wbe]['total_costo'] += cat_costo
                    wbe_data[wbe]['total_offer'] += cat_offer
                    
                    # Collect items for detailed analysis
                    for item in category.get(JsonFields.ITEMS, []):
                        item_data = item.copy()
                        item_data[JsonFields.GROUP_ID] = group.get(JsonFields.GROUP_ID, 'Unknown')
                        item_data[JsonFields.CATEGORY_ID] = category.get(JsonFields.CATEGORY_ID, 'Unknown')
                        wbe_data[wbe][JsonFields.ITEMS].append(item_data)
        
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
                DisplayFields.ITEMS: len(data[JsonFields.ITEMS]),
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
            key="wbe_selector"
        )
        
        if selected_wbe:
            self._display_detailed_wbe_analysis(selected_wbe, wbe_data[selected_wbe], wbe_categories[selected_wbe])
    
    def _display_detailed_wbe_analysis(self, wbe_name: str, wbe_data: Dict[str, Any], wbe_categories: List[Dict[str, Any]]):
        """Display detailed analysis for selected WBE"""
        st.markdown("---")
        st.subheader(f"📊 Detailed Analysis: {wbe_name}")
        
        # Financial overview - include offer price if available
        total_listino = wbe_data['total_listino']
        total_costo = wbe_data['total_costo']
        total_offer = wbe_data.get('total_offer', 0)
        margin = total_listino - total_costo
        margin_perc = (margin / total_listino * 100) if total_listino > 0 else 0
        
        # Calculate offer-based margin if offer price is available
        if total_offer > 0:
            offer_margin = total_offer - total_costo
            offer_margin_perc = (1 - (total_costo / total_offer)) * 100 if total_offer > 0 else 0
        else:
            offer_margin = 0
            offer_margin_perc = 0
        
        # Key metrics - show offer data if available
        if total_offer > 0:
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
                delta_color = "normal" if offer_margin_perc > 20 else "inverse"
                st.metric("Offer Margin %", f"{offer_margin_perc:.2f}%", delta=f"{offer_margin_perc - 20:.1f}%")
        else:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Listino", f"€{total_listino:,.2f}")
            with col2:
                    st.metric("Total Cost", f"€{total_costo:,.2f}")
            with col3:
                    st.metric("Listino Margin", f"€{margin:,.2f}")
            with col4:
                delta_color = "normal" if margin_perc > 20 else "inverse"
                st.metric("Listino Margin %", f"{margin_perc:.2f}%", delta=f"{margin_perc - 20:.1f}%")
        
        # Cost composition analysis
        st.subheader("💰 Cost Composition Analysis")
        
        # Analyze cost components from items
        cost_components = {
            'Material': 0,
            'UTM (Robot)': 0,
            'UTM (LGV)': 0,
            'UTM (Intra)': 0,
            'UTM (Layout)': 0,
            'Engineering (UTE)': 0,
            'Engineering (BA)': 0,
            'Software (PC)': 0,
            'Software (PLC)': 0,
            'Software (LGV)': 0,
            'Manufacturing (Mec)': 0,
            'Manufacturing (Ele)': 0,
            'Testing (Collaudo)': 0,
            'Project Management': 0,
            'Installation': 0,
            'Documentation': 0,
            'After Sales': 0,
            'Other': 0
        }
        
        for item in wbe_data[JsonFields.ITEMS]:
            # Material costs
            cost_components['Material'] += self._safe_float(item.get(JsonFields.MAT, 0))
            
            # UTM costs
            cost_components['UTM (Robot)'] += self._safe_float(item.get(JsonFields.UTM_ROBOT, 0))
            cost_components['UTM (LGV)'] += self._safe_float(item.get(JsonFields.UTM_LGV, 0))
            cost_components['UTM (Intra)'] += self._safe_float(item.get(JsonFields.UTM_INTRA, 0))
            cost_components['UTM (Layout)'] += self._safe_float(item.get(JsonFields.UTM_LAYOUT, 0))
            
            # Engineering costs
            cost_components['Engineering (UTE)'] += self._safe_float(item.get(JsonFields.UTE, 0))
            cost_components['Engineering (BA)'] += self._safe_float(item.get(JsonFields.BA, 0))
            
            # Software costs
            cost_components['Software (PC)'] += self._safe_float(item.get(JsonFields.SW_PC, 0))
            cost_components['Software (PLC)'] += self._safe_float(item.get(JsonFields.SW_PLC, 0))
            cost_components['Software (LGV)'] += self._safe_float(item.get(JsonFields.SW_LGV, 0))
            
            # Manufacturing costs
            cost_components['Manufacturing (Mec)'] += (
                self._safe_float(item.get(JsonFields.MTG_MEC, 0)) + 
                self._safe_float(item.get(JsonFields.MTG_MEC_INTRA, 0))
            )
            cost_components['Manufacturing (Ele)'] += (
                self._safe_float(item.get(JsonFields.CAB_ELE, 0)) + 
                self._safe_float(item.get(JsonFields.CAB_ELE_INTRA, 0))
            )
            
            # Testing costs
            cost_components['Testing (Collaudo)'] += (
                self._safe_float(item.get(JsonFields.COLL_BA, 0)) +
                self._safe_float(item.get(JsonFields.COLL_PC, 0)) +
                self._safe_float(item.get(JsonFields.COLL_PLC, 0)) +
                self._safe_float(item.get(JsonFields.COLL_LGV, 0))
            )
            
            # Project management
            cost_components['Project Management'] += self._safe_float(item.get(JsonFields.PM_COST, 0))
            
            # Installation
            cost_components['Installation'] += self._safe_float(item.get(JsonFields.INSTALL, 0))
            
            # Documentation
            cost_components['Documentation'] += self._safe_float(item.get(JsonFields.DOCUMENT, 0))
            
            # After sales
            cost_components['After Sales'] += self._safe_float(item.get(JsonFields.AFTER_SALES, 0))
        
        # Filter out zero components and create dataframe
        cost_components_filtered = {k: v for k, v in cost_components.items() if v > 0}
        
        if cost_components_filtered:
            df_costs = pd.DataFrame([
                {'Component': comp, 'Cost (€)': cost, 'Percentage': (cost / total_costo * 100) if total_costo > 0 else 0}
                for comp, cost in cost_components_filtered.items()
            ]).sort_values('Cost (€)', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Cost composition pie chart
                fig_pie = px.pie(
                    df_costs,
                    values='Cost (€)',
                    names='Component',
                    title=f'Cost Composition for {wbe_name}'
                )
                fig_pie.update_layout(height=500)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Cost composition bar chart
                fig_bar = px.bar(
                    df_costs.head(10),
                    x='Cost (€)',
                    y='Component',
                    orientation='h',
                    title='Top 10 Cost Components',
                    text='Cost (€)',
                    color='Cost (€)',
                    color_continuous_scale='Reds'
                )
                fig_bar.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
                fig_bar.update_layout(height=500)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Cost breakdown table
            st.subheader("📋 Cost Breakdown Table")
            st.dataframe(df_costs, use_container_width=True)
        
        # Categories within WBE
        st.subheader("📂 Categories in this WBE")
        
        cat_data = []
        for cat_info in wbe_categories:
            category = cat_info['category']
            cat_listino = self._safe_float(category.get(JsonFields.PRICELIST_SUBTOTAL, 0))
            cat_costo = self._safe_float(category.get(JsonFields.COST_SUBTOTAL, 0))
            cat_offer = self._safe_float(category.get(JsonFields.OFFER_PRICE, 0))
            cat_margin = cat_listino - cat_costo
            cat_margin_perc = (cat_margin / cat_listino * 100) if cat_listino > 0 else 0
            
            # Calculate offer-based margin if offer price is available
            cat_offer_margin = cat_offer - cat_costo if cat_offer > 0 else 0
            cat_offer_margin_perc = (1 - (cat_costo / cat_offer)) * 100 if cat_offer > 0 else 0
            
            cat_data.append({
                'Group': cat_info[JsonFields.GROUP_ID],
                'Category': cat_info[JsonFields.CATEGORY_ID],
                'Name': self._truncate_text(cat_info[JsonFields.CATEGORY_NAME], 30),
                'Items': len(category.get(JsonFields.ITEMS, [])),
                'Listino (€)': cat_listino,
                'Costo (€)': cat_costo,
                'Offer (€)': cat_offer,
                'Listino Margin (€)': cat_margin,
                'Listino Margin %': cat_margin_perc,
                'Offer Margin (€)': cat_offer_margin,
                'Offer Margin %': cat_offer_margin_perc
            })
        
        df_categories = pd.DataFrame(cat_data)
        
        if not df_categories.empty:
            st.dataframe(df_categories, use_container_width=True)
            
            # Category comparison chart - prioritize offer data if available
            has_offer_data = any(row['Offer (€)'] > 0 for _, row in df_categories.iterrows())
            
            if len(df_categories) > 1:
                if has_offer_data:
                    # Show offer-based comparison when offer data is available
                    fig_cat = px.bar(
                        df_categories[df_categories['Offer (€)'] > 0],
                        x='Category',
                        y=['Costo (€)', 'Offer Margin (€)'],
                        title=f'Cost vs Offer Margin by Category in {wbe_name}',
                        barmode='stack',
                        color_discrete_map={'Costo (€)': '#ff6b6b', 'Offer Margin (€)': '#51cf66'}
                    )
                else:
                    # Fallback to listino-based comparison
                    fig_cat = px.bar(
                        df_categories,
                        x='Category',
                            y=['Costo (€)', 'Listino Margin (€)'],
                            title=f'Cost vs Listino Margin by Category in {wbe_name}',
                        barmode='stack',
                            color_discrete_map={'Costo (€)': '#ff6b6b', 'Listino Margin (€)': '#51cf66'}
                    )
                    fig_cat.update_layout(height=400)
                st.plotly_chart(fig_cat, use_container_width=True)
        
        # NEW SECTION: Category-level Cost vs Offer Analysis
        if has_offer_data:
            st.subheader("💰 Cost vs Offer Analysis by Category")
            st.markdown("*This analysis compares WBE cost against WBE offer prices from VA21 data for each category.*")
            
            # Filter categories with offer data
            categories_with_offers = df_categories[df_categories['Offer (€)'] > 0].copy()
            
            if not categories_with_offers.empty:
                # Create enhanced comparison table
                st.markdown("##### 📋 Detailed Cost vs Offer Comparison")
                
                # Prepare data for better visualization
                comparison_data = []
                for _, row in categories_with_offers.iterrows():
                    comparison_data.append({
                        'Category': row['Category'],
                        'Name': row['Name'],
                        'Cost (€)': row['Costo (€)'],
                        'Offer (€)': row['Offer (€)'],
                        'Offer Margin (€)': row['Offer Margin (€)'],
                        'Offer Margin %': row['Offer Margin %'],
                        'Cost/Offer Ratio': (row['Costo (€)'] / row['Offer (€)']) if row['Offer (€)'] > 0 else 0
                    })
                
                df_comparison = pd.DataFrame(comparison_data)
                
                # Enhanced metrics display
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_margin_perc = df_comparison['Offer Margin %'].mean()
                    st.metric(
                        "Avg Offer Margin %", 
                        f"{avg_margin_perc:.2f}%",
                        delta=f"{avg_margin_perc - 20:.1f}%" if avg_margin_perc != 0 else None
                    )
                
                with col2:
                    min_margin_perc = df_comparison['Offer Margin %'].min()
                    min_category = df_comparison.loc[df_comparison['Offer Margin %'].idxmin(), 'Category']
                    st.metric(
                        "Lowest Margin %", 
                        f"{min_margin_perc:.2f}%",
                        delta=f"({min_category})"
                    )
                
                with col3:
                    max_margin_perc = df_comparison['Offer Margin %'].max()
                    max_category = df_comparison.loc[df_comparison['Offer Margin %'].idxmax(), 'Category']
                    st.metric(
                        "Highest Margin %", 
                        f"{max_margin_perc:.2f}%",
                        delta=f"({max_category})"
                    )
                
                with col4:
                    profitable_categories = len(df_comparison[df_comparison['Offer Margin %'] > 0])
                    total_categories = len(df_comparison)
                    st.metric(
                        "Profitable Categories", 
                        f"{profitable_categories}/{total_categories}",
                        delta=f"{(profitable_categories/total_categories)*100:.1f}%"
                    )
                
                # Enhanced comparison table
                try:
                    # Try to apply background gradient (requires matplotlib)
                    styled_df = df_comparison.style.format({
                        'Cost (€)': '€{:,.2f}',
                        'Offer (€)': '€{:,.2f}',
                        'Offer Margin (€)': '€{:,.2f}',
                        'Offer Margin %': '{:.2f}%',
                        'Cost/Offer Ratio': '{:.3f}'
                    }).background_gradient(
                        subset=['Offer Margin %'], 
                        cmap='RdYlGn', 
                        vmin=-50, 
                        vmax=50
                    )
                except ImportError:
                    # Fall back to basic formatting if matplotlib is not available
                    styled_df = df_comparison.style.format({
                        'Cost (€)': '€{:,.2f}',
                        'Offer (€)': '€{:,.2f}',
                        'Offer Margin (€)': '€{:,.2f}',
                        'Offer Margin %': '{:.2f}%',
                        'Cost/Offer Ratio': '{:.3f}'
                    })
                
                st.dataframe(styled_df, use_container_width=True)
                
                # Visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    # Margin percentage comparison chart
                    fig_margin = px.bar(
                        df_comparison.sort_values('Offer Margin %', ascending=True),
                        x='Offer Margin %',
                        y='Category',
                        orientation='h',
                        title='Offer Margin % by Category',
                        color='Offer Margin %',
                        color_continuous_scale='RdYlGn',
                        color_continuous_midpoint=0,
                        text='Offer Margin %'
                    )
                    fig_margin.update_traces(
                        texttemplate='%{text:.1f}%', 
                        textposition='outside'
                    )
                    fig_margin.add_vline(x=0, line_dash="dash", line_color="red")
                    fig_margin.add_vline(x=20, line_dash="dash", line_color="green")
                    # Add annotation for the target line
                    fig_margin.add_annotation(
                        x=20,
                        y=df_comparison['Category'].iloc[len(df_comparison)//2],  # Middle of the chart
                        text="Target 20%",
                        showarrow=False,
                        font=dict(color="green", size=10),
                        bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="green",
                        borderwidth=1,
                        xshift=10  # Shift text slightly to the right of the line
                    )
                    fig_margin.update_layout(height=400)
                    st.plotly_chart(fig_margin, use_container_width=True)
                
                with col2:
                    # Cost vs Offer scatter plot
                    fig_scatter = px.scatter(
                        df_comparison,
                        x='Cost (€)',
                        y='Offer (€)',
                        size='Offer Margin (€)',
                        color='Offer Margin %',
                        hover_data=['Category', 'Name'],
                        title='Cost vs Offer Price Analysis',
                        color_continuous_scale='RdYlGn',
                        color_continuous_midpoint=0
                    )
                    # Add diagonal line (break-even line where cost = offer)
                    max_val = max(df_comparison['Cost (€)'].max(), df_comparison['Offer (€)'].max())
                    fig_scatter.add_shape(
                        type="line",
                        x0=0, y0=0, x1=max_val, y1=max_val,
                        line=dict(color="red", width=2, dash="dash")
                    )
                    # Add annotation for the break-even line
                    fig_scatter.add_annotation(
                        x=max_val * 0.8,
                        y=max_val * 0.8,
                        text="Break-even line",
                        showarrow=False,
                        font=dict(color="red", size=12),
                        bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="red",
                        borderwidth=1
                    )
                    fig_scatter.update_layout(height=400)
                    st.plotly_chart(fig_scatter, use_container_width=True)
                
                # Summary insights
                st.markdown("##### 🔍 Key Insights")
                
                # Calculate insights
                negative_margin_cats = df_comparison[df_comparison['Offer Margin %'] < 0]
                high_margin_cats = df_comparison[df_comparison['Offer Margin %'] > 30]
                
                insights = []
                if not negative_margin_cats.empty:
                    insights.append(f"⚠️ **{len(negative_margin_cats)} categories** have negative offer margins")
                if not high_margin_cats.empty:
                    insights.append(f"✅ **{len(high_margin_cats)} categories** have high margins (>30%)")
                
                insights.append(f"📊 Average cost/offer ratio: **{df_comparison['Cost/Offer Ratio'].mean():.3f}**")
                insights.append(f"💰 Total offer value: **€{df_comparison['Offer (€)'].sum():,.2f}**")
                insights.append(f"💸 Total cost: **€{df_comparison['Cost (€)'].sum():,.2f}**")
                
                for insight in insights:
                    st.markdown(insight)
            else:
                st.warning("No categories with offer prices found for detailed analysis.")
        
        # Time analysis for WBE
        st.subheader("⏱️ Time Analysis")
        
        total_hours = {
            'UTM Robot': 0,
            'UTM LGV': 0,
            'UTM Intra': 0,
            'UTM Layout': 0,
            'Engineering': 0,
            'Manufacturing': 0,
            'Testing': 0,
            'Installation': 0,
            'PM Hours': 0
        }
        
        for item in wbe_data[JsonFields.ITEMS]:
            total_hours['UTM Robot'] += self._safe_float(item.get(JsonFields.UTM_ROBOT_H, 0))
            total_hours['UTM LGV'] += self._safe_float(item.get(JsonFields.UTM_LGV_H, 0))
            total_hours['UTM Intra'] += self._safe_float(item.get(JsonFields.UTM_INTRA_H, 0))
            total_hours['UTM Layout'] += self._safe_float(item.get(JsonFields.UTM_LAYOUT_H, 0))
            
            total_hours['Engineering'] += (
                self._safe_float(item.get(JsonFields.UTE_H, 0)) +
                self._safe_float(item.get(JsonFields.BA_H, 0)) +
                self._safe_float(item.get(JsonFields.SW_PC_H, 0)) +
                self._safe_float(item.get(JsonFields.SW_PLC_H, 0)) +
                self._safe_float(item.get(JsonFields.SW_LGV_H, 0))
            )
            
            total_hours['Manufacturing'] += (
                self._safe_float(item.get(JsonFields.MTG_MEC_H, 0)) +
                self._safe_float(item.get(JsonFields.MTG_MEC_INTRA_H, 0)) +
                self._safe_float(item.get(JsonFields.CAB_ELE_H, 0)) +
                self._safe_float(item.get(JsonFields.CAB_ELE_INTRA_H, 0))
            )
            
            total_hours['Testing'] += (
                self._safe_float(item.get(JsonFields.COLL_BA_H, 0)) +
                self._safe_float(item.get(JsonFields.COLL_PC_H, 0)) +
                self._safe_float(item.get(JsonFields.COLL_PLC_H, 0)) +
                self._safe_float(item.get(JsonFields.COLL_LGV_H, 0))
            )
            
            total_hours['Installation'] += (
                self._safe_float(item.get(JsonFields.INSTALL_H, 0)) +
                self._safe_float(item.get(JsonFields.SITE_H, 0)) +
                self._safe_float(item.get(JsonFields.AV_PC_H, 0)) +
                self._safe_float(item.get(JsonFields.AV_PLC_H, 0)) +
                self._safe_float(item.get(JsonFields.AV_LGV_H, 0))
            )
            
            total_hours['PM Hours'] += self._safe_float(item.get(JsonFields.PM_H, 0))
        
        # Filter out zero hours
        hours_filtered = {k: v for k, v in total_hours.items() if v > 0}
        
        if hours_filtered:
            df_hours = pd.DataFrame([
                {'Activity': activity, 'Hours': hours}
                for activity, hours in hours_filtered.items()
            ]).sort_values('Hours', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                total_wbe_hours = sum(hours_filtered.values())
                st.metric("Total Hours", f"{total_wbe_hours:,.1f}")
                
                if total_costo > 0 and total_wbe_hours > 0:
                    cost_per_hour = total_costo / total_wbe_hours
                    st.metric("Cost per Hour", f"€{cost_per_hour:.2f}")
            
            with col2:
                # Hours distribution chart
                fig_hours = px.pie(
                    df_hours,
                    values='Hours',
                    names='Activity',
                    title=f'Time Distribution for {wbe_name}'
                )
                fig_hours.update_layout(height=400)
                st.plotly_chart(fig_hours, use_container_width=True)
            
            # Hours table
            st.dataframe(df_hours, use_container_width=True)
        else:
            st.info("No time tracking data available for this WBE.")
    
    def display_field_analysis(self):
        """Display comprehensive field analysis for all 81 columns"""
        st.header("🔍 Comprehensive Field Analysis")
        
        # Collect field usage statistics
        field_stats = {}
        total_items = 0
        
        # Define field categories
        field_categories = {
            'Basic': [JsonFields.QTY, JsonFields.UNIT_COST, JsonFields.TOTAL_COST, JsonFields.PRICELIST_TOTAL, JsonFields.MAT],
            'UTM': [JsonFields.UTM_ROBOT, JsonFields.UTM_ROBOT_H, JsonFields.UTM_LGV, JsonFields.UTM_LGV_H, 
                   JsonFields.UTM_INTRA, JsonFields.UTM_INTRA_H, JsonFields.UTM_LAYOUT, JsonFields.UTM_LAYOUT_H],
            'Engineering': [JsonFields.UTE, JsonFields.UTE_H, JsonFields.BA, JsonFields.BA_H, JsonFields.SW_PC, 
                          JsonFields.SW_PC_H, JsonFields.SW_PLC, JsonFields.SW_PLC_H, JsonFields.SW_LGV, JsonFields.SW_LGV_H],
            'Manufacturing': [JsonFields.MTG_MEC, JsonFields.MTG_MEC_H, JsonFields.MTG_MEC_INTRA, JsonFields.MTG_MEC_INTRA_H, 
                            JsonFields.CAB_ELE, JsonFields.CAB_ELE_H, JsonFields.CAB_ELE_INTRA, JsonFields.CAB_ELE_INTRA_H],
            'Testing': [JsonFields.COLL_BA, JsonFields.COLL_BA_H, JsonFields.COLL_PC, JsonFields.COLL_PC_H, 
                       JsonFields.COLL_PLC, JsonFields.COLL_PLC_H, JsonFields.COLL_LGV, JsonFields.COLL_LGV_H],
            'Project Management': [JsonFields.PM_COST, JsonFields.PM_H, JsonFields.SPESE_PM],
            'Documentation': [JsonFields.DOCUMENT, JsonFields.DOCUMENT_H],
            'Logistics': [JsonFields.IMBALLO, JsonFields.STOCCAGGIO, JsonFields.TRASPORTO],
            'Field Activities': [JsonFields.SITE, JsonFields.SITE_H, JsonFields.INSTALL, JsonFields.INSTALL_H, 
                               JsonFields.AV_PC, JsonFields.AV_PC_H, JsonFields.AV_PLC, JsonFields.AV_PLC_H, 
                               JsonFields.AV_LGV, JsonFields.AV_LGV_H],
            'Additional': [JsonFields.SPESE_FIELD, JsonFields.SPESE_VARIE, JsonFields.AFTER_SALES, 
                         JsonFields.PROVVIGIONI_ITALIA, JsonFields.PROVVIGIONI_ESTERO, 
                         JsonFields.TESORETTO, JsonFields.MONTAGGIO_BEMA_MBE_US]
        }
        
        # Analyze field usage
        for group in self.product_groups:
            for category in group.get('categories', []):
                for item in category.get('items', []):
                    total_items += 1
                    for field, value in item.items():
                        if isinstance(value, (int, float)) and value != 0:
                            if field not in field_stats:
                                field_stats[field] = {'count': 0, 'sum': 0, 'max': 0}
                            field_stats[field]['count'] += 1
                            field_stats[field]['sum'] += value
                            field_stats[field]['max'] = max(field_stats[field]['max'], value)
        
        # Display field statistics by category
        st.subheader("📈 Field Usage Statistics")
        
        category_stats = []
        for category, fields in field_categories.items():
            category_count = sum(field_stats.get(field, {}).get('count', 0) for field in fields)
            category_sum = sum(field_stats.get(field, {}).get('sum', 0) for field in fields)
            category_max = max([field_stats.get(field, {}).get('max', 0) for field in fields] + [0])
            
            if category_count > 0:
                category_stats.append({
                    'Category': category,
                    'Fields with Data': len([f for f in fields if field_stats.get(f, {}).get('count', 0) > 0]),
                    'Total Fields': len(fields),
                    'Items with Data': category_count,
                    'Usage %': (category_count / total_items * 100) if total_items > 0 else 0,
                    'Total Value': category_sum,
                    'Max Value': category_max
                })
        
        df_category_stats = pd.DataFrame(category_stats)
        
        if not df_category_stats.empty:
            # Category usage chart
            fig_usage = px.bar(
                df_category_stats,
                x='Category',
                y='Usage %',
                title='Field Category Usage Percentage',
                text='Usage %',
                color='Usage %',
                color_continuous_scale='Viridis'
            )
            fig_usage.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_usage.update_layout(height=500)
            st.plotly_chart(fig_usage, use_container_width=True)
            
            # Category statistics table
            st.dataframe(df_category_stats, use_container_width=True)
        
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
            for category in group.get(JsonFields.CATEGORIES, []):
                for item in category.get(JsonFields.ITEMS, []):
                    has_data = any(
                        isinstance(value, (int, float)) and value != 0 
                        for value in item.values()
                    )
                    if has_data:
                        count += 1
        return count
    
    # Implement abstract methods from base class
    def _get_group_total(self, group: Dict[str, Any]) -> float:
        """Get total listino value for a profittabilita group"""
        return sum(cat.get(JsonFields.PRICELIST_SUBTOTAL, 0) for cat in group.get(JsonFields.CATEGORIES, []))
    
    def _get_category_total(self, category: Dict[str, Any]) -> float:
        """Get total listino value for a profittabilita category"""
        return self._safe_float(category.get(JsonFields.PRICELIST_SUBTOTAL, 0))
    
    def _get_item_price(self, item: Dict[str, Any]) -> float:
        """Get listino total for a profittabilita item"""
        return self._safe_float(item.get(JsonFields.PRICELIST_TOTAL, 0))
    
    def _get_item_unit_price(self, item: Dict[str, Any]) -> float:
        """Get unit price for a profittabilita item"""
        return self._safe_float(item.get(JsonFields.PRICELIST_UNIT_PRICE, 0))
    
    def _get_category_specific_fields(self, category: Dict[str, Any]) -> Dict[str, Any]:
        """Get profittabilita-specific category fields"""
        return {
            'Subtotal Listino (€)': self._safe_float(category.get(JsonFields.PRICELIST_SUBTOTAL, 0)),
            'Subtotal Costo (€)': self._safe_float(category.get(JsonFields.COST_SUBTOTAL, 0)),
            'Total Cost (€)': self._safe_float(category.get(JsonFields.TOTAL_COST, 0)),
            'WBE': category.get(JsonFields.WBE, '')
        }
    
    def _get_item_specific_fields(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Get profittabilita-specific item fields"""
        return {
            'Unit Cost (€)': self._safe_float(item.get(JsonFields.UNIT_COST, 0)),
            'Total Cost (€)': self._safe_float(item.get(JsonFields.TOTAL_COST, 0)),
            'UTM Robot': self._safe_float(item.get(JsonFields.UTM_ROBOT, 0)),
            'PM Cost': self._safe_float(item.get(JsonFields.PM_COST, 0)),
            'Install': self._safe_float(item.get(JsonFields.INSTALL, 0)),
            'After Sales': self._safe_float(item.get(JsonFields.AFTER_SALES, 0))
        } 
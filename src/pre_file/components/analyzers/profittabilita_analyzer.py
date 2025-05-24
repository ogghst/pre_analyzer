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
            st.metric("Project ID", self.project.get('id', 'N/A'))
            st.metric("Listino", self.project.get('listino', 'N/A'))
            
        with col2:
            currency = self.project.get('parameters', {}).get('currency', 'EUR')
            exchange_rate = self.project.get('parameters', {}).get('exchange_rate', 1.0)
            st.metric("Currency", currency)
            st.metric("Exchange Rate", f"{exchange_rate:.2f}")
            
        with col3:
            st.metric("Product Groups", len(self.product_groups))
            total_items = sum(len(cat.get('items', [])) for group in self.product_groups for cat in group.get('categories', []))
            st.metric("Total Items", total_items)
            
        with col4:
            margin_perc = self.totals.get('margin_percentage', 0)
            st.metric("Margin %", f"{margin_perc:.2f}%")
            # Count items with data
            items_with_data = self._count_items_with_data()
            st.metric("Items with Data", items_with_data)
        
        # Financial summary
        st.subheader("💰 Profitability Summary")
        fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
        
        with fin_col1:
            st.metric("Total Listino", f"€{self.totals.get('total_listino', 0):,.2f}")
        with fin_col2:
            st.metric("Total Costo", f"€{self.totals.get('total_costo', 0):,.2f}")
        with fin_col3:
            margin = self.totals.get('margin', 0)
            st.metric("Margin", f"€{margin:,.2f}")
        with fin_col4:
            margin_perc = self.totals.get('margin_percentage', 0)
            delta_color = "normal" if margin_perc > 20 else "inverse"
            st.metric("Margin %", f"{margin_perc:.2f}%", delta=f"{margin_perc - 20:.1f}%")
    
    def display_profitability_analysis(self):
        """Display comprehensive profitability analysis"""
        st.header("💹 Profitability Analysis")
        
        # Overall profitability metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # Profitability pie chart
            profit_data = {
                'Category': ['Total Costo', 'Margin'],
                'Amount (€)': [
                    self.totals.get('total_costo', 0),
                    self.totals.get('margin', 0)
                ],
                'Color': ['#ff6b6b', '#51cf66']
            }
            
            df_profit = pd.DataFrame(profit_data)
            
            fig_pie = px.pie(
                df_profit,
                values='Amount (€)',
                names='Category',
                title='Cost vs Margin Distribution',
                color='Category',
                color_discrete_map={'Total Costo': '#ff6b6b', 'Margin': '#51cf66'}
            )
            fig_pie.update_layout(height=500)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Margin gauge chart
            margin_perc = self.totals.get('margin_percentage', 0)
            
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
        
        group_profit_data = []
        for group in self.product_groups:
            group_listino = sum(cat.get('subtotal_listino', 0) for cat in group.get('categories', []))
            group_costo = sum(cat.get('subtotal_costo', 0) for cat in group.get('categories', []))
            group_margin = group_listino - group_costo
            group_margin_perc = (group_margin / group_listino * 100) if group_listino > 0 else 0
            
            group_profit_data.append({
                'Group ID': group.get('group_id', 'Unknown'),
                'Group Name': self._truncate_text(group.get('group_name', 'Unnamed'), 25),
                'Listino (€)': group_listino,
                'Costo (€)': group_costo,
                'Margin (€)': group_margin,
                'Margin %': group_margin_perc
            })
        
        df_group_profit = pd.DataFrame(group_profit_data)
        
        if not df_group_profit.empty:
            # Stacked bar chart for profitability by group
            fig_stacked = px.bar(
                df_group_profit,
                x='Group ID',
                y=['Costo (€)', 'Margin (€)'],
                title='Cost vs Margin by Group',
                barmode='stack',
                color_discrete_map={'Costo (€)': '#ff6b6b', 'Margin (€)': '#51cf66'}
            )
            fig_stacked.update_layout(height=600)
            st.plotly_chart(fig_stacked, use_container_width=True)
            
            # Profitability table
            st.dataframe(df_group_profit, use_container_width=True)
    
    def display_utm_analysis(self):
        """Display UTM (time tracking) analysis"""
        st.header("⏱️ UTM & Time Analysis")
        
        # Collect UTM data from all items
        utm_data = []
        for group in self.product_groups:
            for category in group.get('categories', []):
                for item in category.get('items', []):
                    # UTM fields
                    utm_robot = self._safe_float(item.get('utm_robot', 0))
                    utm_robot_h = self._safe_float(item.get('utm_robot_h', 0))
                    utm_lgv = self._safe_float(item.get('utm_lgv', 0))
                    utm_lgv_h = self._safe_float(item.get('utm_lgv_h', 0))
                    utm_intra = self._safe_float(item.get('utm_intra', 0))
                    utm_intra_h = self._safe_float(item.get('utm_intra_h', 0))
                    utm_layout = self._safe_float(item.get('utm_layout', 0))
                    utm_layout_h = self._safe_float(item.get('utm_layout_h', 0))
                    
                    # PM and other time fields
                    pm_cost = self._safe_float(item.get('pm_cost', 0))
                    pm_h = self._safe_float(item.get('pm_h', 0))
                    
                    # Only include items with UTM data
                    total_utm_value = utm_robot + utm_lgv + utm_intra + utm_layout
                    total_utm_hours = utm_robot_h + utm_lgv_h + utm_intra_h + utm_layout_h + pm_h
                    
                    if total_utm_value > 0 or total_utm_hours > 0:
                        utm_data.append({
                            'Group ID': group.get('group_id', 'Unknown'),
                            'Category ID': category.get('category_id', 'Unknown'),
                            'Item Code': item.get('code', 'Unknown'),
                            'Description': self._truncate_text(item.get('description', ''), 40),
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
                display_cols = ['Group ID', 'Item Code', 'Description', 'Total UTM Value', 'Total Hours', 'UTM Robot', 'UTM LGV', 'PM Cost']
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
            for category in group.get('categories', []):
                wbe = category.get('wbe', '').strip()
                if wbe and wbe != '':
                    if wbe not in wbe_data:
                        wbe_data[wbe] = {
                            'categories': [],
                            'total_listino': 0,
                            'total_costo': 0,
                            'items': []
                        }
                        wbe_categories[wbe] = []
                    
                    # Add category to WBE
                    wbe_categories[wbe].append({
                        'group_id': group.get('group_id', 'Unknown'),
                        'group_name': group.get('group_name', 'Unnamed'),
                        'category_id': category.get('category_id', 'Unknown'),
                        'category_name': category.get('category_name', 'Unnamed'),
                        'category': category
                    })
                    
                    # Aggregate financials
                    cat_listino = self._safe_float(category.get('subtotal_listino', 0))
                    cat_costo = self._safe_float(category.get('subtotal_costo', 0))
                    
                    wbe_data[wbe]['total_listino'] += cat_listino
                    wbe_data[wbe]['total_costo'] += cat_costo
                    
                    # Collect items for detailed analysis
                    for item in category.get('items', []):
                        item_data = item.copy()
                        item_data['group_id'] = group.get('group_id', 'Unknown')
                        item_data['category_id'] = category.get('category_id', 'Unknown')
                        wbe_data[wbe]['items'].append(item_data)
        
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
                'WBE': wbe,
                'Categories': len(wbe_categories[wbe]),
                'Items': len(data['items']),
                'Listino (€)': data['total_listino'],
                'Costo (€)': data['total_costo'],
                'Margin (€)': margin,
                'Margin %': margin_perc
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
        
        # Financial overview
        total_listino = wbe_data['total_listino']
        total_costo = wbe_data['total_costo']
        margin = total_listino - total_costo
        margin_perc = (margin / total_listino * 100) if total_listino > 0 else 0
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Listino", f"€{total_listino:,.2f}")
        with col2:
            st.metric("Total Costo", f"€{total_costo:,.2f}")
        with col3:
            st.metric("Margin", f"€{margin:,.2f}")
        with col4:
            delta_color = "normal" if margin_perc > 20 else "inverse"
            st.metric("Margin %", f"{margin_perc:.2f}%", delta=f"{margin_perc - 20:.1f}%")
        
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
        
        for item in wbe_data['items']:
            # Material costs
            cost_components['Material'] += self._safe_float(item.get('mat', 0))
            
            # UTM costs
            cost_components['UTM (Robot)'] += self._safe_float(item.get('utm_robot', 0))
            cost_components['UTM (LGV)'] += self._safe_float(item.get('utm_lgv', 0))
            cost_components['UTM (Intra)'] += self._safe_float(item.get('utm_intra', 0))
            cost_components['UTM (Layout)'] += self._safe_float(item.get('utm_layout', 0))
            
            # Engineering costs
            cost_components['Engineering (UTE)'] += self._safe_float(item.get('ute', 0))
            cost_components['Engineering (BA)'] += self._safe_float(item.get('ba', 0))
            
            # Software costs
            cost_components['Software (PC)'] += self._safe_float(item.get('sw_pc', 0))
            cost_components['Software (PLC)'] += self._safe_float(item.get('sw_plc', 0))
            cost_components['Software (LGV)'] += self._safe_float(item.get('sw_lgv', 0))
            
            # Manufacturing costs
            cost_components['Manufacturing (Mec)'] += (
                self._safe_float(item.get('mtg_mec', 0)) + 
                self._safe_float(item.get('mtg_mec_intra', 0))
            )
            cost_components['Manufacturing (Ele)'] += (
                self._safe_float(item.get('cab_ele', 0)) + 
                self._safe_float(item.get('cab_ele_intra', 0))
            )
            
            # Testing costs
            cost_components['Testing (Collaudo)'] += (
                self._safe_float(item.get('coll_ba', 0)) +
                self._safe_float(item.get('coll_pc', 0)) +
                self._safe_float(item.get('coll_plc', 0)) +
                self._safe_float(item.get('coll_lgv', 0))
            )
            
            # Project management
            cost_components['Project Management'] += self._safe_float(item.get('pm_cost', 0))
            
            # Installation
            cost_components['Installation'] += self._safe_float(item.get('install', 0))
            
            # Documentation
            cost_components['Documentation'] += self._safe_float(item.get('document', 0))
            
            # After sales
            cost_components['After Sales'] += self._safe_float(item.get('after_sales', 0))
        
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
            cat_listino = self._safe_float(category.get('subtotal_listino', 0))
            cat_costo = self._safe_float(category.get('subtotal_costo', 0))
            cat_margin = cat_listino - cat_costo
            cat_margin_perc = (cat_margin / cat_listino * 100) if cat_listino > 0 else 0
            
            cat_data.append({
                'Group': cat_info['group_id'],
                'Category': cat_info['category_id'],
                'Name': self._truncate_text(cat_info['category_name'], 30),
                'Items': len(category.get('items', [])),
                'Listino (€)': cat_listino,
                'Costo (€)': cat_costo,
                'Margin (€)': cat_margin,
                'Margin %': cat_margin_perc
            })
        
        df_categories = pd.DataFrame(cat_data)
        
        if not df_categories.empty:
            st.dataframe(df_categories, use_container_width=True)
            
            # Category comparison chart
            if len(df_categories) > 1:
                fig_cat = px.bar(
                    df_categories,
                    x='Category',
                    y=['Costo (€)', 'Margin (€)'],
                    title=f'Cost vs Margin by Category in {wbe_name}',
                    barmode='stack',
                    color_discrete_map={'Costo (€)': '#ff6b6b', 'Margin (€)': '#51cf66'}
                )
                fig_cat.update_layout(height=400)
                st.plotly_chart(fig_cat, use_container_width=True)
        
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
        
        for item in wbe_data['items']:
            total_hours['UTM Robot'] += self._safe_float(item.get('utm_robot_h', 0))
            total_hours['UTM LGV'] += self._safe_float(item.get('utm_lgv_h', 0))
            total_hours['UTM Intra'] += self._safe_float(item.get('utm_intra_h', 0))
            total_hours['UTM Layout'] += self._safe_float(item.get('utm_layout_h', 0))
            
            total_hours['Engineering'] += (
                self._safe_float(item.get('ute_h', 0)) +
                self._safe_float(item.get('ba_h', 0)) +
                self._safe_float(item.get('sw_pc_h', 0)) +
                self._safe_float(item.get('sw_plc_h', 0)) +
                self._safe_float(item.get('sw_lgv_h', 0))
            )
            
            total_hours['Manufacturing'] += (
                self._safe_float(item.get('mtg_mec_h', 0)) +
                self._safe_float(item.get('mtg_mec_intra_h', 0)) +
                self._safe_float(item.get('cab_ele_h', 0)) +
                self._safe_float(item.get('cab_ele_intra_h', 0))
            )
            
            total_hours['Testing'] += (
                self._safe_float(item.get('coll_ba_h', 0)) +
                self._safe_float(item.get('coll_pc_h', 0)) +
                self._safe_float(item.get('coll_plc_h', 0)) +
                self._safe_float(item.get('coll_lgv_h', 0))
            )
            
            total_hours['Installation'] += (
                self._safe_float(item.get('install_h', 0)) +
                self._safe_float(item.get('site_h', 0)) +
                self._safe_float(item.get('av_pc_h', 0)) +
                self._safe_float(item.get('av_plc_h', 0)) +
                self._safe_float(item.get('av_lgv_h', 0))
            )
            
            total_hours['PM Hours'] += self._safe_float(item.get('pm_h', 0))
        
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
            'Basic': ['quantity', 'unit_cost', 'total_cost', 'listino_total', 'mat'],
            'UTM': ['utm_robot', 'utm_robot_h', 'utm_lgv', 'utm_lgv_h', 'utm_intra', 'utm_intra_h', 'utm_layout', 'utm_layout_h'],
            'Engineering': ['ute', 'ute_h', 'ba', 'ba_h', 'sw_pc', 'sw_pc_h', 'sw_plc', 'sw_plc_h', 'sw_lgv', 'sw_lgv_h'],
            'Manufacturing': ['mtg_mec', 'mtg_mec_h', 'mtg_mec_intra', 'mtg_mec_intra_h', 'cab_ele', 'cab_ele_h', 'cab_ele_intra', 'cab_ele_intra_h'],
            'Testing': ['coll_ba', 'coll_ba_h', 'coll_pc', 'coll_pc_h', 'coll_plc', 'coll_plc_h', 'coll_lgv', 'coll_lgv_h'],
            'Project Management': ['pm_cost', 'pm_h', 'spese_pm'],
            'Documentation': ['document', 'document_h'],
            'Logistics': ['imballo', 'stoccaggio', 'trasporto'],
            'Field Activities': ['site', 'site_h', 'install', 'install_h', 'av_pc', 'av_pc_h', 'av_plc', 'av_plc_h', 'av_lgv', 'av_lgv_h'],
            'Additional': ['spese_field', 'spese_varie', 'after_sales', 'provvigioni_italia', 'provvigioni_estero', 'tesoretto', 'montaggio_bema_mbe_us']
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
            for category in group.get('categories', []):
                for item in category.get('items', []):
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
        return sum(cat.get('subtotal_listino', 0) for cat in group.get('categories', []))
    
    def _get_category_total(self, category: Dict[str, Any]) -> float:
        """Get total listino value for a profittabilita category"""
        return self._safe_float(category.get('subtotal_listino', 0))
    
    def _get_item_price(self, item: Dict[str, Any]) -> float:
        """Get listino total for a profittabilita item"""
        return self._safe_float(item.get('listino_total', 0))
    
    def _get_item_unit_price(self, item: Dict[str, Any]) -> float:
        """Get unit price for a profittabilita item"""
        return self._safe_float(item.get('list_unit_price', 0))
    
    def _get_category_specific_fields(self, category: Dict[str, Any]) -> Dict[str, Any]:
        """Get profittabilita-specific category fields"""
        return {
            'Subtotal Listino (€)': self._safe_float(category.get('subtotal_listino', 0)),
            'Subtotal Costo (€)': self._safe_float(category.get('subtotal_costo', 0)),
            'Total Cost (€)': self._safe_float(category.get('total_cost', 0)),
            'WBE': category.get('wbe', '')
        }
    
    def _get_item_specific_fields(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Get profittabilita-specific item fields"""
        return {
            'Unit Cost (€)': self._safe_float(item.get('unit_cost', 0)),
            'Total Cost (€)': self._safe_float(item.get('total_cost', 0)),
            'UTM Robot': self._safe_float(item.get('utm_robot', 0)),
            'PM Cost': self._safe_float(item.get('pm_cost', 0)),
            'Install': self._safe_float(item.get('install', 0)),
            'After Sales': self._safe_float(item.get('after_sales', 0))
        } 
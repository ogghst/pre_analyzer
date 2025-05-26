"""
Analisi Profittabilita File Comparator
Specific comparator for comparing two Analisi Profittabilita files
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

# Import field constants
from ..field_constants import JsonFields, DisplayFields


class ProfittabilitaComparator:
    """Comparator specifically for Analisi Profittabilita files"""
    
    def __init__(self, data1: Dict[str, Any], data2: Dict[str, Any], name1: str = "File 1", name2: str = "File 2"):
        """Initialize the comparator with two Analisi Profittabilita file datasets"""
        self.data1 = data1
        self.data2 = data2
        self.name1 = name1
        self.name2 = name2
        
        # Extract key components from both files
        self.project1 = data1.get(JsonFields.PROJECT, {})
        self.project2 = data2.get(JsonFields.PROJECT, {})
        
        self.product_groups1 = data1.get(JsonFields.PRODUCT_GROUPS, [])
        self.product_groups2 = data2.get(JsonFields.PRODUCT_GROUPS, [])
        
        self.totals1 = data1.get(JsonFields.TOTALS, {})
        self.totals2 = data2.get(JsonFields.TOTALS, {})
    
    def get_comparison_views(self) -> List[str]:
        """Return list of available comparison views for Analisi Profittabilita files"""
        return [
            "Project Comparison",
            "Profitability Comparison",
            "WBE Comparison",
            "Cost Elements Comparison",
            "UTM Comparison",
            "Engineering Comparison",
            "Types Comparison",
            "Summary Report"
        ]
    
    def display_project_comparison(self):
        """Display side-by-side project comparison"""
        st.header("📋 Analisi Profittabilita Project Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📄 {self.name1}")
            self._display_project_metrics(self.project1, self.product_groups1, self.totals1)
        
        with col2:
            st.subheader(f"📄 {self.name2}")
            self._display_project_metrics(self.project2, self.product_groups2, self.totals2)
        
        # Differences section
        st.subheader("🔍 Key Differences")
        self._display_project_differences()
    
    def _display_project_metrics(self, project: Dict, product_groups: List, totals: Dict):
        """Display project metrics for a single file"""
        # Basic info
        st.metric("Project ID", project.get(JsonFields.ID, 'N/A'))
        st.metric("Listino", project.get(JsonFields.LISTINO, 'N/A'))
        
        # Parameters
        params = project.get(JsonFields.PARAMETERS, {})
        currency = params.get(JsonFields.CURRENCY, 'EUR')
        exchange_rate = params.get(JsonFields.EXCHANGE_RATE, 1.0)
        
        st.metric("Currency", currency)
        st.metric("Exchange Rate", f"{exchange_rate:.2f}")
        
        # Structure
        st.metric("Product Groups", len(product_groups))
        total_items = sum(len(cat.get(JsonFields.ITEMS, [])) for group in product_groups for cat in group.get(JsonFields.CATEGORIES, []))
        st.metric("Total Items", total_items)
        
        # Financial
        total_listino = totals.get(JsonFields.TOTAL_LISTINO, 0)
        total_costo = totals.get(JsonFields.TOTAL_COSTO, 0)
        margin = totals.get(JsonFields.MARGIN, 0)
        margin_perc = totals.get(JsonFields.MARGIN_PERCENTAGE, 0)
        
        st.metric("Total Listino", f"€{total_listino:,.2f}")
        st.metric("Total Costo", f"€{total_costo:,.2f}")
        st.metric("Margin", f"€{margin:,.2f}")
        st.metric("Margin %", f"{margin_perc:.2f}%")
    
    def _display_project_differences(self):
        """Display key differences between projects"""
        differences = []
        
        # Compare basic project info
        id1 = self.project1.get(JsonFields.ID, 'N/A')
        id2 = self.project2.get(JsonFields.ID, 'N/A')
        if id1 != id2:
            differences.append({"Field": "Project ID", self.name1: id1, self.name2: id2})
        
        listino1 = self.project1.get(JsonFields.LISTINO, 'N/A')
        listino2 = self.project2.get(JsonFields.LISTINO, 'N/A')
        if listino1 != listino2:
            differences.append({"Field": "Listino", self.name1: listino1, self.name2: listino2})
        
        # Compare parameters
        params1 = self.project1.get(JsonFields.PARAMETERS, {})
        params2 = self.project2.get(JsonFields.PARAMETERS, {})
        
        if params1.get(JsonFields.CURRENCY) != params2.get(JsonFields.CURRENCY):
            differences.append({"Field": "Currency", self.name1: params1.get(JsonFields.CURRENCY, 'N/A'), self.name2: params2.get(JsonFields.CURRENCY, 'N/A')})
        
        # Compare structure
        groups1_count = len(self.product_groups1)
        groups2_count = len(self.product_groups2)
        if groups1_count != groups2_count:
            differences.append({"Field": "Product Groups Count", self.name1: groups1_count, self.name2: groups2_count})
        
        # Compare totals
        total_fields = [
            (JsonFields.TOTAL_LISTINO, "Total Listino"),
            (JsonFields.TOTAL_COSTO, "Total Costo"),
            (JsonFields.MARGIN, "Margin"),
            (JsonFields.MARGIN_PERCENTAGE, "Margin %")
        ]
        
        for field, display_name in total_fields:
            val1 = self.totals1.get(field, 0)
            val2 = self.totals2.get(field, 0)
            diff = abs(val1 - val2)
            if field == JsonFields.MARGIN_PERCENTAGE:
                if diff > 0.1:  # Threshold for percentage differences
                    differences.append({"Field": display_name, self.name1: f"{val1:.2f}%", self.name2: f"{val2:.2f}%"})
            else:
                if diff > 0.01:  # Threshold for financial differences
                    differences.append({"Field": display_name, self.name1: f"€{val1:,.2f}", self.name2: f"€{val2:,.2f}"})
        
        if differences:
            df_diff = pd.DataFrame(differences)
            st.dataframe(df_diff, use_container_width=True)
        else:
            st.success("No significant differences found in project parameters!")
    
    def display_profitability_comparison(self):
        """Display comprehensive profitability comparison"""
        st.header("💹 Profitability Comparison")
        
        # Prepare profitability data for both files
        profit_data1 = self._prepare_profitability_data(self.totals1, self.name1)
        profit_data2 = self._prepare_profitability_data(self.totals2, self.name2)
        
        # Display comparison table
        st.subheader("📊 Profitability Metrics Comparison")
        
        comparison_data = {
            'Metric': ['Total Listino (€)', 'Total Costo (€)', 'Margin (€)', 'Margin (%)'],
            self.name1: [
                profit_data1['total_listino'],
                profit_data1['total_costo'],
                profit_data1['margin'],
                profit_data1['margin_perc']
            ],
            self.name2: [
                profit_data2['total_listino'],
                profit_data2['total_costo'],
                profit_data2['margin'],
                profit_data2['margin_perc']
            ]
        }
        
        df_profit = pd.DataFrame(comparison_data)
        df_profit['Difference'] = df_profit[self.name2] - df_profit[self.name1]
        df_profit['Difference %'] = ((df_profit[self.name2] - df_profit[self.name1]) / df_profit[self.name1] * 100).round(2)
        
        st.dataframe(df_profit, use_container_width=True)
        
        # Side-by-side charts
        col1, col2 = st.columns(2)
        
        with col1:
            # File 1 pie chart
            fig1 = px.pie(
                values=[profit_data1['total_costo'], profit_data1['margin']],
                names=['Total Costo', 'Margin'],
                title=f'{self.name1} - Cost vs Margin',
                color_discrete_map={'Total Costo': '#ff6b6b', 'Margin': '#51cf66'}
            )
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # File 2 pie chart
            fig2 = px.pie(
                values=[profit_data2['total_costo'], profit_data2['margin']],
                names=['Total Costo', 'Margin'],
                title=f'{self.name2} - Cost vs Margin',
                color_discrete_map={'Total Costo': '#ff6b6b', 'Margin': '#51cf66'}
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Difference visualization
        st.subheader("📈 Profitability Differences Analysis")
        
        # Bar chart showing margin differences
        fig_diff = px.bar(
            x=['Margin (€)', 'Margin (%)'],
            y=[df_profit.iloc[2]['Difference'], df_profit.iloc[3]['Difference']],
            title='Profitability Differences (File 2 - File 1)',
            color_discrete_sequence=['#4CAF50']
        )
        fig_diff.update_layout(height=400)
        st.plotly_chart(fig_diff, use_container_width=True)
    
    def _prepare_profitability_data(self, totals: Dict, name: str) -> Dict[str, float]:
        """Prepare profitability data for a single file"""
        total_listino = totals.get(JsonFields.TOTAL_LISTINO, 0)
        total_costo = totals.get(JsonFields.TOTAL_COSTO, 0)
        margin = totals.get(JsonFields.MARGIN, 0)
        margin_perc = totals.get(JsonFields.MARGIN_PERCENTAGE, 0)
        
        return {
            'total_listino': total_listino,
            'total_costo': total_costo,
            'margin': margin,
            'margin_perc': margin_perc
        }
    
    def display_wbe_comparison(self):
        """Display WBE (Work Breakdown Element) comparison"""
        st.header("🏗️ WBE Comparison")
        
        # Extract WBE data from both files
        wbe_data1 = self._extract_wbe_data(self.product_groups1, self.name1)
        wbe_data2 = self._extract_wbe_data(self.product_groups2, self.name2)
        
        # Find common and unique WBEs
        wbes1 = set(wbe_data1.keys())
        wbes2 = set(wbe_data2.keys())
        
        common_wbes = wbes1.intersection(wbes2)
        unique_to_1 = wbes1 - wbes2
        unique_to_2 = wbes2 - wbes1
        
        # Display summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Common WBEs", len(common_wbes))
        with col2:
            st.metric(f"Only in {self.name1}", len(unique_to_1))
        with col3:
            st.metric(f"Only in {self.name2}", len(unique_to_2))
        
        # Display unique WBEs
        if unique_to_1:
            st.subheader(f"🔸 WBEs only in {self.name1}")
            unique_1_data = []
            for wbe in unique_to_1:
                data = wbe_data1[wbe]
                unique_1_data.append({
                    'WBE': wbe,
                    'Categories': data['categories_count'],
                    'Items': data['items_count'],
                    'Total Listino (€)': data['total_listino'],
                    'Total Costo (€)': data['total_costo'],
                    'Margin (€)': data['margin'],
                    'Margin (%)': data['margin_perc']
                })
            st.dataframe(pd.DataFrame(unique_1_data), use_container_width=True)
        
        if unique_to_2:
            st.subheader(f"🔹 WBEs only in {self.name2}")
            unique_2_data = []
            for wbe in unique_to_2:
                data = wbe_data2[wbe]
                unique_2_data.append({
                    'WBE': wbe,
                    'Categories': data['categories_count'],
                    'Items': data['items_count'],
                    'Total Listino (€)': data['total_listino'],
                    'Total Costo (€)': data['total_costo'],
                    'Margin (€)': data['margin'],
                    'Margin (%)': data['margin_perc']
                })
            st.dataframe(pd.DataFrame(unique_2_data), use_container_width=True)
        
        # Compare common WBEs
        if common_wbes:
            st.subheader("🔄 Common WBEs Comparison")
            self._display_common_wbes_comparison(wbe_data1, wbe_data2, common_wbes)
    
    def _extract_wbe_data(self, product_groups: List, file_name: str) -> Dict[str, Dict]:
        """Extract WBE data from product groups"""
        wbe_data = {}
        
        for group in product_groups:
            for category in group.get(JsonFields.CATEGORIES, []):
                wbe = category.get(JsonFields.WBE, '').strip()
                if wbe and wbe != '':
                    if wbe not in wbe_data:
                        wbe_data[wbe] = {
                            'categories_count': 0,
                            'items_count': 0,
                            'total_listino': 0,
                            'total_costo': 0,
                            'margin': 0,
                            'margin_perc': 0
                        }
                    
                    # Count categories and items
                    wbe_data[wbe]['categories_count'] += 1
                    wbe_data[wbe]['items_count'] += len(category.get(JsonFields.ITEMS, []))
                    
                    # Sum financials
                    cat_listino = self._safe_float(category.get(JsonFields.PRICELIST_SUBTOTAL, 0))
                    cat_costo = self._safe_float(category.get(JsonFields.COST_SUBTOTAL, 0))
                    
                    wbe_data[wbe]['total_listino'] += cat_listino
                    wbe_data[wbe]['total_costo'] += cat_costo
                    wbe_data[wbe]['margin'] = wbe_data[wbe]['total_listino'] - wbe_data[wbe]['total_costo']
                    
                    if wbe_data[wbe]['total_listino'] > 0:
                        wbe_data[wbe]['margin_perc'] = (wbe_data[wbe]['margin'] / wbe_data[wbe]['total_listino']) * 100
        
        return wbe_data
    
    def _display_common_wbes_comparison(self, wbe_data1: Dict, wbe_data2: Dict, common_wbes: set):
        """Display comparison for common WBEs"""
        comparison_data = []
        
        for wbe in common_wbes:
            data1 = wbe_data1[wbe]
            data2 = wbe_data2[wbe]
            
            comparison_data.append({
                'WBE': wbe,
                f'{self.name1} - Listino (€)': data1['total_listino'],
                f'{self.name2} - Listino (€)': data2['total_listino'],
                f'{self.name1} - Costo (€)': data1['total_costo'],
                f'{self.name2} - Costo (€)': data2['total_costo'],
                f'{self.name1} - Margin (%)': data1['margin_perc'],
                f'{self.name2} - Margin (%)': data2['margin_perc'],
                'Margin Difference (%)': data2['margin_perc'] - data1['margin_perc'],
                'Cost Difference (€)': data2['total_costo'] - data1['total_costo']
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        
        # Filter significant differences
        threshold = st.slider("Minimum cost difference (€) to show", 0, 50000, 1000)
        df_filtered = df_comparison[abs(df_comparison['Cost Difference (€)']) >= threshold]
        
        if not df_filtered.empty:
            st.dataframe(df_filtered, use_container_width=True)
            
            # Top differences chart
            top_diffs = df_filtered.nlargest(10, 'Cost Difference (€)', keep='all')
            if len(top_diffs) > 0:
                fig = px.bar(
                    top_diffs,
                    x='Cost Difference (€)',
                    y='WBE',
                    title='Top WBE Cost Differences',
                    orientation='h',
                    color='Cost Difference (€)',
                    color_continuous_scale='RdBu_r'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No WBEs with cost differences >= €{threshold}")
    
    def display_cost_elements_comparison(self):
        """Display cost elements comparison (Material, UTM, Engineering, etc.)"""
        st.header("💰 Cost Elements Comparison")
        
        # Extract cost elements data
        cost_elements1 = self._extract_cost_elements(self.product_groups1, self.name1)
        cost_elements2 = self._extract_cost_elements(self.product_groups2, self.name2)
        
        # Prepare comparison data
        elements = list(set(cost_elements1.keys()) | set(cost_elements2.keys()))
        comparison_data = []
        
        for element in elements:
            val1 = cost_elements1.get(element, 0)
            val2 = cost_elements2.get(element, 0)
            comparison_data.append({
                'Cost Element': element,
                self.name1: val1,
                self.name2: val2,
                'Difference': val2 - val1,
                'Difference %': ((val2 - val1) / val1 * 100) if val1 != 0 else 0
            })
        
        df_cost_elements = pd.DataFrame(comparison_data)
        df_cost_elements = df_cost_elements.sort_values('Difference', key=abs, ascending=False)
        
        # Display comparison table
        st.subheader("📊 Cost Elements Breakdown Comparison")
        st.dataframe(df_cost_elements, use_container_width=True)
        
        # Side-by-side charts
        col1, col2 = st.columns(2)
        
        with col1:
            # File 1 cost breakdown
            non_zero_elements1 = {k: v for k, v in cost_elements1.items() if v > 0}
            if non_zero_elements1:
                fig1 = px.pie(
                    values=list(non_zero_elements1.values()),
                    names=list(non_zero_elements1.keys()),
                    title=f'{self.name1} - Cost Elements Breakdown'
                )
                fig1.update_layout(height=500)
                st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # File 2 cost breakdown
            non_zero_elements2 = {k: v for k, v in cost_elements2.items() if v > 0}
            if non_zero_elements2:
                fig2 = px.pie(
                    values=list(non_zero_elements2.values()),
                    names=list(non_zero_elements2.keys()),
                    title=f'{self.name2} - Cost Elements Breakdown'
                )
                fig2.update_layout(height=500)
                st.plotly_chart(fig2, use_container_width=True)
        
        # Differences visualization
        st.subheader("📈 Cost Elements Differences")
        
        # Filter significant differences
        significant_diffs = df_cost_elements[abs(df_cost_elements['Difference']) > 100]
        
        if not significant_diffs.empty:
            fig_diff = px.bar(
                significant_diffs,
                x='Cost Element',
                y='Difference',
                title='Cost Elements Differences (File 2 - File 1)',
                color='Difference',
                color_continuous_scale='RdBu_r'
            )
            fig_diff.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_diff, use_container_width=True)
        else:
            st.info("No significant cost element differences found.")
    
    def _extract_cost_elements(self, product_groups: List, file_name: str) -> Dict[str, float]:
        """Extract cost elements data from product groups"""
        cost_elements = {
            'Material': 0,
            'UTM Robot': 0,
            'UTM LGV': 0,
            'UTM Intra': 0,
            'UTM Layout': 0,
            'Engineering UTE': 0,
            'Engineering BA': 0,
            'Software PC': 0,
            'Software PLC': 0,
            'Software LGV': 0,
            'Manufacturing Mec': 0,
            'Manufacturing Ele': 0,
            'Testing Collaudo': 0,
            'Project Management': 0,
            'Installation': 0,
            'Documentation': 0,
            'After Sales': 0
        }
        
        for group in product_groups:
            for category in group.get(JsonFields.CATEGORIES, []):
                for item in category.get(JsonFields.ITEMS, []):
                    # Material costs
                    cost_elements['Material'] += self._safe_float(item.get(JsonFields.MAT, 0))
                    
                    # UTM costs
                    cost_elements['UTM Robot'] += self._safe_float(item.get(JsonFields.UTM_ROBOT, 0))
                    cost_elements['UTM LGV'] += self._safe_float(item.get(JsonFields.UTM_LGV, 0))
                    cost_elements['UTM Intra'] += self._safe_float(item.get(JsonFields.UTM_INTRA, 0))
                    cost_elements['UTM Layout'] += self._safe_float(item.get(JsonFields.UTM_LAYOUT, 0))
                    
                    # Engineering costs
                    cost_elements['Engineering UTE'] += self._safe_float(item.get(JsonFields.UTE, 0))
                    cost_elements['Engineering BA'] += self._safe_float(item.get(JsonFields.BA, 0))
                    
                    # Software costs
                    cost_elements['Software PC'] += self._safe_float(item.get(JsonFields.SW_PC, 0))
                    cost_elements['Software PLC'] += self._safe_float(item.get(JsonFields.SW_PLC, 0))
                    cost_elements['Software LGV'] += self._safe_float(item.get(JsonFields.SW_LGV, 0))
                    
                    # Manufacturing costs
                    cost_elements['Manufacturing Mec'] += (
                        self._safe_float(item.get(JsonFields.MTG_MEC, 0)) + 
                        self._safe_float(item.get(JsonFields.MTG_MEC_INTRA, 0))
                    )
                    cost_elements['Manufacturing Ele'] += (
                        self._safe_float(item.get(JsonFields.CAB_ELE, 0)) + 
                        self._safe_float(item.get(JsonFields.CAB_ELE_INTRA, 0))
                    )
                    
                    # Testing costs
                    cost_elements['Testing Collaudo'] += (
                        self._safe_float(item.get(JsonFields.COLL_BA, 0)) +
                        self._safe_float(item.get(JsonFields.COLL_PC, 0)) +
                        self._safe_float(item.get(JsonFields.COLL_PLC, 0)) +
                        self._safe_float(item.get(JsonFields.COLL_LGV, 0))
                    )
                    
                    # Project management
                    cost_elements['Project Management'] += self._safe_float(item.get(JsonFields.PM_COST, 0))
                    
                    # Installation
                    cost_elements['Installation'] += self._safe_float(item.get(JsonFields.INSTALL, 0))
                    
                    # Documentation
                    cost_elements['Documentation'] += self._safe_float(item.get(JsonFields.DOCUMENT, 0))
                    
                    # After sales
                    cost_elements['After Sales'] += self._safe_float(item.get(JsonFields.AFTER_SALES, 0))
        
        return cost_elements
    
    def display_utm_comparison(self):
        """Display UTM (time tracking) comparison"""
        st.header("⏱️ UTM Comparison")
        
        # Extract UTM data
        utm_data1 = self._extract_utm_data(self.product_groups1, self.name1)
        utm_data2 = self._extract_utm_data(self.product_groups2, self.name2)
        
        # Prepare comparison
        utm_categories = ['UTM Robot', 'UTM LGV', 'UTM Intra', 'UTM Layout']
        comparison_data = []
        
        for category in utm_categories:
            val1 = utm_data1.get(category, 0)
            val2 = utm_data2.get(category, 0)
            comparison_data.append({
                'UTM Category': category,
                f'{self.name1} Cost (€)': val1,
                f'{self.name2} Cost (€)': val2,
                'Difference (€)': val2 - val1,
                'Difference %': ((val2 - val1) / val1 * 100) if val1 != 0 else 0
            })
        
        df_utm = pd.DataFrame(comparison_data)
        
        # Display comparison table
        st.subheader("📊 UTM Categories Comparison")
        st.dataframe(df_utm, use_container_width=True)
        
        # Side-by-side charts
        col1, col2 = st.columns(2)
        
        with col1:
            # File 1 UTM breakdown
            non_zero_utm1 = {k: v for k, v in utm_data1.items() if v > 0}
            if non_zero_utm1:
                fig1 = px.bar(
                    x=list(non_zero_utm1.keys()),
                    y=list(non_zero_utm1.values()),
                    title=f'{self.name1} - UTM Distribution'
                )
                fig1.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # File 2 UTM breakdown
            non_zero_utm2 = {k: v for k, v in utm_data2.items() if v > 0}
            if non_zero_utm2:
                fig2 = px.bar(
                    x=list(non_zero_utm2.keys()),
                    y=list(non_zero_utm2.values()),
                    title=f'{self.name2} - UTM Distribution'
                )
                fig2.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig2, use_container_width=True)
        
        # Differences visualization
        st.subheader("📈 UTM Differences")
        fig_diff = px.bar(
            df_utm,
            x='UTM Category',
            y='Difference (€)',
            title='UTM Differences (File 2 - File 1)',
            color='Difference (€)',
            color_continuous_scale='RdBu_r'
        )
        fig_diff.update_layout(height=400)
        st.plotly_chart(fig_diff, use_container_width=True)
    
    def _extract_utm_data(self, product_groups: List, file_name: str) -> Dict[str, float]:
        """Extract UTM data from product groups"""
        utm_data = {
            'UTM Robot': 0,
            'UTM LGV': 0,
            'UTM Intra': 0,
            'UTM Layout': 0
        }
        
        for group in product_groups:
            for category in group.get(JsonFields.CATEGORIES, []):
                for item in category.get(JsonFields.ITEMS, []):
                    utm_data['UTM Robot'] += self._safe_float(item.get(JsonFields.UTM_ROBOT, 0))
                    utm_data['UTM LGV'] += self._safe_float(item.get(JsonFields.UTM_LGV, 0))
                    utm_data['UTM Intra'] += self._safe_float(item.get(JsonFields.UTM_INTRA, 0))
                    utm_data['UTM Layout'] += self._safe_float(item.get(JsonFields.UTM_LAYOUT, 0))
        
        return utm_data
    
    def display_engineering_comparison(self):
        """Display engineering costs comparison"""
        st.header("⚙️ Engineering Comparison")
        
        # Extract engineering data
        eng_data1 = self._extract_engineering_data(self.product_groups1, self.name1)
        eng_data2 = self._extract_engineering_data(self.product_groups2, self.name2)
        
        # Prepare comparison
        eng_categories = ['UTE', 'BA', 'Software PC', 'Software PLC', 'Software LGV']
        comparison_data = []
        
        for category in eng_categories:
            val1 = eng_data1.get(category, 0)
            val2 = eng_data2.get(category, 0)
            comparison_data.append({
                'Engineering Category': category,
                f'{self.name1} Cost (€)': val1,
                f'{self.name2} Cost (€)': val2,
                'Difference (€)': val2 - val1,
                'Difference %': ((val2 - val1) / val1 * 100) if val1 != 0 else 0
            })
        
        df_eng = pd.DataFrame(comparison_data)
        
        # Display comparison table
        st.subheader("📊 Engineering Categories Comparison")
        st.dataframe(df_eng, use_container_width=True)
        
        # Combined chart
        fig = px.bar(
            df_eng,
            x='Engineering Category',
            y=[f'{self.name1} Cost (€)', f'{self.name2} Cost (€)'],
            title='Engineering Costs Comparison',
            barmode='group'
        )
        fig.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    def _extract_engineering_data(self, product_groups: List, file_name: str) -> Dict[str, float]:
        """Extract engineering data from product groups"""
        eng_data = {
            'UTE': 0,
            'BA': 0,
            'Software PC': 0,
            'Software PLC': 0,
            'Software LGV': 0
        }
        
        for group in product_groups:
            for category in group.get(JsonFields.CATEGORIES, []):
                for item in category.get(JsonFields.ITEMS, []):
                    eng_data['UTE'] += self._safe_float(item.get(JsonFields.UTE, 0))
                    eng_data['BA'] += self._safe_float(item.get(JsonFields.BA, 0))
                    eng_data['Software PC'] += self._safe_float(item.get(JsonFields.SW_PC, 0))
                    eng_data['Software PLC'] += self._safe_float(item.get(JsonFields.SW_PLC, 0))
                    eng_data['Software LGV'] += self._safe_float(item.get(JsonFields.SW_LGV, 0))
        
        return eng_data
    
    def display_types_comparison(self):
        """Display types comparison (equipment types, categories, etc.)"""
        st.header("🏷️ Types Comparison")
        
        # Extract types data from group and category names
        types_data1 = self._extract_types_data(self.product_groups1, self.name1)
        types_data2 = self._extract_types_data(self.product_groups2, self.name2)
        
        # Compare group types
        st.subheader("📦 Group Types Comparison")
        group_types1 = set(types_data1['group_types'].keys())
        group_types2 = set(types_data2['group_types'].keys())
        
        common_groups = group_types1.intersection(group_types2)
        unique_groups_1 = group_types1 - group_types2
        unique_groups_2 = group_types2 - group_types1
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Common Group Types", len(common_groups))
        with col2:
            st.metric(f"Only in {self.name1}", len(unique_groups_1))
        with col3:
            st.metric(f"Only in {self.name2}", len(unique_groups_2))
        
        # Display unique group types
        if unique_groups_1:
            st.write(f"**Group types only in {self.name1}:**")
            st.write(", ".join(sorted(unique_groups_1)))
        
        if unique_groups_2:
            st.write(f"**Group types only in {self.name2}:**")
            st.write(", ".join(sorted(unique_groups_2)))
        
        # Compare category types
        st.subheader("📂 Category Types Comparison")
        cat_types1 = set(types_data1['category_types'].keys())
        cat_types2 = set(types_data2['category_types'].keys())
        
        common_cats = cat_types1.intersection(cat_types2)
        unique_cats_1 = cat_types1 - cat_types2
        unique_cats_2 = cat_types2 - cat_types1
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Common Category Types", len(common_cats))
        with col2:
            st.metric(f"Only in {self.name1}", len(unique_cats_1))
        with col3:
            st.metric(f"Only in {self.name2}", len(unique_cats_2))
        
        # Show common types with different counts
        if common_groups:
            st.subheader("🔄 Common Group Types - Count Differences")
            group_comparison = []
            for group_type in sorted(common_groups):
                count1 = types_data1['group_types'][group_type]
                count2 = types_data2['group_types'][group_type]
                if count1 != count2:
                    group_comparison.append({
                        'Group Type': group_type,
                        f'{self.name1} Count': count1,
                        f'{self.name2} Count': count2,
                        'Difference': count2 - count1
                    })
            
            if group_comparison:
                df_group_comp = pd.DataFrame(group_comparison)
                st.dataframe(df_group_comp, use_container_width=True)
            else:
                st.success("All common group types have the same counts!")
    
    def _extract_types_data(self, product_groups: List, file_name: str) -> Dict[str, Dict]:
        """Extract types data from product groups"""
        group_types = {}
        category_types = {}
        
        for group in product_groups:
            # Analyze group names/types
            group_name = group.get(JsonFields.GROUP_NAME, 'Unknown')
            # Extract type from group name (simplified logic)
            group_type = self._extract_type_from_name(group_name)
            group_types[group_type] = group_types.get(group_type, 0) + 1
            
            for category in group.get(JsonFields.CATEGORIES, []):
                # Analyze category names/types
                cat_name = category.get(JsonFields.CATEGORY_NAME, 'Unknown')
                cat_type = self._extract_type_from_name(cat_name)
                category_types[cat_type] = category_types.get(cat_type, 0) + 1
        
        return {
            'group_types': group_types,
            'category_types': category_types
        }
    
    def _extract_type_from_name(self, name: str) -> str:
        """Extract equipment type from name (simplified logic)"""
        name_lower = name.lower()
        
        # Common equipment types
        if 'robot' in name_lower or 'agv' in name_lower:
            return 'Robot/AGV'
        elif 'conveyor' in name_lower or 'belt' in name_lower:
            return 'Conveyor'
        elif 'storage' in name_lower or 'warehouse' in name_lower:
            return 'Storage'
        elif 'software' in name_lower or 'sw' in name_lower:
            return 'Software'
        elif 'mechanical' in name_lower or 'mech' in name_lower:
            return 'Mechanical'
        elif 'electrical' in name_lower or 'elect' in name_lower:
            return 'Electrical'
        elif 'installation' in name_lower or 'install' in name_lower:
            return 'Installation'
        elif 'service' in name_lower or 'maintenance' in name_lower:
            return 'Service'
        else:
            return 'Other'
    
    def display_summary_report(self):
        """Display comprehensive comparison summary report"""
        st.header("📄 Analisi Profittabilita Comparison Summary Report")
        
        # Executive Summary
        st.subheader("📝 Executive Summary")
        
        # Financial summary
        total_listino1 = self.totals1.get(JsonFields.TOTAL_LISTINO, 0)
        total_listino2 = self.totals2.get(JsonFields.TOTAL_LISTINO, 0)
        total_costo1 = self.totals1.get(JsonFields.TOTAL_COSTO, 0)
        total_costo2 = self.totals2.get(JsonFields.TOTAL_COSTO, 0)
        margin1 = self.totals1.get(JsonFields.MARGIN, 0)
        margin2 = self.totals2.get(JsonFields.MARGIN, 0)
        margin_perc1 = self.totals1.get(JsonFields.MARGIN_PERCENTAGE, 0)
        margin_perc2 = self.totals2.get(JsonFields.MARGIN_PERCENTAGE, 0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"{self.name1} Listino", f"€{total_listino1:,.2f}")
            st.metric(f"{self.name1} Margin %", f"{margin_perc1:.2f}%")
        with col2:
            st.metric(f"{self.name2} Listino", f"€{total_listino2:,.2f}")
            st.metric(f"{self.name2} Margin %", f"{margin_perc2:.2f}%")
        with col3:
            listino_diff = total_listino2 - total_listino1
            margin_diff = margin_perc2 - margin_perc1
            st.metric("Listino Difference", f"€{listino_diff:,.2f}")
            st.metric("Margin % Difference", f"{margin_diff:.2f}%")
        
        # Structural summary
        groups1_count = len(self.product_groups1)
        groups2_count = len(self.product_groups2)
        
        items1_count = sum(len(cat.get(JsonFields.ITEMS, [])) for group in self.product_groups1 for cat in group.get(JsonFields.CATEGORIES, []))
        items2_count = sum(len(cat.get(JsonFields.ITEMS, [])) for group in self.product_groups2 for cat in group.get(JsonFields.CATEGORIES, []))
        
        st.subheader("🏗️ Structural Summary")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{self.name1}:**")
            st.write(f"- Groups: {groups1_count}")
            st.write(f"- Total Items: {items1_count}")
            
        with col2:
            st.write(f"**{self.name2}:**")
            st.write(f"- Groups: {groups2_count}")
            st.write(f"- Total Items: {items2_count}")
        
        # Cost analysis summary
        st.subheader("💰 Cost Analysis Summary")
        cost_elements1 = self._extract_cost_elements(self.product_groups1, self.name1)
        cost_elements2 = self._extract_cost_elements(self.product_groups2, self.name2)
        
        # Find largest cost differences
        largest_diffs = []
        for element in cost_elements1.keys():
            diff = cost_elements2.get(element, 0) - cost_elements1.get(element, 0)
            if abs(diff) > 1000:  # Only significant differences
                largest_diffs.append((element, diff))
        
        largest_diffs.sort(key=lambda x: abs(x[1]), reverse=True)
        
        if largest_diffs:
            st.write("**Largest cost element differences:**")
            for element, diff in largest_diffs[:5]:
                direction = "increased" if diff > 0 else "decreased"
                st.write(f"• {element}: {direction} by €{abs(diff):,.2f}")
        
        # Key insights
        st.subheader("💡 Key Insights")
        insights = []
        
        # Profitability insights
        if abs(margin_diff) > 2:
            direction = "increased" if margin_diff > 0 else "decreased"
            insights.append(f"Margin percentage {direction} by {abs(margin_diff):.2f}%")
        
        # Structural insights
        if groups1_count != groups2_count:
            insights.append(f"Different number of product groups: {groups1_count} vs {groups2_count}")
        
        if abs(items1_count - items2_count) > 10:
            insights.append(f"Significant difference in item count: {items1_count} vs {items2_count}")
        
        # Cost insights
        if largest_diffs:
            insights.append(f"Major cost changes detected in {len(largest_diffs)} categories")
        
        if insights:
            for insight in insights:
                st.write(f"• {insight}")
        else:
            st.success("Files are structurally and financially similar!")
        
        # Recommendations
        st.subheader("📋 Recommendations")
        
        if abs(margin_diff) > 5:
            st.warning("Significant margin difference detected. Review cost structure and pricing strategy.")
        elif abs(margin_diff) > 2:
            st.info("Moderate margin difference. Consider reviewing key cost drivers.")
        else:
            st.success("Margin differences are within acceptable range.")
        
        if largest_diffs:
            st.info("Review the highlighted cost element changes to understand impact on profitability.")
        
        if groups1_count != groups2_count or abs(items1_count - items2_count) > 10:
            st.info("Structural differences found. Review scope changes between versions.")
    
    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float"""
        try:
            if value is None or value == '':
                return default
            return float(value)
        except (ValueError, TypeError):
            return default 
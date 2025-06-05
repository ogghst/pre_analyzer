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
from components.field_constants import JsonFields, DisplayFields
from utils.format import safe_format_currency, safe_format_percentage, safe_format_number, safe_float, parse_currency_string


class ProfittabilitaComparator:
    """Comparator specifically for Analisi Profittabilita files"""
    
    def __init__(self, data1: Dict[str, Any], data2: Dict[str, Any], name1: str = "File 1", name2: str = "File 2"):
        """Initialize the comparator with two Analisi Profittabilita file datasets"""
        self.data1 = data1
        self.data2 = data2
        self.name1 = "File A" #TODO hardcoded, change to name1
        self.name2 = "File B" #TODO hardcoded, change to name2
        
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
            "WBE Comparison",
            "Cost Elements Comparison",
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
        
        # Profitability comparison section
        st.subheader("💹 Profitability Metrics Comparison")
        self._display_profitability_table()
    
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
        st.metric("Exchange Rate", safe_format_number(exchange_rate, decimals=2))
        
        # Structure
        st.metric("Product Groups", len(product_groups))
        total_items = sum(len(cat.get(JsonFields.ITEMS, [])) for group in product_groups for cat in group.get(JsonFields.CATEGORIES, []))
        st.metric("Total Items", total_items)
        
        # Financial - including VA21 offer prices if available
        total_listino = totals.get(JsonFields.TOTAL_LISTINO, 0)
        total_costo = totals.get(JsonFields.TOTAL_COSTO, 0)
        total_offer = totals.get(JsonFields.TOTAL_OFFER, 0)
        margin = totals.get(JsonFields.MARGIN, 0)
        margin_perc = totals.get(JsonFields.MARGIN_PERCENTAGE, 0)
        offer_margin = totals.get(JsonFields.OFFER_MARGIN, 0)
        offer_margin_perc = totals.get(JsonFields.OFFER_MARGIN_PERCENTAGE, 0)
        
        st.metric("Total Listino", safe_format_currency(total_listino, decimals=2))
        st.metric("Total Cost", safe_format_currency(total_costo, decimals=2))
        
        # Show offer price if available (from VA21)
        if total_offer > 0:
            st.metric("Total Offer (VA21)", safe_format_currency(total_offer, decimals=2))
            st.metric("Offer Margin", safe_format_currency(offer_margin, decimals=2))
            st.metric("Offer Margin %", safe_format_percentage(offer_margin_perc, decimals=2))
    
    
    def _display_profitability_table(self):
        """Display profitability comparison table"""
        # Prepare profitability data for both files
        profit_data1 = self._prepare_profitability_data(self.totals1, self.name1)
        profit_data2 = self._prepare_profitability_data(self.totals2, self.name2)
        
        # Determine which metrics to show based on available data
        has_offer_data1 = profit_data1.get(JsonFields.TOTAL_OFFER, 0) > 0
        has_offer_data2 = profit_data2.get(JsonFields.TOTAL_OFFER, 0) > 0
        has_any_offer_data = has_offer_data1 or has_offer_data2
        
        # Always show offer data comparison with safe value conversion
        comparison_data = {
            DisplayFields.COMPONENT: [
                'Total Listino', 'Total Cost', 'Total Offer VA21', 
                'Offer Margin', 'Offer Margin (%)'
            ],
            'File A': [
                safe_format_currency(profit_data1.get(JsonFields.TOTAL_LISTINO, 0)),
                safe_format_currency(profit_data1.get(JsonFields.TOTAL_COSTO, 0)),
                safe_format_currency(profit_data1.get(JsonFields.TOTAL_OFFER, 0)),
                safe_format_currency(profit_data1.get(JsonFields.OFFER_MARGIN, 0)),
                safe_format_percentage(profit_data1.get(JsonFields.OFFER_MARGIN_PERCENTAGE, 0))
            ],
            'File B': [
                safe_format_currency(profit_data2.get(JsonFields.TOTAL_LISTINO, 0)),
                safe_format_currency(profit_data2.get(JsonFields.TOTAL_COSTO, 0)),
                safe_format_currency(profit_data2.get(JsonFields.TOTAL_OFFER, 0)),
                safe_format_currency(profit_data2.get(JsonFields.OFFER_MARGIN, 0)),
                safe_format_percentage(profit_data2.get(JsonFields.OFFER_MARGIN_PERCENTAGE, 0))
            ]
        }
        
        df_profit = pd.DataFrame(comparison_data)
        st.dataframe(df_profit, use_container_width=True)
    

    
    def _prepare_profitability_data(self, totals: Dict, name: str) -> Dict[str, float]:
        """Prepare profitability data for a single file"""
        total_listino = safe_float(totals.get(JsonFields.TOTAL_LISTINO, 0))
        total_costo = safe_float(totals.get(JsonFields.TOTAL_COSTO, 0))
        total_offer = safe_float(totals.get(JsonFields.TOTAL_OFFER, 0))
        offer_margin = safe_float(totals.get(JsonFields.OFFER_MARGIN, 0))
        offer_margin_perc = safe_float(totals.get(JsonFields.OFFER_MARGIN_PERCENTAGE, 0))
        
        return {
            JsonFields.TOTAL_LISTINO: total_listino,
            JsonFields.TOTAL_COSTO: total_costo,
            JsonFields.TOTAL_OFFER: total_offer,
            JsonFields.OFFER_MARGIN: offer_margin,
            JsonFields.OFFER_MARGIN_PERCENTAGE: offer_margin_perc
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
                    DisplayFields.WBE: str(wbe),
                    DisplayFields.CATEGORIES: safe_format_number(data.get('categories_count', 0)),
                    DisplayFields.ITEMS: safe_format_number(data.get('items_count', 0)),
                    'Total Listino': safe_format_currency(data.get(JsonFields.TOTAL_LISTINO, 0)),
                    'Total Offer': safe_format_currency(data.get(JsonFields.TOTAL_OFFER, 0)),
                    'Total Cost': safe_format_currency(data.get(JsonFields.TOTAL_COSTO, 0)),
                    'Offer Margin': safe_format_currency(data.get(JsonFields.OFFER_MARGIN, 0)),
                    'Offer Margin (%)': safe_format_percentage(data.get(JsonFields.OFFER_MARGIN_PERCENTAGE, 0))
                })
            st.dataframe(pd.DataFrame(unique_1_data), use_container_width=True)
        
        if unique_to_2:
            st.subheader(f"🔹 WBEs only in {self.name2}")
            unique_2_data = []
            for wbe in unique_to_2:
                data = wbe_data2[wbe]
                unique_2_data.append({
                    DisplayFields.WBE: str(wbe),
                    DisplayFields.CATEGORIES: safe_format_number(data.get('categories_count', 0)),
                    DisplayFields.ITEMS: safe_format_number(data.get('items_count', 0)),
                    'Total Listino': safe_format_currency(data.get(JsonFields.TOTAL_LISTINO, 0)),
                    'Total Offer': safe_format_currency(data.get(JsonFields.TOTAL_OFFER, 0)),
                    'Total Cost': safe_format_currency(data.get(JsonFields.TOTAL_COSTO, 0)),
                    'Offer Margin': safe_format_currency(data.get(JsonFields.OFFER_MARGIN, 0)),
                    'Offer Margin (%)': safe_format_percentage(data.get(JsonFields.OFFER_MARGIN_PERCENTAGE, 0))
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
                            JsonFields.TOTAL_COSTO: 0,
                            JsonFields.OFFER_PRICE: 0,
                            JsonFields.OFFER_MARGIN: 0,
                            JsonFields.OFFER_MARGIN_PERCENTAGE: 0
                        }
                    
                    # Count categories and items
                    wbe_data[wbe]['categories_count'] += 1
                    wbe_data[wbe]['items_count'] += len(category.get(JsonFields.ITEMS, []))
                    
                    # Sum financials
                    cat_offer = safe_float(category.get(JsonFields.OFFER_PRICE, 0))
                    cat_costo = safe_float(category.get(JsonFields.COST_SUBTOTAL, 0))
                    
                    wbe_data[wbe][JsonFields.TOTAL_COSTO] += cat_costo
                    wbe_data[wbe][JsonFields.OFFER_PRICE] += cat_offer
                    
                    # Calculate offer margins only
                    wbe_data[wbe][JsonFields.OFFER_MARGIN] = wbe_data[wbe][JsonFields.OFFER_PRICE] - wbe_data[wbe][JsonFields.TOTAL_COSTO]
                    
                    # Calculate offer margin percentage
                    if wbe_data[wbe][JsonFields.OFFER_PRICE] > 0:
                        wbe_data[wbe][JsonFields.OFFER_MARGIN_PERCENTAGE] = (wbe_data[wbe][JsonFields.OFFER_MARGIN] / wbe_data[wbe][JsonFields.OFFER_PRICE]) * 100
        
        return wbe_data
    
    def _display_common_wbes_comparison(self, wbe_data1: Dict, wbe_data2: Dict, common_wbes: set):
        """Display comparison for common WBEs"""
        comparison_data = []
        
        for wbe in common_wbes:
            data1 = wbe_data1[wbe]
            data2 = wbe_data2[wbe]
            
            val1_offer = safe_float(data1.get(JsonFields.OFFER_PRICE, 0))
            val2_offer = safe_float(data2.get(JsonFields.OFFER_PRICE, 0))
            val1_costo = safe_float(data1.get(JsonFields.TOTAL_COSTO, 0))
            val2_costo = safe_float(data2.get(JsonFields.TOTAL_COSTO, 0))
            val1_margin = safe_float(data1.get(JsonFields.OFFER_MARGIN, 0))
            val2_margin = safe_float(data2.get(JsonFields.OFFER_MARGIN, 0))
            val1_margin_perc = safe_float(data1.get(JsonFields.OFFER_MARGIN_PERCENTAGE, 0))
            val2_margin_perc = safe_float(data2.get(JsonFields.OFFER_MARGIN_PERCENTAGE, 0))
            
            margin_diff_eur = val2_margin - val1_margin
            margin_diff_perc = val2_margin_perc - val1_margin_perc
            cost_diff = val2_costo - val1_costo
            
            comparison_data.append({
                DisplayFields.WBE: str(wbe),
                f'{self.name1} - Offer': safe_format_currency(val1_offer),
                f'{self.name2} - Offer': safe_format_currency(val2_offer),
                f'{self.name1} - Cost': safe_format_currency(val1_costo),
                f'{self.name2} - Cost': safe_format_currency(val2_costo),
                f'{self.name1} - Margin': safe_format_currency(val1_margin),
                f'{self.name2} - Margin': safe_format_currency(val2_margin),
                f'{self.name1} - Margin (%)': safe_format_percentage(val1_margin_perc),
                f'{self.name2} - Margin (%)': safe_format_percentage(val2_margin_perc),
                'Margin Diff (€)': safe_format_currency(margin_diff_eur),
                'Margin Diff (%)': safe_format_percentage(margin_diff_perc),
                'Cost Diff (€)': safe_format_currency(cost_diff)
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True)
     
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
            val1 = safe_float(cost_elements1.get(element, 0))
            val2 = safe_float(cost_elements2.get(element, 0))
            diff = val2 - val1
            diff_perc = ((val2 - val1) / val1 * 100) if val1 != 0 else 0
            
            comparison_data.append({
                'Cost Element': str(element),
                f'{self.name1}': safe_format_currency(val1),
                f'{self.name2}': safe_format_currency(val2),
                'Difference': safe_format_currency(diff),
                'Difference %': safe_format_percentage(diff_perc)
            })
        
        df_cost_elements = pd.DataFrame(comparison_data)
        # Sort by absolute difference amount (parse from formatted string)
        df_cost_elements['_sort_key'] = df_cost_elements['Difference'].apply(
            lambda x: abs(parse_currency_string(x))
        )
        df_cost_elements = df_cost_elements.sort_values('_sort_key', ascending=False).drop('_sort_key', axis=1)
        
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
        
        # Show summary of significant differences
        significant_diffs = []
        for _, row in df_cost_elements.iterrows():  
            diff_val = parse_currency_string(row['Difference'])
            if abs(diff_val) > 100:
                significant_diffs.append({
                    'Cost Element': str(row['Cost Element']),
                    'Difference': str(row['Difference']),
                    'Difference %': str(row['Difference %'])
                })
        
        if significant_diffs:
            st.subheader("🔍 Cost Element Differences")
            st.dataframe(pd.DataFrame(significant_diffs), use_container_width=True)
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
                    cost_elements['Material'] += safe_float(item.get(JsonFields.MAT, 0))
                    
                    # UTM costs
                    cost_elements['UTM Robot'] += safe_float(item.get(JsonFields.UTM_ROBOT, 0))
                    cost_elements['UTM LGV'] += safe_float(item.get(JsonFields.UTM_LGV, 0))
                    cost_elements['UTM Intra'] += safe_float(item.get(JsonFields.UTM_INTRA, 0))
                    cost_elements['UTM Layout'] += safe_float(item.get(JsonFields.UTM_LAYOUT, 0))
                    
                    # Engineering costs
                    cost_elements['Engineering UTE'] += safe_float(item.get(JsonFields.UTE, 0))
                    cost_elements['Engineering BA'] += safe_float(item.get(JsonFields.BA, 0))
                    
                    # Software costs
                    cost_elements['Software PC'] += safe_float(item.get(JsonFields.SW_PC, 0))
                    cost_elements['Software PLC'] += safe_float(item.get(JsonFields.SW_PLC, 0))
                    cost_elements['Software LGV'] += safe_float(item.get(JsonFields.SW_LGV, 0))
                    
                    # Manufacturing costs
                    cost_elements['Manufacturing Mec'] += (
                        safe_float(item.get(JsonFields.MTG_MEC, 0)) + 
                        safe_float(item.get(JsonFields.MTG_MEC_INTRA, 0))
                    )
                    cost_elements['Manufacturing Ele'] += (
                        safe_float(item.get(JsonFields.CAB_ELE, 0)) + 
                        safe_float(item.get(JsonFields.CAB_ELE_INTRA, 0))
                    )
                    
                    # Testing costs
                    cost_elements['Testing Collaudo'] += (
                        safe_float(item.get(JsonFields.COLL_BA, 0)) +
                        safe_float(item.get(JsonFields.COLL_PC, 0)) +
                        safe_float(item.get(JsonFields.COLL_PLC, 0)) +
                        safe_float(item.get(JsonFields.COLL_LGV, 0))
                    )
                    
                    # Project management
                    cost_elements['Project Management'] += safe_float(item.get(JsonFields.PM_COST, 0))
                    
                    # Installation
                    cost_elements['Installation'] += safe_float(item.get(JsonFields.INSTALL, 0))
                    
                    # Documentation
                    cost_elements['Documentation'] += safe_float(item.get(JsonFields.DOCUMENT, 0))
                    
                    # After sales
                    cost_elements['After Sales'] += safe_float(item.get(JsonFields.AFTER_SALES, 0))
        
        return cost_elements
    

    

    
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
                        'Group Type': str(group_type),
                        f'{self.name1} Count': safe_format_number(count1),
                        f'{self.name2} Count': safe_format_number(count2),
                        'Difference': safe_format_number(count2 - count1, show_sign=True)
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
            st.metric(f"{self.name1} Listino", safe_format_currency(total_listino1))
            st.metric(f"{self.name1} Margin %", safe_format_percentage(margin_perc1))
        with col2:
            st.metric(f"{self.name2} Listino", safe_format_currency(total_listino2))
            st.metric(f"{self.name2} Margin %", safe_format_percentage(margin_perc2))
        with col3:
            listino_diff = total_listino2 - total_listino1
            margin_diff = margin_perc2 - margin_perc1
            st.metric("Listino Difference", safe_format_currency(listino_diff))
            st.metric("Margin % Difference", safe_format_number(margin_diff, decimals=1, show_sign=True) + "%")
        
        # Structural summary
        groups1_count = len(self.product_groups1)
        groups2_count = len(self.product_groups2)
        
        items1_count = sum(len(cat.get(JsonFields.ITEMS, [])) for group in self.product_groups1 for cat in group.get(JsonFields.CATEGORIES, []))
        items2_count = sum(len(cat.get(JsonFields.ITEMS, [])) for group in self.product_groups2 for cat in group.get(JsonFields.CATEGORIES, []))
        
        st.subheader("🏗️ Structural Summary")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{self.name1}:**")
            st.write(f"- Groups: {safe_format_number(groups1_count)}")
            st.write(f"- Total Items: {safe_format_number(items1_count)}")
            
        with col2:
            st.write(f"**{self.name2}:**")
            st.write(f"- Groups: {safe_format_number(groups2_count)}")
            st.write(f"- Total Items: {safe_format_number(items2_count)}")
        
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
                st.write(f"• {element}: {direction} by {safe_format_currency(abs(diff))}")
        
        # Key insights
        st.subheader("💡 Key Insights")
        insights = []
        
        # Profitability insights
        if abs(margin_diff) > 2:
            direction = "increased" if margin_diff > 0 else "decreased"
            insights.append(f"Margin percentage {direction} by {safe_format_percentage(abs(margin_diff))}")
        
        # Structural insights
        if groups1_count != groups2_count:
            insights.append(f"Different number of product groups: {safe_format_number(groups1_count)} vs {safe_format_number(groups2_count)}")
        
        if abs(items1_count - items2_count) > 10:
            insights.append(f"Significant difference in item count: {safe_format_number(items1_count)} vs {safe_format_number(items2_count)}")
        
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
    

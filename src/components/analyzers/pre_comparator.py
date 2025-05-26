"""
PRE File Comparator
Specific comparator for comparing two PRE quotation files
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

# Import field constants
from ..field_constants import JsonFields, DisplayFields


class PreComparator:
    """Comparator specifically for PRE quotation files"""
    
    def __init__(self, data1: Dict[str, Any], data2: Dict[str, Any], name1: str = "File 1", name2: str = "File 2"):
        """Initialize the comparator with two PRE file datasets"""
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
        """Return list of available comparison views for PRE files"""
        return [
            "Project Comparison",
            "Financial Comparison", 
            "Groups Comparison",
            "Categories Comparison",
            "Items Comparison",
            "Summary Report"
        ]
    
    def display_project_comparison(self):
        """Display side-by-side PRE project comparison"""
        st.header("📋 PRE Project Comparison")
        
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
        st.metric("Customer", project.get('customer', 'N/A'))
        
        # Parameters
        params = project.get(JsonFields.PARAMETERS, {})
        currency = params.get(JsonFields.CURRENCY, 'N/A')
        exchange_rate = params.get(JsonFields.EXCHANGE_RATE, 0)
        doc_perc = params.get(JsonFields.DOC_PERCENTAGE, 0)
        pm_perc = params.get(JsonFields.PM_PERCENTAGE, 0)
        
        st.metric("Currency", currency)
        st.metric("Exchange Rate", f"{exchange_rate:.2f}")
        st.metric("DOC %", f"{doc_perc:.3%}")
        st.metric("PM %", f"{pm_perc:.3%}")
        
        # Structure
        st.metric("Product Groups", len(product_groups))
        total_items = sum(len(cat.get(JsonFields.ITEMS, [])) for group in product_groups for cat in group.get(JsonFields.CATEGORIES, []))
        st.metric("Total Items", total_items)
        
        # Financial
        equipment_total = totals.get(JsonFields.EQUIPMENT_TOTAL, 0)
        installation_total = totals.get(JsonFields.INSTALLATION_TOTAL, 0)
        grand_total = totals.get(JsonFields.GRAND_TOTAL, 0)
        
        st.metric("Equipment Total", f"€{equipment_total:,.2f}")
        st.metric("Installation Total", f"€{installation_total:,.2f}")
        st.metric("Grand Total", f"€{grand_total:,.2f}")
    
    def _display_project_differences(self):
        """Display key differences between projects"""
        differences = []
        
        # Compare basic project info
        id1 = self.project1.get(JsonFields.ID, 'N/A')
        id2 = self.project2.get(JsonFields.ID, 'N/A')
        if id1 != id2:
            differences.append({"Field": "Project ID", self.name1: id1, self.name2: id2})
        
        # Compare parameters
        params1 = self.project1.get(JsonFields.PARAMETERS, {})
        params2 = self.project2.get(JsonFields.PARAMETERS, {})
        
        param_fields = [
            (JsonFields.CURRENCY, "Currency"),
            (JsonFields.EXCHANGE_RATE, "Exchange Rate"),
            (JsonFields.DOC_PERCENTAGE, "DOC %"),
            (JsonFields.PM_PERCENTAGE, "PM %")
        ]
        
        for field, display_name in param_fields:
            val1 = params1.get(field, 0)
            val2 = params2.get(field, 0)
            if val1 != val2:
                if display_name in ["DOC %", "PM %"]:
                    differences.append({"Field": display_name, self.name1: f"{val1:.3%}", self.name2: f"{val2:.3%}"})
                else:
                    differences.append({"Field": display_name, self.name1: str(val1), self.name2: str(val2)})
        
        # Compare structure
        groups1_count = len(self.product_groups1)
        groups2_count = len(self.product_groups2)
        if groups1_count != groups2_count:
            differences.append({"Field": "Product Groups Count", self.name1: groups1_count, self.name2: groups2_count})
        
        # Compare totals
        total_fields = [
            (JsonFields.EQUIPMENT_TOTAL, "Equipment Total"),
            (JsonFields.INSTALLATION_TOTAL, "Installation Total"),
            (JsonFields.GRAND_TOTAL, "Grand Total")
        ]
        
        for field, display_name in total_fields:
            val1 = self.totals1.get(field, 0)
            val2 = self.totals2.get(field, 0)
            diff = abs(val1 - val2)
            if diff > 0.01:  # Threshold for financial differences
                differences.append({"Field": display_name, self.name1: f"€{val1:,.2f}", self.name2: f"€{val2:,.2f}"})
        
        if differences:
            df_diff = pd.DataFrame(differences)
            st.dataframe(df_diff, use_container_width=True)
        else:
            st.success("No significant differences found in project parameters!")
    
    def display_financial_comparison(self):
        """Display comprehensive financial comparison"""
        st.header("💰 PRE Financial Comparison")
        
        # Prepare financial data for both files
        financial_data1 = self._prepare_financial_data(self.totals1, self.name1)
        financial_data2 = self._prepare_financial_data(self.totals2, self.name2)
        
        # Combine data for comparison
        combined_data = []
        categories = ['Equipment', 'Installation', 'DOC Fee', 'PM Fee', 'Warranty Fee']
        
        for cat in categories:
            val1 = financial_data1.get(cat, 0)
            val2 = financial_data2.get(cat, 0)
            combined_data.append({
                'Category': cat,
                self.name1: val1,
                self.name2: val2,
                'Difference': val2 - val1,
                'Difference %': ((val2 - val1) / val1 * 100) if val1 != 0 else 0
            })
        
        df_financial = pd.DataFrame(combined_data)
        
        # Display comparison table
        st.subheader("📊 Financial Breakdown Comparison")
        st.dataframe(df_financial, use_container_width=True)
        
        # Side-by-side charts
        col1, col2 = st.columns(2)
        
        with col1:
            # File 1 pie chart
            fig1 = px.pie(
                values=list(financial_data1.values()),
                names=list(financial_data1.keys()),
                title=f'{self.name1} - Financial Breakdown'
            )
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # File 2 pie chart
            fig2 = px.pie(
                values=list(financial_data2.values()),
                names=list(financial_data2.keys()),
                title=f'{self.name2} - Financial Breakdown'
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Difference visualization
        st.subheader("📈 Financial Differences Analysis")
        
        # Bar chart showing differences
        fig_diff = px.bar(
            df_financial,
            x='Category',
            y='Difference',
            title='Financial Differences (File 2 - File 1)',
            color='Difference',
            color_continuous_scale='RdBu_r'
        )
        fig_diff.update_layout(height=400)
        st.plotly_chart(fig_diff, use_container_width=True)
        
        # Percentage differences
        fig_perc = px.bar(
            df_financial,
            x='Category',
            y='Difference %',
            title='Percentage Differences',
            color='Difference %',
            color_continuous_scale='RdBu_r'
        )
        fig_perc.update_layout(height=400)
        st.plotly_chart(fig_perc, use_container_width=True)
    
    def _prepare_financial_data(self, totals: Dict, name: str) -> Dict[str, float]:
        """Prepare financial data for a single file"""
        return {
            'Equipment': totals.get(JsonFields.EQUIPMENT_TOTAL, 0),
            'Installation': totals.get(JsonFields.INSTALLATION_TOTAL, 0),
            'DOC Fee': totals.get(JsonFields.DOC_FEE, 0),
            'PM Fee': totals.get(JsonFields.PM_FEE, 0),
            'Warranty Fee': totals.get(JsonFields.WARRANTY_FEE, 0)
        }
    
    def display_groups_comparison(self):
        """Display groups comparison analysis"""
        st.header("📦 Product Groups Comparison")
        
        # Prepare groups data for both files
        groups_data1 = self._prepare_groups_data(self.product_groups1, self.name1)
        groups_data2 = self._prepare_groups_data(self.product_groups2, self.name2)
        
        # Find common and unique groups
        groups1_ids = set(g[DisplayFields.GROUP_ID] for g in groups_data1)
        groups2_ids = set(g[DisplayFields.GROUP_ID] for g in groups_data2)
        
        common_groups = groups1_ids.intersection(groups2_ids)
        unique_to_1 = groups1_ids - groups2_ids
        unique_to_2 = groups2_ids - groups1_ids
        
        # Display summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Common Groups", len(common_groups))
        with col2:
            st.metric(f"Only in {self.name1}", len(unique_to_1))
        with col3:
            st.metric(f"Only in {self.name2}", len(unique_to_2))
        
        # Display unique groups
        if unique_to_1:
            st.subheader(f"🔸 Groups only in {self.name1}")
            unique_1_data = [g for g in groups_data1 if g[DisplayFields.GROUP_ID] in unique_to_1]
            st.dataframe(pd.DataFrame(unique_1_data), use_container_width=True)
        
        if unique_to_2:
            st.subheader(f"🔹 Groups only in {self.name2}")
            unique_2_data = [g for g in groups_data2 if g[DisplayFields.GROUP_ID] in unique_to_2]
            st.dataframe(pd.DataFrame(unique_2_data), use_container_width=True)
        
        # Compare common groups
        if common_groups:
            st.subheader("🔄 Common Groups Comparison")
            self._display_common_groups_comparison(groups_data1, groups_data2, common_groups)
    
    def _prepare_groups_data(self, product_groups: List, file_name: str) -> List[Dict]:
        """Prepare groups data for analysis"""
        groups_data = []
        for group in product_groups:
            group_total = sum(cat.get(JsonFields.TOTAL_OFFER, 0) for cat in group.get(JsonFields.CATEGORIES, []))
            total_items = sum(len(cat.get(JsonFields.ITEMS, [])) for cat in group.get(JsonFields.CATEGORIES, []))
            
            groups_data.append({
                DisplayFields.GROUP_ID: group.get(JsonFields.GROUP_ID, 'Unknown'),
                DisplayFields.GROUP_NAME: group.get(JsonFields.GROUP_NAME, 'Unnamed'),
                DisplayFields.CATEGORIES_COUNT: len(group.get(JsonFields.CATEGORIES, [])),
                DisplayFields.TOTAL_ITEMS: total_items,
                DisplayFields.TOTAL_EUR: group_total,
                'File': file_name
            })
        
        return groups_data
    
    def _display_common_groups_comparison(self, groups_data1: List, groups_data2: List, common_groups: set):
        """Display comparison for common groups"""
        comparison_data = []
        
        # Create lookup dictionaries
        groups1_dict = {g[DisplayFields.GROUP_ID]: g for g in groups_data1}
        groups2_dict = {g[DisplayFields.GROUP_ID]: g for g in groups_data2}
        
        for group_id in common_groups:
            g1 = groups1_dict[group_id]
            g2 = groups2_dict[group_id]
            
            comparison_data.append({
                DisplayFields.GROUP_ID: group_id,
                DisplayFields.GROUP_NAME: g1[DisplayFields.GROUP_NAME],
                f'{self.name1} - Categories': g1[DisplayFields.CATEGORIES_COUNT],
                f'{self.name2} - Categories': g2[DisplayFields.CATEGORIES_COUNT],
                f'{self.name1} - Items': g1[DisplayFields.TOTAL_ITEMS],
                f'{self.name2} - Items': g2[DisplayFields.TOTAL_ITEMS],
                f'{self.name1} - Total (€)': g1[DisplayFields.TOTAL_EUR],
                f'{self.name2} - Total (€)': g2[DisplayFields.TOTAL_EUR],
                'Value Difference (€)': g2[DisplayFields.TOTAL_EUR] - g1[DisplayFields.TOTAL_EUR]
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True)
        
        # Visualization of differences
        if len(comparison_data) > 0:
            fig = px.bar(
                df_comparison,
                x=DisplayFields.GROUP_ID,
                y='Value Difference (€)',
                title='Group Value Differences (File 2 - File 1)',
                color='Value Difference (€)',
                color_continuous_scale='RdBu_r'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    def display_categories_comparison(self):
        """Display categories comparison analysis"""
        st.header("📂 Categories Comparison")
        
        # Prepare categories data
        categories_data1 = self._prepare_categories_data(self.product_groups1, self.name1)
        categories_data2 = self._prepare_categories_data(self.product_groups2, self.name2)
        
        # Find common and unique categories
        cats1_ids = set((c[DisplayFields.GROUP_ID], c[DisplayFields.CATEGORY_ID]) for c in categories_data1)
        cats2_ids = set((c[DisplayFields.GROUP_ID], c[DisplayFields.CATEGORY_ID]) for c in categories_data2)
        
        common_cats = cats1_ids.intersection(cats2_ids)
        unique_to_1 = cats1_ids - cats2_ids
        unique_to_2 = cats2_ids - cats1_ids
        
        # Display summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Common Categories", len(common_cats))
        with col2:
            st.metric(f"Only in {self.name1}", len(unique_to_1))
        with col3:
            st.metric(f"Only in {self.name2}", len(unique_to_2))
        
        # Show differences if any
        if unique_to_1 or unique_to_2:
            with st.expander("📋 View Unique Categories", expanded=False):
                if unique_to_1:
                    st.subheader(f"Categories only in {self.name1}")
                    unique_1_data = [c for c in categories_data1 if (c[DisplayFields.GROUP_ID], c[DisplayFields.CATEGORY_ID]) in unique_to_1]
                    st.dataframe(pd.DataFrame(unique_1_data), use_container_width=True)
                
                if unique_to_2:
                    st.subheader(f"Categories only in {self.name2}")
                    unique_2_data = [c for c in categories_data2 if (c[DisplayFields.GROUP_ID], c[DisplayFields.CATEGORY_ID]) in unique_to_2]
                    st.dataframe(pd.DataFrame(unique_2_data), use_container_width=True)
        
        # Compare common categories
        if common_cats:
            st.subheader("🔄 Common Categories Value Comparison")
            self._display_common_categories_comparison(categories_data1, categories_data2, common_cats)
    
    def _prepare_categories_data(self, product_groups: List, file_name: str) -> List[Dict]:
        """Prepare categories data for analysis"""
        categories_data = []
        for group in product_groups:
            for category in group.get(JsonFields.CATEGORIES, []):
                cat_total = category.get(JsonFields.TOTAL_OFFER, 0)
                categories_data.append({
                    DisplayFields.GROUP_ID: group.get(JsonFields.GROUP_ID, 'Unknown'),
                    DisplayFields.CATEGORY_ID: category.get(JsonFields.CATEGORY_ID, 'Unknown'),
                    DisplayFields.CATEGORY_NAME: category.get(JsonFields.CATEGORY_NAME, 'Unnamed'),
                    DisplayFields.ITEMS_COUNT: len(category.get(JsonFields.ITEMS, [])),
                    DisplayFields.TOTAL_EUR: cat_total,
                    'File': file_name
                })
        
        return categories_data
    
    def _display_common_categories_comparison(self, categories_data1: List, categories_data2: List, common_cats: set):
        """Display comparison for common categories"""
        comparison_data = []
        
        # Create lookup dictionaries
        cats1_dict = {(c[DisplayFields.GROUP_ID], c[DisplayFields.CATEGORY_ID]): c for c in categories_data1}
        cats2_dict = {(c[DisplayFields.GROUP_ID], c[DisplayFields.CATEGORY_ID]): c for c in categories_data2}
        
        for group_id, cat_id in common_cats:
            c1 = cats1_dict[(group_id, cat_id)]
            c2 = cats2_dict[(group_id, cat_id)]
            
            comparison_data.append({
                DisplayFields.GROUP_ID: group_id,
                DisplayFields.CATEGORY_ID: cat_id,
                DisplayFields.CATEGORY_NAME: c1[DisplayFields.CATEGORY_NAME],
                f'{self.name1} - Items': c1[DisplayFields.ITEMS_COUNT],
                f'{self.name2} - Items': c2[DisplayFields.ITEMS_COUNT],
                f'{self.name1} - Total (€)': c1[DisplayFields.TOTAL_EUR],
                f'{self.name2} - Total (€)': c2[DisplayFields.TOTAL_EUR],
                'Value Difference (€)': c2[DisplayFields.TOTAL_EUR] - c1[DisplayFields.TOTAL_EUR]
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        
        # Filter significant differences
        threshold = st.slider("Minimum value difference (€) to show", 0, 10000, 100)
        df_filtered = df_comparison[abs(df_comparison['Value Difference (€)']) >= threshold]
        
        if not df_filtered.empty:
            st.dataframe(df_filtered, use_container_width=True)
            
            # Top differences chart
            top_diffs = df_filtered.nlargest(10, 'Value Difference (€)', keep='all')
            if len(top_diffs) > 0:
                fig = px.bar(
                    top_diffs,
                    x='Value Difference (€)',
                    y=DisplayFields.CATEGORY_ID,
                    title='Top Category Value Differences',
                    orientation='h',
                    color='Value Difference (€)',
                    color_continuous_scale='RdBu_r'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No categories with differences >= €{threshold}")
    
    def display_items_comparison(self):
        """Display items comparison analysis"""
        st.header("🔧 Items Comparison")
        
        # This is a simplified items comparison - in a real implementation
        # you might want to compare items by code across categories
        st.info("Items comparison shows high-level statistics. Detailed item-by-item comparison can be implemented for specific use cases.")
        
        # Get item counts and value statistics
        items_stats1 = self._get_items_statistics(self.product_groups1, self.name1)
        items_stats2 = self._get_items_statistics(self.product_groups2, self.name2)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📊 {self.name1} Items Statistics")
            st.metric("Total Items", items_stats1['total_items'])
            st.metric("Total Value", f"€{items_stats1['total_value']:,.2f}")
            st.metric("Average Item Value", f"€{items_stats1['avg_item_value']:,.2f}")
            st.metric("Max Item Value", f"€{items_stats1['max_item_value']:,.2f}")
        
        with col2:
            st.subheader(f"📊 {self.name2} Items Statistics")
            st.metric("Total Items", items_stats2['total_items'])
            st.metric("Total Value", f"€{items_stats2['total_value']:,.2f}")
            st.metric("Average Item Value", f"€{items_stats2['avg_item_value']:,.2f}")
            st.metric("Max Item Value", f"€{items_stats2['max_item_value']:,.2f}")
        
        # Comparison summary
        st.subheader("📈 Items Comparison Summary")
        comparison_stats = {
            'Metric': ['Total Items', 'Total Value (€)', 'Average Item Value (€)', 'Max Item Value (€)'],
            self.name1: [
                items_stats1['total_items'],
                items_stats1['total_value'],
                items_stats1['avg_item_value'],
                items_stats1['max_item_value']
            ],
            self.name2: [
                items_stats2['total_items'],
                items_stats2['total_value'],
                items_stats2['avg_item_value'],
                items_stats2['max_item_value']
            ]
        }
        
        df_stats = pd.DataFrame(comparison_stats)
        df_stats['Difference'] = df_stats[self.name2] - df_stats[self.name1]
        
        st.dataframe(df_stats, use_container_width=True)
    
    def _get_items_statistics(self, product_groups: List, file_name: str) -> Dict:
        """Get items statistics for a file"""
        all_items = []
        
        for group in product_groups:
            for category in group.get(JsonFields.CATEGORIES, []):
                for item in category.get(JsonFields.ITEMS, []):
                    item_value = item.get(JsonFields.PRICELIST_TOTAL_PRICE, 0)
                    if item_value > 0:
                        all_items.append(item_value)
        
        if all_items:
            return {
                'total_items': len(all_items),
                'total_value': sum(all_items),
                'avg_item_value': np.mean(all_items),
                'max_item_value': max(all_items)
            }
        else:
            return {
                'total_items': 0,
                'total_value': 0,
                'avg_item_value': 0,
                'max_item_value': 0
            }
    
    def display_summary_report(self):
        """Display comprehensive comparison summary report"""
        st.header("📄 PRE Comparison Summary Report")
        
        # Executive Summary
        st.subheader("📝 Executive Summary")
        
        # Financial summary
        total1 = self.totals1.get(JsonFields.GRAND_TOTAL, 0)
        total2 = self.totals2.get(JsonFields.GRAND_TOTAL, 0)
        diff_amount = total2 - total1
        diff_percent = (diff_amount / total1 * 100) if total1 != 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"{self.name1} Total", f"€{total1:,.2f}")
        with col2:
            st.metric(f"{self.name2} Total", f"€{total2:,.2f}")
        with col3:
            st.metric("Difference", f"€{diff_amount:,.2f}", f"{diff_percent:.1f}%")
        
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
        
        # Key insights
        st.subheader("💡 Key Insights")
        insights = []
        
        if abs(diff_percent) > 5:
            insights.append(f"Significant total value difference: {diff_percent:.1f}%")
        
        if groups1_count != groups2_count:
            insights.append(f"Different number of product groups: {groups1_count} vs {groups2_count}")
        
        if abs(items1_count - items2_count) > 10:
            insights.append(f"Significant difference in item count: {items1_count} vs {items2_count}")
        
        # Check parameter differences
        params1 = self.project1.get(JsonFields.PARAMETERS, {})
        params2 = self.project2.get(JsonFields.PARAMETERS, {})
        
        if params1.get(JsonFields.CURRENCY) != params2.get(JsonFields.CURRENCY):
            insights.append("Different currencies used")
        
        if abs(params1.get(JsonFields.DOC_PERCENTAGE, 0) - params2.get(JsonFields.DOC_PERCENTAGE, 0)) > 0.001:
            insights.append("Different DOC percentages")
        
        if insights:
            for insight in insights:
                st.write(f"• {insight}")
        else:
            st.success("Files are structurally similar with minimal differences!")
        
        # Recommendations
        st.subheader("📋 Recommendations")
        if abs(diff_percent) > 10:
            st.warning("Large financial difference detected. Review pricing and quantities carefully.")
        elif abs(diff_percent) > 5:
            st.info("Moderate financial difference. Consider reviewing major line items.")
        else:
            st.success("Financial values are relatively similar.")
        
        if groups1_count != groups2_count or abs(items1_count - items2_count) > 10:
            st.info("Structural differences found. Review scope changes between versions.") 
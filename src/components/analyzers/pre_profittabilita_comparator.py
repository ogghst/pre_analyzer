"""
PRE vs Analisi Profittabilita Cross-Comparator
Compare PRE quotation files with Analisi Profittabilita elaborations to validate data consistency
and analyze impact of changes on WBE structure and project profitability
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional, Tuple, Set
import numpy as np
from dataclasses import dataclass
from enum import Enum

# Import field constants
from ..field_constants import JsonFields, DisplayFields


class ComparisonResult(Enum):
    """Enumeration for comparison result types"""
    MATCH = "match"
    DIFFERENCE = "difference"
    MISSING_IN_PRE = "missing_in_pre"
    MISSING_IN_PROFITTABILITA = "missing_in_profittabilita"
    VALUE_MISMATCH = "value_mismatch"


@dataclass
class ItemComparisonResult:
    """Data class to store item comparison results"""
    pre_item: Optional[Dict[str, Any]]
    prof_item: Optional[Dict[str, Any]]
    result_type: ComparisonResult
    differences: List[str]
    code: str
    description: str
    wbe: Optional[str] = None


@dataclass
class WBEImpactAnalysis:
    """Data class to store WBE impact analysis"""
    wbe_id: str
    total_listino_change: float
    total_cost_change: float
    margin_change: float
    margin_percentage_change: float
    items_affected: int
    items_added: int
    items_removed: int
    items_modified: int


class PreProfittabilitaComparator:
    """
    Cross-comparator for PRE files and Analisi Profittabilita files
    
    This comparator performs comprehensive analysis to:
    1. Validate that all PRE information is correctly transferred to Profittabilita
    2. Analyze the impact of PRE changes on existing Profittabilita structure
    3. Show how WBE structure will be affected by PRE file changes
    4. Provide detailed pricelist and project structure comparison
    """
    
    def __init__(self, pre_data: Dict[str, Any], prof_data: Dict[str, Any], 
                 pre_name: str = "PRE File", prof_name: str = "Analisi Profittabilita"):
        """
        Initialize the cross-comparator with PRE and Profittabilita datasets
        
        Args:
            pre_data: Parsed PRE file data
            prof_data: Parsed Analisi Profittabilita file data
            pre_name: Display name for PRE file
            prof_name: Display name for Profittabilita file
        """
        self.pre_data = pre_data
        self.prof_data = prof_data
        self.pre_name = pre_name
        self.prof_name = prof_name
        
        # Extract key components
        self._extract_components()
        
        # Perform analysis
        self._analyze_data_consistency()
        self._analyze_wbe_impact()
        self._analyze_pricelist_changes()
    
    def _extract_components(self):
        """Extract key components from both datasets for comparison"""
        # PRE file components
        self.pre_project = self.pre_data.get(JsonFields.PROJECT, {})
        self.pre_product_groups = self.pre_data.get(JsonFields.PRODUCT_GROUPS, [])
        self.pre_totals = self.pre_data.get(JsonFields.TOTALS, {})
        
        # Profittabilita components  
        self.prof_project = self.prof_data.get(JsonFields.PROJECT, {})
        self.prof_product_groups = self.prof_data.get(JsonFields.PRODUCT_GROUPS, [])
        self.prof_totals = self.prof_data.get(JsonFields.TOTALS, {})
        
        # Create item mappings for efficient lookup
        self.pre_items_map = self._create_items_map(self.pre_product_groups)
        self.prof_items_map = self._create_items_map(self.prof_product_groups)
        
        # Create WBE mapping from profittabilita
        self.wbe_map = self._create_wbe_map(self.prof_product_groups)
    
    def _create_items_map(self, product_groups: List[Dict]) -> Dict[str, Dict]:
        """Create a mapping of item codes to item data for efficient lookup"""
        items_map = {}
        
        for group in product_groups:
            for category in group.get(JsonFields.CATEGORIES, []):
                for item in category.get(JsonFields.ITEMS, []):
                    code = item.get(JsonFields.CODE, "").strip()
                    if code:
                        items_map[code] = {
                            'item_data': item,
                            'group_id': group.get(JsonFields.GROUP_ID, ""),
                            'group_name': group.get(JsonFields.GROUP_NAME, ""),
                            'category_id': category.get(JsonFields.CATEGORY_ID, ""),
                            'category_name': category.get(JsonFields.CATEGORY_NAME, ""),
                            'wbe': category.get(JsonFields.WBE, "")
                        }
        
        return items_map
    
    def _create_wbe_map(self, product_groups: List[Dict]) -> Dict[str, Dict]:
        """Create a mapping of WBE codes to their associated data"""
        wbe_map = {}
        
        for group in product_groups:
            for category in group.get(JsonFields.CATEGORIES, []):
                wbe = category.get(JsonFields.WBE, "").strip()
                if wbe:
                    if wbe not in wbe_map:
                        wbe_map[wbe] = {
                            'categories': [],
                            'items': [],
                            'total_listino': 0,
                            'total_cost': 0,
                            'items_count': 0
                        }
                    
                    wbe_map[wbe]['categories'].append(category)
                    items = category.get(JsonFields.ITEMS, [])
                    wbe_map[wbe]['items'].extend(items)
                    wbe_map[wbe]['items_count'] += len(items)
                    
                    # Aggregate financial data
                    for item in items:
                        listino_total = self._safe_float(item.get(JsonFields.PRICELIST_TOTAL, 0))
                        cost_total = self._safe_float(item.get(JsonFields.TOTAL_COST, 0))
                        wbe_map[wbe]['total_listino'] += listino_total
                        wbe_map[wbe]['total_cost'] += cost_total
        
        return wbe_map
    
    def _analyze_data_consistency(self):
        """Analyze consistency between PRE and Profittabilita data"""
        self.item_comparisons = []
        
        # Get all unique item codes from both datasets
        all_codes = set(self.pre_items_map.keys()) | set(self.prof_items_map.keys())
        
        for code in all_codes:
            pre_item_data = self.pre_items_map.get(code)
            prof_item_data = self.prof_items_map.get(code)
            
            differences = []
            result_type = ComparisonResult.MATCH
            
            if pre_item_data is None:
                result_type = ComparisonResult.MISSING_IN_PRE
                description = prof_item_data['item_data'].get(JsonFields.DESCRIPTION, 'N/A')
                wbe = prof_item_data.get('wbe')
            elif prof_item_data is None:
                result_type = ComparisonResult.MISSING_IN_PROFITTABILITA
                description = pre_item_data['item_data'].get(JsonFields.DESCRIPTION, 'N/A')
                wbe = None
            else:
                # Compare item details
                pre_item = pre_item_data['item_data']
                prof_item = prof_item_data['item_data']
                description = pre_item.get(JsonFields.DESCRIPTION, 'N/A')
                wbe = prof_item_data.get('wbe')
                
                # Check for differences in key fields
                differences = self._compare_item_fields(pre_item, prof_item)
                if differences:
                    result_type = ComparisonResult.VALUE_MISMATCH
            
            comparison = ItemComparisonResult(
                pre_item=pre_item_data,
                prof_item=prof_item_data,
                result_type=result_type,
                differences=differences,
                code=code,
                description=description,
                wbe=wbe
            )
            
            self.item_comparisons.append(comparison)
    
    def _compare_item_fields(self, pre_item: Dict, prof_item: Dict) -> List[str]:
        """Compare specific fields between PRE and Profittabilita items"""
        differences = []
        
        # Fields to compare (mapping PRE field -> Prof field)
        field_mappings = {
            JsonFields.DESCRIPTION: JsonFields.DESCRIPTION,
            JsonFields.QUANTITY: JsonFields.QTY,
            JsonFields.PRICELIST_UNIT_PRICE: JsonFields.PRICELIST_UNIT_PRICE,
            JsonFields.PRICELIST_TOTAL_PRICE: JsonFields.PRICELIST_TOTAL,
        }
        
        for pre_field, prof_field in field_mappings.items():
            pre_value = pre_item.get(pre_field, "")
            prof_value = prof_item.get(prof_field, "")
            
            # Handle numeric comparisons
            if pre_field in [JsonFields.QUANTITY, JsonFields.PRICELIST_UNIT_PRICE, JsonFields.PRICELIST_TOTAL_PRICE]:
                pre_num = self._safe_float(pre_value)
                prof_num = self._safe_float(prof_value)
                
                if abs(pre_num - prof_num) > 0.01:  # Allow for small rounding differences
                    differences.append(f"{pre_field}: PRE={pre_num:.2f}, Prof={prof_num:.2f}")
            else:
                # String comparison
                if str(pre_value).strip() != str(prof_value).strip():
                    differences.append(f"{pre_field}: PRE='{pre_value}', Prof='{prof_value}'")
        
        return differences
    
    def _analyze_wbe_impact(self):
        """Analyze the impact on WBE structure from PRE changes"""
        self.wbe_impacts = []
        
        for wbe_id, wbe_data in self.wbe_map.items():
            impact = WBEImpactAnalysis(
                wbe_id=wbe_id,
                total_listino_change=0,
                total_cost_change=0,
                margin_change=0,
                margin_percentage_change=0,
                items_affected=0,
                items_added=0,
                items_removed=0,
                items_modified=0
            )
            
            # Analyze items in this WBE
            wbe_item_codes = set()
            current_listino = 0
            current_cost = 0
            
            for item in wbe_data['items']:
                code = item.get(JsonFields.CODE, "").strip()
                if code:
                    wbe_item_codes.add(code)
                    current_listino += self._safe_float(item.get(JsonFields.PRICELIST_TOTAL, 0))
                    current_cost += self._safe_float(item.get(JsonFields.TOTAL_COST, 0))
            
            # Calculate new totals based on PRE data
            new_listino = 0
            new_cost = 0
            
            for code in wbe_item_codes:
                if code in self.pre_items_map:
                    pre_item = self.pre_items_map[code]['item_data']
                    new_listino += self._safe_float(pre_item.get(JsonFields.PRICELIST_TOTAL_PRICE, 0))
                    # For cost, use current cost if not available in PRE
                    if code in self.prof_items_map:
                        prof_item = self.prof_items_map[code]['item_data']
                        new_cost += self._safe_float(prof_item.get(JsonFields.TOTAL_COST, 0))
                    impact.items_affected += 1
                else:
                    impact.items_removed += 1
            
            # Check for new items in PRE that might affect this WBE
            for comparison in self.item_comparisons:
                if (comparison.result_type == ComparisonResult.MISSING_IN_PROFITTABILITA and 
                    comparison.wbe == wbe_id):
                    impact.items_added += 1
                    if comparison.pre_item:
                        pre_item = comparison.pre_item['item_data']
                        new_listino += self._safe_float(pre_item.get(JsonFields.PRICELIST_TOTAL_PRICE, 0))
                elif (comparison.result_type == ComparisonResult.VALUE_MISMATCH and 
                      comparison.wbe == wbe_id):
                    impact.items_modified += 1
            
            # Calculate changes
            impact.total_listino_change = new_listino - current_listino
            impact.total_cost_change = new_cost - current_cost
            impact.margin_change = impact.total_listino_change - impact.total_cost_change
            
            if current_listino > 0:
                current_margin_perc = ((current_listino - current_cost) / current_listino) * 100
                new_margin_perc = ((new_listino - new_cost) / new_listino) * 100 if new_listino > 0 else 0
                impact.margin_percentage_change = new_margin_perc - current_margin_perc
            
            self.wbe_impacts.append(impact)
    
    def _analyze_pricelist_changes(self):
        """Analyze overall pricelist and project structure changes"""
        self.pricelist_analysis = {
            'total_items_pre': len(self.pre_items_map),
            'total_items_prof': len(self.prof_items_map),
            'items_missing_in_prof': len([c for c in self.item_comparisons if c.result_type == ComparisonResult.MISSING_IN_PROFITTABILITA]),
            'items_missing_in_pre': len([c for c in self.item_comparisons if c.result_type == ComparisonResult.MISSING_IN_PRE]),
            'items_with_differences': len([c for c in self.item_comparisons if c.result_type == ComparisonResult.VALUE_MISMATCH]),
            'items_matching': len([c for c in self.item_comparisons if c.result_type == ComparisonResult.MATCH]),
        }
        
        # Calculate financial impact
        pre_total_listino = self.pre_totals.get(JsonFields.GRAND_TOTAL, 0)
        prof_total_listino = self.prof_totals.get(JsonFields.TOTAL_LISTINO, 0)
        
        self.pricelist_analysis.update({
            'pre_total_listino': pre_total_listino,
            'prof_total_listino': prof_total_listino,
            'listino_difference': pre_total_listino - prof_total_listino,
            'listino_difference_percentage': ((pre_total_listino - prof_total_listino) / prof_total_listino * 100) if prof_total_listino > 0 else 0
        })
    
    def get_comparison_views(self) -> List[str]:
        """Return list of available comparison views"""
        return [
            "Executive Summary",
            "Data Consistency Check",
            "WBE Impact Analysis", 
            "Pricelist Comparison",
            "Project Structure Analysis",
            "Missing Items Analysis",
            "Financial Impact Assessment",
            "Detailed Item Comparison"
        ]
    
    def display_executive_summary(self):
        """Display executive summary of the comparison"""
        st.header("📊 PRE vs Analisi Profittabilita - Executive Summary")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Data Consistency", 
                f"{self.pricelist_analysis['items_matching']}/{len(self.item_comparisons)}",
                f"{(self.pricelist_analysis['items_matching']/len(self.item_comparisons)*100):.1f}% match"
            )
        
        with col2:
            st.metric(
                "Items Missing in Prof", 
                self.pricelist_analysis['items_missing_in_prof'],
                "Items to add"
            )
        
        with col3:
            st.metric(
                "Items with Differences", 
                self.pricelist_analysis['items_with_differences'],
                "Items to review"
            )
        
        with col4:
            wbe_count = len([w for w in self.wbe_impacts if w.total_listino_change != 0])
            st.metric(
                "WBEs Affected", 
                wbe_count,
                f"out of {len(self.wbe_impacts)} total"
            )
        
        # Financial impact summary
        st.subheader("💰 Financial Impact Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                f"{self.pre_name} Total", 
                f"€{self.pricelist_analysis['pre_total_listino']:,.2f}"
            )
        
        with col2:
            st.metric(
                f"{self.prof_name} Total", 
                f"€{self.pricelist_analysis['prof_total_listino']:,.2f}"
            )
        
        with col3:
            diff = self.pricelist_analysis['listino_difference']
            diff_perc = self.pricelist_analysis['listino_difference_percentage']
            st.metric(
                "Difference", 
                f"€{diff:,.2f}",
                f"{diff_perc:+.2f}%"
            )
        
        # Recommendations
        st.subheader("🎯 Key Recommendations")
        
        recommendations = []
        
        if self.pricelist_analysis['items_missing_in_prof'] > 0:
            recommendations.append(f"• Add {self.pricelist_analysis['items_missing_in_prof']} missing items to Analisi Profittabilita")
        
        if self.pricelist_analysis['items_with_differences'] > 0:
            recommendations.append(f"• Review and reconcile {self.pricelist_analysis['items_with_differences']} items with value differences")
        
        if abs(diff_perc) > 5:
            recommendations.append(f"• Investigate significant financial difference of {diff_perc:.1f}%")
        
        high_impact_wbes = [w for w in self.wbe_impacts if abs(w.margin_percentage_change) > 10]
        if high_impact_wbes:
            recommendations.append(f"• Review {len(high_impact_wbes)} WBEs with significant margin impact (>10%)")
        
        if not recommendations:
            st.success("✅ No critical issues identified. Data appears to be well-aligned.")
        else:
            for rec in recommendations:
                st.warning(rec)
    
    def display_data_consistency_check(self):
        """Display detailed data consistency analysis"""
        st.header("🔍 Data Consistency Check")
        
        # Summary statistics
        st.subheader("📈 Consistency Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart of comparison results
            result_counts = {}
            for comparison in self.item_comparisons:
                result_type = comparison.result_type.value
                result_counts[result_type] = result_counts.get(result_type, 0) + 1
            
            if result_counts:
                fig_pie = px.pie(
                    values=list(result_counts.values()),
                    names=list(result_counts.keys()),
                    title="Item Comparison Results",
                    color_discrete_map={
                        'match': '#28a745',
                        'difference': '#ffc107', 
                        'missing_in_pre': '#dc3545',
                        'missing_in_profittabilita': '#fd7e14',
                        'value_mismatch': '#6f42c1'
                    }
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Consistency metrics table
            consistency_data = {
                'Status': ['Perfect Match', 'Value Differences', 'Missing in Prof', 'Missing in PRE', 'Total Items'],
                'Count': [
                    self.pricelist_analysis['items_matching'],
                    self.pricelist_analysis['items_with_differences'], 
                    self.pricelist_analysis['items_missing_in_prof'],
                    self.pricelist_analysis['items_missing_in_pre'],
                    len(self.item_comparisons)
                ],
                'Percentage': [
                    (self.pricelist_analysis['items_matching']/len(self.item_comparisons)*100),
                    (self.pricelist_analysis['items_with_differences']/len(self.item_comparisons)*100),
                    (self.pricelist_analysis['items_missing_in_prof']/len(self.item_comparisons)*100),
                    (self.pricelist_analysis['items_missing_in_pre']/len(self.item_comparisons)*100),
                    100.0
                ]
            }
            
            df_consistency = pd.DataFrame(consistency_data)
            df_consistency['Percentage'] = df_consistency['Percentage'].round(1)
            st.dataframe(df_consistency, use_container_width=True, hide_index=True)
        
        # Detailed issues table
        st.subheader("🚨 Items Requiring Attention")
        
        # Filter for items with issues
        issue_comparisons = [c for c in self.item_comparisons 
                           if c.result_type != ComparisonResult.MATCH]
        
        if issue_comparisons:
            issue_data = []
            for comp in issue_comparisons:
                issue_data.append({
                    'Code': comp.code,
                    'Description': comp.description[:50] + "..." if len(comp.description) > 50 else comp.description,
                    'Issue Type': comp.result_type.value.replace('_', ' ').title(),
                    'WBE': comp.wbe or 'N/A',
                    'Differences': '; '.join(comp.differences) if comp.differences else 'N/A'
                })
            
            df_issues = pd.DataFrame(issue_data)
            st.dataframe(df_issues, use_container_width=True, hide_index=True)
            
            # Export functionality
            if st.button("📥 Export Issues to CSV"):
                csv = df_issues.to_csv(index=False)
                st.download_button(
                    label="Download Issues CSV",
                    data=csv,
                    file_name="pre_profittabilita_issues.csv",
                    mime="text/csv"
                )
        else:
            st.success("✅ No consistency issues found!")
    
    def display_wbe_impact_analysis(self):
        """Display WBE impact analysis"""
        st.header("🏗️ WBE Impact Analysis")
        
        st.markdown("""
        This analysis shows how the PRE file changes will impact each Work Breakdown Element (WBE) 
        in the Analisi Profittabilita structure.
        """)
        
        # WBE impact summary
        wbe_data = []
        for impact in self.wbe_impacts:
            wbe_data.append({
                'WBE': impact.wbe_id,
                'Items Affected': impact.items_affected,
                'Items Added': impact.items_added,
                'Items Removed': impact.items_removed,
                'Items Modified': impact.items_modified,
                'Listino Change (€)': impact.total_listino_change,
                'Cost Change (€)': impact.total_cost_change,
                'Margin Change (€)': impact.margin_change,
                'Margin % Change': impact.margin_percentage_change
            })
        
        df_wbe = pd.DataFrame(wbe_data)
        
        # Filter for WBEs with changes
        df_wbe_changes = df_wbe[
            (df_wbe['Items Added'] > 0) | 
            (df_wbe['Items Removed'] > 0) | 
            (df_wbe['Items Modified'] > 0) |
            (abs(df_wbe['Listino Change (€)']) > 0.01)
        ]
        
        if not df_wbe_changes.empty:
            st.subheader("🎯 WBEs with Changes")
            
            # Format the dataframe for better display
            df_display = df_wbe_changes.copy()
            df_display['Listino Change (€)'] = df_display['Listino Change (€)'].apply(lambda x: f"€{x:,.2f}")
            df_display['Cost Change (€)'] = df_display['Cost Change (€)'].apply(lambda x: f"€{x:,.2f}")
            df_display['Margin Change (€)'] = df_display['Margin Change (€)'].apply(lambda x: f"€{x:,.2f}")
            df_display['Margin % Change'] = df_display['Margin % Change'].apply(lambda x: f"{x:+.2f}%")
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Visual analysis
            col1, col2 = st.columns(2)
            
            with col1:
                # WBE impact bar chart
                fig_impact = px.bar(
                    df_wbe_changes,
                    x='WBE',
                    y='Listino Change (€)',
                    title='Listino Impact by WBE',
                    color='Listino Change (€)',
                    color_continuous_scale='RdYlGn_r'
                )
                fig_impact.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_impact, use_container_width=True)
            
            with col2:
                # Margin impact scatter plot
                fig_margin = px.scatter(
                    df_wbe_changes,
                    x='Margin Change (€)',
                    y='Margin % Change',
                    size='Items Affected',
                    hover_data=['WBE', 'Items Added', 'Items Removed'],
                    title='Margin Impact Analysis',
                    color='Items Affected'
                )
                st.plotly_chart(fig_margin, use_container_width=True)
            
            # High-impact WBEs alert
            high_impact = df_wbe_changes[abs(df_wbe_changes['Margin % Change']) > 10]
            if not high_impact.empty:
                st.warning(f"⚠️ {len(high_impact)} WBE(s) have margin changes >10%: {', '.join(high_impact['WBE'].tolist())}")
        
        else:
            st.info("ℹ️ No significant WBE changes detected.")
    
    def display_pricelist_comparison(self):
        """Display detailed pricelist comparison"""
        st.header("💰 Pricelist Comparison")
        
        # Overall comparison metrics
        st.subheader("📊 Overall Financial Comparison")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                f"{self.pre_name} Total",
                f"€{self.pricelist_analysis['pre_total_listino']:,.2f}",
                f"{self.pricelist_analysis['total_items_pre']} items"
            )
        
        with col2:
            st.metric(
                f"{self.prof_name} Total",
                f"€{self.pricelist_analysis['prof_total_listino']:,.2f}",
                f"{self.pricelist_analysis['total_items_prof']} items"
            )
        
        with col3:
            diff = self.pricelist_analysis['listino_difference']
            diff_perc = self.pricelist_analysis['listino_difference_percentage']
            st.metric(
                "Difference",
                f"€{diff:,.2f}",
                f"{diff_perc:+.2f}%"
            )
        
        # Price comparison by group/category
        st.subheader("📈 Price Analysis by Product Group")
        
        # Aggregate data by product groups
        pre_groups_data = self._aggregate_by_groups(self.pre_product_groups, "PRE")
        prof_groups_data = self._aggregate_by_groups(self.prof_product_groups, "Prof")
        
        # Combine data for comparison
        all_group_ids = set(pre_groups_data.keys()) | set(prof_groups_data.keys())
        
        comparison_data = []
        for group_id in all_group_ids:
            pre_data = pre_groups_data.get(group_id, {'total': 0, 'name': 'N/A', 'items': 0})
            prof_data = prof_groups_data.get(group_id, {'total': 0, 'name': 'N/A', 'items': 0})
            
            comparison_data.append({
                'Group ID': group_id,
                'Group Name': pre_data.get('name', prof_data.get('name', 'N/A')),
                f'{self.pre_name} Total (€)': pre_data['total'],
                f'{self.prof_name} Total (€)': prof_data['total'],
                f'{self.pre_name} Items': pre_data['items'],
                f'{self.prof_name} Items': prof_data['items'],
                'Difference (€)': pre_data['total'] - prof_data['total'],
                'Difference %': ((pre_data['total'] - prof_data['total']) / prof_data['total'] * 100) if prof_data['total'] > 0 else 0
            })
        
        df_groups = pd.DataFrame(comparison_data)
        df_groups = df_groups.sort_values('Difference (€)', key=abs, ascending=False)
        
        # Display formatted table
        df_display = df_groups.copy()
        for col in [f'{self.pre_name} Total (€)', f'{self.prof_name} Total (€)', 'Difference (€)']:
            df_display[col] = df_display[col].apply(lambda x: f"€{x:,.2f}")
        df_display['Difference %'] = df_display['Difference %'].apply(lambda x: f"{x:+.2f}%")
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Visual comparison
        col1, col2 = st.columns(2)
        
        with col1:
            # Group totals comparison
            fig_groups = px.bar(
                df_groups,
                x='Group ID',
                y=[f'{self.pre_name} Total (€)', f'{self.prof_name} Total (€)'],
                title='Total Value by Product Group',
                barmode='group'
            )
            fig_groups.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_groups, use_container_width=True)
        
        with col2:
            # Differences visualization
            fig_diff = px.bar(
                df_groups,
                x='Group ID',
                y='Difference (€)',
                title='Value Differences by Group',
                color='Difference (€)',
                color_continuous_scale='RdYlGn'
            )
            fig_diff.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_diff, use_container_width=True)
    
    def display_missing_items_analysis(self):
        """Display analysis of missing items"""
        st.header("🔍 Missing Items Analysis")
        
        # Items missing in Profittabilita
        missing_in_prof = [c for c in self.item_comparisons 
                          if c.result_type == ComparisonResult.MISSING_IN_PROFITTABILITA]
        
        # Items missing in PRE
        missing_in_pre = [c for c in self.item_comparisons 
                         if c.result_type == ComparisonResult.MISSING_IN_PRE]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📋 Items Missing in {self.prof_name}")
            st.metric("Count", len(missing_in_prof))
            
            if missing_in_prof:
                missing_prof_data = []
                total_value = 0
                
                for comp in missing_in_prof:
                    if comp.pre_item:
                        item = comp.pre_item['item_data']
                        value = self._safe_float(item.get(JsonFields.PRICELIST_TOTAL_PRICE, 0))
                        total_value += value
                        
                        missing_prof_data.append({
                            'Code': comp.code,
                            'Description': comp.description[:40] + "..." if len(comp.description) > 40 else comp.description,
                            'Quantity': item.get(JsonFields.QUANTITY, 0),
                            'Unit Price (€)': self._safe_float(item.get(JsonFields.PRICELIST_UNIT_PRICE, 0)),
                            'Total Value (€)': value,
                            'Group': comp.pre_item.get('group_name', 'N/A')
                        })
                
                st.metric("Total Value", f"€{total_value:,.2f}")
                
                df_missing_prof = pd.DataFrame(missing_prof_data)
                
                # Format for display
                df_display = df_missing_prof.copy()
                df_display['Unit Price (€)'] = df_display['Unit Price (€)'].apply(lambda x: f"€{x:,.2f}")
                df_display['Total Value (€)'] = df_display['Total Value (€)'].apply(lambda x: f"€{x:,.2f}")
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # Download CSV
                if st.button("📥 Export Missing Items (Prof)", key="export_missing_prof"):
                    csv = df_missing_prof.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="items_missing_in_profittabilita.csv",
                        mime="text/csv",
                        key="download_missing_prof"
                    )
            else:
                st.success("✅ No items missing!")
        
        with col2:
            st.subheader(f"📋 Items Missing in {self.pre_name}")
            st.metric("Count", len(missing_in_pre))
            
            if missing_in_pre:
                missing_pre_data = []
                total_value = 0
                
                for comp in missing_in_pre:
                    if comp.prof_item:
                        item = comp.prof_item['item_data']
                        value = self._safe_float(item.get(JsonFields.PRICELIST_TOTAL, 0))
                        total_value += value
                        
                        missing_pre_data.append({
                            'Code': comp.code,
                            'Description': comp.description[:40] + "..." if len(comp.description) > 40 else comp.description,
                            'Quantity': item.get(JsonFields.QTY, 0),
                            'Unit Price (€)': self._safe_float(item.get(JsonFields.PRICELIST_UNIT_PRICE, 0)),
                            'Total Value (€)': value,
                            'WBE': comp.wbe or 'N/A'
                        })
                
                st.metric("Total Value", f"€{total_value:,.2f}")
                
                df_missing_pre = pd.DataFrame(missing_pre_data)
                
                # Format for display
                df_display = df_missing_pre.copy()
                df_display['Unit Price (€)'] = df_display['Unit Price (€)'].apply(lambda x: f"€{x:,.2f}")
                df_display['Total Value (€)'] = df_display['Total Value (€)'].apply(lambda x: f"€{x:,.2f}")
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # Download CSV
                if st.button("📥 Export Missing Items (PRE)", key="export_missing_pre"):
                    csv = df_missing_pre.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="items_missing_in_pre.csv",
                        mime="text/csv",
                        key="download_missing_pre"
                    )
            else:
                st.success("✅ No items missing!")
    
    def display_detailed_item_comparison(self):
        """Display detailed item-by-item comparison"""
        st.header("🔍 Detailed Item Comparison")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_type = st.selectbox(
                "Filter by Status",
                ["All", "Matches", "Differences", "Missing in Prof", "Missing in PRE", "Value Mismatches"]
            )
        
        with col2:
            wbe_options = ["All"] + list(self.wbe_map.keys())
            filter_wbe = st.selectbox("Filter by WBE", wbe_options)
        
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                ["Code", "Description", "Value", "Status"]
            )
        
        # Apply filters
        filtered_comparisons = self.item_comparisons.copy()
        
        if filter_type != "All":
            type_mapping = {
                "Matches": ComparisonResult.MATCH,
                "Differences": ComparisonResult.DIFFERENCE,
                "Missing in Prof": ComparisonResult.MISSING_IN_PROFITTABILITA,
                "Missing in PRE": ComparisonResult.MISSING_IN_PRE,
                "Value Mismatches": ComparisonResult.VALUE_MISMATCH
            }
            filtered_comparisons = [c for c in filtered_comparisons 
                                  if c.result_type == type_mapping[filter_type]]
        
        if filter_wbe != "All":
            filtered_comparisons = [c for c in filtered_comparisons 
                                  if c.wbe == filter_wbe]
        
        # Create detailed comparison table
        if filtered_comparisons:
            comparison_data = []
            
            for comp in filtered_comparisons:
                # Get values from both files
                pre_qty = pre_unit_price = pre_total = ""
                prof_qty = prof_unit_price = prof_total = ""
                
                if comp.pre_item:
                    pre_item = comp.pre_item['item_data']
                    pre_qty = str(pre_item.get(JsonFields.QUANTITY, ""))
                    pre_unit_price = f"€{self._safe_float(pre_item.get(JsonFields.PRICELIST_UNIT_PRICE, 0)):,.2f}"
                    pre_total = f"€{self._safe_float(pre_item.get(JsonFields.PRICELIST_TOTAL_PRICE, 0)):,.2f}"
                
                if comp.prof_item:
                    prof_item = comp.prof_item['item_data']
                    prof_qty = str(prof_item.get(JsonFields.QTY, ""))
                    prof_unit_price = f"€{self._safe_float(prof_item.get(JsonFields.PRICELIST_UNIT_PRICE, 0)):,.2f}"
                    prof_total = f"€{self._safe_float(prof_item.get(JsonFields.PRICELIST_TOTAL, 0)):,.2f}"
                
                comparison_data.append({
                    'Code': comp.code,
                    'Description': comp.description[:60] + "..." if len(comp.description) > 60 else comp.description,
                    'Status': comp.result_type.value.replace('_', ' ').title(),
                    'WBE': comp.wbe or 'N/A',
                    f'{self.pre_name} Qty': pre_qty,
                    f'{self.prof_name} Qty': prof_qty,
                    f'{self.pre_name} Unit €': pre_unit_price,
                    f'{self.prof_name} Unit €': prof_unit_price,
                    f'{self.pre_name} Total €': pre_total,
                    f'{self.prof_name} Total €': prof_total,
                    'Differences': '; '.join(comp.differences) if comp.differences else ''
                })
            
            df_comparison = pd.DataFrame(comparison_data)
            
            # Sort data
            if sort_by == "Code":
                df_comparison = df_comparison.sort_values('Code')
            elif sort_by == "Description":
                df_comparison = df_comparison.sort_values('Description')
            elif sort_by == "Status":
                df_comparison = df_comparison.sort_values('Status')
            # For Value sorting, we'd need to extract numeric values
            
            st.dataframe(df_comparison, use_container_width=True, hide_index=True)
            
            # Summary statistics
            st.subheader("📊 Filtered Results Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            status_counts = df_comparison['Status'].value_counts()
            
            with col1:
                st.metric("Total Items", len(df_comparison))
            with col2:
                st.metric("Perfect Matches", status_counts.get('Match', 0))
            with col3:
                st.metric("With Issues", len(df_comparison) - status_counts.get('Match', 0))
            with col4:
                if filter_wbe != "All":
                    wbe_items = len([c for c in filtered_comparisons if c.wbe == filter_wbe])
                    st.metric(f"Items in {filter_wbe}", wbe_items)
                else:
                    unique_wbes = len(set([c.wbe for c in filtered_comparisons if c.wbe]))
                    st.metric("Unique WBEs", unique_wbes)
            
            # Export functionality
            if st.button("📥 Export Filtered Results"):
                csv = df_comparison.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"detailed_comparison_{filter_type.lower().replace(' ', '_')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No items match the selected filters.")
    
    def _aggregate_by_groups(self, product_groups: List[Dict], source: str) -> Dict[str, Dict]:
        """Aggregate financial data by product groups"""
        groups_data = {}
        
        for group in product_groups:
            group_id = group.get(JsonFields.GROUP_ID, "Unknown")
            group_name = group.get(JsonFields.GROUP_NAME, "Unknown")
            
            total_value = 0
            items_count = 0
            
            for category in group.get(JsonFields.CATEGORIES, []):
                for item in category.get(JsonFields.ITEMS, []):
                    if source == "PRE":
                        value = self._safe_float(item.get(JsonFields.PRICELIST_TOTAL_PRICE, 0))
                    else:  # Prof
                        value = self._safe_float(item.get(JsonFields.PRICELIST_TOTAL, 0))
                    
                    total_value += value
                    items_count += 1
            
            groups_data[group_id] = {
                'name': group_name,
                'total': total_value,
                'items': items_count
            }
        
        return groups_data
    
    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float"""
        try:
            if value is None or value == "":
                return default
            return float(value)
        except (ValueError, TypeError):
            return default 
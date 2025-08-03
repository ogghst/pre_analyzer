"""
Unified Comparator for Industrial Equipment Quotations
Compare two IndustrialQuotation objects from unified parser with comprehensive analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional, Tuple, Set
import numpy as np
from dataclasses import dataclass
from enum import Enum

# Import field constants and formatters
from ..field_constants import JsonFields, DisplayFields
from utils.format import safe_format_number, safe_format_currency, safe_format_percentage


class ComparisonResult(Enum):
    """Enumeration for comparison result types"""
    MATCH = "match"
    DIFFERENCE = "difference"
    MISSING_IN_FIRST = "missing_in_first"
    MISSING_IN_SECOND = "missing_in_second"
    VALUE_MISMATCH = "value_mismatch"


@dataclass
class ItemComparisonResult:
    """Data class to store item comparison results"""
    first_item: Optional[Dict[str, Any]]
    second_item: Optional[Dict[str, Any]]
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


class UnifiedComparator:
    """
    Unified comparator for two IndustrialQuotation objects
    
    This comparator performs comprehensive analysis to:
    1. Compare two quotation files parsed by unified parser
    2. Analyze differences in structure, pricing, and costs
    3. Show impact on WBE structure and project profitability
    4. Provide detailed financial and structural comparison
    """
    
    def __init__(self, first_quotation: Any, second_quotation: Any, 
                 first_name: str = "First File", second_name: str = "Second File"):
        """
        Initialize the unified comparator with two quotation objects
        
        Args:
            first_quotation: First IndustrialQuotation object
            second_quotation: Second IndustrialQuotation object
            first_name: Display name for first file
            second_name: Display name for second file
        """
        self.first_quotation = first_quotation
        self.second_quotation = second_quotation
        self.first_name = first_name
        self.second_name = second_name
        
        # Analysis completion flag
        self._analysis_completed = False
        
        # Initialize analysis results as None - will be computed on demand
        self.item_comparisons = None
        self.wbe_impacts = None
        self.pricelist_analysis = None
        self.first_items_map = None
        self.second_items_map = None
        self.wbe_map = None
    
    def is_analysis_completed(self) -> bool:
        """Check if analysis has been completed"""
        return self._analysis_completed
    
    def get_analysis_status(self) -> str:
        """Get the current analysis status"""
        if self._analysis_completed:
            return "✅ Analysis completed (cached)"
        else:
            return "🔄 Analysis pending"
    
    def _ensure_analysis_completed(self):
        """Ensure analysis has been completed, run it if needed"""
        if not self._analysis_completed:
            st.sidebar.info("🔄 Performing unified comparison analysis...")
            # Extract key components
            self._extract_components()
            
            # Perform analysis
            self._analyze_data_consistency()
            self._analyze_wbe_impact()
            self._analyze_pricelist_changes()
            
            # Mark analysis as completed
            self._analysis_completed = True
            st.sidebar.success("✅ Analysis completed successfully")
        else:
            st.sidebar.info("📋 Using cached analysis results")
    
    def get_cached_analysis_results(self) -> Dict[str, Any]:
        """Get cached analysis results to prevent re-computation"""
        self._ensure_analysis_completed()
        return {
            'item_comparisons': self.item_comparisons,
            'wbe_impacts': self.wbe_impacts,
            'pricelist_analysis': self.pricelist_analysis,
            'first_items_map': self.first_items_map,
            'second_items_map': self.second_items_map,
            'wbe_map': self.wbe_map,
            'analysis_completed': self._analysis_completed
        }
    
    def _extract_components(self):
        """Extract key components from both quotation objects for comparison"""
        # First quotation components
        self.first_project = self.first_quotation.project
        self.first_product_groups = self.first_quotation.product_groups
        self.first_totals = self.first_quotation.totals
        
        # Second quotation components  
        self.second_project = self.second_quotation.project
        self.second_product_groups = self.second_quotation.product_groups
        self.second_totals = self.second_quotation.totals
        
        # Create item mappings for efficient lookup
        self.first_items_map = self._create_items_map(self.first_product_groups)
        self.second_items_map = self._create_items_map(self.second_product_groups)
        
        # Create WBE mapping from second quotation
        self.wbe_map = self._create_wbe_map(self.second_product_groups)
    
    def _create_items_map(self, product_groups: List[Any]) -> Dict[str, Dict]:
        """Create a mapping of item codes to item data for efficient lookup"""
        items_map = {}
        
        for group in product_groups:
            for category in group.categories:
                for item in category.items:
                    code = item.code.strip() if item.code else ""
                    if code:
                        items_map[code] = {
                            'item_data': item,
                            'group_id': group.group_id,
                            'group_name': group.group_name,
                            'category_id': category.category_id,
                            'category_name': category.category_name,
                            'wbe': category.wbe
                        }
        
        return items_map
    
    def _create_wbe_map(self, product_groups: List[Any]) -> Dict[str, Dict]:
        """Create a mapping of WBE codes to their associated data"""
        wbe_map = {}
        
        for group in product_groups:
            for category in group.categories:
                wbe = category.wbe.strip() if category.wbe else ""
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
                    wbe_map[wbe]['items'].extend(category.items)
                    wbe_map[wbe]['items_count'] += len(category.items)
                    
                    # Aggregate financial data
                    for item in category.items:
                        listino_total = self._safe_float(item.pricelist_total_price)
                        cost_total = self._safe_float(item.total_cost)
                        wbe_map[wbe]['total_listino'] += listino_total
                        wbe_map[wbe]['total_cost'] += cost_total
        
        return wbe_map
    
    def _analyze_data_consistency(self):
        """Analyze consistency between first and second quotation data"""
        self.item_comparisons = []
        
        # Get all unique item codes from both datasets
        all_codes = set(self.first_items_map.keys()) | set(self.second_items_map.keys())
        
        for code in all_codes:
            first_item_data = self.first_items_map.get(code)
            second_item_data = self.second_items_map.get(code)
            
            differences = []
            result_type = ComparisonResult.MATCH
            
            if first_item_data is None:
                result_type = ComparisonResult.MISSING_IN_FIRST
                description = second_item_data['item_data'].description or 'N/A'
                wbe = second_item_data.get('wbe')
            elif second_item_data is None:
                result_type = ComparisonResult.MISSING_IN_SECOND
                description = first_item_data['item_data'].description or 'N/A'
                wbe = None
            else:
                # Compare item details
                first_item = first_item_data['item_data']
                second_item = second_item_data['item_data']
                description = first_item.description or 'N/A'
                wbe = second_item_data.get('wbe')
                
                # Check for differences in key fields
                differences = self._compare_item_fields(first_item, second_item)
                if differences:
                    result_type = ComparisonResult.VALUE_MISMATCH
            
            comparison = ItemComparisonResult(
                first_item=first_item_data,
                second_item=second_item_data,
                result_type=result_type,
                differences=differences,
                code=code,
                description=description,
                wbe=wbe
            )
            
            self.item_comparisons.append(comparison)
    
    def _compare_item_fields(self, first_item: Any, second_item: Any) -> List[str]:
        """Compare specific fields between first and second items"""
        differences = []
        
        # Fields to compare
        field_mappings = {
            'description': 'description',
            'quantity': 'quantity',
            'pricelist_unit_price': 'pricelist_unit_price',
            'pricelist_total_price': 'pricelist_total_price',
        }
        
        for first_field, second_field in field_mappings.items():
            first_value = getattr(first_item, first_field, "")
            second_value = getattr(second_item, second_field, "")
            
            # Handle numeric comparisons
            if first_field in ['quantity', 'pricelist_unit_price', 'pricelist_total_price']:
                first_num = self._safe_float(first_value)
                second_num = self._safe_float(second_value)
                
                if abs(first_num - second_num) > 0.01:  # Allow for small rounding differences
                    differences.append(f"{first_field}: First={first_num:.2f}, Second={second_num:.2f}")
            else:
                # String comparison
                if str(first_value).strip() != str(second_value).strip():
                    differences.append(f"{first_field}: First='{first_value}', Second='{second_value}'")
        
        return differences
    
    def _analyze_wbe_impact(self):
        """Analyze the impact on WBE structure from first quotation changes"""
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
                code = item.code.strip() if item.code else ""
                if code:
                    wbe_item_codes.add(code)
                    current_listino += self._safe_float(item.pricelist_total_price)
                    current_cost += self._safe_float(item.total_cost)
            
            # Calculate new totals based on first quotation data
            new_listino = 0
            new_cost = 0
            
            for code in wbe_item_codes:
                if code in self.first_items_map:
                    first_item = self.first_items_map[code]['item_data']
                    new_listino += self._safe_float(first_item.pricelist_total_price)
                    # For cost, use current cost if not available in first
                    if code in self.second_items_map:
                        second_item = self.second_items_map[code]['item_data']
                        new_cost += self._safe_float(second_item.total_cost)
                    impact.items_affected += 1
                else:
                    impact.items_removed += 1
            
            # Check for new items in first that might affect this WBE
            for comparison in self.item_comparisons:
                if (comparison.result_type == ComparisonResult.MISSING_IN_SECOND and 
                    comparison.wbe == wbe_id):
                    impact.items_added += 1
                    if comparison.first_item:
                        first_item = comparison.first_item['item_data']
                        new_listino += self._safe_float(first_item.pricelist_total_price)
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
            'total_items_first': len(self.first_items_map),
            'total_items_second': len(self.second_items_map),
            'items_missing_in_second': len([c for c in self.item_comparisons if c.result_type == ComparisonResult.MISSING_IN_SECOND]),
            'items_missing_in_first': len([c for c in self.item_comparisons if c.result_type == ComparisonResult.MISSING_IN_FIRST]),
            'items_with_differences': len([c for c in self.item_comparisons if c.result_type == ComparisonResult.VALUE_MISMATCH]),
            'items_matching': len([c for c in self.item_comparisons if c.result_type == ComparisonResult.MATCH]),
        }
        
        # Calculate financial impact
        first_total_listino = self._safe_float(self.first_totals.total_pricelist)
        second_total_listino = self._safe_float(self.second_totals.total_pricelist)
        
        self.pricelist_analysis.update({
            'first_total_listino': first_total_listino,
            'second_total_listino': second_total_listino,
            'listino_difference': first_total_listino - second_total_listino,
            'listino_difference_percentage': ((first_total_listino - second_total_listino) / second_total_listino * 100) if second_total_listino > 0 else 0
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
        self._ensure_analysis_completed()
        st.header("📊 Unified Quotation Comparison - Executive Summary")
        
        # Show analysis status
        st.info(self.get_analysis_status())
        
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
                "Items Missing in Second", 
                self.pricelist_analysis['items_missing_in_second'],
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
                f"{self.first_name} Total", 
                safe_format_currency(self.pricelist_analysis['first_total_listino'])
            )
        
        with col2:
            st.metric(
                f"{self.second_name} Total", 
                safe_format_currency(self.pricelist_analysis['second_total_listino'])
            )
        
        with col3:
            diff = self.pricelist_analysis['listino_difference']
            diff_perc = self.pricelist_analysis['listino_difference_percentage']
            st.metric(
                "Difference", 
                safe_format_currency(diff),
                f"{diff_perc:+.2f}%"
            )
        
        # Recommendations
        st.subheader("🎯 Key Recommendations")
        
        recommendations = []
        
        if self.pricelist_analysis['items_missing_in_second'] > 0:
            recommendations.append(f"• Add {self.pricelist_analysis['items_missing_in_second']} missing items to {self.second_name}")
        
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
        self._ensure_analysis_completed()
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
                        'missing_in_first': '#dc3545',
                        'missing_in_second': '#fd7e14',
                        'value_mismatch': '#6f42c1'
                    }
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Consistency metrics table
            consistency_data = {
                'Status': ['Perfect Match', 'Value Differences', 'Missing in Second', 'Missing in First', 'Total Items'],
                'Count': [
                    self.pricelist_analysis['items_matching'],
                    self.pricelist_analysis['items_with_differences'], 
                    self.pricelist_analysis['items_missing_in_second'],
                    self.pricelist_analysis['items_missing_in_first'],
                    len(self.item_comparisons)
                ],
                'Percentage': [
                    (self.pricelist_analysis['items_matching']/len(self.item_comparisons)*100),
                    (self.pricelist_analysis['items_with_differences']/len(self.item_comparisons)*100),
                    (self.pricelist_analysis['items_missing_in_second']/len(self.item_comparisons)*100),
                    (self.pricelist_analysis['items_missing_in_first']/len(self.item_comparisons)*100),
                    100.0
                ]
            }
            
            df_consistency = pd.DataFrame(consistency_data)
            df_consistency['Percentage'] = df_consistency['Percentage'].round(1)
            
            # Use NumberColumn for formatting
            st.dataframe(
                df_consistency, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Count": st.column_config.NumberColumn(
                        "Count",
                        help="Number of items",
                        format="%d"
                    ),
                    "Percentage": st.column_config.NumberColumn(
                        "Percentage",
                        help="Percentage of total items",
                        format="%.1f%%"
                    )
                }
            )
        
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
                    file_name="unified_comparison_issues.csv",
                    mime="text/csv"
                )
        else:
            st.success("✅ No consistency issues found!") 
    
    def display_wbe_impact_analysis(self):
        """Display WBE impact analysis"""
        self._ensure_analysis_completed()
        st.header("🏗️ WBE Impact Analysis")
        
        st.markdown("""
        This analysis shows how the first quotation changes will impact each Work Breakdown Element (WBE) 
        in the second quotation structure.
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
            
            # Format the dataframe for better display with NumberColumn
            st.dataframe(
                df_wbe_changes, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Items Affected": st.column_config.NumberColumn(
                        "Items Affected",
                        help="Number of items affected",
                        format="%d"
                    ),
                    "Items Added": st.column_config.NumberColumn(
                        "Items Added",
                        help="Number of items added",
                        format="%d"
                    ),
                    "Items Removed": st.column_config.NumberColumn(
                        "Items Removed",
                        help="Number of items removed",
                        format="%d"
                    ),
                    "Items Modified": st.column_config.NumberColumn(
                        "Items Modified",
                        help="Number of items modified",
                        format="%d"
                    ),
                    "Listino Change (€)": st.column_config.NumberColumn(
                        "Listino Change (€)",
                        help="Change in listino value",
                        format="€%.2f"
                    ),
                    "Cost Change (€)": st.column_config.NumberColumn(
                        "Cost Change (€)",
                        help="Change in cost value",
                        format="€%.2f"
                    ),
                    "Margin Change (€)": st.column_config.NumberColumn(
                        "Margin Change (€)",
                        help="Change in margin value",
                        format="€%.2f"
                    ),
                    "Margin % Change": st.column_config.NumberColumn(
                        "Margin % Change",
                        help="Change in margin percentage",
                        format="%.2f%%"
                    )
                }
            )
            
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
        self._ensure_analysis_completed()
        st.header("💰 Pricelist Comparison")
        
        # Overall comparison metrics
        st.subheader("📊 Overall Financial Comparison")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                f"{self.first_name} Total",
                safe_format_currency(self.pricelist_analysis['first_total_listino']),
                f"{self.pricelist_analysis['total_items_first']} items"
            )
        
        with col2:
            st.metric(
                f"{self.second_name} Total",
                safe_format_currency(self.pricelist_analysis['second_total_listino']),
                f"{self.pricelist_analysis['total_items_second']} items"
            )
        
        with col3:
            diff = self.pricelist_analysis['listino_difference']
            diff_perc = self.pricelist_analysis['listino_difference_percentage']
            st.metric(
                "Difference",
                safe_format_currency(diff),
                f"{diff_perc:+.2f}%"
            )
        
        # Price comparison by group/category
        st.subheader("📈 Price Analysis by Product Group")
        
        # Aggregate data by product groups
        first_groups_data = self._aggregate_by_groups(self.first_product_groups, "First")
        second_groups_data = self._aggregate_by_groups(self.second_product_groups, "Second")
        
        # Combine data for comparison
        all_group_ids = set(first_groups_data.keys()) | set(second_groups_data.keys())
        
        comparison_data = []
        for group_id in all_group_ids:
            first_data = first_groups_data.get(group_id, {'total': 0, 'name': 'N/A', 'items': 0})
            second_data = second_groups_data.get(group_id, {'total': 0, 'name': 'N/A', 'items': 0})
            
            comparison_data.append({
                'Group ID': group_id,
                'Group Name': first_data.get('name', second_data.get('name', 'N/A')),
                f'{self.first_name} Total (€)': first_data['total'],
                f'{self.second_name} Total (€)': second_data['total'],
                f'{self.first_name} Items': first_data['items'],
                f'{self.second_name} Items': second_data['items'],
                'Difference (€)': first_data['total'] - second_data['total'],
                'Difference %': ((first_data['total'] - second_data['total']) / second_data['total'] * 100) if second_data['total'] > 0 else 0
            })
        
        df_groups = pd.DataFrame(comparison_data)
        df_groups = df_groups.sort_values('Difference (€)', key=abs, ascending=False)
        
        # Display formatted table with NumberColumn
        st.dataframe(
            df_groups, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                f'{self.first_name} Total (€)': st.column_config.NumberColumn(
                    f'{self.first_name} Total (€)',
                    help="Total value in first file",
                    format="€%.2f"
                ),
                f'{self.second_name} Total (€)': st.column_config.NumberColumn(
                    f'{self.second_name} Total (€)',
                    help="Total value in second file",
                    format="€%.2f"
                ),
                f'{self.first_name} Items': st.column_config.NumberColumn(
                    f'{self.first_name} Items',
                    help="Number of items in first file",
                    format="%d"
                ),
                f'{self.second_name} Items': st.column_config.NumberColumn(
                    f'{self.second_name} Items',
                    help="Number of items in second file",
                    format="%d"
                ),
                'Difference (€)': st.column_config.NumberColumn(
                    'Difference (€)',
                    help="Difference in total value",
                    format="€%.2f"
                ),
                'Difference %': st.column_config.NumberColumn(
                    'Difference %',
                    help="Percentage difference",
                    format="%.2f%%"
                )
            }
        )
        
        # Visual comparison
        col1, col2 = st.columns(2)
        
        with col1:
            # Group totals comparison
            fig_groups = px.bar(
                df_groups,
                x='Group ID',
                y=[f'{self.first_name} Total (€)', f'{self.second_name} Total (€)'],
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
        self._ensure_analysis_completed()
        st.header("🔍 Missing Items Analysis")
        
        # Items missing in second
        missing_in_second = [c for c in self.item_comparisons 
                          if c.result_type == ComparisonResult.MISSING_IN_SECOND]
        
        # Items missing in first
        missing_in_first = [c for c in self.item_comparisons 
                         if c.result_type == ComparisonResult.MISSING_IN_FIRST]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📋 Items Missing in {self.second_name}")
            st.metric("Count", len(missing_in_second))
            
            if missing_in_second:
                missing_second_data = []
                total_value = 0
                
                for comp in missing_in_second:
                    if comp.first_item:
                        item = comp.first_item['item_data']
                        value = self._safe_float(item.pricelist_total_price)
                        total_value += value
                        
                        missing_second_data.append({
                            'Code': comp.code,
                            'Description': comp.description[:40] + "..." if len(comp.description) > 40 else comp.description,
                            'Quantity': item.quantity,
                            'Unit Price (€)': self._safe_float(item.pricelist_unit_price),
                            'Total Value (€)': value,
                            'Group': comp.first_item.get('group_name', 'N/A')
                        })
                
                st.metric("Total Value", safe_format_currency(total_value))
                
                df_missing_second = pd.DataFrame(missing_second_data)
                
                # Format for display with NumberColumn
                st.dataframe(
                    df_missing_second, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Quantity": st.column_config.NumberColumn(
                            "Quantity",
                            help="Item quantity",
                            format="%.2f"
                        ),
                        "Unit Price (€)": st.column_config.NumberColumn(
                            "Unit Price (€)",
                            help="Unit price in euros",
                            format="€%.2f"
                        ),
                        "Total Value (€)": st.column_config.NumberColumn(
                            "Total Value (€)",
                            help="Total value in euros",
                            format="€%.2f"
                        )
                    }
                )
                
                # Download CSV
                if st.button("📥 Export Missing Items (Second)", key="export_missing_second"):
                    csv = df_missing_second.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="items_missing_in_second.csv",
                        mime="text/csv",
                        key="download_missing_second"
                    )
            else:
                st.success("✅ No items missing!")
        
        with col2:
            st.subheader(f"📋 Items Missing in {self.first_name}")
            st.metric("Count", len(missing_in_first))
            
            if missing_in_first:
                missing_first_data = []
                total_value = 0
                
                for comp in missing_in_first:
                    if comp.second_item:
                        item = comp.second_item['item_data']
                        value = self._safe_float(item.pricelist_total_price)
                        total_value += value
                        
                        missing_first_data.append({
                            'Code': comp.code,
                            'Description': comp.description[:40] + "..." if len(comp.description) > 40 else comp.description,
                            'Quantity': item.quantity,
                            'Unit Price (€)': self._safe_float(item.pricelist_unit_price),
                            'Total Value (€)': value,
                            'WBE': comp.wbe or 'N/A'
                        })
                
                st.metric("Total Value", safe_format_currency(total_value))
                
                df_missing_first = pd.DataFrame(missing_first_data)
                
                # Format for display with NumberColumn
                st.dataframe(
                    df_missing_first, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Quantity": st.column_config.NumberColumn(
                            "Quantity",
                            help="Item quantity",
                            format="%.2f"
                        ),
                        "Unit Price (€)": st.column_config.NumberColumn(
                            "Unit Price (€)",
                            help="Unit price in euros",
                            format="€%.2f"
                        ),
                        "Total Value (€)": st.column_config.NumberColumn(
                            "Total Value (€)",
                            help="Total value in euros",
                            format="€%.2f"
                        )
                    }
                )
                
                # Download CSV
                if st.button("📥 Export Missing Items (First)", key="export_missing_first"):
                    csv = df_missing_first.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="items_missing_in_first.csv",
                        mime="text/csv",
                        key="download_missing_first"
                    )
            else:
                st.success("✅ No items missing!")
    
    def display_detailed_item_comparison(self):
        """Display detailed item-by-item comparison"""
        self._ensure_analysis_completed()
        st.header("🔍 Detailed Item Comparison")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_type = st.selectbox(
                "Filter by Status",
                ["All", "Matches", "Differences", "Missing in Second", "Missing in First", "Value Mismatches"]
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
                "Missing in Second": ComparisonResult.MISSING_IN_SECOND,
                "Missing in First": ComparisonResult.MISSING_IN_FIRST,
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
                first_qty = first_unit_price = first_total = ""
                second_qty = second_unit_price = second_total = ""
                
                if comp.first_item:
                    first_item = comp.first_item['item_data']
                    first_qty = str(first_item.quantity)
                    first_unit_price = f"€{self._safe_float(first_item.pricelist_unit_price):,.2f}"
                    first_total = f"€{self._safe_float(first_item.pricelist_total_price):,.2f}"
                
                if comp.second_item:
                    second_item = comp.second_item['item_data']
                    second_qty = str(second_item.quantity)
                    second_unit_price = f"€{self._safe_float(second_item.pricelist_unit_price):,.2f}"
                    second_total = f"€{self._safe_float(second_item.pricelist_total_price):,.2f}"
                
                comparison_data.append({
                    'Code': comp.code,
                    'Description': comp.description[:60] + "..." if len(comp.description) > 60 else comp.description,
                    'Status': comp.result_type.value.replace('_', ' ').title(),
                    'WBE': comp.wbe or 'N/A',
                    f'{self.first_name} Qty': first_qty,
                    f'{self.second_name} Qty': second_qty,
                    f'{self.first_name} Unit €': first_unit_price,
                    f'{self.second_name} Unit €': second_unit_price,
                    f'{self.first_name} Total €': first_total,
                    f'{self.second_name} Total €': second_total,
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
    
    def display_project_structure_analysis(self):
        """Display project structure analysis"""
        self._ensure_analysis_completed()
        st.header("🏗️ Project Structure Analysis")
        
        st.markdown("""
        This analysis compares the structural organization of both quotation files,
        including product groups, categories, and their relationships.
        """)
        
        # Project structure comparison
        st.subheader("📊 Project Structure Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📋 {self.first_name} Structure")
            
            # First file structure
            first_groups_count = len(self.first_product_groups)
            first_categories_count = sum(len(group.categories) for group in self.first_product_groups)
            first_items_count = sum(len(category.items) for group in self.first_product_groups for category in group.categories)
            
            st.metric("Product Groups", first_groups_count)
            st.metric("Categories", first_categories_count)
            st.metric("Total Items", first_items_count)
            
            # Group breakdown
            first_groups_data = []
            for group in self.first_product_groups:
                categories_count = len(group.categories)
                items_count = sum(len(category.items) for category in group.categories)
                total_value = sum(
                    self._safe_float(item.pricelist_total_price) 
                    for category in group.categories 
                    for item in category.items
                )
                
                first_groups_data.append({
                    'Group ID': group.group_id,
                    'Group Name': group.group_name,
                    'Categories': categories_count,
                    'Items': items_count,
                    'Total Value (€)': total_value
                })
            
            if first_groups_data:
                df_first_groups = pd.DataFrame(first_groups_data)
                st.dataframe(
                    df_first_groups,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Categories": st.column_config.NumberColumn(
                            "Categories",
                            help="Number of categories",
                            format="%d"
                        ),
                        "Items": st.column_config.NumberColumn(
                            "Items",
                            help="Number of items",
                            format="%d"
                        ),
                        "Total Value (€)": st.column_config.NumberColumn(
                            "Total Value (€)",
                            help="Total value in euros",
                            format="€%.2f"
                        )
                    }
                )
        
        with col2:
            st.subheader(f"📋 {self.second_name} Structure")
            
            # Second file structure
            second_groups_count = len(self.second_product_groups)
            second_categories_count = sum(len(group.categories) for group in self.second_product_groups)
            second_items_count = sum(len(category.items) for group in self.second_product_groups for category in group.categories)
            
            st.metric("Product Groups", second_groups_count)
            st.metric("Categories", second_categories_count)
            st.metric("Total Items", second_items_count)
            
            # Group breakdown
            second_groups_data = []
            for group in self.second_product_groups:
                categories_count = len(group.categories)
                items_count = sum(len(category.items) for category in group.categories)
                total_value = sum(
                    self._safe_float(item.pricelist_total_price) 
                    for category in group.categories 
                    for item in category.items
                )
                
                second_groups_data.append({
                    'Group ID': group.group_id,
                    'Group Name': group.group_name,
                    'Categories': categories_count,
                    'Items': items_count,
                    'Total Value (€)': total_value
                })
            
            if second_groups_data:
                df_second_groups = pd.DataFrame(second_groups_data)
                st.dataframe(
                    df_second_groups,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Categories": st.column_config.NumberColumn(
                            "Categories",
                            help="Number of categories",
                            format="%d"
                        ),
                        "Items": st.column_config.NumberColumn(
                            "Items",
                            help="Number of items",
                            format="%d"
                        ),
                        "Total Value (€)": st.column_config.NumberColumn(
                            "Total Value (€)",
                            help="Total value in euros",
                            format="€%.2f"
                        )
                    }
                )
        
        # Structure comparison summary
        st.subheader("📈 Structure Comparison Summary")
        
        comparison_data = {
            'Metric': ['Product Groups', 'Categories', 'Total Items', 'Average Items per Group', 'Average Items per Category'],
            f'{self.first_name}': [
                first_groups_count,
                first_categories_count,
                first_items_count,
                round(first_items_count / first_groups_count, 1) if first_groups_count > 0 else 0,
                round(first_items_count / first_categories_count, 1) if first_categories_count > 0 else 0
            ],
            f'{self.second_name}': [
                second_groups_count,
                second_categories_count,
                second_items_count,
                round(second_items_count / second_groups_count, 1) if second_groups_count > 0 else 0,
                round(second_items_count / second_categories_count, 1) if second_categories_count > 0 else 0
            ],
            'Difference': [
                first_groups_count - second_groups_count,
                first_categories_count - second_categories_count,
                first_items_count - second_items_count,
                round(first_items_count / first_groups_count, 1) - round(second_items_count / second_groups_count, 1) if first_groups_count > 0 and second_groups_count > 0 else 0,
                round(first_items_count / first_categories_count, 1) - round(second_items_count / second_categories_count, 1) if first_categories_count > 0 and second_categories_count > 0 else 0
            ]
        }
        
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(
            df_comparison,
            use_container_width=True,
            hide_index=True,
            column_config={
                f'{self.first_name}': st.column_config.NumberColumn(
                    f'{self.first_name}',
                    help="Value in first file",
                    format="%.1f"
                ),
                f'{self.second_name}': st.column_config.NumberColumn(
                    f'{self.second_name}',
                    help="Value in second file",
                    format="%.1f"
                ),
                'Difference': st.column_config.NumberColumn(
                    'Difference',
                    help="Difference between files",
                    format="%+.1f"
                )
            }
        )
    
    def display_financial_impact_assessment(self):
        """Display financial impact assessment"""
        self._ensure_analysis_completed()
        st.header("💰 Financial Impact Assessment")
        
        st.markdown("""
        This analysis provides a comprehensive assessment of the financial impact
        when applying changes from the first quotation to the second quotation.
        """)
        
        # Overall financial impact
        st.subheader("📊 Overall Financial Impact")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Listino Change",
                safe_format_currency(self.pricelist_analysis['listino_difference']),
                f"{self.pricelist_analysis['listino_difference_percentage']:+.2f}%"
            )
        
        with col2:
            # Calculate cost impact (if available)
            first_total_cost = self._safe_float(self.first_totals.total_cost)
            second_total_cost = self._safe_float(self.second_totals.total_cost)
            cost_difference = first_total_cost - second_total_cost
            cost_difference_perc = ((cost_difference / second_total_cost) * 100) if second_total_cost > 0 else 0
            
            st.metric(
                "Total Cost Change",
                safe_format_currency(cost_difference),
                f"{cost_difference_perc:+.2f}%"
            )
        
        with col3:
            # Calculate margin impact
            margin_difference = self.pricelist_analysis['listino_difference'] - cost_difference
            first_margin = self.pricelist_analysis['first_total_listino'] - first_total_cost
            second_margin = self.pricelist_analysis['second_total_listino'] - second_total_cost
            margin_difference_perc = ((margin_difference / second_margin) * 100) if second_margin > 0 else 0
            
            st.metric(
                "Margin Change",
                safe_format_currency(margin_difference),
                f"{margin_difference_perc:+.2f}%"
            )
        
        with col4:
            # Calculate margin percentage change
            first_margin_perc = (first_margin / self.pricelist_analysis['first_total_listino'] * 100) if self.pricelist_analysis['first_total_listino'] > 0 else 0
            second_margin_perc = (second_margin / self.pricelist_analysis['second_total_listino'] * 100) if self.pricelist_analysis['second_total_listino'] > 0 else 0
            margin_perc_change = first_margin_perc - second_margin_perc
            
            st.metric(
                "Margin % Change",
                f"{margin_perc_change:+.1f}%",
                f"From {second_margin_perc:.1f}% to {first_margin_perc:.1f}%"
            )
        
        # Detailed financial breakdown
        st.subheader("📈 Detailed Financial Breakdown")
        
        financial_data = {
            'Metric': ['Total Listino', 'Total Cost', 'Total Margin', 'Margin %'],
            f'{self.first_name}': [
                self.pricelist_analysis['first_total_listino'],
                first_total_cost,
                first_margin,
                first_margin_perc
            ],
            f'{self.second_name}': [
                self.pricelist_analysis['second_total_listino'],
                second_total_cost,
                second_margin,
                second_margin_perc
            ],
            'Difference': [
                self.pricelist_analysis['listino_difference'],
                cost_difference,
                margin_difference,
                margin_perc_change
            ],
            'Change %': [
                self.pricelist_analysis['listino_difference_percentage'],
                cost_difference_perc,
                margin_difference_perc,
                margin_perc_change
            ]
        }
        
        df_financial = pd.DataFrame(financial_data)
        st.dataframe(
            df_financial,
            use_container_width=True,
            hide_index=True,
            column_config={
                f'{self.first_name}': st.column_config.NumberColumn(
                    f'{self.first_name}',
                    help="Value in first file",
                    format="€%.2f"
                ),
                f'{self.second_name}': st.column_config.NumberColumn(
                    f'{self.second_name}',
                    help="Value in second file",
                    format="€%.2f"
                ),
                'Difference': st.column_config.NumberColumn(
                    'Difference',
                    help="Difference between files",
                    format="€%.2f"
                ),
                'Change %': st.column_config.NumberColumn(
                    'Change %',
                    help="Percentage change",
                    format="%.2f%%"
                )
            }
        )
        
        # Financial impact visualization
        st.subheader("📊 Financial Impact Visualization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart showing composition
            fig_composition = px.pie(
                values=[self.pricelist_analysis['first_total_listino'], first_total_cost, first_margin],
                names=['Listino', 'Cost', 'Margin'],
                title=f'{self.first_name} Financial Composition',
                color_discrete_map={'Listino': '#1f77b4', 'Cost': '#ff7f0e', 'Margin': '#2ca02c'}
            )
            st.plotly_chart(fig_composition, use_container_width=True)
        
        with col2:
            # Bar chart comparing totals
            fig_comparison = px.bar(
                x=['Listino', 'Cost', 'Margin'],
                y=[
                    self.pricelist_analysis['first_total_listino'],
                    first_total_cost,
                    first_margin
                ],
                title=f'{self.first_name} vs {self.second_name}',
                color=['First', 'First', 'First'],
                barmode='group'
            )
            fig_comparison.add_bar(
                x=['Listino', 'Cost', 'Margin'],
                y=[
                    self.pricelist_analysis['second_total_listino'],
                    second_total_cost,
                    second_margin
                ],
                name='Second'
            )
            st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Risk assessment
        st.subheader("⚠️ Risk Assessment")
        
        risks = []
        
        if abs(self.pricelist_analysis['listino_difference_percentage']) > 10:
            risks.append(f"⚠️ **High Listino Change**: {self.pricelist_analysis['listino_difference_percentage']:+.1f}% change in total listino")
        
        if abs(margin_perc_change) > 5:
            risks.append(f"⚠️ **Margin Impact**: {margin_perc_change:+.1f}% change in margin percentage")
        
        if abs(cost_difference_perc) > 15:
            risks.append(f"⚠️ **Cost Impact**: {cost_difference_perc:+.1f}% change in total cost")
        
        if self.pricelist_analysis['items_missing_in_second'] > 0:
            risks.append(f"⚠️ **Missing Items**: {self.pricelist_analysis['items_missing_in_second']} items missing in second file")
        
        if self.pricelist_analysis['items_with_differences'] > 0:
            risks.append(f"⚠️ **Value Differences**: {self.pricelist_analysis['items_with_differences']} items have value differences")
        
        if risks:
            for risk in risks:
                st.warning(risk)
        else:
            st.success("✅ No significant financial risks identified.")
    
    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float"""
        try:
            if value is None or value == "":
                return default
            return float(value)
        except (ValueError, TypeError):
            return default 
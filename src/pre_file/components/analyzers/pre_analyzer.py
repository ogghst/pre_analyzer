"""
PRE File Analyzer
Specific analyzer for PRE quotation files
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
from .base_analyzer import BaseAnalyzer

# Import field constants
from ..field_constants import JsonFields, DisplayFields


class PreAnalyzer(BaseAnalyzer):
    """Analyzer specifically for PRE quotation files"""
    
    def get_analysis_views(self) -> List[str]:
        """Return list of available analysis views for PRE files"""
        return [
            "Project Summary",
            "Tree Structure", 
            "Groups Analysis",
            "Categories Analysis",
            "Items Analysis",
            "Financial Analysis"
        ]
    
    def display_project_summary(self):
        """Display PRE-specific project summary information"""
        st.header("📋 PRE Quotation Summary")
        
        # Create columns for metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Project ID", self.project.get(JsonFields.ID, 'N/A'))
            st.metric("Customer", self.project.get('customer', 'N/A'))
            
        with col2:
            currency = self.project.get(JsonFields.PARAMETERS, {}).get(JsonFields.CURRENCY, 'N/A')
            exchange_rate = self.project.get(JsonFields.PARAMETERS, {}).get(JsonFields.EXCHANGE_RATE, 0)
            st.metric("Currency", currency)
            st.metric("Exchange Rate", f"{exchange_rate:.2f}")
            
        with col3:
            doc_perc = self.project.get(JsonFields.PARAMETERS, {}).get(JsonFields.DOC_PERCENTAGE, 0)
            pm_perc = self.project.get(JsonFields.PARAMETERS, {}).get(JsonFields.PM_PERCENTAGE, 0)
            st.metric("DOC %", f"{doc_perc:.3%}")
            st.metric("PM %", f"{pm_perc:.3%}")
            
        with col4:
            st.metric("Product Groups", len(self.product_groups))
            total_items = sum(len(cat.get(JsonFields.ITEMS, [])) for group in self.product_groups for cat in group.get(JsonFields.CATEGORIES, []))
            st.metric("Total Items", total_items)
        
        # Financial summary
        st.subheader("💰 Financial Summary")
        fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
        
        with fin_col1:
            st.metric("Equipment Total", f"€{self.totals.get(JsonFields.EQUIPMENT_TOTAL, 0):,.2f}")
        with fin_col2:
            st.metric("Installation Total", f"€{self.totals.get(JsonFields.INSTALLATION_TOTAL, 0):,.2f}")
        with fin_col3:
            fees_total = (self.totals.get(JsonFields.DOC_FEE, 0) + 
                         self.totals.get(JsonFields.PM_FEE, 0) + 
                         self.totals.get(JsonFields.WARRANTY_FEE, 0))
            st.metric("Fees Total", f"€{fees_total:,.2f}")
        with fin_col4:
            st.metric("Grand Total", f"€{self.totals.get(JsonFields.GRAND_TOTAL, 0):,.2f}")
    
    def display_financial_analysis(self):
        """Display comprehensive financial analysis for PRE files"""
        st.header("💰 PRE Financial Analysis")
        
        # Financial breakdown
        financial_data = {
            DisplayFields.CATEGORY_NAME: ['Equipment', 'Installation', 'DOC Fee', 'PM Fee', 'Warranty Fee'],
            'Amount (€)': [
                self.totals.get(JsonFields.EQUIPMENT_TOTAL, 0),
                self.totals.get(JsonFields.INSTALLATION_TOTAL, 0), 
                self.totals.get(JsonFields.DOC_FEE, 0),
                self.totals.get(JsonFields.PM_FEE, 0),
                self.totals.get(JsonFields.WARRANTY_FEE, 0)
            ]
        }
        
        df_financial = pd.DataFrame(financial_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Financial breakdown pie chart
            fig_pie = px.pie(
                df_financial,
                values='Amount (€)',
                names=DisplayFields.CATEGORY_NAME,
                title='PRE Financial Breakdown'
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
                text=[f"€{x:,.0f}" for x in financial_data['Amount (€)']] + [f"€{self.totals.get(JsonFields.GRAND_TOTAL, 0):,.0f}"],
                y=[
                    self.totals.get(JsonFields.EQUIPMENT_TOTAL, 0),
                    self.totals.get(JsonFields.INSTALLATION_TOTAL, 0),
                    self.totals.get(JsonFields.DOC_FEE, 0),
                    self.totals.get(JsonFields.PM_FEE, 0),
                    self.totals.get(JsonFields.WARRANTY_FEE, 0),
                    self.totals.get(JsonFields.GRAND_TOTAL, 0)
                ],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
            ))
            
            fig_waterfall.update_layout(
                title="PRE Financial Waterfall Analysis",
                showlegend=False,
                height=500
            )
            st.plotly_chart(fig_waterfall, use_container_width=True)
        
        # Group-level financial analysis
        st.subheader("📊 Financial Analysis by Group")
        
        group_financial = []
        for group in self.product_groups:
            equipment_total = sum(cat.get(JsonFields.TOTAL_OFFER, 0) for cat in group.get(JsonFields.CATEGORIES, []) 
                                if not cat.get(JsonFields.CATEGORY_ID, '').startswith('E'))
            installation_total = sum(cat.get(JsonFields.TOTAL_OFFER, 0) for cat in group.get(JsonFields.CATEGORIES, []) 
                                   if cat.get(JsonFields.CATEGORY_ID, '').startswith('E'))
            
            group_name = group.get(JsonFields.GROUP_NAME, 'Unnamed')
            if len(group_name) > 30:
                group_name = group_name[:30] + '...'
            
            group_financial.append({
                DisplayFields.GROUP_ID: group.get(JsonFields.GROUP_ID, 'Unknown'),
                DisplayFields.GROUP_NAME: group_name,
                DisplayFields.EQUIPMENT_EUR: equipment_total,
                DisplayFields.INSTALLATION_EUR: installation_total,
                DisplayFields.TOTAL_EUR: equipment_total + installation_total
            })
        
        df_group_financial = pd.DataFrame(group_financial)
        
        if not df_group_financial.empty:
            # Stacked bar chart for group financial breakdown
            fig_stacked = px.bar(
                df_group_financial,
                x=DisplayFields.GROUP_ID,
                y=[DisplayFields.EQUIPMENT_EUR, DisplayFields.INSTALLATION_EUR],
                title='Equipment vs Installation Costs by Group',
                barmode='stack'
            )
            fig_stacked.update_layout(height=600)
            st.plotly_chart(fig_stacked, use_container_width=True)
            
            # Financial summary table
            st.dataframe(df_group_financial, use_container_width=True)
        else:
            st.warning("No financial data to display.")
    
    # Implement abstract methods from base class
    def _get_group_total(self, group: Dict[str, Any]) -> float:
        """Get total offer value for a PRE group"""
        return sum(cat.get(JsonFields.TOTAL_OFFER, 0) for cat in group.get(JsonFields.CATEGORIES, []))
    
    def _get_category_total(self, category: Dict[str, Any]) -> float:
        """Get total offer value for a PRE category"""
        return self._safe_float(category.get(JsonFields.TOTAL_OFFER, 0))
    
    def _get_item_price(self, item: Dict[str, Any]) -> float:
        """Get total price for a PRE item"""
        return self._safe_float(item.get(JsonFields.PRICELIST_TOTAL_PRICE, 0))
    
    def _get_item_unit_price(self, item: Dict[str, Any]) -> float:
        """Get unit price for a PRE item"""
        return self._safe_float(item.get(JsonFields.PRICELIST_UNIT_PRICE, 0))
    
    def _get_category_specific_fields(self, category: Dict[str, Any]) -> Dict[str, Any]:
        """Get PRE-specific category fields"""
        return {
            'Subtotal Listino (€)': self._safe_float(category.get(JsonFields.SUBTOTAL_LISTINO, 0)),
            'Subtotal Codice (€)': self._safe_float(category.get(JsonFields.SUBTOTAL_CODICE, 0)),
            'Total (€)': self._safe_float(category.get(JsonFields.TOTAL, 0)),
            'Total Offer (€)': self._safe_float(category.get(JsonFields.TOTAL_OFFER, 0))
        }
    
    def _get_item_specific_fields(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Get PRE-specific item fields"""
        return {
            'Unit Cost (€)': self._safe_float(item.get(JsonFields.UNIT_COST, 0)),
            'Total Cost (€)': self._safe_float(item.get(JsonFields.TOTAL_COST, 0)),
            'Listino Unit (€)': self._safe_float(item.get(JsonFields.LISTINO_UNIT_PRICE, 0)),
            'Listino Total (€)': self._safe_float(item.get(JsonFields.LISTINO_TOTAL_PRICE, 0))
        } 
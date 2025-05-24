"""
Base Analyzer Class
Defines common interface and functionality for all file analyzers
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod


class BaseAnalyzer(ABC):
    """Abstract base class for all file analyzers"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.project = data.get('project', {})
        self.product_groups = data.get('product_groups', [])
        self.totals = data.get('totals', {})
    
    @abstractmethod
    def get_analysis_views(self) -> List[str]:
        """Return list of available analysis views for this file type"""
        pass
    
    @abstractmethod
    def display_project_summary(self):
        """Display project-specific summary information"""
        pass
    
    def display_tree_structure(self):
        """Display hierarchical tree structure (common for all types)"""
        st.header("🌳 Hierarchical Structure")
        
        if not self.product_groups:
            st.warning("No product groups found in the data.")
            return
        
        # Create expandable tree structure
        for group_idx, group in enumerate(self.product_groups):
            group_total = self._get_group_total(group)
            
            with st.expander(
                f"🏗️ {group.get('group_id', 'Unknown')}: {group.get('group_name', 'Unnamed Group')} (€{group_total:,.2f})", 
                expanded=False
            ):
                categories = group.get('categories', [])
                if not categories:
                    st.info("No categories found in this group.")
                    continue
                
                for category in categories:
                    cat_total = self._get_category_total(category)
                    st.markdown(f"**📂 {category.get('category_id', 'Unknown')}: {category.get('category_name', 'Unnamed Category')}** (€{cat_total:,.2f})")
                    
                    # Show top items in this category
                    items = category.get('items', [])
                    items_with_value = [item for item in items if self._get_item_price(item) > 0]
                    
                    if items_with_value:
                        top_items = sorted(items_with_value, key=lambda x: self._get_item_price(x), reverse=True)
                        
                        for item in top_items[:10]:  # Show top 10 items
                            description = item.get('description', 'No description')
                            if len(description) > 80:
                                description = description[:80] + "..."
                            price = self._get_item_price(item)
                            st.markdown(f"  • `{item.get('code', 'Unknown')}`: {description} (€{price:,.2f})")
                    else:
                        st.markdown("  • *No items with value*")
                    
                    st.markdown("---")
    
    def display_groups_analysis(self):
        """Display groups analysis with charts (common for all types)"""
        st.header("📦 Product Groups Analysis")
        
        if not self.product_groups:
            st.warning("No product groups found in the data.")
            return
        
        # Prepare groups data
        groups_data = []
        for group in self.product_groups:
            group_total = self._get_group_total(group)
            total_items = sum(len(cat.get('items', [])) for cat in group.get('categories', []))
            
            groups_data.append({
                'Group ID': group.get('group_id', 'Unknown'),
                'Group Name': group.get('group_name', 'Unnamed'),
                'Categories': len(group.get('categories', [])),
                'Total Items': total_items,
                'Total Value (€)': group_total,
                'Quantity': group.get('quantity', 1)
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
                x='Group ID', 
                y='Total Value (€)',
                title='Total Value by Product Group',
                text='Total Value (€)',
                color='Total Value (€)',
                color_continuous_scale='Blues'
            )
            fig_bar.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
            fig_bar.update_layout(height=500)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Pie chart of total value distribution
            fig_pie = px.pie(
                df_groups, 
                values='Total Value (€)', 
                names='Group ID',
                title='Total Value Distribution by Group'
            )
            fig_pie.update_layout(height=500)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Treemap visualization
        st.subheader("🗺️ Groups Treemap")
        fig_treemap = px.treemap(
            df_groups,
            path=['Group ID'],
            values='Total Value (€)',
            title='Product Groups by Total Value',
            color='Total Value (€)',
            color_continuous_scale='RdYlBu'
        )
        fig_treemap.update_layout(height=600)
        st.plotly_chart(fig_treemap, use_container_width=True)
    
    def display_categories_analysis(self):
        """Display categories analysis with charts (common for all types)"""
        st.header("📂 Categories Analysis")
        
        # Prepare categories data
        categories_data = []
        for group in self.product_groups:
            for category in group.get('categories', []):
                cat_total = self._get_category_total(category)
                categories_data.append({
                    'Group ID': group.get('group_id', 'Unknown'),
                    'Group Name': group.get('group_name', 'Unnamed'),
                    'Category ID': category.get('category_id', 'Unknown'),
                    'Category Name': category.get('category_name', 'Unnamed'),
                    'Items Count': len(category.get('items', [])),
                    'Total Value (€)': cat_total,
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
                options=df_categories['Group ID'].unique(),
                default=df_categories['Group ID'].unique(),
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
            (df_categories['Group ID'].isin(selected_groups)) &
            (df_categories['Total Value (€)'] >= min_value)
        ]
        
        # Display filtered table
        st.subheader("📊 Categories Summary Table")
        st.dataframe(filtered_df, use_container_width=True)
        
        if len(filtered_df) > 0:
            # Top categories chart
            top_categories = filtered_df.nlargest(15, 'Total Value (€)')
            
            fig_top = px.bar(
                top_categories,
                x='Total Value (€)',
                y='Category ID',
                orientation='h',
                title=f'Top {len(top_categories)} Categories by Total Value',
                text='Total Value (€)',
                color='Total Value (€)',
                color_continuous_scale='Viridis'
            )
            fig_top.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
            fig_top.update_layout(height=600)
            st.plotly_chart(fig_top, use_container_width=True)
    
    def display_items_analysis(self):
        """Display items analysis with charts (common for all types)"""
        st.header("🔧 Items Analysis")
        
        # Prepare items data
        items_data = []
        for group in self.product_groups:
            for category in group.get('categories', []):
                for item in category.get('items', []):
                    item_data = {
                        'Group ID': group.get('group_id', 'Unknown'),
                        'Group Name': group.get('group_name', 'Unnamed'),
                        'Category ID': category.get('category_id', 'Unknown'),
                        'Category Name': category.get('category_name', 'Unnamed'),
                        'Position': item.get('position', ''),
                        'Code': item.get('code', 'Unknown'),
                        'Description': item.get('description', 'No description')[:100] + ('...' if len(item.get('description', '')) > 100 else ''),
                        'Full Description': item.get('description', 'No description'),
                        'Quantity': item.get('quantity', 0),
                        'Unit Price (€)': self._get_item_unit_price(item),
                        'Total Price (€)': self._get_item_price(item),
                        **self._get_item_specific_fields(item)
                    }
                    items_data.append(item_data)
        
        df_items = pd.DataFrame(items_data)
        
        if df_items.empty:
            st.warning("No item data to display.")
            return
        
        # Filter controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            unique_groups = df_items['Group ID'].unique()
            selected_groups = st.multiselect(
                "Filter by Groups",
                options=unique_groups,
                default=unique_groups[:min(5, len(unique_groups))],
                key="items_group_filter"
            )
        
        with col2:
            min_total_price = st.number_input(
                "Minimum Total Price (€)",
                min_value=0.0,
                value=1000.0,
                step=100.0,
                key="items_min_price"
            )
        
        with col3:
            search_term = st.text_input(
                "Search in Description",
                value="",
                placeholder="Enter search term...",
                key="items_search"
            )
        
        # Apply filters
        filtered_items = df_items[
            (df_items['Group ID'].isin(selected_groups)) &
            (df_items['Total Price (€)'] >= min_total_price)
        ]
        
        if search_term:
            filtered_items = filtered_items[
                filtered_items['Full Description'].str.contains(search_term, case=False, na=False)
            ]
        
        # Display summary metrics
        if len(filtered_items) > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Filtered Items", len(filtered_items))
            with col2:
                st.metric("Total Value", f"€{filtered_items['Total Price (€)'].sum():,.2f}")
            with col3:
                st.metric("Average Price", f"€{filtered_items['Total Price (€)'].mean():,.2f}")
            with col4:
                st.metric("Max Price", f"€{filtered_items['Total Price (€)'].max():,.2f}")
            
            # Display top items table
            st.subheader("🔝 Top Items by Value")
            top_items = filtered_items.nlargest(20, 'Total Price (€)')
            
            # Create display table
            display_columns = ['Group ID', 'Category ID', 'Code', 'Description', 'Quantity', 'Unit Price (€)', 'Total Price (€)']
            st.dataframe(top_items[display_columns], use_container_width=True)
            
            # Top items chart
            if len(top_items) > 0:
                fig_items = px.bar(
                    top_items.head(15),
                    x='Total Price (€)',
                    y='Code',
                    orientation='h',
                    title='Top 15 Items by Total Price',
                    text='Total Price (€)',
                    color='Total Price (€)',
                    color_continuous_scale='Plasma'
                )
                fig_items.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
                fig_items.update_layout(height=600)
                st.plotly_chart(fig_items, use_container_width=True)
        else:
            st.warning("No items match the current filters. Please adjust your criteria.")
    
    # Abstract methods for subclasses to implement
    @abstractmethod
    def _get_group_total(self, group: Dict[str, Any]) -> float:
        """Get total value for a group"""
        pass
    
    @abstractmethod
    def _get_category_total(self, category: Dict[str, Any]) -> float:
        """Get total value for a category"""
        pass
    
    @abstractmethod
    def _get_item_price(self, item: Dict[str, Any]) -> float:
        """Get price for an item"""
        pass
    
    @abstractmethod
    def _get_item_unit_price(self, item: Dict[str, Any]) -> float:
        """Get unit price for an item"""
        pass
    
    @abstractmethod
    def _get_category_specific_fields(self, category: Dict[str, Any]) -> Dict[str, Any]:
        """Get category-specific fields for analysis"""
        pass
    
    @abstractmethod
    def _get_item_specific_fields(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Get item-specific fields for analysis"""
        pass
    
    # Utility methods
    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float"""
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    def _truncate_text(self, text: str, max_length: int = 50) -> str:
        """Truncate text to specified length"""
        if text and len(text) > max_length:
            return text[:max_length] + "..."
        return text or "" 
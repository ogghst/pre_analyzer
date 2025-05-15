import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import DETAIL_FIELD_DISPLAY_NAMES, CURRENCY_FORMAT, QUANTITY_FORMAT

def create_detail_comparison_viz(file1_data, file2_data):
    """Create visualizations comparing detail data between two files"""
    file1_name = file1_data['name']
    file2_name = file2_data['name']
    
    detail_df1 = file1_data['detail_df']
    detail_df2 = file2_data['detail_df']
    
    st.subheader(f"Detail Data Comparison: {file1_name} vs {file2_name}")
    
    # Check if we have necessary data
    if not detail_df1.empty and not detail_df2.empty and 'wbe_group_desc' in detail_df1.columns and 'wbe_group_desc' in detail_df2.columns:
        st.subheader(f"Changes in Items by {DETAIL_FIELD_DISPLAY_NAMES.get('wbe_group_desc', 'WBE Group')}: {file1_name} vs {file2_name}")
        
        # Count items by group for each file
        group_counts1 = detail_df1['wbe_group_desc'].value_counts().reset_index()
        group_counts1.columns = [DETAIL_FIELD_DISPLAY_NAMES.get('wbe_group_desc', 'WBE Group'), 'Count']
        group_counts1['Source'] = file1_name
        
        group_counts2 = detail_df2['wbe_group_desc'].value_counts().reset_index()
        group_counts2.columns = [DETAIL_FIELD_DISPLAY_NAMES.get('wbe_group_desc', 'WBE Group'), 'Count']
        group_counts2['Source'] = file2_name
        
        # Merge the counts for comparison
        merged_counts = pd.merge(
            group_counts1, 
            group_counts2, 
            on=DETAIL_FIELD_DISPLAY_NAMES.get('wbe_group_desc', 'WBE Group'), 
            suffixes=('_1', '_2')
        )
        
        # Calculate differences
        merged_counts['diff'] = merged_counts['Count_1'] - merged_counts['Count_2']
        merged_counts['pct_diff'] = merged_counts.apply(
            lambda row: ((row['Count_1'] - row['Count_2']) / row['Count_2']) * 100 
            if row['Count_2'] != 0 else 0, 
            axis=1
        )
        
        # Sort by difference
        merged_counts = merged_counts.sort_values(by='diff', ascending=False)
        
        # Create a copy for display with formatted values
        display_counts = merged_counts.copy()
        display_counts['Count_1'] = display_counts['Count_1'].map(lambda x: CURRENCY_FORMAT(x) if pd.notna(x) else 'N/A')
        display_counts['Count_2'] = display_counts['Count_2'].map(lambda x: CURRENCY_FORMAT(x) if pd.notna(x) else 'N/A')
        display_counts['diff'] = display_counts['diff'].map(lambda x: CURRENCY_FORMAT(x) if pd.notna(x) else 'N/A')
        display_counts['pct_diff'] = display_counts['pct_diff'].map(lambda x: '{:,.2f}%'.format(x) if pd.notna(x) else 'N/A')
        
        # Show tabular data
        st.write("Item Count Changes by WBE Group:")
        st.dataframe(
            display_counts[[DETAIL_FIELD_DISPLAY_NAMES.get('wbe_group_desc', 'WBE Group'), 'Count_1', 'Count_2', 'diff', 'pct_diff']], 
            use_container_width=True
        )
        
        # Combine for plotting
        combined_counts = pd.concat([group_counts1, group_counts2])
        
        # Create grouped bar chart
        fig = px.bar(
            combined_counts, 
            x=DETAIL_FIELD_DISPLAY_NAMES.get('wbe_group_desc', 'WBE Group'), 
            y='Count',
            color='Source',
            barmode='group',
            title=f'Item Counts by {DETAIL_FIELD_DISPLAY_NAMES.get("wbe_group_desc", "WBE Group")}: {file1_name} vs {file2_name}',
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            yaxis_tickformat=',.0f'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Create a chart showing the differences
        fig = px.bar(
            merged_counts,
            x=DETAIL_FIELD_DISPLAY_NAMES.get('wbe_group_desc', 'WBE Group'),
            y='diff',
            color='diff',
            color_continuous_scale='RdBu_r',
            title=f'Difference in Item Counts by {DETAIL_FIELD_DISPLAY_NAMES.get("wbe_group_desc", "WBE Group")}: {file1_name} - {file2_name}'
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            yaxis_tickformat=',.0f'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Type distribution comparison
        if 'wbe_type_code' in detail_df1.columns and 'wbe_type_code' in detail_df2.columns:
            # Count by type for each file
            type_counts1 = detail_df1['wbe_type_code'].value_counts().reset_index()
            type_counts1.columns = [DETAIL_FIELD_DISPLAY_NAMES.get('wbe_type_code', 'WBE Type'), 'Count']
            type_counts1['Source'] = file1_name
            
            type_counts2 = detail_df2['wbe_type_code'].value_counts().reset_index()
            type_counts2.columns = [DETAIL_FIELD_DISPLAY_NAMES.get('wbe_type_code', 'WBE Type'), 'Count']
            type_counts2['Source'] = file2_name
            
            # Combine data
            combined = pd.concat([type_counts1, type_counts2])
            
            # Create stacked bar chart
            fig = px.bar(
                combined,
                x=DETAIL_FIELD_DISPLAY_NAMES.get('wbe_type_code', 'WBE Type'),
                y='Count',
                color='Source',
                barmode='group',
                title=f'Distribution of Items by {DETAIL_FIELD_DISPLAY_NAMES.get("wbe_type_code", "WBE Type")}: {file1_name} vs {file2_name}'
            )
            fig.update_layout(yaxis_tickformat=',.0f')
            st.plotly_chart(fig, use_container_width=True)
            
            # Compare quantities if available
            if 'wbe_item_quantity' in detail_df1.columns and 'wbe_item_quantity' in detail_df2.columns:
                # Group by type and sum quantities
                type_qty1 = detail_df1.groupby('wbe_type_code')['wbe_item_quantity'].sum().reset_index()
                type_qty1.columns = [DETAIL_FIELD_DISPLAY_NAMES.get('wbe_type_code', 'WBE Type'), 
                                   DETAIL_FIELD_DISPLAY_NAMES.get('wbe_item_quantity', 'Total Quantity')]
                type_qty1['Source'] = file1_name
                
                type_qty2 = detail_df2.groupby('wbe_type_code')['wbe_item_quantity'].sum().reset_index()
                type_qty2.columns = [DETAIL_FIELD_DISPLAY_NAMES.get('wbe_type_code', 'WBE Type'), 
                                   DETAIL_FIELD_DISPLAY_NAMES.get('wbe_item_quantity', 'Total Quantity')]
                type_qty2['Source'] = file2_name
                
                # Combine for plotting
                combined_qty = pd.concat([type_qty1, type_qty2])
                
                # Create bar chart
                fig = px.bar(
                    combined_qty,
                    x=DETAIL_FIELD_DISPLAY_NAMES.get('wbe_type_code', 'WBE Type'),
                    y=DETAIL_FIELD_DISPLAY_NAMES.get('wbe_item_quantity', 'Total Quantity'),
                    color='Source',
                    barmode='group',
                    title=f'Total Quantities by {DETAIL_FIELD_DISPLAY_NAMES.get("wbe_type_code", "WBE Type")}: {file1_name} vs {file2_name}'
                )
                fig.update_layout(yaxis_tickformat=',.2f')
                st.plotly_chart(fig, use_container_width=True)
            
            # Compare prices if available
            if 'wbe_item_list_price' in detail_df1.columns and 'wbe_item_list_price' in detail_df2.columns:
                # Group by type and calculate average prices
                type_price1 = detail_df1.groupby('wbe_type_code')['wbe_item_list_price'].mean().reset_index()
                type_price1.columns = [DETAIL_FIELD_DISPLAY_NAMES.get('wbe_type_code', 'WBE Type'), 
                                     DETAIL_FIELD_DISPLAY_NAMES.get('wbe_item_list_price', 'Average List Price')]
                type_price1['Source'] = file1_name
                
                type_price2 = detail_df2.groupby('wbe_type_code')['wbe_item_list_price'].mean().reset_index()
                type_price2.columns = [DETAIL_FIELD_DISPLAY_NAMES.get('wbe_type_code', 'WBE Type'), 
                                     DETAIL_FIELD_DISPLAY_NAMES.get('wbe_item_list_price', 'Average List Price')]
                type_price2['Source'] = file2_name
                
                # Combine for plotting
                combined_price = pd.concat([type_price1, type_price2])
                
                # Create bar chart
                fig = px.bar(
                    combined_price,
                    x=DETAIL_FIELD_DISPLAY_NAMES.get('wbe_type_code', 'WBE Type'),
                    y=DETAIL_FIELD_DISPLAY_NAMES.get('wbe_item_list_price', 'Average List Price'),
                    color='Source',
                    barmode='group',
                    title=f'Average List Prices by {DETAIL_FIELD_DISPLAY_NAMES.get("wbe_type_code", "WBE Type")}: {file1_name} vs {file2_name}'
                )
                fig.update_layout(yaxis_tickformat=',.2f')
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cannot compare items by WBE Group - missing data from one or both files.") 
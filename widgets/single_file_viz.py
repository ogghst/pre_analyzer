import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import SUMMARY_FIELD_DISPLAY_NAMES, DETAIL_FIELD_DISPLAY_NAMES, CURRENCY_FORMAT, QUANTITY_FORMAT

def create_visualizations(detail_df, summary_df, file_name):
    """Create interactive visualizations based on the data for a single file"""
    st.header(f"Data Visualizations - {file_name}")
    
    # Create tabs for different visualization categories
    viz_tabs = st.tabs(["Detail Analysis", "Summary Analysis"])
    
    with viz_tabs[0]:
        if not detail_df.empty:
            st.subheader(f"Detail Data - {file_name}")
            # Format detail table columns for display
            display_detail = detail_df.copy(deep=True)
            for col in display_detail.columns:
                if 'price' in col.lower() or 'cost' in col.lower() or 'eur' in col.lower():
                    display_detail[col] = display_detail[col].astype('object')
                    display_detail[col] = display_detail[col].map(lambda x: CURRENCY_FORMAT(x) if pd.notna(x) else '')
                elif 'quantity' in col.lower() or 'qty' in col.lower():
                    display_detail[col] = display_detail[col].astype('object')
                    display_detail[col] = display_detail[col].map(lambda x: QUANTITY_FORMAT.format(x) if pd.notna(x) else '')
            display_detail.columns = [DETAIL_FIELD_DISPLAY_NAMES.get(col, col) for col in display_detail.columns]
            st.dataframe(display_detail, use_container_width=True)
            
            # Group data visualization
            if 'wbe_group_code' in detail_df.columns:
                # Count items by group
                group_counts = detail_df['wbe_group_code'].value_counts().reset_index()
                group_counts.columns = [DETAIL_FIELD_DISPLAY_NAMES.get('wbe_group_code', 'WBE Group'), 'Count']
                
                # Create display copy with formatted values
                display_counts = group_counts.copy()
                display_counts['Count'] = display_counts['Count'].map(lambda x: QUANTITY_FORMAT.format(x) if pd.notna(x) else 'N/A')
                
                fig = px.bar(
                    group_counts, 
                    x=DETAIL_FIELD_DISPLAY_NAMES.get('wbe_group_code', 'WBE Group'), 
                    y='Count',
                    title='Number of Items by WBE Group',
                    color=DETAIL_FIELD_DISPLAY_NAMES.get('wbe_group_code', 'WBE Group')
                )
                fig.update_layout(
                    yaxis_tickformat=',.0f',
                    yaxis_title='Count'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display formatted table
                st.dataframe(display_counts, use_container_width=True)
            
            # Type and subtype analysis
            if 'wbe_type_code' in detail_df.columns and 'wbe_item_quantity' in detail_df.columns:
                # Group by type and sum quantities
                type_qty = detail_df.groupby('wbe_type_code')['wbe_item_quantity'].sum().reset_index()
                type_qty.columns = [DETAIL_FIELD_DISPLAY_NAMES.get('wbe_type_code', 'WBE Type'), 
                                  DETAIL_FIELD_DISPLAY_NAMES.get('wbe_item_quantity', 'Total Quantity')]
                
                # Create display copy with formatted values
                display_qty = type_qty.copy()
                display_qty[DETAIL_FIELD_DISPLAY_NAMES.get('wbe_item_quantity', 'Total Quantity')] = display_qty[DETAIL_FIELD_DISPLAY_NAMES.get('wbe_item_quantity', 'Total Quantity')].map(
                    lambda x: QUANTITY_FORMAT.format(x) if pd.notna(x) else 'N/A'
                )
                
                fig = px.pie(
                    type_qty, 
                    values=DETAIL_FIELD_DISPLAY_NAMES.get('wbe_item_quantity', 'Total Quantity'), 
                    names=DETAIL_FIELD_DISPLAY_NAMES.get('wbe_type_code', 'WBE Type'),
                    title='Distribution of Quantities by WBE Type',
                    hole=0.4
                )
                fig.update_traces(
                    texttemplate=QUANTITY_FORMAT,
                    textposition='inside'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display formatted table
                st.dataframe(display_qty, use_container_width=True)
            
            # Price analysis if price data is available
            if 'wbe_item_list_price' in detail_df.columns:
                # Filter out rows with null prices
                price_data = detail_df.dropna(subset=['wbe_item_list_price'])
                if not price_data.empty:
                    # Create display copy with formatted values
                    display_price = price_data.copy()
                    display_price['wbe_item_list_price'] = display_price['wbe_item_list_price'].map(
                        lambda x: CURRENCY_FORMAT(x) if pd.notna(x) else 'N/A'
                    )
                    
                    fig = px.histogram(
                        price_data,
                        x='wbe_item_list_price',
                        title=f'Distribution of {DETAIL_FIELD_DISPLAY_NAMES.get("wbe_item_list_price", "List Prices")}',
                        nbins=20
                    )
                    fig.update_layout(
                        xaxis_title=DETAIL_FIELD_DISPLAY_NAMES.get('wbe_item_list_price', 'List Price'),
                        xaxis_tickformat=',.2f'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display statistics with formatted numbers
                    stats = price_data['wbe_item_list_price'].describe()
                    stats_df = pd.DataFrame({
                        'Statistic': stats.index,
                        'Value': stats.values
                    })
                    stats_df['Value'] = stats_df['Value'].map(lambda x: CURRENCY_FORMAT(x) if isinstance(x, (int, float)) else x)
                    st.write(f"{DETAIL_FIELD_DISPLAY_NAMES.get('wbe_item_list_price', 'List Price')} Statistics:")
                    st.dataframe(stats_df, use_container_width=True)
                    
                    # Display formatted price data
                    st.write("Price Data:")
                    st.dataframe(display_price, use_container_width=True)
        else:
            st.info("No detail data available for visualization.")
    
    with viz_tabs[1]:
        if not summary_df.empty:
            st.subheader(f"Summary Data - {file_name}")
            # Format summary table columns for display
            display_summary = summary_df.copy(deep=True)
            for col in display_summary.columns:
                if 'price' in col.lower() or 'cost' in col.lower() or 'eur' in col.lower():
                    display_summary[col] = display_summary[col].astype('object')
                    display_summary[col] = display_summary[col].map(lambda x: CURRENCY_FORMAT(x) if pd.notna(x) else '')
                elif 'quantity' in col.lower() or 'qty' in col.lower():
                    display_summary[col] = display_summary[col].astype('object')
                    display_summary[col] = display_summary[col].map(lambda x: QUANTITY_FORMAT.format(x) if pd.notna(x) else '')
            # Show the full summary table with display names
            display_summary_all = display_summary.copy()
            display_summary_all.columns = [SUMMARY_FIELD_DISPLAY_NAMES.get(col, col) for col in display_summary_all.columns]
            st.dataframe(display_summary_all, use_container_width=True)
            # If you want to show only price columns as a separate table:
            price_cols = [col for col in summary_df.columns if 'price' in col.lower()]
            if price_cols:
                price_display = display_summary[price_cols].copy()
                price_display.columns = [SUMMARY_FIELD_DISPLAY_NAMES.get(col, col) for col in price_display.columns]
                st.write("Price Data:")
                st.dataframe(price_display, use_container_width=True)
            
            # Quantity analysis
            if 'quantity' in summary_df.columns:
                # Scatter plot of quantity vs price if both exist
                if 'wbe_list_price' in summary_df.columns:
                    fig = px.scatter(
                        summary_df,
                        x='quantity',
                        y='wbe_list_price',
                        title=f'{SUMMARY_FIELD_DISPLAY_NAMES.get("quantity", "Quantity")} vs. {SUMMARY_FIELD_DISPLAY_NAMES.get("wbe_list_price", "List Price")}',
                        color='wbe_code' if 'wbe_code' in summary_df.columns else None,
                        size='wbe_list_price' if 'wbe_list_price' in summary_df.columns else None,
                        hover_data=['wbe_description'] if 'wbe_description' in summary_df.columns else None
                    )
                    fig.update_layout(
                        xaxis_title=SUMMARY_FIELD_DISPLAY_NAMES.get('quantity', 'Quantity'),
                        yaxis_title=SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_list_price', 'List Price'),
                        yaxis_tickformat=',.2f',
                        xaxis_tickformat=',.0f'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Display quantity statistics
                if summary_df['quantity'].dtype in ['float64', 'float32', 'int64']:
                    stats = summary_df['quantity'].describe()
                    stats_df = pd.DataFrame({
                        'Statistic': stats.index,
                        'Value': stats.values
                    })
                    stats_df['Value'] = stats_df['Value'].map(lambda x: QUANTITY_FORMAT.format(x) if isinstance(x, (int, float)) else x)
                    st.write(f"{SUMMARY_FIELD_DISPLAY_NAMES.get('quantity', 'Quantity')} Statistics:")
                    st.dataframe(stats_df, use_container_width=True)
                
                # Display formatted quantity data
                st.write("Quantity Data:")
                st.dataframe(display_summary[['quantity']], use_container_width=True)
        else:
            st.info("No summary data available for visualization.") 
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import SUMMARY_FIELD_DISPLAY_NAMES, DETAIL_FIELD_DISPLAY_NAMES, format_value

def create_visualizations(detail_df, summary_df, file_name):
    """Create interactive visualizations based on the data for a single file"""
    st.header(f"Data Visualizations - {file_name}")
    
    # Create tabs for different visualization categories
    viz_tabs = st.tabs(["Summary Analysis", "Detail Analysis"])
    
    
    with viz_tabs[1]:
        if not detail_df.empty:
            st.subheader(f"Detail Data - {file_name}")
            display_detail = detail_df.copy(deep=True)
            for col in display_detail.columns:
                display_detail[col] = display_detail[col].map(lambda x: format_value(col, x, 'detail'))
            display_detail.columns = [DETAIL_FIELD_DISPLAY_NAMES.get(col, {'display_name': col})['display_name'] for col in display_detail.columns]
            
            # Rearrange columns to put 'Proto WBE' as second column
            #cols = display_detail.columns.tolist()
            #proto_wbe_col = next((col for col in cols if col == 'Proto WBE'), None)
            #if proto_wbe_col:
            #    cols.remove(proto_wbe_col)
            #    cols.insert(1, proto_wbe_col)
            #    display_detail = display_detail[cols]
            
            st.dataframe(display_detail, use_container_width=True)
                    
            
            # Price analysis if price data is available
            if 'wbe_item_list_price' in detail_df.columns:
                # Filter out rows with null prices
                price_data = detail_df.dropna(subset=['wbe_item_list_price'])
                if not price_data.empty:
                    # Create display copy with formatted values
                    display_price = price_data.copy()
                    display_price['wbe_item_list_price'] = display_price['wbe_item_list_price'].map(
                        lambda x: format_value('wbe_item_list_price', x, 'detail')
                    )
                    
                    fig = px.histogram(
                        price_data,
                        x='wbe_item_list_price',
                        title=f'Distribution of {DETAIL_FIELD_DISPLAY_NAMES.get("wbe_item_list_price", "List Prices")["display_name"]}',
                        nbins=20
                    )
                    fig.update_layout(
                        xaxis_title=DETAIL_FIELD_DISPLAY_NAMES.get("wbe_item_list_price", "List Prices")['display_name'],
                        xaxis_tickformat=',.2f'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display statistics with formatted numbers
                    stats = price_data['wbe_item_list_price'].describe()
                    stats_df = pd.DataFrame({
                        'Statistic': stats.index,
                        'Value': stats.values
                    })
                    stats_df['Value'] = stats_df['Value'].map(lambda x: format_value('wbe_item_list_price', x, 'detail'))
                    st.write(f"{DETAIL_FIELD_DISPLAY_NAMES.get('wbe_item_list_price', 'List Prices')['display_name']} Statistics:")
                    st.dataframe(stats_df, use_container_width=True)
                    
                    # Display formatted price data
                    st.write("Price Data:")
                    st.dataframe(display_price, use_container_width=True)
        else:
            st.info("No detail data available for visualization.")
    
    with viz_tabs[0]:
        if not summary_df.empty:
            st.subheader(f"Summary Data - {file_name}")
            display_summary = summary_df.copy(deep=True)
            for col in display_summary.columns:
                display_summary[col] = display_summary[col].map(lambda x: format_value(col, x, 'summary'))
            display_summary_all = display_summary.copy()
            display_summary_all.columns = [SUMMARY_FIELD_DISPLAY_NAMES.get(col, {'display_name': col})['display_name'] for col in display_summary_all.columns]
            st.dataframe(display_summary_all, use_container_width=True)
            
        if not summary_df.empty:
            # Create a copy of the data for visualization
            viz_data = summary_df.copy()
            
            # Create the bar chart with both metrics
            fig = px.bar(
                viz_data,
                x='wbe_code',
                y=['wbe_direct_cost', 'wbe_list_price'],
                title=f'Distribution of Costs and List Prices by WBE Code',
                barmode='group',
                labels={
                    'wbe_code': SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_code', 'WBE Code')['display_name'],
                    'wbe_description': SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_description', 'WBE Description')['display_name'],
                    'value': 'Amount (EUR)',
                    'variable': 'Metric'
                }
            )
            
            # Update layout for better readability
            fig.update_layout(
                xaxis_title=SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_code', 'WBE Code')['display_name'],
                yaxis_title='Amount (EUR)',
                yaxis_tickformat=',.2f',
                showlegend=True,
                legend_title='Metric'
            )
            
            # Rename legend labels
            fig.data[0].name = SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_direct_cost', 'Direct Cost')['display_name']
            fig.data[1].name = SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_list_price', 'List Price')['display_name']
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

        if not summary_df.empty:
            # Create a copy of the data for visualization
            viz_data = summary_df.copy()
            
            # Extract first two letters of wbe_code and group by them
            viz_data['wbe_prefix'] = viz_data['wbe_code'].str[:2]
            grouped_data = viz_data.groupby('wbe_prefix')['wbe_direct_cost'].sum().reset_index()
            
            # Create pie chart
            fig = px.pie(
                grouped_data,
                values='wbe_direct_cost',
                names='wbe_prefix',
                title='Distribution of Direct Costs by WBE Code Prefix',
                labels={
                    'wbe_prefix': 'WBE Code Prefix',
                    'wbe_direct_cost': 'Direct Cost (EUR)'
                }
            )
            
            # Update layout for better readability
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Direct Cost: %{value:,.2f} EUR<br>Percentage: %{percent:.1%}'
            )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No summary data available for visualization.") 
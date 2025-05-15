import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import tempfile
import sys
import logging
import uuid
from datetime import datetime

# Add the current directory to the path so we can import the functions from test.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import functions from test.py
from test import (
    find_pre_detail_from_excel, 
    parse_pre_detail_from_excel, 
    process_pre_detal,
    find_mdc_summary, 
    parse_mdc_summary,
    print_dataframe
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_page():
    """Configure the Streamlit page layout and title"""
    st.set_page_config(
        page_title="PRE Excel Data Analyzer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("PRE Excel Data Analyzer")
    st.markdown("""
    This application allows you to upload one or more Excel files and analyze the extracted data.
    You can view individual files or compare multiple files to identify differences.
    """)

def save_uploaded_file(uploaded_file):
    """Save the uploaded file to a temporary location and return the path"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            tmp.write(uploaded_file.getvalue())
            return tmp.name
    except Exception as e:
        st.error(f"Error saving uploaded file: {e}")
        return None

def process_data(file_path):
    """Process the Excel file and return both detail and summary DataFrames"""
    try:
        # Process detailed data
        raw_df = parse_pre_detail_from_excel(file_path)
        detail_df = process_pre_detal(raw_df)
        
        # Process summary data
        mdc_raw_df, cod_row_idx = find_mdc_summary(file_path)
        if not mdc_raw_df.empty and cod_row_idx is not None:
            summary_df = parse_mdc_summary(mdc_raw_df, cod_row_idx)
        else:
            summary_df = pd.DataFrame()
            logging.warning("No summary data (MDC sheet) found in the uploaded file.")
        
        return detail_df, summary_df
    except Exception as e:
        logging.error(f"Error processing the file: {e}")
        return pd.DataFrame(), pd.DataFrame()

def show_data_tables(detail_df, summary_df, file_name):
    """Display the data tables with expanded options for a single file"""
    tabs = st.tabs([f"Detail Data - {file_name}", f"Summary Data - {file_name}"])
    
    with tabs[0]:
        if not detail_df.empty:
            st.subheader(f"Detailed Data - {file_name}")
            st.dataframe(detail_df, use_container_width=True)
            st.download_button(
                label="Download Detail Data as CSV",
                data=detail_df.to_csv(index=False).encode('utf-8'),
                file_name=f'detail_data_{file_name}.csv',
                mime='text/csv',
            )
        else:
            st.info(f"No detail data available for {file_name}.")
    
    with tabs[1]:
        if not summary_df.empty:
            st.subheader(f"Summary Data - {file_name}")
            st.dataframe(summary_df, use_container_width=True)
            st.download_button(
                label="Download Summary Data as CSV",
                data=summary_df.to_csv(index=False).encode('utf-8'),
                file_name=f'summary_data_{file_name}.csv',
                mime='text/csv',
            )
        else:
            st.info(f"No summary data available for {file_name}.")

def highlight_diff(value, compare_value):
    """Highlight differences between two values"""
    if pd.isna(value) and pd.isna(compare_value):
        return ''
    if pd.isna(value) or pd.isna(compare_value):
        return 'background-color: #FFC7CE; color: #9C0006'
    if value != compare_value:
        return 'background-color: #FFC7CE; color: #9C0006'
    return ''

def show_comparison_tables(file1_data, file2_data):
    """Display comparison tables between two files"""
    file1_name = file1_data['name']
    file2_name = file2_data['name']
    
    # Create tabs for detail and summary comparisons
    comp_tabs = st.tabs(["Detail Data Comparison", "Summary Data Comparison"])
    
    # Detail data comparison
    with comp_tabs[0]:
        df1 = file1_data['detail_df']
        df2 = file2_data['detail_df']
        
        if not df1.empty and not df2.empty:
            st.subheader(f"Detail Data Comparison: {file1_name} vs {file2_name}")
            
            # Find common columns
            common_cols = list(set(df1.columns).intersection(set(df2.columns)))
            
            if 'wbe_item_code' in common_cols:
                # Prepare for merge to show differences
                df1_subset = df1[common_cols].copy()
                df2_subset = df2[common_cols].copy()
                
                # Format any float columns with thousands and decimal separators
                for col in common_cols:
                    if df1_subset[col].dtype in ['float64', 'float32']:
                        df1_subset[col] = df1_subset[col].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else x)
                    if df2_subset[col].dtype in ['float64', 'float32']:
                        df2_subset[col] = df2_subset[col].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else x)
                
                # Add source indicator
                df1_subset['source'] = file1_name
                df2_subset['source'] = file2_name
                
                # Find items unique to each file
                df1_unique = df1_subset[~df1_subset['wbe_item_code'].isin(df2_subset['wbe_item_code'])]
                df2_unique = df2_subset[~df2_subset['wbe_item_code'].isin(df1_subset['wbe_item_code'])]
                
                # Find common items
                df1_common = df1_subset[df1_subset['wbe_item_code'].isin(df2_subset['wbe_item_code'])]
                df2_common = df2_subset[df2_subset['wbe_item_code'].isin(df1_subset['wbe_item_code'])]
                
                # Show unique items
                if not df1_unique.empty or not df2_unique.empty:
                    unique_items = pd.concat([df1_unique, df2_unique])
                    # Reset index to ensure it's unique before styling
                    unique_items = unique_items.reset_index(drop=True)
                    st.write(f"Found {len(unique_items)} items that appear in only one file:")
                    st.dataframe(
                        unique_items.style.apply(
                            lambda x: ['background-color: #DDEBF7' if v == file1_name else 'background-color: #E2EFDA' for v in x], 
                            subset=['source']
                        ),
                        use_container_width=True
                    )
                
                # Compare common items for differences
                if not df1_common.empty and not df2_common.empty:
                    # First store the original DataFrame with float columns for proper comparison
                    df1_common_orig = df1[common_cols].copy()
                    df1_common_orig = df1_common_orig[df1_common_orig['wbe_item_code'].isin(df2_subset['wbe_item_code'])]
                    
                    df2_common_orig = df2[common_cols].copy()
                    df2_common_orig = df2_common_orig[df2_common_orig['wbe_item_code'].isin(df1_subset['wbe_item_code'])]
                    
                    # Merge to compare numeric values
                    merge_cols = [c for c in common_cols if c != 'wbe_item_description']  # Exclude description for comparison
                    merged_orig = pd.merge(
                        df1_common_orig, 
                        df2_common_orig, 
                        on='wbe_item_code', 
                        suffixes=('_1', '_2')
                    )
                    # Reset index to ensure it's unique for styling
                    merged_orig = merged_orig.reset_index(drop=True)
                    
                    # Find rows with differences
                    diff_rows = merged_orig[merged_orig.filter(like='_1').values != merged_orig.filter(like='_2').values]
                    
                    if not diff_rows.empty:
                        # Now format the difference rows with the formatted numbers
                        # First, get the columns with differences
                        diff_cols = []
                        for col in merge_cols:
                            if col == 'wbe_item_code':
                                continue
                            if any(diff_rows[f'{col}_1'] != diff_rows[f'{col}_2']):
                                diff_cols.append(col)
                        
                        # Format float columns in the diff_rows - use .loc to avoid SettingWithCopyWarning
                        diff_rows = diff_rows.copy()  # Create an explicit copy to avoid SettingWithCopyWarning
                        for col in diff_cols:
                            if diff_rows[f'{col}_1'].dtype in ['float64', 'float32']:
                                diff_rows.loc[:, f'{col}_1'] = diff_rows[f'{col}_1'].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else 'N/A')
                            if diff_rows[f'{col}_2'].dtype in ['float64', 'float32']:
                                diff_rows.loc[:, f'{col}_2'] = diff_rows[f'{col}_2'].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else 'N/A')
                        
                        st.write(f"Found {len(diff_rows)} items with differences between files:")
                        st.dataframe(diff_rows, use_container_width=True)
                    else:
                        st.success("All common items are identical between the two files.")
            else:
                st.warning("Cannot compare detail data - no common identifier column found.")
        else:
            st.info("Cannot compare detail data - missing data from one or both files.")
    
    # Summary data comparison
    with comp_tabs[1]:
        df1 = file1_data['summary_df']
        df2 = file2_data['summary_df']
        
        if not df1.empty and not df2.empty:
            st.subheader(f"Summary Data Comparison: {file1_name} vs {file2_name}")
            
            # Find common columns
            common_cols = list(set(df1.columns).intersection(set(df2.columns)))
            
            if 'wbe_code' in common_cols:
                # Prepare for merge to show differences
                df1_subset = df1[common_cols].copy()
                df2_subset = df2[common_cols].copy()
                
                # Format any float columns with thousands and decimal separators
                for col in common_cols:
                    if df1_subset[col].dtype in ['float64', 'float32']:
                        df1_subset[col] = df1_subset[col].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else x)
                    if df2_subset[col].dtype in ['float64', 'float32']:
                        df2_subset[col] = df2_subset[col].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else x)
                
                # Add source indicator
                df1_subset['source'] = file1_name
                df2_subset['source'] = file2_name
                
                # Find items unique to each file
                df1_unique = df1_subset[~df1_subset['wbe_code'].isin(df2_subset['wbe_code'])]
                df2_unique = df2_subset[~df2_subset['wbe_code'].isin(df1_subset['wbe_code'])]
                
                # Show unique items
                if not df1_unique.empty or not df2_unique.empty:
                    unique_items = pd.concat([df1_unique, df2_unique])
                    # Reset index to ensure it's unique before styling
                    unique_items = unique_items.reset_index(drop=True)
                    st.write(f"Found {len(unique_items)} summary items that appear in only one file:")
                    st.dataframe(
                        unique_items.style.apply(
                            lambda x: ['background-color: #DDEBF7' if v == file1_name else 'background-color: #E2EFDA' for v in x], 
                            subset=['source']
                        ),
                        use_container_width=True
                    )
                
                # Compare common items - use original data for comparison
                df1_orig = df1[common_cols].copy()
                df2_orig = df2[common_cols].copy()
                
                # Merge data for comparison
                merge_cols = [c for c in common_cols if c != 'wbe_description']  # Exclude description for comparison
                merged_orig = pd.merge(
                    df1_orig, 
                    df2_orig, 
                    on='wbe_code',
                    suffixes=('_1', '_2')
                )
                # Reset index to ensure it's unique for styling
                merged_orig = merged_orig.reset_index(drop=True)
                
                if not merged_orig.empty:
                    # Find numeric columns for comparison
                    numeric_cols = [c for c in common_cols if c in ['quantity', 'wbe_direct_cost', 'wbe_list_price', 'wbe_offer_price', 'wbe_sell_price']]
                    
                    if numeric_cols:
                        diff_rows = merged_orig[merged_orig.filter(like='_1').values != merged_orig.filter(like='_2').values]
                        # Reset index to ensure it's unique for styling
                        diff_rows = diff_rows.reset_index(drop=True)
                        
                        # Format the numeric columns for display - use .loc to avoid SettingWithCopyWarning
                        diff_rows = diff_rows.copy()  # Create an explicit copy to avoid SettingWithCopyWarning
                        for col in numeric_cols:
                            if diff_rows[f'{col}_1'].dtype in ['float64', 'float32']:
                                diff_rows.loc[:, f'{col}_1'] = diff_rows[f'{col}_1'].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else 'N/A')
                            if diff_rows[f'{col}_2'].dtype in ['float64', 'float32']:
                                diff_rows.loc[:, f'{col}_2'] = diff_rows[f'{col}_2'].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else 'N/A')
                        
                        if not diff_rows.empty:
                            st.write(f"Found {len(diff_rows)} summary items with differences between files:")
                            st.dataframe(diff_rows, use_container_width=True)
                        else:
                            st.success("All common summary items are identical between the two files.")
            else:
                st.warning("Cannot compare summary data - no common identifier column found.")
        else:
            st.info("Cannot compare summary data - missing data from one or both files.")

def create_comparison_charts(file1_data, file2_data):
    """Create comparative visualizations between two files"""
    file1_name = file1_data['name']
    file2_name = file2_data['name']
    
    st.subheader("Comparative Visualizations")
    
    # Compare detail data
    detail_df1 = file1_data['detail_df']
    detail_df2 = file2_data['detail_df']
    
    # Compare summary data
    summary_df1 = file1_data['summary_df']
    summary_df2 = file2_data['summary_df']
    
    # Create tabs for different comparison chart types
    chart_tabs = st.tabs(["Summary: Direct Cost Changes", "Detail: Items by Group", "Item Counts", "Price Comparisons", "Distribution Comparisons"])
    
    # New tab for direct cost changes by wbe_code
    with chart_tabs[0]:
        if not summary_df1.empty and not summary_df2.empty and 'wbe_direct_cost' in summary_df1.columns and 'wbe_direct_cost' in summary_df2.columns:
            st.subheader(f"Changes in Direct Cost by WBE Code: {file1_name} vs {file2_name}")
            
            # Get common WBE codes
            common_codes = set(summary_df1['wbe_code']).intersection(set(summary_df2['wbe_code']))
            
            if common_codes:
                # Filter for common codes
                df1_common = summary_df1[summary_df1['wbe_code'].isin(common_codes)]
                df2_common = summary_df2[summary_df2['wbe_code'].isin(common_codes)]
                
                # Merge data for comparison
                merged = pd.merge(
                    df1_common[['wbe_code', 'wbe_description', 'wbe_direct_cost']], 
                    df2_common[['wbe_code', 'wbe_description', 'wbe_direct_cost']],
                    on='wbe_code',
                    suffixes=('_1', '_2')
                )
                
                # Reset index to ensure it's unique for styling
                merged = merged.reset_index(drop=True)
                
                # Calculate direct cost differences
                merged['cost_diff'] = merged['wbe_direct_cost_1'] - merged['wbe_direct_cost_2']
                # Handle division by zero in percentage calculation
                merged['cost_pct_diff'] = merged.apply(
                    lambda row: ((row['wbe_direct_cost_1'] - row['wbe_direct_cost_2']) / row['wbe_direct_cost_2']) * 100 
                    if row['wbe_direct_cost_2'] != 0 else 0, 
                    axis=1
                )
                
                # Format floats with commas and decimals - use .loc to avoid SettingWithCopyWarning
                merged_formatted = merged.copy()  # Create explicit copy to avoid SettingWithCopyWarning
                merged_formatted.loc[:, 'wbe_direct_cost_1'] = merged['wbe_direct_cost_1'].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else 'N/A')
                merged_formatted.loc[:, 'wbe_direct_cost_2'] = merged['wbe_direct_cost_2'].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else 'N/A')
                merged_formatted.loc[:, 'cost_diff'] = merged['cost_diff'].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else 'N/A')
                merged_formatted.loc[:, 'cost_pct_diff'] = merged['cost_pct_diff'].map(lambda x: '{:,.2f}%'.format(x) if pd.notna(x) else 'N/A')
                
                # Sort by percentage difference for better visualization
                merged_sorted = merged.sort_values(by='cost_pct_diff', ascending=False)
                merged_formatted_sorted = merged_formatted.sort_values(by='cost_pct_diff', ascending=False)
                
                # Show tabular data
                st.write("Direct Cost Comparison Table:")
                st.dataframe(
                    merged_formatted_sorted[['wbe_code', 'wbe_description_1', 'wbe_direct_cost_1', 'wbe_direct_cost_2', 'cost_diff', 'cost_pct_diff']], 
                    use_container_width=True
                )
                
                # Create visualization for direct cost comparison
                # First, create a copy for plotting (with numeric values)
                plot_data = pd.merge(
                    df1_common[['wbe_code', 'wbe_description', 'wbe_direct_cost']], 
                    df2_common[['wbe_code', 'wbe_description', 'wbe_direct_cost']],
                    on='wbe_code',
                    suffixes=('_1', '_2')
                )
                plot_data['cost_diff'] = plot_data['wbe_direct_cost_1'] - plot_data['wbe_direct_cost_2']
                # Handle division by zero in percentage calculation
                plot_data['cost_pct_diff'] = plot_data.apply(
                    lambda row: ((row['wbe_direct_cost_1'] - row['wbe_direct_cost_2']) / row['wbe_direct_cost_2']) * 100 
                    if row['wbe_direct_cost_2'] != 0 else 0, 
                    axis=1
                )
                
                # Sort by percentage difference and get top/bottom 10
                top_bottom = pd.concat([
                    plot_data.nlargest(10, 'cost_pct_diff'),
                    plot_data.nsmallest(10, 'cost_pct_diff')
                ]).drop_duplicates()
                
                # Create bar chart of percentage differences
                fig = px.bar(
                    top_bottom,
                    x='wbe_code',
                    y='cost_pct_diff',
                    color='cost_pct_diff',
                    color_continuous_scale='RdBu_r',
                    labels={'cost_pct_diff': 'Direct Cost % Change', 'wbe_code': 'WBE Code'},
                    title='Top Changes in Direct Cost (Percentage)',
                    hover_data=['wbe_description_1', 'wbe_direct_cost_1', 'wbe_direct_cost_2', 'cost_diff']
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
                # Create scatter plot comparing costs
                fig = px.scatter(
                    plot_data,
                    x='wbe_direct_cost_1',
                    y='wbe_direct_cost_2',
                    hover_name='wbe_code',
                    hover_data=['wbe_description_1', 'cost_diff', 'cost_pct_diff'],
                    size=abs(plot_data['cost_pct_diff']).fillna(0) + 1,  # Add 1 to ensure no zero sizes and handle NaN
                    color='cost_pct_diff',
                    color_continuous_scale='RdBu_r',
                    title=f'Direct Cost Comparison: {file1_name} vs {file2_name}',
                    labels={
                        'wbe_direct_cost_1': f'{file1_name} Direct Cost',
                        'wbe_direct_cost_2': f'{file2_name} Direct Cost'
                    }
                )
                
                # Add diagonal reference line
                fig.add_trace(
                    go.Scatter(
                        x=[plot_data['wbe_direct_cost_1'].min(), plot_data['wbe_direct_cost_1'].max()],
                        y=[plot_data['wbe_direct_cost_1'].min(), plot_data['wbe_direct_cost_1'].max()],
                        mode='lines',
                        line=dict(color='green', dash='dash'),
                        name='Equal Cost Line'
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Cannot compare direct costs - missing data from one or both files.")
    
    # New tab for item changes by wbe_group_desc
    with chart_tabs[1]:
        if not detail_df1.empty and not detail_df2.empty and 'wbe_group_desc' in detail_df1.columns and 'wbe_group_desc' in detail_df2.columns:
            st.subheader(f"Changes in Items by WBE Group: {file1_name} vs {file2_name}")
            
            # Count items by group for each file
            group_counts1 = detail_df1['wbe_group_desc'].value_counts().reset_index()
            group_counts1.columns = ['WBE Group', 'Count']
            group_counts1['Source'] = file1_name
            
            group_counts2 = detail_df2['wbe_group_desc'].value_counts().reset_index()
            group_counts2.columns = ['WBE Group', 'Count']
            group_counts2['Source'] = file2_name
            
            # Merge the counts for comparison
            merged_counts = pd.merge(
                group_counts1, 
                group_counts2, 
                on='WBE Group', 
                suffixes=('_1', '_2')
            )
            
            # Calculate differences
            merged_counts['diff'] = merged_counts['Count_1'] - merged_counts['Count_2']
            merged_counts['pct_diff'] = ((merged_counts['Count_1'] - merged_counts['Count_2']) / merged_counts['Count_2']) * 100
            
            # Sort by difference
            merged_counts = merged_counts.sort_values(by='diff', ascending=False)
            
            # Format percentage with commas and decimals
            merged_counts['pct_diff'] = merged_counts['pct_diff'].map(lambda x: '{:,.2f}%'.format(x) if pd.notna(x) else 'N/A')
            
            # Show tabular data
            st.write("Item Count Changes by WBE Group:")
            st.dataframe(
                merged_counts[['WBE Group', 'Count_1', 'Count_2', 'diff', 'pct_diff']], 
                use_container_width=True
            )
            
            # Combine for plotting
            combined_counts = pd.concat([group_counts1, group_counts2])
            
            # Create grouped bar chart
            fig = px.bar(
                combined_counts, 
                x='WBE Group', 
                y='Count',
                color='Source',
                barmode='group',
                title=f'Item Counts by WBE Group: {file1_name} vs {file2_name}',
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Create a chart showing the differences
            fig = px.bar(
                merged_counts,
                x='WBE Group',
                y='diff',
                color='diff',
                color_continuous_scale='RdBu_r',
                title=f'Difference in Item Counts by WBE Group: {file1_name} - {file2_name}'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Cannot compare items by WBE Group - missing data from one or both files.")
    
    with chart_tabs[2]:
        # Compare item counts if we have detail data
        if not detail_df1.empty and not detail_df2.empty and 'wbe_group_code' in detail_df1.columns and 'wbe_group_code' in detail_df2.columns:
            # Get counts by group for each file
            group_counts1 = detail_df1['wbe_group_code'].value_counts().reset_index()
            group_counts1.columns = ['WBE Group', 'Count']
            group_counts1['Source'] = file1_name
            
            group_counts2 = detail_df2['wbe_group_code'].value_counts().reset_index()
            group_counts2.columns = ['WBE Group', 'Count']
            group_counts2['Source'] = file2_name
            
            # Combine for plotting
            combined_counts = pd.concat([group_counts1, group_counts2])
            
            # Create grouped bar chart
            fig = px.bar(
                combined_counts, 
                x='WBE Group', 
                y='Count',
                color='Source',
                barmode='group',
                title=f'Item Counts by WBE Group: {file1_name} vs {file2_name}',
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with chart_tabs[3]:
        # Price comparisons using summary data
        if not summary_df1.empty and not summary_df2.empty:
            if 'wbe_list_price' in summary_df1.columns and 'wbe_list_price' in summary_df2.columns:
                # Create box plots for price comparison
                fig = go.Figure()
                
                # Add box plot for file 1
                fig.add_trace(go.Box(
                    y=summary_df1['wbe_list_price'].dropna(),
                    name=f"{file1_name} List Price",
                    boxmean=True,
                    marker_color='#636EFA'
                ))
                
                # Add box plot for file 2
                fig.add_trace(go.Box(
                    y=summary_df2['wbe_list_price'].dropna(),
                    name=f"{file2_name} List Price",
                    boxmean=True,
                    marker_color='#EF553B'
                ))
                
                # Update layout
                fig.update_layout(
                    title=f'List Price Distribution Comparison: {file1_name} vs {file2_name}',
                    yaxis_title='List Price'
                )
                st.plotly_chart(fig, use_container_width=True)
                
            # Compare price columns if available
            price_cols = [col for col in summary_df1.columns if 'price' in col.lower()]
            price_cols = [col for col in price_cols if col in summary_df2.columns]
            
            if price_cols and 'wbe_code' in summary_df1.columns and 'wbe_code' in summary_df2.columns:
                # Get common WBE codes
                common_codes = set(summary_df1['wbe_code']).intersection(set(summary_df2['wbe_code']))
                
                if common_codes:
                    # Filter for common codes
                    df1_common = summary_df1[summary_df1['wbe_code'].isin(common_codes)]
                    df2_common = summary_df2[summary_df2['wbe_code'].isin(common_codes)]
                    
                    # Merge data for comparison
                    merged = pd.merge(
                        df1_common[['wbe_code', 'wbe_description'] + price_cols], 
                        df2_common[['wbe_code', 'wbe_description'] + price_cols],
                        on='wbe_code',
                        suffixes=('_1', '_2')
                    )
                    
                    if not merged.empty:
                        # Calculate price differences
                        for col in price_cols:
                            merged[f'{col}_diff'] = merged[f'{col}_1'] - merged[f'{col}_2']
                            merged[f'{col}_pct_diff'] = ((merged[f'{col}_1'] - merged[f'{col}_2']) / merged[f'{col}_2']) * 100
                        
                        # Find items with significant differences
                        sig_diff = merged[merged[f'{price_cols[0]}_pct_diff'].abs() > 1]  # >1% difference
                        
                        if not sig_diff.empty:
                            st.write(f"Items with significant price differences (>1%):")
                            
                            # Create a scatter plot showing price differences
                            fig = px.scatter(
                                sig_diff,
                                x=f'{price_cols[0]}_1',
                                y=f'{price_cols[0]}_2',
                                hover_data=['wbe_code', 'wbe_description_1', f'{price_cols[0]}_diff', f'{price_cols[0]}_pct_diff'],
                                size=sig_diff[f'{price_cols[0]}_pct_diff'].abs(),
                                color=sig_diff[f'{price_cols[0]}_pct_diff'],
                                color_continuous_scale='RdBu_r',
                                title=f'Price Comparison: {file1_name} vs {file2_name}',
                                labels={
                                    f'{price_cols[0]}_1': f'{file1_name} Price',
                                    f'{price_cols[0]}_2': f'{file2_name} Price'
                                }
                            )
                            
                            # Add diagonal reference line
                            fig.add_trace(
                                go.Scatter(
                                    x=[sig_diff[f'{price_cols[0]}_1'].min(), sig_diff[f'{price_cols[0]}_1'].max()],
                                    y=[sig_diff[f'{price_cols[0]}_1'].min(), sig_diff[f'{price_cols[0]}_1'].max()],
                                    mode='lines',
                                    line=dict(color='green', dash='dash'),
                                    name='Equal Price Line'
                                )
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Show table with significant differences
                            cols_to_show = ['wbe_code', 'wbe_description_1']
                            for col in price_cols:
                                cols_to_show.extend([f'{col}_1', f'{col}_2', f'{col}_diff', f'{col}_pct_diff'])
                            
                            st.dataframe(sig_diff[cols_to_show], use_container_width=True)
    
    with chart_tabs[4]:
        # Distribution comparisons
        if not detail_df1.empty and not detail_df2.empty:
            if 'wbe_type_code' in detail_df1.columns and 'wbe_type_code' in detail_df2.columns:
                # Count by type for each file
                type_counts1 = detail_df1['wbe_type_code'].value_counts().reset_index()
                type_counts1.columns = ['WBE Type', 'Count']
                type_counts1['Source'] = file1_name
                
                type_counts2 = detail_df2['wbe_type_code'].value_counts().reset_index()
                type_counts2.columns = ['WBE Type', 'Count']
                type_counts2['Source'] = file2_name
                
                # Combine data
                combined = pd.concat([type_counts1, type_counts2])
                
                # Create stacked bar chart
                fig = px.bar(
                    combined,
                    x='WBE Type',
                    y='Count',
                    color='Source',
                    barmode='group',
                    title=f'Distribution of Items by Type: {file1_name} vs {file2_name}'
                )
                st.plotly_chart(fig, use_container_width=True)

def create_visualizations(detail_df, summary_df, file_name):
    """Create interactive visualizations based on the data for a single file"""
    st.header(f"Data Visualizations - {file_name}")
    
    # Create tabs for different visualization categories
    viz_tabs = st.tabs(["Detail Analysis", "Summary Analysis"])
    
    with viz_tabs[0]:
        if not detail_df.empty:
            st.subheader("Detail Data Analysis")
            
            # Group data visualization
            if 'wbe_group_code' in detail_df.columns:
                # Count items by group
                group_counts = detail_df['wbe_group_code'].value_counts().reset_index()
                group_counts.columns = ['WBE Group', 'Count']
                
                fig = px.bar(
                    group_counts, 
                    x='WBE Group', 
                    y='Count',
                    title='Number of Items by WBE Group',
                    color='WBE Group'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Type and subtype analysis
            if 'wbe_type_code' in detail_df.columns and 'wbe_item_quantity' in detail_df.columns:
                # Group by type and sum quantities
                type_qty = detail_df.groupby('wbe_type_code')['wbe_item_quantity'].sum().reset_index()
                type_qty.columns = ['WBE Type', 'Total Quantity']
                
                fig = px.pie(
                    type_qty, 
                    values='Total Quantity', 
                    names='WBE Type',
                    title='Distribution of Quantities by WBE Type',
                    hole=0.4
                )
                fig.update_traces(texttemplate='%{value:,.2f}', textposition='inside')
                st.plotly_chart(fig, use_container_width=True)
            
            # Price analysis if price data is available
            if 'wbe_item_list_price' in detail_df.columns:
                # Filter out rows with null prices
                price_data = detail_df.dropna(subset=['wbe_item_list_price'])
                if not price_data.empty:
                    fig = px.histogram(
                        price_data,
                        x='wbe_item_list_price',
                        title='Distribution of List Prices',
                        nbins=20
                    )
                    fig.update_layout(xaxis_tickformat=',.2f')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display statistics with formatted numbers
                    stats = price_data['wbe_item_list_price'].describe()
                    stats_df = pd.DataFrame({
                        'Statistic': stats.index,
                        'Value': stats.values
                    })
                    stats_df['Value'] = stats_df['Value'].map(lambda x: '{:,.2f}'.format(x) if isinstance(x, (int, float)) else x)
                    st.write("Price Statistics:")
                    st.dataframe(stats_df, use_container_width=True)
        else:
            st.info("No detail data available for visualization.")
    
    with viz_tabs[1]:
        if not summary_df.empty:
            st.subheader("Summary Data Analysis")
            
            # Check if we have price columns to analyze
            price_cols = [col for col in summary_df.columns if 'price' in col.lower()]
            if price_cols:
                # Create a box plot for price distributions
                fig = px.box(
                    summary_df,
                    y=price_cols,
                    title='Distribution of Prices',
                    points="all"
                )
                fig.update_layout(yaxis_tickformat=',.2f')
                st.plotly_chart(fig, use_container_width=True)
                
                # Display statistics with formatted numbers
                st.write("Price Statistics:")
                for col in price_cols:
                    if summary_df[col].dtype in ['float64', 'float32']:
                        stats = summary_df[col].describe()
                        stats_df = pd.DataFrame({
                            'Statistic': stats.index,
                            'Value': stats.values
                        })
                        stats_df['Value'] = stats_df['Value'].map(lambda x: '{:,.2f}'.format(x) if isinstance(x, (int, float)) else x)
                        st.write(f"{col} Statistics:")
                        st.dataframe(stats_df, use_container_width=True)
            
            # Quantity analysis
            if 'quantity' in summary_df.columns:
                # Scatter plot of quantity vs price if both exist
                if 'wbe_list_price' in summary_df.columns:
                    fig = px.scatter(
                        summary_df,
                        x='quantity',
                        y='wbe_list_price',
                        title='Quantity vs. List Price',
                        color='wbe_code' if 'wbe_code' in summary_df.columns else None,
                        size='wbe_list_price' if 'wbe_list_price' in summary_df.columns else None,
                        hover_data=['wbe_description'] if 'wbe_description' in summary_df.columns else None
                    )
                    fig.update_layout(
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
                    stats_df['Value'] = stats_df['Value'].map(lambda x: '{:,.2f}'.format(x) if isinstance(x, (int, float)) else x)
                    st.write("Quantity Statistics:")
                    st.dataframe(stats_df, use_container_width=True)
        else:
            st.info("No summary data available for visualization.")

def main():
    """Main application function"""
    # Set up the page
    setup_page()
    
    # Initialize session state for file storage
    if 'files' not in st.session_state:
        st.session_state.files = {}
    
    # Sidebar for file upload and options
    with st.sidebar:
        st.header("Upload Data")
        uploaded_files = st.file_uploader("Choose Excel files", type=['xlsx', 'xls', 'xlsm'], accept_multiple_files=True)
        
        if uploaded_files:
            # Process each uploaded file
            for uploaded_file in uploaded_files:
                # Generate a unique identifier for this file
                file_id = str(uuid.uuid4())
                file_name = uploaded_file.name
                
                # Check if we've already processed this file
                existing_ids = [fid for fid, fdata in st.session_state.files.items() 
                               if fdata['name'] == file_name]
                
                if not existing_ids:
                    # Save file temporarily
                    with st.spinner(f"Processing {file_name}..."):
                        file_path = save_uploaded_file(uploaded_file)
                        
                        if file_path:
                            # Process the file
                            detail_df, summary_df = process_data(file_path)
                            
                            # Store in session state
                            st.session_state.files[file_id] = {
                                'name': file_name,
                                'path': file_path,
                                'detail_df': detail_df,
                                'summary_df': summary_df,
                                'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            
                            # Clean up temporary file
                            try:
                                os.unlink(file_path)
                            except:
                                pass
                else:
                    st.info(f"File {file_name} already uploaded.")
        
        st.divider()
        
        # Options section
        st.header("Options")
        show_tables = st.checkbox("Show Data Tables", value=True)
        show_viz = st.checkbox("Show Visualizations", value=True)
        
        # Clear files button
        if st.button("Clear All Files"):
            st.session_state.files = {}
            st.experimental_rerun()
    
    # Main area - File selection and viewing
    if st.session_state.files:
        st.header("Uploaded Files")
        
        # Display the list of uploaded files
        file_table = []
        for file_id, file_data in st.session_state.files.items():
            file_table.append({
                "ID": file_id,
                "Filename": file_data['name'],
                "Detail Items": len(file_data['detail_df']),
                "Summary Items": len(file_data['summary_df']),
                "Upload Time": file_data['upload_time']
            })
        
        st.dataframe(pd.DataFrame(file_table).set_index("ID"), use_container_width=True)
        
        # Analysis mode selection
        st.subheader("Analysis Mode")
        analysis_mode = st.radio(
            "Choose analysis mode:",
            options=["Single File Analysis", "File Comparison"],
            horizontal=True,
            index=0
        )
        
        if analysis_mode == "Single File Analysis":
            # Single file selection
            file_ids = list(st.session_state.files.keys())
            file_names = [st.session_state.files[fid]['name'] for fid in file_ids]
            
            selected_idx = st.selectbox(
                "Select a file to analyze:",
                range(len(file_ids)),
                format_func=lambda i: file_names[i]
            )
            
            selected_file_id = file_ids[selected_idx]
            selected_file_data = st.session_state.files[selected_file_id]
            
            # Display single file data
            if show_tables:
                show_data_tables(
                    selected_file_data['detail_df'],
                    selected_file_data['summary_df'],
                    selected_file_data['name']
                )
            
            if show_viz:
                create_visualizations(
                    selected_file_data['detail_df'],
                    selected_file_data['summary_df'],
                    selected_file_data['name']
                )
        
        else:  # File Comparison mode
            if len(st.session_state.files) < 2:
                st.warning("You need at least 2 files to use comparison mode.")
            else:
                # File selection for comparison
                file_ids = list(st.session_state.files.keys())
                file_names = [st.session_state.files[fid]['name'] for fid in file_ids]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_idx1 = st.selectbox(
                        "Select first file:",
                        range(len(file_ids)),
                        format_func=lambda i: file_names[i],
                        key="file1"
                    )
                
                with col2:
                    # Create a list excluding the first selection
                    remaining_indices = [i for i in range(len(file_ids)) if i != selected_idx1]
                    selected_idx2 = st.selectbox(
                        "Select second file:",
                        remaining_indices,
                        format_func=lambda i: file_names[i],
                        key="file2"
                    )
                
                selected_file_id1 = file_ids[selected_idx1]
                selected_file_id2 = file_ids[selected_idx2]
                
                file1_data = st.session_state.files[selected_file_id1]
                file2_data = st.session_state.files[selected_file_id2]
                
                # Display comparison
                if show_tables:
                    show_comparison_tables(file1_data, file2_data)
                
                if show_viz:
                    create_comparison_charts(file1_data, file2_data)
    else:
        # Show instructions when no files are uploaded
        st.info("Please upload Excel files using the sidebar to get started.")
        
        # Sample visualizations or placeholder
        st.markdown("""
        ## What you can do with this app
        
        1. **Upload Multiple Excel Files**: Upload multiple PRE Excel files to extract and compare data.
        2. **View Individual Files**: Explore each file's data in interactive tables and charts.
        3. **Compare Files**: Select any two files to see differences in both tabular and graphical format.
        4. **Download Results**: Export processed data as CSV files for further analysis.
        
        The app supports comparison of:
        - Items present in one file but not the other
        - Differences in prices, quantities, and other numeric values
        - Distribution differences across item types and groups
        """)

if __name__ == "__main__":
    main() 
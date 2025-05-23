import streamlit as st
import pandas as pd
from config import SUMMARY_FIELD_DISPLAY_NAMES, DETAIL_FIELD_DISPLAY_NAMES, format_value

def show_data_tables(detail_df, summary_df, file_name):
    """Display the data tables with expanded options for a single file"""
    tabs = st.tabs([f"Summary Data - {file_name}", f"Detail Data - {file_name}"])
    
    with tabs[1]:
        if not detail_df.empty:
            st.subheader(f"Detailed Data - {file_name}")
            display_df = detail_df.copy(deep=True)
            for col in display_df.columns:
                display_df[col] = display_df[col].map(lambda x: format_value(col, x, 'detail'))
            display_df.columns = [DETAIL_FIELD_DISPLAY_NAMES.get(col, {'display_name': col})['display_name'] for col in display_df.columns]
            st.dataframe(display_df, use_container_width=True)
            st.download_button(
                label="Download Detail Data as CSV",
                data=detail_df.to_csv(index=False).encode('utf-8'),
                file_name=f'detail_data_{file_name}.csv',
                mime='text/csv',
            )
        else:
            st.info(f"No detail data available for {file_name}.")
    
    with tabs[0]:
        if not summary_df.empty:
            st.subheader(f"Summary Data - {file_name}")
            display_df = summary_df.copy(deep=True)
            for col in display_df.columns:
                display_df[col] = display_df[col].map(lambda x: format_value(col, x, 'summary'))
            display_df.columns = [SUMMARY_FIELD_DISPLAY_NAMES.get(col, {'display_name': col})['display_name'] for col in display_df.columns]
            st.dataframe(display_df, use_container_width=True)
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
                
                # Add source indicator
                df1_subset['source'] = file1_name
                df2_subset['source'] = file2_name
                
                # Find items unique to each file
                df1_unique = df1_subset[~df1_subset['wbe_item_code'].isin(df2_subset['wbe_item_code'])]
                df2_unique = df2_subset[~df2_subset['wbe_item_code'].isin(df1_subset['wbe_item_code'])]
                
                # Show unique items
                if not df1_unique.empty or not df2_unique.empty:
                    unique_items = pd.concat([df1_unique, df2_unique])
                    # Reset index to ensure it's unique before styling
                    unique_items = unique_items.reset_index(drop=True)
                    # Create a display DataFrame for formatting
                    display_unique = unique_items.copy()
                    for col in display_unique.columns:
                        display_type = DETAIL_FIELD_DISPLAY_NAMES.get(col, {}).get('type', None)
                        if display_type == 'float':
                            display_unique[col] = display_unique[col].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else x)
                    # Rename columns using display names
                    display_unique.columns = [DETAIL_FIELD_DISPLAY_NAMES.get(col, {"display_name": col})["display_name"] for col in display_unique.columns]
                    st.write(f"Found {len(display_unique)} items that appear in only one file:")
                    st.dataframe(
                        display_unique.style.apply(
                            lambda x: ['background-color: #DDEBF7' if v == file1_name else 'background-color: #E2EFDA' for v in x], 
                            subset=['source']
                        ),
                        use_container_width=True
                    )
                
                # Compare common items
                df1_common = df1_subset[df1_subset['wbe_item_code'].isin(df2_subset['wbe_item_code'])]
                df2_common = df2_subset[df2_subset['wbe_item_code'].isin(df1_subset['wbe_item_code'])]
                
                # Merge data for comparison
                merge_cols = [c for c in common_cols if c != 'wbe_item_description']  # Exclude description for comparison
                merged = pd.merge(
                    df1_common, 
                    df2_common, 
                    on='wbe_item_code',
                    suffixes=('_1', '_2')
                )
                
                # Find differences
                diff_mask = (merged.filter(like='_1').values != merged.filter(like='_2').values)
                diff_rows = merged[diff_mask.any(axis=1)]
                
                if not diff_rows.empty:
                    # Create a display DataFrame for formatting
                    display_diff = diff_rows.copy()
                    for col in display_diff.columns:
                        base_col = col.split('_')[0]
                        display_type = DETAIL_FIELD_DISPLAY_NAMES.get(base_col, {}).get('type', None)
                        if display_type == 'float':
                            display_diff[col] = display_diff[col].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else x)
                    # Rename columns using display names
                    display_diff.columns = [DETAIL_FIELD_DISPLAY_NAMES.get(col.split('_')[0], {"display_name": col})["display_name"] + (' (File 1)' if col.endswith('_1') else ' (File 2)') 
                                       if col != 'wbe_item_code' else DETAIL_FIELD_DISPLAY_NAMES.get(col, {"display_name": col})["display_name"]
                                       for col in display_diff.columns]
                    st.write(f"Found {len(display_diff)} items with differences between files:")
                    st.dataframe(display_diff, use_container_width=True)
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
                    # Create a display DataFrame for formatting
                    display_unique = unique_items.copy()
                    for col in display_unique.columns:
                        display_type = SUMMARY_FIELD_DISPLAY_NAMES.get(col, {}).get('type', None)
                        if display_type == 'float':
                            display_unique[col] = display_unique[col].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else x)
                    # Rename columns using display names
                    display_unique.columns = [SUMMARY_FIELD_DISPLAY_NAMES.get(col, {"display_name": col})["display_name"] for col in display_unique.columns]
                    st.write(f"Found {len(display_unique)} summary items that appear in only one file:")
                    st.dataframe(
                        display_unique.style.apply(
                            lambda x: ['background-color: #DDEBF7' if v == file1_name else 'background-color: #E2EFDA' for v in x], 
                            subset=['source']
                        ),
                        use_container_width=True
                    )
                
                # Compare common items
                df1_common = df1_subset[df1_subset['wbe_code'].isin(df2_subset['wbe_code'])]
                df2_common = df2_subset[df2_subset['wbe_code'].isin(df1_subset['wbe_code'])]
                
                # Merge data for comparison
                merge_cols = [c for c in common_cols if c != 'wbe_description']  # Exclude description for comparison
                merged = pd.merge(
                    df1_common, 
                    df2_common, 
                    on='wbe_code',
                    suffixes=('_1', '_2')
                )
                
                # Find differences
                diff_mask = (merged.filter(like='_1').values != merged.filter(like='_2').values)
                diff_rows = merged[diff_mask.any(axis=1)]
                
                if not diff_rows.empty:
                    # Create a display DataFrame for formatting
                    display_diff = diff_rows.copy()
                    for col in display_diff.columns:
                        base_col = col.split('_')[0]
                        display_type = SUMMARY_FIELD_DISPLAY_NAMES.get(base_col, {}).get('type', None)
                        if display_type == 'float':
                            display_diff[col] = display_diff[col].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else x)
                    # Rename columns using display names
                    display_diff.columns = [SUMMARY_FIELD_DISPLAY_NAMES.get(col.split('_')[0], {"display_name": col})["display_name"] + (' (File 1)' if col.endswith('_1') else ' (File 2)') 
                                       if col != 'wbe_code' else SUMMARY_FIELD_DISPLAY_NAMES.get(col, {"display_name": col})["display_name"]
                                       for col in display_diff.columns]
                    st.write(f"Found {len(display_diff)} summary items with differences between files:")
                    st.dataframe(display_diff, use_container_width=True)
                else:
                    st.success("All common summary items are identical between the two files.")
            else:
                st.warning("Cannot compare summary data - no common identifier column found.")
        else:
            st.info("Cannot compare summary data - missing data from one or both files.") 
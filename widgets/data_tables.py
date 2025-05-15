import streamlit as st
import pandas as pd
from config import SUMMARY_FIELD_DISPLAY_NAMES, DETAIL_FIELD_DISPLAY_NAMES, CURRENCY_FORMAT, QUANTITY_FORMAT

def show_data_tables(detail_df, summary_df, file_name):
    """Display the data tables with expanded options for a single file"""
    tabs = st.tabs([f"Detail Data - {file_name}", f"Summary Data - {file_name}"])
    
    with tabs[0]:
        if not detail_df.empty:
            st.subheader(f"Detailed Data - {file_name}")
            display_df = detail_df.copy(deep=True)
            for col in display_df.columns:
                if 'price' in col.lower() or 'cost' in col.lower() or 'eur' in col.lower():
                    display_df[col] = display_df[col].astype('object')
                    display_df[col] = display_df[col].map(lambda x: CURRENCY_FORMAT(x) if pd.notna(x) else '')
                elif 'quantity' in col.lower() or 'qty' in col.lower():
                    display_df[col] = display_df[col].astype('object')
                    display_df[col] = display_df[col].map(lambda x: QUANTITY_FORMAT.format(x) if pd.notna(x) else '')
            display_df.columns = [DETAIL_FIELD_DISPLAY_NAMES.get(col, col) for col in display_df.columns]
            st.dataframe(display_df, use_container_width=True)
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
            display_df = summary_df.copy(deep=True)
            for col in display_df.columns:
                if 'price' in col.lower() or 'cost' in col.lower() or 'eur' in col.lower():
                    display_df[col] = display_df[col].astype('object')
                    display_df[col] = display_df[col].map(lambda x: CURRENCY_FORMAT(x) if pd.notna(x) else '')
                elif 'quantity' in col.lower() or 'qty' in col.lower():
                    display_df[col] = display_df[col].astype('object')
                    display_df[col] = display_df[col].map(lambda x: QUANTITY_FORMAT.format(x) if pd.notna(x) else '')
            display_df.columns = [SUMMARY_FIELD_DISPLAY_NAMES.get(col, col) for col in display_df.columns]
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
                
                # Format any float columns with thousands and decimal separators
                for col in common_cols:
                    if df1_subset[col].dtype in ['float64', 'float32']:
                        df1_subset.loc[:, col] = df1_subset[col].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else x)
                    if df2_subset[col].dtype in ['float64', 'float32']:
                        df2_subset.loc[:, col] = df2_subset[col].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else x)
                
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
                    # Rename columns using display names
                    unique_items.columns = [DETAIL_FIELD_DISPLAY_NAMES.get(col, col) for col in unique_items.columns]
                    st.write(f"Found {len(unique_items)} items that appear in only one file:")
                    st.dataframe(
                        unique_items.style.apply(
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
                diff_rows = merged[merged.filter(like='_1').values != merged.filter(like='_2').values]
                
                if not diff_rows.empty:
                    # Rename columns using display names
                    diff_rows.columns = [DETAIL_FIELD_DISPLAY_NAMES.get(col.split('_')[0], col) + (' (File 1)' if col.endswith('_1') else ' (File 2)') 
                                       if col != 'wbe_item_code' else DETAIL_FIELD_DISPLAY_NAMES.get(col, col)
                                       for col in diff_rows.columns]
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
                        df1_subset.loc[:, col] = df1_subset[col].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else x)
                    if df2_subset[col].dtype in ['float64', 'float32']:
                        df2_subset.loc[:, col] = df2_subset[col].map(lambda x: '{:,.2f}'.format(x) if pd.notna(x) else x)
                
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
                    # Rename columns using display names
                    unique_items.columns = [SUMMARY_FIELD_DISPLAY_NAMES.get(col, col) for col in unique_items.columns]
                    st.write(f"Found {len(unique_items)} summary items that appear in only one file:")
                    st.dataframe(
                        unique_items.style.apply(
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
                diff_rows = merged[merged.filter(like='_1').values != merged.filter(like='_2').values]
                
                if not diff_rows.empty:
                    # Rename columns using display names
                    diff_rows.columns = [SUMMARY_FIELD_DISPLAY_NAMES.get(col.split('_')[0], col) + (' (File 1)' if col.endswith('_1') else ' (File 2)') 
                                       if col != 'wbe_code' else SUMMARY_FIELD_DISPLAY_NAMES.get(col, col)
                                       for col in diff_rows.columns]
                    st.write(f"Found {len(diff_rows)} summary items with differences between files:")
                    st.dataframe(diff_rows, use_container_width=True)
                else:
                    st.success("All common summary items are identical between the two files.")
            else:
                st.warning("Cannot compare summary data - no common identifier column found.")
        else:
            st.info("Cannot compare summary data - missing data from one or both files.") 
import streamlit as st
import pandas as pd
import numpy as np
from config import SUMMARY_FIELD_DISPLAY_NAMES, format_value

def show_table_difference(df1, df2, key_column, data_columns, df1_title="Dataset 1", df2_title="Dataset 2"):
    """
    Display a side by side comparison of two dataframes with indicators for numeric changes.
    
    Args:
        df1 (pd.DataFrame): First dataframe
        df2 (pd.DataFrame): Second dataframe
        key_column (str): Column name to use as the key for linking rows
        data_columns (list): List of column names to compare
        df1_title (str): Title for the first dataframe
        df2_title (str): Title for the second dataframe
    """
    if not isinstance(df1, pd.DataFrame) or not isinstance(df2, pd.DataFrame):
        st.error("Both inputs must be pandas DataFrames")
        return
    
    if key_column not in df1.columns or key_column not in df2.columns:
        st.error(f"Key column '{key_column}' must exist in both dataframes")
        return
    
    # Ensure all data columns exist in both dataframes
    for col in data_columns:
        if col not in df1.columns or col not in df2.columns:
            st.error(f"Column '{col}' must exist in both dataframes")
            return
    
    # Merge dataframes on key column
    merged = pd.merge(
        df1[[key_column] + data_columns], 
        df2[[key_column] + data_columns], 
        on=key_column, 
        how='outer',
        suffixes=('_df1', '_df2')
    )
    
    # Create comparison dataframe
    comparison_data = []
    
    # Use display names from config if available
    display_key = SUMMARY_FIELD_DISPLAY_NAMES.get(key_column, {'display_name': key_column})['display_name']
    
    for _, row in merged.iterrows():
        key_value = row[key_column]
        row_data = {display_key: key_value}
        
        for col in data_columns:
            col_df1 = f"{col}_df1"
            col_df2 = f"{col}_df2"
            
            # Get values (handle NaN)
            val1 = row[col_df1] if not pd.isna(row[col_df1]) else None
            val2 = row[col_df2] if not pd.isna(row[col_df2]) else None
            
            # Get display name from config if available
            display_col = SUMMARY_FIELD_DISPLAY_NAMES.get(col, {'display_name': col})['display_name']
            
            # Format column headers with line breaks to limit width
            # Use shorter titles to help with width
            col1_header = f"{display_col}\n({df1_title})"
            col2_header = f"{display_col}\n({df2_title})"
            
            row_data[col1_header] = format_value(col, val1, 'summary')
            row_data[col2_header] = format_value(col, val2, 'summary')
            
            # Add change indicator for numeric values using icons
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if val1 < val2:
                    row_data[f"Δ {display_col}"] = "↑"  # Increase
                elif val1 > val2:
                    row_data[f"Δ {display_col}"] = "↓"  # Decrease
                else:
                    row_data[f"Δ {display_col}"] = "="  # No change
            elif val1 is None and val2 is not None:
                row_data[f"Δ {display_col}"] = "+"  # Added
            elif val1 is not None and val2 is None:
                row_data[f"Δ {display_col}"] = "-"  # Removed
            else:
                row_data[f"Δ {display_col}"] = ""
                
        comparison_data.append(row_data)
    
    # Create the comparison dataframe
    comparison_df = pd.DataFrame(comparison_data)
    
    # Create a copy for display with formatted values
    display_df = comparison_df.copy()
    
    # Define styling function for the delta column
    def style_delta(val):
        if val == "↑":  # Increase
            return "color: green; font-size: 20px; font-weight: bold;"
        elif val == "↓":  # Decrease
            return "color: red; font-size: 20px; font-weight: bold;"
        elif val == "=":  # No change
            return "color: gray; font-size: 20px;"
        elif val == "+":  # Added
            return "color: blue; font-size: 20px; font-weight: bold;"
        elif val == "-":  # Removed
            return "color: orange; font-size: 20px; font-weight: bold;"
        return ""
    
    # Define column configurations for better width management
    col_config = {
        display_key: st.column_config.TextColumn(
            display_key,
            width="small",
        )
    }
    
    # Configure column widths for all columns
    for col in data_columns:
        display_col = SUMMARY_FIELD_DISPLAY_NAMES.get(col, {'display_name': col})['display_name']
        col1_header = f"{display_col}\n({df1_title})"
        col2_header = f"{display_col}\n({df2_title})"
        delta_col = f"Δ {display_col}"
        
        # Set column widths
        col_config[col1_header] = st.column_config.TextColumn(
            col1_header,
            width="medium",
        )
        col_config[col2_header] = st.column_config.TextColumn(
            col2_header,
            width="medium",
        )
        col_config[delta_col] = st.column_config.TextColumn(
            delta_col,
            width="small",
        )
    
    # Create a styled dataframe with icons
    styled_df = display_df.style.map(
        style_delta,
        subset=[f"Δ {SUMMARY_FIELD_DISPLAY_NAMES.get(col, {'display_name': col})['display_name']}" for col in data_columns]
    )
    
    # Display the dataframe with styling
    st.dataframe(
        styled_df,
        use_container_width=True,
        column_config=col_config,
        hide_index=True,
        height=min(400, len(display_df) * 35 + 38),  # Adjust height based on row count
    )
    
    # Show summary statistics
    st.subheader("Summary of Changes")
    
    # For displaying total sums
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader(f"Totals - {df1_title}")
    with col2:
        st.subheader(f"Totals - {df2_title}")
    with col3:
        st.subheader("Difference")
    
    # Calculate totals for each data column
    for col in data_columns:
        # Get display name
        display_col = SUMMARY_FIELD_DISPLAY_NAMES.get(col, {'display_name': col})['display_name']
        
        # Only process numeric columns
        if pd.api.types.is_numeric_dtype(df1[col]) and pd.api.types.is_numeric_dtype(df2[col]):
            # Calculate sums
            sum1 = df1[col].sum()
            sum2 = df2[col].sum()
            sum_diff = sum2 - sum1
            percent_change = (sum_diff / sum1 * 100) if sum1 != 0 else float('inf')
            
            # Format values
            sum1_formatted = format_value(col, sum1, 'summary')
            sum2_formatted = format_value(col, sum2, 'summary')
            diff_formatted = format_value(col, sum_diff, 'summary')
            
            # Display in columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"{display_col}", sum1_formatted)
            with col2:
                st.metric(f"{display_col}", sum2_formatted)
            with col3:
                # Add arrow to indicate direction
                arrow = "↑" if sum_diff > 0 else "↓" if sum_diff < 0 else "="
                color = "green" if sum_diff > 0 else "red" if sum_diff < 0 else "gray"
                st.markdown(f"<h3 style='color:{color}'>{diff_formatted} {arrow} ({percent_change:.1f}%)</h3>", unsafe_allow_html=True)
    
    # Individual column statistics
    st.subheader("Row-by-Row Change Details")
    
    for col in data_columns:
        # Get display name
        display_col = SUMMARY_FIELD_DISPLAY_NAMES.get(col, {'display_name': col})['display_name']
        
        # Filter to rows where both values exist
        valid_pairs = merged[~pd.isna(merged[f"{col}_df1"]) & ~pd.isna(merged[f"{col}_df2"])]
        
        if len(valid_pairs) > 0 and pd.api.types.is_numeric_dtype(valid_pairs[f"{col}_df1"]):
            # Calculate difference statistics
            increases = sum(valid_pairs[f"{col}_df2"] > valid_pairs[f"{col}_df1"])
            decreases = sum(valid_pairs[f"{col}_df2"] < valid_pairs[f"{col}_df1"])
            unchanged = sum(valid_pairs[f"{col}_df2"] == valid_pairs[f"{col}_df1"])
            
            avg_change = (valid_pairs[f"{col}_df2"] - valid_pairs[f"{col}_df1"]).mean()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(f"{display_col}: Increases", increases)
            with col2:
                st.metric(f"{display_col}: Decreases", decreases)
            with col3:
                st.metric(f"{display_col}: Unchanged", unchanged)
            with col4:
                avg_change_formatted = format_value(col, avg_change, 'summary')
                st.metric(f"{display_col}: Avg Change", avg_change_formatted) 
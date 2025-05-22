import streamlit as st
import pandas as pd
import numpy as np
from widgets.table_difference import show_table_difference

def main():
    st.title("Table Difference Widget Demo")
    
    # Create sample data
    data1 = {
        'ID': [1, 2, 3, 4, 5],
        'Name': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
        'Price': [10.5, 20.0, 15.75, 30.25, 25.0],
        'Quantity': [100, 50, 75, 25, 60],
        'Rating': [4.2, 3.8, 4.5, 4.0, 3.5]
    }
    
    data2 = {
        'ID': [1, 2, 3, 4, 6],  # Note: ID 5 is missing, ID 6 is new
        'Name': ['Product A', 'Product B', 'Product C', 'Product D+', 'Product F'],
        'Price': [10.5, 25.0, 15.75, 32.75, 18.5],  # Some prices changed
        'Quantity': [80, 60, 75, 25, 45],  # Some quantities changed
        'Rating': [4.5, 3.8, 4.5, 3.8, 4.2]  # Some ratings changed
    }
    
    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)
    
    st.subheader("Dataset 1 (Original)")
    st.dataframe(df1)
    
    st.subheader("Dataset 2 (Updated)")
    st.dataframe(df2)
    
    st.subheader("Table Difference Comparison")
    
    # Define key column and data columns to compare
    key_column = "ID"
    data_columns = ["Price", "Quantity", "Rating"]
    
    # Show the table difference widget
    show_table_difference(
        df1, 
        df2, 
        key_column, 
        data_columns, 
        df1_title="Original", 
        df2_title="Updated"
    )
    
    # Example with different data types
    st.subheader("Example with Different Data Types")
    
    # Sample data with different column types
    mixed_data1 = {
        'ID': [101, 102, 103, 104],
        'Product': ['Widget A', 'Widget B', 'Widget C', 'Widget D'],
        'In Stock': [True, False, True, True],
        'Price': [9.99, 14.99, 19.99, 24.99],
        'Launch Date': pd.to_datetime(['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05'])
    }
    
    mixed_data2 = {
        'ID': [101, 102, 103, 105],  # ID 104 removed, 105 added
        'Product': ['Widget A+', 'Widget B', 'Widget C', 'Widget E'],
        'In Stock': [True, True, False, True],  # Some status changed
        'Price': [9.99, 14.99, 24.99, 29.99],
        'Launch Date': pd.to_datetime(['2023-01-15', '2023-02-25', '2023-03-10', '2023-05-01'])
    }
    
    mixed_df1 = pd.DataFrame(mixed_data1)
    mixed_df2 = pd.DataFrame(mixed_data2)
    
    st.dataframe(mixed_df1)
    st.dataframe(mixed_df2)
    
    # Show the table difference widget for mixed data
    show_table_difference(
        mixed_df1,
        mixed_df2,
        "ID",
        ["Price", "In Stock"],
        df1_title="Before",
        df2_title="After"
    )

if __name__ == "__main__":
    main() 
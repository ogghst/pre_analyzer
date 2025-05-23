import pandas as pd
import os
import numpy as np

def create_test_excel():
    """
    Create a test Excel file in the expected format with sample data.
    """
    # Create a dataframe for the test data
    data = []
    
    # Add header row
    data.append(['COD', None, None, None, None, None, None])
    
    # Group 1
    data.append([None, None, 'G1', 'Group 1', None, None, None])
    
    # Type 1
    data.append([None, None, 'T1', 'Type 1', None, None, None])
    
    # Item 1 in Type 1
    data.append([None, '1', 'I1', 'Item 1', 10, 100, 1000])
    
    # Item 2 in Type 1
    data.append([None, '2', 'I2', 'Item 2', 5, 200, 1000])
    
    # Empty row
    data.append([None, None, None, None, None, None, None])
    
    # Type 2
    data.append([None, None, 'T2', 'Type 2', None, None, None])
    
    # Item 3 in Type 2
    data.append([None, '3', 'I3', 'Item 3', 2, 300, 600])
    
    # Installation item
    data.append(['E1', None, None, 'Installation 1', None, None, None, 500])
    
    # Empty rows
    for _ in range(15):
        data.append([None, None, None, None, None, None, None])
    
    # New group
    data.append(['COD', None, None, None, None, None, None])
    data.append([None, None, 'G2', 'Group 2', None, None, None])
    
    # Type in Group 2
    data.append([None, None, 'T3', 'Type 3', None, None, None])
    
    # Items in Type 3
    data.append([None, '4', 'I4', 'Item 4', 1, 400, 400])
    data.append([None, '5', 'I5', 'Item 5', 3, 500, 1500])
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create directory if it doesn't exist
    os.makedirs('test_data', exist_ok=True)
    
    # Write to Excel
    excel_path = 'test_data/test_pre.xlsx'
    df.to_excel(excel_path, index=False, header=False)
    
    print(f"Test Excel file created: {excel_path}")
    
    # Create a second sheet for MDC summary data
    # COD row structure
    mdc_data = []
    mdc_data.append(['COD', None, None, None, None, None, None])
    mdc_data.append(['Code', 'Description', 'Quantity', 'Direct Cost', 'List Price', 'Offer Price', 'Sell Price'])
    
    # Summary rows
    mdc_data.append(['G1', 'Group 1', 15, 2000, 2500, 2300, 2200])
    mdc_data.append(['G2', 'Group 2', 4, 1900, 2200, 2100, 2000])
    
    # Create new Excel writer
    with pd.ExcelWriter(excel_path, mode='a') as writer:
        pd.DataFrame(mdc_data).to_excel(writer, sheet_name='MDC', index=False, header=False)
    
    print(f"MDC sheet added to test Excel file")
    
    return excel_path

if __name__ == "__main__":
    excel_path = create_test_excel()
    print(f"To debug the extraction, run: python debug_excel.py {excel_path}") 
import pandas as pd
import logging
import os

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def find_pre_detail_from_excel(file_path):
    """Verify Excel file exists and return file path.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        str: Validated file path
    """
    logging.info(f"Finding Excel file: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")
    
    return file_path

def parse_pre_detail_from_excel(file_path):
    """Parse Excel file and return a DataFrame.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        pandas.DataFrame: Raw Excel data
    """
    logging.info(f"Parsing Excel file: {file_path}")
    
    # Read first sheet of Excel without setting any headers
    return pd.read_excel(file_path, sheet_name=0, header=None)

def load_excel(file_path):
    """Load Excel file and return a DataFrame.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        pandas.DataFrame: Raw Excel data
    """
    validated_path = find_pre_detail_from_excel(file_path)
    return parse_pre_detail_from_excel(validated_path)

def find_mdc_summary(file_path):
    """Find and load the MDC sheet from Excel file.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        tuple: (pandas.DataFrame, int) Raw Excel data and the index of the COD row
    """
    logging.info(f"Loading MDC sheet from Excel file: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        # First try to read the sheet named 'MDC'
        df = pd.read_excel(file_path, sheet_name='MDC', header=None)
        logging.info(f"Successfully loaded 'MDC' sheet with {len(df)} rows")
    except ValueError as e:
        # If sheet name not found, try to read all sheets and look for one with 'COD'
        logging.warning(f"Sheet 'MDC' not found: {e}. Trying to find sheet with 'COD' header.")
        xl = pd.ExcelFile(file_path)
        sheet_found = False
        
        for sheet_name in xl.sheet_names:
            sheet_df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            # Look for 'COD' in the first column (potential header row)
            for idx, row in sheet_df.iterrows():
                if pd.notna(row[0]) and str(row[0]).strip() == 'COD':
                    df = sheet_df
                    logging.info(f"Found 'COD' header in sheet '{sheet_name}' at row {idx+1}")
                    sheet_found = True
                    break
            if sheet_found:
                break
        
        if not sheet_found:
            logging.error("Could not find any sheet with 'COD' header")
            return pd.DataFrame(), None  # Return empty DataFrame and None for cod_row_idx
    
    # Find the row with 'COD' header
    cod_row_idx = None
    for idx, row in df.iterrows():
        if pd.notna(row[0]) and str(row[0]).strip() == 'COD':
            cod_row_idx = idx
            break
    
    if cod_row_idx is None:
        logging.error("Could not find 'COD' row in the data")
        return pd.DataFrame(), None  # Return empty DataFrame and None for cod_row_idx
    
    return df, cod_row_idx

def parse_mdc_summary(df, cod_row_idx):
    """Parse the MDC sheet data starting from the 'COD' row.
    
    Args:
        df (pandas.DataFrame): Raw Excel data
        cod_row_idx (int): Index of the row containing 'COD'
        
    Returns:
        pandas.DataFrame: Processed table data with specific fields extracted
    """
    if df.empty or cod_row_idx is None:
        return pd.DataFrame()
    
    # Define column names for our output DataFrame
    output_columns = [
        'wbe_code', 
        'wbe_description', 
        'quantity', 
        'wbe_direct_cost', 
        'wbe_list_price', 
        'wbe_offer_price', 
        'wbe_sell_price'
    ]
    
    # Prepare data storage
    data = []
    
    # Start processing from the row after 'COD' (usually descriptions) + 1 more row to get to actual data
    data_start_idx = cod_row_idx + 2  # Skip COD row and header row
    
    # Process rows
    for i in range(data_start_idx, len(df)):
        row = df.iloc[i]
        
        # Stop if we reach a row where columns 1, 2, and 3 are all empty
        if pd.isna(row[1]) and pd.isna(row[2]) and pd.isna(row[3]):
            logging.info(f"Reached end of table at row {i+1} (empty values in columns 1,2,3)")
            break
        
        # Only process rows with a value in column 0
        if pd.notna(row[0]):
            wbe_code = str(row[0]).strip() if pd.notna(row[0]) else None
            wbe_description = str(row[1]).strip() if pd.notna(row[1]) else None
            
            # Extract and convert numeric values
            try:
                quantity = float(row[2]) if pd.notna(row[2]) else None
            except (ValueError, TypeError):
                quantity = None
                logging.warning(f"Invalid quantity value at row {i+1}: {row[2]}")
            
            try:
                wbe_direct_cost = float(row[3]) if pd.notna(row[3]) else None
            except (ValueError, TypeError):
                wbe_direct_cost = None
                logging.warning(f"Invalid direct cost value at row {i+1}: {row[3]}")
                
            try:
                wbe_list_price = float(row[4]) if pd.notna(row[4]) else None
            except (ValueError, TypeError):
                wbe_list_price = None
                logging.warning(f"Invalid list price value at row {i+1}: {row[4]}")
                
            try:
                wbe_offer_price = float(row[5]) if pd.notna(row[5]) else None
            except (ValueError, TypeError):
                wbe_offer_price = None
                logging.warning(f"Invalid offer price value at row {i+1}: {row[5]}")
                
            try:
                wbe_sell_price = float(row[6]) if pd.notna(row[6]) else None
            except (ValueError, TypeError):
                wbe_sell_price = None
                logging.warning(f"Invalid sell price value at row {i+1}: {row[6]}")
            
            # Add to data
            data.append({
                'wbe_code': wbe_code,
                'wbe_description': wbe_description,
                'quantity': quantity,
                'wbe_direct_cost': wbe_direct_cost,
                'wbe_list_price': wbe_list_price,
                'wbe_offer_price': wbe_offer_price,
                'wbe_sell_price': wbe_sell_price
            })
            
            logging.debug(f"Extracted WBE: {wbe_code} - {wbe_description}")
    
    # Create DataFrame
    result_df = pd.DataFrame(data, columns=output_columns)
    logging.info(f"Extracted {len(result_df)} WBE items from table")
    
    return result_df

def load_mdc_sheet(file_path):
    """Load MDC sheet from Excel file and transform the table with 'COD' header.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        pandas.DataFrame: Processed table data with specific fields extracted
    """
    df, cod_row_idx = find_mdc_summary(file_path)
    return parse_mdc_summary(df, cod_row_idx)

def process_pre_detal(df):
    """Parse the Excel DataFrame into a denormalized table structure.
    
    Args:
        df (pandas.DataFrame): Raw Excel data
        
    Returns:
        pandas.DataFrame: Denormalized table with hierarchy information
    """
    data = []
    current_group = {'code': None, 'desc': None}
    current_type = {'code': None, 'title': None}
    current_subtype = {'code': None, 'desc': None}
    
    # Check if DataFrame has expected columns
    min_required_columns = 7  # Needs columns A-G (0-6)
    if df.shape[1] < min_required_columns:
        logging.error(f"Excel file has insufficient columns: {df.shape[1]}, expected at least {min_required_columns}")
        return pd.DataFrame(data)
    
    i = 0
    while i < len(df):
        row = df.iloc[i]
        
        # Check if row is a WBE Group header (starts with 'COD' in column A)
        if pd.notna(row[0]) and str(row[0]).strip() == 'COD':
            logging.info(f"Found WBE Group header at row {i+1}")
            current_type = {'code': None, 'title': None}
            
            # Look at the next row for group code and description
            if i + 1 < len(df):
                next_row = df.iloc[i+1]
                
                # Group code in column C (index 2), description in column D (index 3)
                if pd.notna(next_row[2]):
                    current_group['code'] = str(next_row[2]).strip()
                    current_group['desc'] = str(next_row[3]).strip() if pd.notna(next_row[3]) else None
                    logging.info(f"WBE Group: {current_group['code']} - {current_group['desc']}")
                    
                    # Reset type and subtype when new group is found
                    current_type = {'code': None, 'title': None}
                    current_subtype = {'code': None, 'desc': None}
                   
                    # Move to the type row (skip the group header and group data row)
                    i += 2
                    continue


            
        # Check if row is a WBE Type (follows group, has values in columns A, C & D)
        elif current_group['code'] is not None and pd.notna(row[2]) and pd.notna(row[3]) and current_subtype['code'] is None:
            
            # If we already have a type and are seeing another potential type row
            # This could be a subtype
            if current_type['code'] is not None:
                # This appears to be a subtype row
                current_subtype['code'] = str(row[2]).strip()
                current_subtype['desc'] = str(row[3]).strip()
                logging.info(f"WBE Subtype: {current_subtype['code']} - {current_subtype['desc']}")
            else:
                # This is a type row
                current_type['code'] = str(row[2]).strip()
                current_type['title'] = str(row[3]).strip()
                logging.info(f"WBE Type: {current_type['code']} - {current_type['title']}")
            
            i += 1
            continue
            
        # Check if row is a WBE Item (has values in columns C, D)
        elif current_group['code'] is not None and current_type['code'] is not None and \
             pd.isna(row[0]) and pd.notna(row[3]):
            
            position = str(row[1]).strip()
            code = str(row[2]).strip()
            desc = str(row[3]).strip()
            
            # Parse quantity (column E) and list price (column F) as floats
            quantity = float(row[4]) if pd.notna(row[4]) else None
            list_price = float(row[5]) if pd.notna(row[5]) else None
            
            item = {
                'wbe_group_code': current_group['code'],
                'wbe_group_desc': current_group['desc'],
                'wbe_type_code': current_type['code'],
                'wbe_type_title': current_type['title'],
                'wbe_subtype_code': current_subtype['code'],
                'wbe_subtype_desc': current_subtype['desc'],
                'wbe_item_position': position,
                'wbe_item_code': code,
                'wbe_item_desc': desc,
                'wbe_item_quantity': quantity,
                'wbe_item_list_price': list_price
            }
            
            data.append(item)
            logging.info(f"WBE Item: {code} - {desc}")
            
            i += 1
            continue

        # Installazione
        elif pd.notna(row[0]) and str(row[0]).strip().startswith('E'):
            item = {
                'wbe_group_code': current_group['code'],
                'wbe_group_desc': current_group['desc'],
                'wbe_type_code': current_type['code'],
                'wbe_type_title': current_type['title'],
                'wbe_subtype_code': str(row[0]).strip(),
                'wbe_subtype_desc': str(row[3]).strip() if pd.notna(row[3]) else None,
                'wbe_item_position': None,
                'wbe_item_code': str(row[0]).strip(),
                'wbe_item_desc': str(row[3]).strip() if pd.notna(row[3]) else None,
                'wbe_item_quantity': 1,
                'wbe_item_list_price': float(row[7]) if pd.notna(row[7]) else None
            }
            data.append(item)
            logging.info(f"WBE Item - Installazione: {code} - {desc}")
            
            i += 1
            continue
            
        # Check if row is empty (reset subtype context but keep group and type)
        elif current_group['code'] is not None and all(pd.isna(row[j]) for j in range(4)):
            logging.info("Empty row - resetting subtype context")
            current_subtype = {'code': None, 'desc': None}
            
            # If we see multiple consecutive empty rows, we might be at the end of a section
            # Check if the next several rows are also empty, in which case reset type as well
            empty_rows_count = 1
            for j in range(1, 11):  # Look ahead up to 3 more rows
                if i + j < len(df) and all(pd.isna(df.iloc[i+j][k]) for k in range(4)):
                    empty_rows_count += 1
            
            if empty_rows_count >= 10:
                #logging.info("Multiple empty rows - resetting type context")
                #current_type = {'code': None, 'title': None}
                result_df = pd.DataFrame(data)
                logging.info(f"Processed {len(data)} WBE items")
                return result_df
            
            i += 1
            continue
            
        else:
            # Skip any rows that don't match our patterns
            i += 1
    
    # Create DataFrame from collected data
    result_df = pd.DataFrame(data)
    logging.info(f"Processed {len(data)} WBE items")
    return result_df



def print_dataframe(df, max_rows=None, max_cols=None):
    """Print DataFrame contents with optional row/column limits.
    
    Args:
        df (pandas.DataFrame): DataFrame to print
        max_rows (int, optional): Maximum number of rows to show
        max_cols (int, optional): Maximum number of columns to show
    """
    # Save current pandas display settings
    orig_max_rows = pd.get_option('display.max_rows')
    orig_max_columns = pd.get_option('display.max_columns')
    orig_width = pd.get_option('display.width')
    
    # Temporarily update display settings
    if max_rows is not None:
        pd.set_option('display.max_rows', max_rows)
    if max_cols is not None:
        pd.set_option('display.max_columns', max_cols)
    pd.set_option('display.width', 1000)  # Wider display to prevent wrapping
    
    # Print DataFrame
    print("\n=== DATAFRAME CONTENTS ===")
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
    print("==========================")
    print(df)
    print("==========================\n")
    
    # Restore original display settings
    pd.set_option('display.max_rows', orig_max_rows)
    pd.set_option('display.max_columns', orig_max_columns)
    pd.set_option('display.width', orig_width)

def export_to_csv(df, output_file):
    """Export DataFrame to CSV file.
    
    Args:
        df (pandas.DataFrame): DataFrame to export
        output_file (str): Output file path
    """
    df.to_csv(output_file, index=False)
    logging.info(f"Exported {len(df)} rows to {output_file}")

def main():
    """Main function to execute the workflow."""
    setup_logging()
    
    # File paths
    input_file = 'input/PRE_LSU2300105_NEW_06_QS.xlsm'
    output_file = 'output/detail_output.csv'
    
    # Process data using the separated functions
    try:
        # First verify file exists and get validated path
        validated_path = find_pre_detail_from_excel(input_file)
        
        # Then parse the Excel file
        raw_df = parse_pre_detail_from_excel(validated_path)
        
        # Process the data
        parsed_df = process_pre_detal(raw_df)
        
        # Display results
        print_dataframe(parsed_df, max_rows=20)
        
        # Export to CSV
        export_to_csv(parsed_df, output_file)
    except Exception as e:
        logging.error(f"Error processing Excel file: {e}")
        return
    
    # Now process the MDC sheet using the separated functions
    try:
        # First find the MDC sheet
        mdc_raw_df, cod_row_idx = find_mdc_summary(input_file)
        
        if not mdc_raw_df.empty and cod_row_idx is not None:
            # Then parse the MDC sheet data
            mdc_df = parse_mdc_summary(mdc_raw_df, cod_row_idx)
            
            print("\n=== MDC SHEET DATA ===")
            print_dataframe(mdc_df, max_rows=20)
            
            # Export MDC data to separate CSV
            mdc_output_file = 'output/summary_output.csv'
            export_to_csv(mdc_df, mdc_output_file)
            logging.info(f"MDC sheet data exported to {mdc_output_file}")
        else:
            logging.warning("No valid MDC sheet found")
    except Exception as e:
        logging.error(f"Error processing MDC sheet: {e}")
    
    logging.info("Processing complete")

if __name__ == "__main__":
    main() 
import pandas as pd
import logging
import sys
import os
from utils.excel_processor import (
    find_detail,
    process_detail,
    find_summary,
    parse_summary
)

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def debug_process_excel(file_path):
    """Debug the Excel processing logic"""
    logging.info(f"Starting debug of Excel processing for file: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return
    
    # Process detail data
    try:
        logging.info("Loading raw Excel data...")
        raw_df = find_detail(file_path)
        logging.info(f"Raw DataFrame shape: {raw_df.shape}")
        
        # Debug: Print first few rows of raw data
        logging.debug("First 10 rows of raw data:")
        for i in range(min(10, len(raw_df))):
            row = raw_df.iloc[i]
            logging.debug(f"Row {i}: {row.values}")
        
        # Process detail data
        logging.info("Processing detail data...")
        detail_df = process_detail(raw_df)
        
        logging.info(f"Processed detail data. Found {len(detail_df)} rows.")
        if len(detail_df) > 0:
            logging.debug("First few rows of processed detail data:")
            pd.set_option('display.max_columns', None)
            logging.debug(detail_df.head())
        else:
            logging.warning("No detail data was extracted!")
            
            # Extra debugging for specific patterns
            logging.debug("Searching for 'COD' pattern in raw data...")
            cod_count = 0
            for i in range(len(raw_df)):
                row = raw_df.iloc[i]
                if pd.notna(row[0]) and str(row[0]).strip() == 'COD':
                    cod_count += 1
                    logging.debug(f"Found 'COD' at row {i}")
                    # Look at the next row for debugging
                    if i + 1 < len(raw_df):
                        next_row = raw_df.iloc[i+1]
                        logging.debug(f"Next row after COD: {next_row.values}")
            logging.debug(f"Total 'COD' patterns found: {cod_count}")
            
            # Check for potential data rows
            logging.debug("Checking for potential item rows...")
            potential_items = 0
            for i in range(len(raw_df)):
                row = raw_df.iloc[i]
                if pd.notna(row[0]) and pd.notna(row[1]) and pd.notna(row[2]) and pd.notna(row[6]):
                    potential_items += 1
                    logging.debug(f"Potential item at row {i}: {row.values[:8]}")
                    if potential_items >= 5:  # Limit to first 5 potential items
                        break
            logging.debug(f"First {min(potential_items, 5)} potential items checked")
        
        # Process summary data
        logging.info("Processing summary data...")
        mdc_raw_df, cod_row_idx = find_summary(file_path)
        
        if not mdc_raw_df.empty and cod_row_idx is not None:
            summary_df = parse_summary(mdc_raw_df, cod_row_idx)
            logging.info(f"Processed summary data. Found {len(summary_df)} rows.")
            if len(summary_df) > 0:
                logging.debug("First few rows of processed summary data:")
                logging.debug(summary_df.head())
        else:
            logging.warning("No summary data was found or extracted!")
        
        return detail_df
        
    except Exception as e:
        logging.error(f"Error during processing: {e}", exc_info=True)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_excel.py <excel_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    debug_process_excel(file_path) 
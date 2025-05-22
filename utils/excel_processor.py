import pandas as pd
import logging
import os
import tempfile

from config import PRE_FILE_TYPE, ANALISI_PROFITTABILITA_TYPE


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
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


def find_detail(file_path: str) -> tuple[pd.DataFrame, str]:
    """Parse Excel file and return a DataFrame with file type.

    Args:
        file_path (str): Path to the Excel file

    Returns:
        tuple[pd.DataFrame, str]: A tuple containing:
            - pandas.DataFrame: Raw Excel data
            - str: File type identifier ('PRE_FILE' or 'ANALISI_PROFITTABILITA')

    Raises:
        ValueError: If neither 'OFFER1' nor 'NEW_OFFER1' sheets are found
    """
    logging.info(f"Parsing Excel file: {file_path}")

    try:
        # Try to read 'OFFER1' sheet first
        df = pd.read_excel(file_path, sheet_name="OFFER1", header=None)
        file_type = PRE_FILE_TYPE
        return df, file_type
    except ValueError:
        try:
            # Try to read 'NEW_OFFER1' sheet
            df = pd.read_excel(file_path, sheet_name="NEW_OFFER1", header=None)
            file_type = ANALISI_PROFITTABILITA_TYPE
            return df, file_type
        except ValueError:
            raise ValueError(
                "Neither 'OFFER1' nor 'NEW_OFFER1' sheets found in the Excel file"
            )


def create_wbe_dataframe(data):
    """
    Creates a DataFrame from WBE item data with standardized columns.

    Args:
        data (list): List of dictionaries containing WBE item data

    Returns:
        pandas.DataFrame: DataFrame with standardized WBE item columns
    """
    result_df = pd.DataFrame(data)
    columns = [
        "wbe_item_code",
        "wbe_item_description",
        "wbe_item_quantity",
        "wbe_item_total_price",
        "wbe_item_unit_price",
        "wbe_item_list_price",
        "wbe_group_code",
        "wbe_group_desc",
        "wbe_type_code",
        "wbe_type_title",
        "wbe_subtype_code",
        "wbe_subtype_desc",
    ]
    # Make sure DataFrame has all the expected columns
    for col in columns:
        if col not in result_df.columns:
            result_df[col] = None

    result_df = result_df[columns]  # Reorder columns
    return result_df


def process_detail(df: pd.DataFrame, file_type: str) -> pd.DataFrame:
    """Parse the Excel DataFrame into a denormalized table structure.

    Args:
        df (pandas.DataFrame): Raw Excel data
        file_type (str): Type of file being processed ('PRE_FILE' or 'ANALISI_PROFITTABILITA')

    Returns:
        pandas.DataFrame: Denormalized table with hierarchy information
    """

    if file_type == ANALISI_PROFITTABILITA_TYPE:
        logging.info("Processing ANALISI_PROFITTABILITA file")

    elif file_type == PRE_FILE_TYPE:
        logging.info("Processing PRE_FILE file")
    else:
        raise ValueError(f"Invalid file type: {file_type}")

    data = []
    current_group = {"code": None, "desc": None}
    current_type = {"code": None, "title": None}
    current_subtype = {"code": None, "desc": None}

    logging.debug(f"Starting detail extraction on DataFrame with shape {df.shape}")

    proto_wbe_col = 0
    priority_col = -1 if file_type == PRE_FILE_TYPE else 1
    wbe_col = -1 if file_type == PRE_FILE_TYPE else 5
    position_col = 1 if file_type == PRE_FILE_TYPE else 6
    code_col = 2 if file_type == PRE_FILE_TYPE else 7
    desc_col = 3 if file_type == PRE_FILE_TYPE else 9
    quantity_col = 4 if file_type == PRE_FILE_TYPE else 10
    list_price_col = 5 if file_type == PRE_FILE_TYPE else 12
    total_price_col = 6 if file_type == PRE_FILE_TYPE else 13

    # row index
    i = 0

    # Find start of table if not already found
    while i < len(df):
        row = df.iloc[i]
        if str(row[proto_wbe_col]).strip() == "COD":
            logging.info(f"Found start of table at row {i}")
            i += 1
            break
        i += 1

    row = df.iloc[i]

    while i < len(df):
        row = df.iloc[i]

        # skip rows until we find a row with a value in description column
        while pd.isna(row[desc_col]) and i < len(df) -1:
            i += 1
            row = df.iloc[i]

        logging.debug(f"Processing row {i}")

        if i == len(df):
            logging.debug(f"Found end of table at row {i}")
            return pd.DataFrame()

        # L1
        if file_type == ANALISI_PROFITTABILITA_TYPE:
            # group (L!): row is a group row (level 1) if only code and desc are not empty and all other columns are empty
            if pd.notna(row[priority_col]) and str(row[priority_col]).strip() == "0":
                current_type = {"code": None, "title": None}
                current_subtype = {"code": None, "desc": None}
                current_group["code"] = str(row[code_col]).strip()
                current_group["desc"] = (
                    str(row[desc_col]).strip() if pd.notna(row[desc_col]) else None
                )
                logging.debug(
                    f"     L1 - WBE Group: {current_group['code']} - {current_group['desc']}"
                )
                i += 1
                continue
        elif (
            pd.notna(row[code_col])
            and pd.notna(row[desc_col])
            and pd.isna(row[proto_wbe_col])
            and pd.isna(row[position_col])
            and pd.notna(row[quantity_col])
            and pd.isna(row[list_price_col])
            and pd.isna(row[total_price_col])
        ):
            current_type = {"code": None, "title": None}
            current_subtype = {"code": None, "desc": None}
            current_group["code"] = str(row[code_col]).strip()
            current_group["desc"] = (
                str(row[desc_col]).strip() if pd.notna(row[desc_col]) else None
            )
            logging.debug(
                f"     L1 - WBE Group: {current_group['code']} - {current_group['desc']}"
            )
            i += 1
            continue

        # L2
        if file_type == ANALISI_PROFITTABILITA_TYPE:
            if pd.notna(row[proto_wbe_col]):
                current_type["code"] = str(row[code_col]).strip()
                current_type["title"] = str(row[desc_col]).strip()
                logging.debug(
                    f"         L2 -WBE Type: {current_type['code']} - {current_type['title']}"
                )
                i += 1
                continue
        elif (
            pd.notna(row[proto_wbe_col])
            and pd.isna(row[position_col])
            and pd.notna(row[code_col])
            and pd.notna(row[desc_col])
            and pd.isna(row[quantity_col])
            and pd.isna(row[list_price_col])
            and pd.isna(row[total_price_col])
        ):
            current_type["code"] = str(row[code_col]).strip()
            current_type["title"] = str(row[desc_col]).strip()
            logging.debug(
                f"         L2 -WBE Type: {current_type['code']} - {current_type['title']}"
            )
            i += 1
            continue

        # L3
        if file_type == ANALISI_PROFITTABILITA_TYPE:
            if (
                pd.isna(row[proto_wbe_col])
                and pd.notna(row[code_col])
                and pd.notna(row[desc_col])
                and pd.isna(row[proto_wbe_col])
                and pd.isna(row[position_col])
                and pd.isna(row[quantity_col])
                and pd.isna(row[list_price_col])
                and pd.isna(row[total_price_col])
                and pd.notna(row[priority_col])
                and str(row[priority_col]).strip() != "0"
            ):
                current_subtype["code"] = str(row[code_col]).strip()
                current_subtype["desc"] = str(row[desc_col]).strip()
                logging.debug(
                    f"             L3 - WBE Subtype: {current_subtype['code']} - {current_subtype['desc']}"
                )
                i += 1
                continue
        elif (
            pd.isna(row[proto_wbe_col])
            and pd.notna(row[code_col])
            and pd.notna(row[desc_col])
            and pd.isna(row[proto_wbe_col])
            and pd.isna(row[position_col])
            and pd.isna(row[quantity_col])
            and pd.isna(row[list_price_col])
            and pd.isna(row[total_price_col])
        ):
            current_subtype["code"] = str(row[code_col]).strip()
            current_subtype["desc"] = str(row[desc_col]).strip()
            logging.debug(
                f"             L3 - WBE Subtype: {current_subtype['code']} - {current_subtype['desc']}"
            )
            i += 1
            continue

        if (
            pd.notna(row[code_col])
            and pd.notna(row[desc_col])
            and pd.notna(row[quantity_col])
            and pd.notna(row[list_price_col])
            and pd.notna(row[total_price_col])
        ):
            position = (
                str(row[position_col]).strip() if pd.notna(row[position_col]) else ""
            )
            code = str(row[code_col]).strip() if pd.notna(row[code_col]) else ""
            desc = str(row[desc_col]).strip() if pd.notna(row[desc_col]) else ""

            # Parse quantity (column E) and list price (column F) as floats
            try:
                quantity = (
                    float(row[quantity_col]) if pd.notna(row[quantity_col]) else 0.0
                )
            except (ValueError, TypeError):
                quantity = 0.0
                logging.warning(f"Invalid quantity at row {i+1}: {row[quantity_col]}")

            try:
                list_price = (
                    float(row[list_price_col]) if pd.notna(row[list_price_col]) else 0.0
                )
            except (ValueError, TypeError):
                list_price = 0.0
                logging.warning(
                    f"Invalid list price at row {i+1}: {row[list_price_col]}"
                )

            try:
                total_price = (
                    float(row[total_price_col])
                    if pd.notna(row[total_price_col])
                    else 0.0
                )
            except (ValueError, TypeError):
                total_price = 0.0
                logging.warning(
                    f"Invalid total price at row {i+1}: {row[total_price_col]}"
                )

            # Calculate unit price if quantity is not zero
            unit_price = 0.0
            if quantity > 0:
                unit_price = total_price / quantity
            i += 1

            item = {
                "wbe_item_code": code,
                "wbe_item_description": desc,
                "wbe_item_quantity": quantity,
                "wbe_item_total_price": total_price,
                "wbe_item_unit_price": unit_price,
                "wbe_item_list_price": list_price,
                "wbe_group_code": current_group["code"],
                "wbe_group_desc": current_group["desc"],
                "wbe_type_code": current_type["code"],
                "wbe_type_title": current_type["title"],
                "wbe_subtype_code": current_subtype["code"],
                "wbe_subtype_desc": current_subtype["desc"],
            }

            data.append(item)
            logging.debug(f"                    Extracted item {code} - {desc}")

            continue

        # If we see multiple consecutive empty rows, we might be at the end of a section
        empty_rows_count = 1
        for j in range(1, 11):  # Look ahead up to 10 more rows
            if i + j < len(df) and all(pd.isna(df.iloc[i + j][k]) for k in range(9)):
                empty_rows_count += 1

        if empty_rows_count >= 10:
            logging.debug("Multiple empty rows detected - likely end of section")
            # If we have collected data, we can return it now
            if data:
                return create_wbe_dataframe(data)

            i += 1
            continue

        else:
            # Skip any rows that don't match our patterns
            i += 1

    return create_wbe_dataframe(data)


def find_summary(file_path, file_type) -> tuple[pd.DataFrame, int]:
    """Find and load the MDC sheet from Excel file.

    Args:
        file_path (str): Path to the Excel file

    Returns:
        tuple: (pandas.DataFrame, int) Raw Excel data and the index of the COD row
    """

    if file_type == ANALISI_PROFITTABILITA_TYPE:
        logging.info("Processing ANALISI_PROFITTABILITA file")
        logging.info(f"Loading VA21 sheet from Excel file: {file_path}")
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Get all sheet names
            xl = pd.ExcelFile(file_path)
            va21_sheets = [
                sheet for sheet in xl.sheet_names if sheet.startswith("VA21_A")
            ]

            if not va21_sheets:
                logging.error("No sheet found starting with 'VA21_A'")
                return pd.DataFrame(), None

            # Extract numbers after 'VA21_A' and find the sheet with highest number
            max_num = -1
            target_sheet = None

            for sheet in va21_sheets:
                try:
                    num = int(sheet.split("VA21_A")[1])
                    if num > max_num:
                        max_num = num
                        target_sheet = sheet
                except ValueError:
                    continue

            if target_sheet is None:
                logging.error("Could not find valid VA21_A sheet with number")
                return pd.DataFrame(), None

            df = pd.read_excel(file_path, sheet_name=target_sheet, header=None)
            logging.info(
                f"Successfully loaded '{target_sheet}' sheet with {len(df)} rows"
            )

            # Find the row with 'PO' header
            cod_row_idx = None
            for idx, row in df.iterrows():
                if pd.notna(row[0]) and str(row[0]).startswith("PO"):
                    cod_row_idx = idx
                    break

            if cod_row_idx is None:
                logging.error("Could not find 'PO' row in the data")
                return pd.DataFrame(), None

            return df, cod_row_idx

        except Exception as e:
            logging.error(f"Error processing VA21 sheet: {e}")
            return pd.DataFrame(), None
        return pd.DataFrame(), None

    elif file_type == PRE_FILE_TYPE:
        logging.info("Processing PRE_FILE file")

        logging.info(f"Loading MDC sheet from Excel file: {file_path}")
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # First try to read the sheet named 'MDC'
            df = pd.read_excel(file_path, sheet_name="MDC", header=None)
            logging.info(f"Successfully loaded 'MDC' sheet with {len(df)} rows")
        except ValueError as e:
            # If sheet name not found, try to read all sheets and look for one with 'COD'
            logging.warning(
                f"Sheet 'MDC' not found: {e}. Trying to find sheet with 'COD' header."
            )
            xl = pd.ExcelFile(file_path)
            sheet_found = False

            for sheet_name in xl.sheet_names:
                sheet_df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                # Look for 'COD' in the first column (potential header row)
                for idx, row in sheet_df.iterrows():
                    if pd.notna(row[0]) and str(row[0]).strip() == "COD":
                        df = sheet_df
                        logging.info(
                            f"Found 'COD' header in sheet '{sheet_name}' at row {idx+1}"
                        )
                        sheet_found = True
                        break
                if sheet_found:
                    break

            if not sheet_found:
                logging.error("Could not find any sheet with 'COD' header")
                return (
                    pd.DataFrame(),
                    None,
                )  # Return empty DataFrame and None for cod_row_idx

        # Find the row with 'COD' header
        cod_row_idx = None
        for idx, row in df.iterrows():
            if pd.notna(row[0]) and str(row[0]).strip() == "COD":
                cod_row_idx = idx
                break

        if cod_row_idx is None:
            logging.error("Could not find 'COD' row in the data")
            return (
                pd.DataFrame(),
                None,
            )  # Return empty DataFrame and None for cod_row_idx

        return df, cod_row_idx
    else:
        raise ValueError(f"Invalid file type: {file_type}")


def process_summary(df, cod_row_idx, file_type) -> pd.DataFrame:
    """Parse the MDC sheet data starting from the 'COD' row.

    Args:
        df (pandas.DataFrame): Raw Excel data
        cod_row_idx (int): Index of the row containing header row

    Returns:
        pandas.DataFrame: Processed table data with specific fields extracted
    """
    if df.empty or cod_row_idx is None:
        return pd.DataFrame()

    # Define column names for our output DataFrame
    output_columns = [
        "wbe_code",
        "wbe_description",
        "wbe_direct_cost",
        "wbe_list_price",
        "wbe_offer_price",
        "wbe_sell_price",
        "commissions_cost",
        "contribution_margin",
        "contribution_margin_percent",
    ]

    # Prepare data storage
    data = []

    if file_type == ANALISI_PROFITTABILITA_TYPE:

        wbe_code_col = 1
        wbe_description_col = 10
        wbe_direct_cost_col = 26
        wbe_list_price_col = 21
        wbe_offer_price_col = 24
        wbe_sell_price_col = 24
        commissions_cost_col = -1
        contribution_margin_col = -1
        contribution_margin_percent_col = 27

        # Process rows
        for i in range(cod_row_idx + 1, len(df)):
            row = df.iloc[i]

            # continue if we reach a row where columns 1, 2, and 3 are all empty
            if pd.isna(row[1]) and pd.isna(row[2]) and pd.isna(row[3]):
                logging.debug(
                    f"Reached end of table at row {i+1} (empty values in columns 1,2,3)"
                )
                continue

            # stop if in column 1 there is a value 'TOT'
            if pd.notna(row[1]) and str(row[1]).strip() == "TOT":
                logging.debug(
                    f"Reached end of table at row {i+1} (TOT value in column 1)"
                )
                break

            # Only process rows with a value in column 1
            if pd.notna(row[wbe_code_col]):
                wbe_code = (
                    str(row[wbe_code_col]).strip()
                    if pd.notna(row[wbe_code_col])
                    else None
                )
                wbe_description = (
                    str(row[wbe_description_col]).strip()
                    if pd.notna(row[wbe_description_col])
                    else None
                )

                try:
                    wbe_direct_cost = (
                        float(row[wbe_direct_cost_col])
                        if pd.notna(row[wbe_direct_cost_col])
                        else None
                    )
                except (ValueError, TypeError):
                    wbe_direct_cost = None
                    logging.warning(
                        f"Invalid direct cost value at row {i}: {row[wbe_direct_cost_col]}"
                    )

                try:
                    wbe_list_price = (
                        float(row[wbe_list_price_col])
                        if pd.notna(row[wbe_list_price_col])
                        else None
                    )
                except (ValueError, TypeError):
                    wbe_list_price = None
                    logging.warning(
                        f"Invalid list price value at row {i}: {row[wbe_list_price_col]}"
                    )

                try:
                    wbe_offer_price = (
                        float(row[wbe_offer_price_col])
                        if pd.notna(row[wbe_offer_price_col])
                        else None
                    )
                except (ValueError, TypeError):
                    wbe_offer_price = None
                    logging.warning(
                        f"Invalid offer price value at row {i}: {row[wbe_offer_price_col]}"
                    )

                try:
                    wbe_sell_price = (
                        float(row[wbe_sell_price_col])
                        if pd.notna(row[wbe_sell_price_col])
                        else None
                    )
                except (ValueError, TypeError):
                    wbe_sell_price = None
                    logging.warning(
                        f"Invalid sell price value at row {i}: {row[wbe_sell_price_col]}"
                    )

                try:
                    contribution_margin_percent = (
                        float(row[contribution_margin_percent_col])
                        if pd.notna(row[contribution_margin_percent_col])
                        else None
                    )
                except (ValueError, TypeError):
                    contribution_margin_percent = None
                    logging.warning(
                        f"Invalid contribution margin percent value at row {i}: {row[contribution_margin_percent_col]}"
                    )

                # Add to data
                data.append(
                    {
                        "wbe_code": wbe_code,
                        "wbe_description": wbe_description,
                        "wbe_direct_cost": wbe_direct_cost,
                        "wbe_list_price": wbe_list_price,
                        "wbe_offer_price": wbe_offer_price,
                        "wbe_sell_price": wbe_sell_price,
                        "contribution_margin_percent": contribution_margin_percent,
                    }
                )

                logging.debug(f"Extracted WBE: {wbe_code} - {wbe_description}")

        # Create DataFrame
        result_df = pd.DataFrame(data, columns=output_columns)
        logging.info(f"Extracted {len(result_df)} WBE items from table")

        return result_df

    elif file_type == PRE_FILE_TYPE:

        # Start processing from the row after 'COD' (usually descriptions) + 1 more row to get to actual data
        data_start_idx = cod_row_idx + 2  # Skip COD row and header row

        # Process rows
        for i in range(data_start_idx, len(df)):
            row = df.iloc[i]

            # Stop if we reach a row where columns 1, 2, and 3 are all empty
            if pd.isna(row[1]) and pd.isna(row[2]) and pd.isna(row[3]):
                logging.debug(
                    f"Reached end of table at row {i+1} (empty values in columns 1,2,3)"
                )
                break

            # Only process rows with a value in column 0
            if pd.notna(row[0]):
                wbe_code = str(row[0]).strip() if pd.notna(row[0]) else None
                wbe_description = str(row[1]).strip() if pd.notna(row[1]) else None

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

                try:
                    commissions_cost = float(row[8]) if pd.notna(row[8]) else None
                except (ValueError, TypeError):
                    commissions_cost = None
                    logging.warning(
                        f"Invalid commissions cost value at row {i+1}: {row[8]}"
                    )

                try:
                    contribution_margin = float(row[15]) if pd.notna(row[15]) else None
                except (ValueError, TypeError):
                    contribution_margin = None
                    logging.warning(
                        f"Invalid contribution margin value at row {i+1}: {row[15]}"
                    )

                try:
                    contribution_margin_percent = (
                        float(row[16]) if pd.notna(row[16]) else None
                    )
                except (ValueError, TypeError):
                    contribution_margin_percent = None
                    logging.warning(
                        f"Invalid contribution margin percent value at row {i+1}: {row[16]}"
                    )

                # Add to data
                data.append(
                    {
                        "wbe_code": wbe_code,
                        "wbe_description": wbe_description,
                        "wbe_direct_cost": wbe_direct_cost,
                        "wbe_list_price": wbe_list_price,
                        "wbe_offer_price": wbe_offer_price,
                        "wbe_sell_price": wbe_sell_price,
                        "commissions_cost": commissions_cost,
                        "contribution_margin": contribution_margin,
                        "contribution_margin_percent": contribution_margin_percent,
                    }
                )

                logging.debug(f"Extracted WBE: {wbe_code} - {wbe_description}")

        # Create DataFrame
        result_df = pd.DataFrame(data, columns=output_columns)
        logging.info(f"Extracted {len(result_df)} WBE items from table")

        return result_df


def process_data(file_path):
    """Process the Excel file and return both detail and summary DataFrames"""
    try:
        logging.info(f"Starting processing of Excel file: {file_path}")

        # Process detailed data
        logging.info("Extracting raw detail data from Excel...")
        raw_df, file_type = find_detail(file_path)
        logging.debug(f"Raw DataFrame shape: {raw_df.shape}")
        logging.info(f"File type: {file_type}")

        logging.info("Processing detail data...")
        detail_df = process_detail(raw_df, file_type)

        if detail_df.empty:
            logging.warning(
                "No detail data was extracted. Check if the Excel format is as expected."
            )
        else:
            logging.info(f"Successfully extracted {len(detail_df)} detail rows")

        # Process summary data
        logging.info("Extracting summary data...")
        mdc_raw_df, cod_row_idx = find_summary(file_path, file_type)
        if not mdc_raw_df.empty and cod_row_idx is not None:
            logging.info(f"Found summary data with header row at index {cod_row_idx}")
            summary_df = process_summary(mdc_raw_df, cod_row_idx, file_type)
            logging.info(f"Extracted {len(summary_df)} summary rows")
        else:
            summary_df = pd.DataFrame()
            logging.warning("No summary data (MDC sheet) found in the uploaded file.")

        return detail_df, summary_df
    except Exception as e:
        logging.error(f"Error processing the file: {e}", exc_info=True)
        return pd.DataFrame(), pd.DataFrame()


def save_uploaded_file(uploaded_file):
    """Save the uploaded file to a temporary location and return the path"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(uploaded_file.getvalue())
            return tmp.name
    except Exception as e:
        logging.error(f"Error saving uploaded file: {e}")
        return None


def print_dataframe(df, max_rows=None, max_cols=None):
    """Print a DataFrame in a formatted way with options to limit rows/columns.

    Args:
        df (pandas.DataFrame): DataFrame to print
        max_rows (int, optional): Maximum number of rows to print. Defaults to None.
        max_cols (int, optional): Maximum number of columns to print. Defaults to None.
    """
    # Save original display settings
    orig_max_rows = pd.get_option("display.max_rows")
    orig_max_columns = pd.get_option("display.max_columns")

    try:
        # Set display options based on parameters
        if max_rows is not None:
            pd.set_option("display.max_rows", max_rows)
        if max_cols is not None:
            pd.set_option("display.max_columns", max_cols)

        # Print DataFrame
        print(df)
    finally:
        # Restore original display settings
        pd.set_option("display.max_rows", orig_max_rows)
        pd.set_option("display.max_columns", orig_max_columns)


def export_to_csv(df, output_file):
    """Export DataFrame to CSV file.

    Args:
        df (pandas.DataFrame): DataFrame to export
        output_file (str): Path to save the CSV file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        df.to_csv(output_file, index=False, encoding="utf-8")
        logging.info(f"Exported data to {output_file}")
        return True
    except Exception as e:
        logging.error(f"Error exporting to CSV: {e}")
        return False

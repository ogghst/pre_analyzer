"""
Configuration settings for PRE Excel Data Analyzer.
Contains field name mappings for UI display and format type.
"""

import locale
import pandas as pd
try:
    locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
except locale.Error:
    # Fallback for systems where Italian locale is not installed
    locale.setlocale(locale.LC_ALL, '')

PRE_FILE_TYPE = 'PRE_FILE'
ANALISI_PROFITTABILITA_TYPE = 'ANALISI_PROFITTABILITA'

def CURRENCY_FORMAT(x):
    try:
        return locale.format_string('%.2f', x, grouping=True).replace('.', '#').replace(',', '.').replace('#', ',')
    except Exception:
        return str(x)

# Summary field name to display name and format mapping
SUMMARY_FIELD_DISPLAY_NAMES = {
    'wbe_code': {'display_name': 'Proto WBE', 'format': 'default'},
    'wbe_description': {'display_name': 'Description', 'format': 'default'},
    'wbe_direct_cost': {'display_name': 'Direct Cost EUR', 'format': 'currency'},
    'wbe_list_price': {'display_name': 'Listino EUR', 'format': 'currency'},
    'wbe_offer_price': {'display_name': 'Offer Price EUR', 'format': 'currency'},
    'wbe_sell_price': {'display_name': 'Sell Price EUR', 'format': 'currency'},
    'commissions_cost': {'display_name': 'Commissions Cost EUR', 'format': 'currency'},
    'contribution_margin': {'display_name': 'Contribution Margin EUR', 'format': 'currency'},
    'contribution_margin_percent': {'display_name': 'Contribution Margin %', 'format': 'default'}
}

# Detail field name to display name and format mapping
DETAIL_FIELD_DISPLAY_NAMES = {
    'wbe_item_code': {'display_name': 'Proto BOM', 'format': 'default'},
    'wbe_item_description': {'display_name': 'Description', 'format': 'default'},
    'wbe_item_quantity': {'display_name': 'Quantity', 'format': 'quantity'},
    'wbe_item_total_price': {'display_name': 'Total Price EUR', 'format': 'currency'},
    'wbe_item_unit_price': {'display_name': 'Unit Price EUR', 'format': 'currency'},
    'wbe_item_list_price': {'display_name': 'Listino EUR', 'format': 'currency'},
    'wbe_group_code': {'display_name': 'Group', 'format': 'default'},
    'wbe_group_desc': {'display_name': 'Group Description', 'format': 'default'},
    'wbe_type_code': {'display_name': 'Proto WBE', 'format': 'default'},
    'wbe_type_title': {'display_name': 'Proto WBE Description', 'format': 'default'},
    'wbe_subtype_code': {'display_name': 'SubType', 'format': 'default'},
    'wbe_subtype_desc': {'display_name': 'SubType Desc', 'format': 'default'}
}

# Default quantity format
QUANTITY_FORMAT = "{:.2f}"

def format_value(field, value, summary_or_detail='summary'):
    """
    Format a value according to the field's format type as defined in the config mappings.
    Args:
        field (str): The field name (column name)
        value: The value to format
        summary_or_detail (str): 'summary' or 'detail' to select the correct mapping
    Returns:
        str: The formatted value
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    mapping = SUMMARY_FIELD_DISPLAY_NAMES if summary_or_detail == 'summary' else DETAIL_FIELD_DISPLAY_NAMES
    field_info = mapping.get(field, {'format': 'default'})
    fmt = field_info.get('format', 'default')
    if fmt == 'currency':
        return CURRENCY_FORMAT(value)
    elif fmt == 'quantity':
        return QUANTITY_FORMAT.format(value)
    else:
        return str(value) 
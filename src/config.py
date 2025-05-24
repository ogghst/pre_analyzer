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

# Field name constants
WBE_CODE = 'wbe_code'
WBE_DESCRIPTION = 'wbe_description'
WBE_DIRECT_COST = 'wbe_direct_cost'
WBE_LIST_PRICE = 'wbe_list_price'
WBE_OFFER_PRICE = 'wbe_offer_price'
WBE_SELL_PRICE = 'wbe_sell_price'
COMMISSIONS_COST = 'commissions_cost'
CONTRIBUTION_MARGIN = 'contribution_margin'
CONTRIBUTION_MARGIN_PERCENT = 'contribution_margin_percent'

WBE_ITEM_CODE = 'wbe_item_code'
WBE_ITEM_DESCRIPTION = 'wbe_item_description'
WBE_ITEM_QUANTITY = 'wbe_item_quantity'
WBE_ITEM_TOTAL_PRICE = 'wbe_item_total_price'
WBE_ITEM_UNIT_PRICE = 'wbe_item_unit_price'
WBE_ITEM_LIST_PRICE = 'wbe_item_list_price'
WBE_GROUP_CODE = 'wbe_group_code'
WBE_GROUP_DESC = 'wbe_group_desc'
WBE_TYPE_CODE = 'wbe_type_code'
WBE_TYPE_TITLE = 'wbe_type_title'
WBE_SUBTYPE_CODE = 'wbe_subtype_code'
WBE_SUBTYPE_DESC = 'wbe_subtype_desc'

# Summary field name to display name and format mapping
SUMMARY_FIELD_DISPLAY_NAMES = {
    WBE_CODE: {'display_name': 'Proto WBE', 'format': 'default'},
    WBE_DESCRIPTION: {'display_name': 'Description', 'format': 'default'},
    WBE_DIRECT_COST: {'display_name': 'Direct Cost EUR', 'format': 'currency'},
    WBE_LIST_PRICE: {'display_name': 'Listino EUR', 'format': 'currency'},
    WBE_OFFER_PRICE: {'display_name': 'Offer Price EUR', 'format': 'currency'},
    WBE_SELL_PRICE: {'display_name': 'Sell Price EUR', 'format': 'currency'},
    COMMISSIONS_COST: {'display_name': 'Commissions Cost EUR', 'format': 'currency'},
    CONTRIBUTION_MARGIN: {'display_name': 'Contribution Margin EUR', 'format': 'currency'},
    CONTRIBUTION_MARGIN_PERCENT: {'display_name': 'Contribution Margin %', 'format': 'default'}
}

# Detail field name to display name and format mapping
DETAIL_FIELD_DISPLAY_NAMES = {
    WBE_ITEM_CODE: {'display_name': 'Proto BOM', 'format': 'default'},
    WBE_ITEM_DESCRIPTION: {'display_name': 'Description', 'format': 'default'},
    WBE_ITEM_QUANTITY: {'display_name': 'Quantity', 'format': 'quantity'},
    WBE_ITEM_TOTAL_PRICE: {'display_name': 'Total Price EUR', 'format': 'currency'},
    WBE_ITEM_UNIT_PRICE: {'display_name': 'Unit Price EUR', 'format': 'currency'},
    WBE_ITEM_LIST_PRICE: {'display_name': 'Listino EUR', 'format': 'currency'},
    WBE_GROUP_CODE: {'display_name': 'Group', 'format': 'default'},
    WBE_GROUP_DESC: {'display_name': 'Group Description', 'format': 'default'},
    WBE_TYPE_CODE: {'display_name': 'Proto WBE', 'format': 'default'},
    WBE_TYPE_TITLE: {'display_name': 'Proto WBE Description', 'format': 'default'},
    WBE_SUBTYPE_CODE: {'display_name': 'SubType', 'format': 'default'},
    WBE_SUBTYPE_DESC: {'display_name': 'SubType Desc', 'format': 'default'}
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
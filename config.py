"""
Configuration settings for PRE Excel Data Analyzer.
Contains field name mappings for UI display.
"""

import locale
try:
    locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
except locale.Error:
    # Fallback for systems where Italian locale is not installed
    locale.setlocale(locale.LC_ALL, '')

def CURRENCY_FORMAT(x):
    try:
        return locale.format_string('%.2f', x, grouping=True).replace('.', '#').replace(',', '.').replace('#', ',')
    except Exception:
        return str(x)

# Summary field name to display name mapping
SUMMARY_FIELD_DISPLAY_NAMES = {
    'wbe_code': 'Proto WBE',
    'wbe_description': 'Description',
    'wbe_direct_cost': 'Direct Cost EUR',
    'wbe_list_price': 'Listino EUR',
    'wbe_offer_price': 'Offer Price EUR',
    'wbe_sell_price': 'Sell Price EUR',
    'commissions_cost': 'Commissions Cost EUR',
    'contribution_margin': 'Contribution Margin EUR',
    'contribution_margin_percent': 'Contribution Margin %'
}

# Detail field name to display name mapping
DETAIL_FIELD_DISPLAY_NAMES = {
    'wbe_item_code': 'Proto BOM',
    'wbe_item_description': 'Description',
    'wbe_item_quantity': 'Quantity',
    'wbe_item_total_price': 'Total Price EUR',
    'wbe_item_unit_price': 'Unit Price EUR',
    'wbe_item_list_price': 'Listino EUR',
    'wbe_group_code': 'Group',
    'wbe_group_desc': 'Group Description',
    'wbe_type_code': 'Proto WBE',
    'wbe_type_title': 'Proto WBE Description',
    'wbe_subtype_code': 'SubType',
    'wbe_subtype_desc': 'SubType Desc'
}

# Numeric fields that should be formatted as currency
CURRENCY_FIELDS = [
    'wbe_direct_cost',
    'wbe_list_price',
    'wbe_offer_price',
    'wbe_sell_price',
    'wbe_item_total_price',
    'wbe_item_unit_price',
    'wbe_item_list_price',
    'commissions_cost',
    'contribution_margin'
]

# Numeric fields that should be formatted as quantities
QUANTITY_FIELDS = [
    'quantity',
    'wbe_item_quantity'
]

# Default quantity format
QUANTITY_FORMAT = "{:.2f}" 
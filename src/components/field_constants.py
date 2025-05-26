"""
Shared Field Constants
Contains all field name constants used across parsers and analyzers
"""

class JsonFields:
    """JSON field name constants"""
    
    # Project fields
    PROJECT = "project"
    ID = "id"
    LISTINO = "listino"
    PARAMETERS = "parameters"
    SALES_INFO = "sales_info"
    
    # Parameter fields
    DOC_PERCENTAGE = "doc_percentage"
    PM_PERCENTAGE = "pm_percentage"
    FINANCIAL_COSTS = "financial_costs"
    CURRENCY = "currency"
    EXCHANGE_RATE = "exchange_rate"
    WASTE_DISPOSAL = "waste_disposal"
    WARRANTY_PERCENTAGE = "warranty_percentage"
    IS_24H_SERVICE = "is_24h_service"
    
    # Sales info fields
    AREA_MANAGER = "area_manager"
    AGENT = "agent"
    COMMISSION_PERCENTAGE = "commission_percentage"
    AUTHOR = "author"
    
    # Product group fields
    PRODUCT_GROUPS = "product_groups"
    GROUP_ID = "group_id"
    GROUP_NAME = "group_name"
    QUANTITY = "quantity"
    CATEGORIES = "categories"
    
    # Category fields
    CATEGORY_ID = "category_id"
    CATEGORY_NAME = "category_name"
    CATEGORY_CODE = "category_code"
    WBE = "wbe"
    ITEMS = "items"
    PRICELIST_SUBTOTAL = "pricelist_subtotal"
    COST_SUBTOTAL = "cost_subtotal"
    TOTAL_COST = "total_cost"
    
    # Basic item fields
    POSITION = "position"
    CODE = "code"
    COD_LISTINO = "cod_listino"
    DESCRIPTION = "description"
    QTY = "quantity"
    PRICELIST_UNIT_PRICE = "list_unit_price"
    PRICELIST_TOTAL = "listino_total"
    UNIT_COST = "unit_cost"
    TOTAL_COST = "total_cost"
    INTERNAL_CODE = "internal_code"
    PRIORITY_ORDER = "priority_order"
    PRIORITY = "priority"
    LINE_NUMBER = "line_number"
    WBS = "wbs"
    TOTAL = "totale"
    
    # Material and UTM fields
    MAT = "mat"
    UTM_ROBOT = "utm_robot"
    UTM_ROBOT_H = "utm_robot_h"
    UTM_LGV = "utm_lgv"
    UTM_LGV_H = "utm_lgv_h"
    UTM_INTRA = "utm_intra"
    UTM_INTRA_H = "utm_intra_h"
    UTM_LAYOUT = "utm_layout"
    UTM_LAYOUT_H = "utm_layout_h"
    
    # Engineering fields
    UTE = "ute"
    UTE_H = "ute_h"
    BA = "ba"
    BA_H = "ba_h"
    SW_PC = "sw_pc"
    SW_PC_H = "sw_pc_h"
    SW_PLC = "sw_plc"
    SW_PLC_H = "sw_plc_h"
    SW_LGV = "sw_lgv"
    SW_LGV_H = "sw_lgv_h"
    
    # Manufacturing fields
    MTG_MEC = "mtg_mec"
    MTG_MEC_H = "mtg_mec_h"
    MTG_MEC_INTRA = "mtg_mec_intra"
    MTG_MEC_INTRA_H = "mtg_mec_intra_h"
    CAB_ELE = "cab_ele"
    CAB_ELE_H = "cab_ele_h"
    CAB_ELE_INTRA = "cab_ele_intra"
    CAB_ELE_INTRA_H = "cab_ele_intra_h"
    COLL_BA = "coll_ba"
    COLL_BA_H = "coll_ba_h"
    
    # Testing fields
    COLL_PC = "coll_pc"
    COLL_PC_H = "coll_pc_h"
    COLL_PLC = "coll_plc"
    COLL_PLC_H = "coll_plc_h"
    COLL_LGV = "coll_lgv"
    COLL_LGV_H = "coll_lgv_h"
    PM_COST = "pm_cost"
    PM_H = "pm_h"
    SPESE_PM = "spese_pm"
    DOCUMENT = "document"
    
    # Logistics and field fields
    DOCUMENT_H = "document_h"
    IMBALLO = "imballo"
    STOCCAGGIO = "stoccaggio"
    TRASPORTO = "trasporto"
    SITE = "site"
    SITE_H = "site_h"
    INSTALL = "install"
    INSTALL_H = "install_h"
    AV_PC = "av_pc"
    AV_PC_H = "av_pc_h"
    
    # Additional field fields
    AV_PLC = "av_plc"
    AV_PLC_H = "av_plc_h"
    AV_LGV = "av_lgv"
    AV_LGV_H = "av_lgv_h"
    SPESE_FIELD = "spese_field"
    SPESE_VARIE = "spese_varie"
    AFTER_SALES = "after_sales"
    PROVVIGIONI_ITALIA = "provvigioni_italia"
    PROVVIGIONI_ESTERO = "provvigioni_estero"
    TESORETTO = "tesoretto"
    MONTAGGIO_BEMA_MBE_US = "montaggio_bema_mbe_us"
    
    # PRE-specific fields
    PRICELIST_TOTAL_PRICE = "pricelist_total_price"
    PRICELIST_UNIT_PRICE = "pricelist_unit_price"
    LISTINO_UNIT_PRICE = "listino_unit_price"
    LISTINO_TOTAL_PRICE = "listino_total_price"
    SUBTOTAL_LISTINO = "subtotal_listino"
    SUBTOTAL_CODICE = "subtotal_codice"
    TOTAL_OFFER = "total_offer"
    
    # Totals fields
    TOTALS = "totals"
    EQUIPMENT_TOTAL = "equipment_total"
    INSTALLATION_TOTAL = "installation_total"
    SUBTOTAL = "subtotal"
    TOTAL_LISTINO = "total_listino"
    TOTAL_COSTO = "total_costo"
    MARGIN = "margin"
    MARGIN_PERCENTAGE = "margin_percentage"
    GRAND_TOTAL = "grand_total"
    DOC_FEE = "doc_fee"
    PM_FEE = "pm_fee"
    WARRANTY_FEE = "warranty_fee"


class DisplayFields:
    """Display field name constants for UI components"""
    
    # Common display fields
    GROUP_ID = "Group ID"
    GROUP_NAME = "Group Name"
    CATEGORY_ID = "Category ID"
    CATEGORY_NAME = "Category Name"
    ITEM_CODE = "Code"
    ITEM_DESCRIPTION = "Description"
    FULL_DESCRIPTION = "Full Description"
    POSITION = "Position"
    QUANTITY = "Quantity"
    UNIT_PRICE = "Unit Price (€)"
    TOTAL_PRICE = "Total Price (€)"
    
    # Financial display fields
    LISTINO_EUR = "Listino (€)"
    COSTO_EUR = "Costo (€)"
    MARGIN_EUR = "Margin (€)"
    MARGIN_PERCENT = "Margin %"
    EQUIPMENT_EUR = "Equipment (€)"
    INSTALLATION_EUR = "Installation (€)"
    TOTAL_EUR = "Total (€)"
    
    # Category specific
    ITEMS_COUNT = "Items"
    CATEGORIES_COUNT = "Categories"
    TOTAL_ITEMS = "Total Items"
    
    # Analysis specific
    WBE = "WBE"
    CATEGORIES = "Categories"
    ITEMS = "Items"
    USAGE_PERCENT = "Usage %"
    TOTAL_VALUE = "Total Value"
    AVERAGE_VALUE = "Average Value"
    MAX_VALUE = "Max Value"
    COMPONENT = "Component"
    COST_EUR = "Cost (€)"
    PERCENTAGE = "Percentage"
    ACTIVITY = "Activity"
    HOURS = "Hours" 
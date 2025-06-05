"""
Field Mapping Utilities for Parser Integration
Maps legacy parser field names to unified model field names for backward compatibility
"""

from typing import Dict, Any


class FieldMapper:
    """
    Utility class for mapping between different field naming conventions
    and ensuring compatibility between parsers and the unified model.
    """
    
    # =============================================================================
    # PRE FILE PARSER FIELD MAPPINGS
    # =============================================================================
    
    PRE_PROJECT_FIELD_MAP = {
        # Legacy field -> Model field
        "id": "id",
        "customer": "customer",
        "parameters": "parameters",
        "sales_info": "sales_info"
    }
    
    PRE_PARAMETERS_FIELD_MAP = {
        "doc_percentage": "doc_percentage",
        "pm_percentage": "pm_percentage", 
        "financial_costs": "financial_costs",
        "currency": "currency",
        "exchange_rate": "exchange_rate",
        "waste_disposal": "waste_disposal",
        "warranty_percentage": "warranty_percentage",
        "is_24h_service": "is_24h_service"
    }
    
    PRE_SALES_INFO_FIELD_MAP = {
        "area_manager": "area_manager",
        "agent": "agent",
        "commission_percentage": "commission_percentage",
        "author": "author"
    }
    
    PRE_GROUP_FIELD_MAP = {
        "group_id": "group_id",
        "group_name": "group_name",
        "quantity": "quantity",
        "categories": "categories"
    }
    
    PRE_CATEGORY_FIELD_MAP = {
        "category_id": "category_id",
        "code": "category_code",
        "category_name": "category_name",
        "items": "items",
        "subtotal_listino": "pricelist_subtotal",
        "subtotal_codice": "pricelist_subtotal",  # Fallback mapping
        "subtotal_cost": "cost_subtotal",
        "total_cost": "total_cost",
        "total": "total_cost",
        "groups": "wbe",  # Sometimes groups field contains WBE info
        "total_offer": "offer_price",
        "total_offer_currency": "offer_price",
        "notes": "category_code",  # Sometimes notes contain additional codes
        "pricelist_code": "category_code",
        "total_discounted": "offer_price",  # Alternative mapping
    }
    
    PRE_ITEM_FIELD_MAP = {
        "position": "position",
        "code": "code",
        "description": "description",
        "quantity": "quantity",
        "pricelist_unit_price": "pricelist_unit_price",
        "pricelist_total_price": "pricelist_total_price",
        "unit_cost": "unit_cost",
        "total_cost": "total_cost",
        "notes": "cod_listino",
        "pricelist_code": "cod_listino",
    }
    
    PRE_TOTALS_FIELD_MAP = {
        "equipment_total": "equipment_total",
        "installation_total": "installation_total", 
        "subtotal": "subtotal",
        "doc_fee": "doc_fee",
        "pm_fee": "pm_fee",
        "warranty_fee": "warranty_fee",
        "grand_total": "grand_total",
        # Map to enhanced fields as well
        "equipment_total": "total_listino",  # Equipment total often represents listino
        "subtotal": "total_listino",
    }
    
    # =============================================================================
    # ANALISI PROFITTABILITA PARSER FIELD MAPPINGS
    # =============================================================================
    
    AP_PROJECT_FIELD_MAP = {
        "id": "id",
        "listino": "listino",
        "parameters": "parameters",
        "sales_info": "sales_info"
    }
    
    AP_GROUP_FIELD_MAP = {
        "group_id": "group_id",
        "group_name": "group_name", 
        "quantity": "quantity",
        "categories": "categories"
    }
    
    AP_CATEGORY_FIELD_MAP = {
        "category_id": "category_id",
        "category_code": "category_code",
        "category_name": "category_name",
        "wbe": "wbe",
        "pricelist_subtotal": "pricelist_subtotal",
        "cost_subtotal": "cost_subtotal",
        "total_cost": "total_cost",
        "offer_price": "offer_price",
        "items": "items"
    }
    
    AP_ITEM_FIELD_MAP = {
        # Basic fields
        "position": "position",
        "code": "code",
        "cod_listino": "cod_listino",
        "description": "description",
        "quantity": "quantity",  # Maps to QTY field
        "pricelist_unit_price": "pricelist_unit_price",  # Maps to LIST_UNIT
        "pricelist_total_price": "pricelist_total_price",  # Maps to LISTINO_TOTALE
        "unit_cost": "unit_cost",
        "total_cost": "total_cost",
        "internal_code": "internal_code",
        "priority_order": "priority_order",
        "priority": "priority",
        "line_number": "line_number",
        "wbs": "wbs",
        "total": "total",
        
        # All the detailed cost fields (direct mapping)
        "mat": "mat",
        "utm_robot": "utm_robot",
        "utm_robot_h": "utm_robot_h",
        "utm_lgv": "utm_lgv",
        "utm_lgv_h": "utm_lgv_h",
        "utm_intra": "utm_intra",
        "utm_intra_h": "utm_intra_h",
        "utm_layout": "utm_layout",
        "utm_layout_h": "utm_layout_h",
        "ute": "ute",
        "ute_h": "ute_h",
        "ba": "ba",
        "ba_h": "ba_h",
        "sw_pc": "sw_pc",
        "sw_pc_h": "sw_pc_h",
        "sw_plc": "sw_plc",
        "sw_plc_h": "sw_plc_h",
        "sw_lgv": "sw_lgv",
        "sw_lgv_h": "sw_lgv_h",
        "mtg_mec": "mtg_mec",
        "mtg_mec_h": "mtg_mec_h",
        "mtg_mec_intra": "mtg_mec_intra",
        "mtg_mec_intra_h": "mtg_mec_intra_h",
        "cab_ele": "cab_ele",
        "cab_ele_h": "cab_ele_h",
        "cab_ele_intra": "cab_ele_intra",
        "cab_ele_intra_h": "cab_ele_intra_h",
        "coll_ba": "coll_ba",
        "coll_ba_h": "coll_ba_h",
        "coll_pc": "coll_pc",
        "coll_pc_h": "coll_pc_h",
        "coll_plc": "coll_plc",
        "coll_plc_h": "coll_plc_h",
        "coll_lgv": "coll_lgv",
        "coll_lgv_h": "coll_lgv_h",
        "pm_cost": "pm_cost",
        "pm_h": "pm_h",
        "spese_pm": "spese_pm",
        "document": "document",
        "document_h": "document_h",
        "imballo": "imballo",
        "stoccaggio": "stoccaggio",
        "trasporto": "trasporto",
        "site": "site",
        "site_h": "site_h",
        "install": "install",
        "install_h": "install_h",
        "av_pc": "av_pc",
        "av_pc_h": "av_pc_h",
        "av_plc": "av_plc",
        "av_plc_h": "av_plc_h",
        "av_lgv": "av_lgv",
        "av_lgv_h": "av_lgv_h",
        "spese_field": "spese_field",
        "spese_varie": "spese_varie",
        "after_sales": "after_sales",
        "provvigioni_italia": "provvigioni_italia",
        "provvigioni_estero": "provvigioni_estero",
        "tesoretto": "tesoretto",
        "montaggio_bema_mbe_us": "montaggio_bema_mbe_us"
    }
    
    AP_TOTALS_FIELD_MAP = {
        "equipment_total": "equipment_total",
        "installation_total": "installation_total",
        "subtotal": "subtotal",
        "total_listino": "total_listino",
        "total_costo": "total_costo",
        "total_offer": "total_offer",
        "margin": "margin",
        "margin_percentage": "margin_percentage",
        "offer_margin": "offer_margin",
        "offer_margin_percentage": "offer_margin_percentage"
    }
    
    # =============================================================================
    # MAPPING FUNCTIONS
    # =============================================================================
    
    @classmethod
    def map_pre_project_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map PRE file project data to unified model format"""
        mapped = {}
        
        for legacy_field, model_field in cls.PRE_PROJECT_FIELD_MAP.items():
            if legacy_field in data:
                mapped[model_field] = data[legacy_field]
        
        # Handle parameters sub-mapping
        if "parameters" in data:
            mapped["parameters"] = cls.map_dict_fields(
                data["parameters"], cls.PRE_PARAMETERS_FIELD_MAP
            )
        
        # Handle sales_info sub-mapping
        if "sales_info" in data:
            mapped["sales_info"] = cls.map_dict_fields(
                data["sales_info"], cls.PRE_SALES_INFO_FIELD_MAP
            )
        
        return mapped
    
    @classmethod
    def map_pre_category_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map PRE file category data to unified model format"""
        mapped = cls.map_dict_fields(data, cls.PRE_CATEGORY_FIELD_MAP)
        
        # Handle items sub-mapping
        if "items" in data:
            mapped["items"] = [
                cls.map_dict_fields(item, cls.PRE_ITEM_FIELD_MAP) 
                for item in data["items"]
            ]
        
        return mapped
    
    @classmethod
    def map_pre_totals_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map PRE file totals data to unified model format"""
        return cls.map_dict_fields(data, cls.PRE_TOTALS_FIELD_MAP)
    
    @classmethod
    def map_ap_project_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map Analisi Profittabilita project data to unified model format"""
        mapped = {}
        
        for legacy_field, model_field in cls.AP_PROJECT_FIELD_MAP.items():
            if legacy_field in data:
                mapped[model_field] = data[legacy_field]
        
        # Handle parameters - AP uses defaults for most parameters
        if "parameters" in data:
            mapped["parameters"] = data["parameters"]
        else:
            mapped["parameters"] = {}
            
        # Handle sales_info - AP uses defaults for sales info
        if "sales_info" in data:
            mapped["sales_info"] = data["sales_info"]
        else:
            mapped["sales_info"] = {}
        
        return mapped
    
    @classmethod
    def map_ap_category_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map Analisi Profittabilita category data to unified model format"""
        mapped = cls.map_dict_fields(data, cls.AP_CATEGORY_FIELD_MAP)
        
        # Handle items sub-mapping
        if "items" in data:
            mapped["items"] = [
                cls.map_dict_fields(item, cls.AP_ITEM_FIELD_MAP)
                for item in data["items"]
            ]
        
        return mapped
    
    @classmethod
    def map_ap_totals_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map Analisi Profittabilita totals data to unified model format"""
        return cls.map_dict_fields(data, cls.AP_TOTALS_FIELD_MAP)
    
    @classmethod
    def map_dict_fields(cls, data: Dict[str, Any], field_map: Dict[str, str]) -> Dict[str, Any]:
        """Generic function to map dictionary fields using a field mapping"""
        mapped = {}
        
        for legacy_field, model_field in field_map.items():
            if legacy_field in data and data[legacy_field] is not None:
                mapped[model_field] = data[legacy_field]
        
        return mapped
    
    @classmethod
    def convert_pre_parser_dict(cls, parser_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert complete PRE parser output to unified model format
        
        Args:
            parser_data: Dictionary from pre_file_parser.parse()
            
        Returns:
            Dictionary compatible with IndustrialQuotation model
        """
        converted = {}
        
        # Map project data
        if "project" in parser_data:
            converted["project"] = cls.map_pre_project_data(parser_data["project"])
        
        # Map product groups and categories
        if "product_groups" in parser_data:
            converted_groups = []
            
            for group in parser_data["product_groups"]:
                converted_group = cls.map_dict_fields(group, cls.PRE_GROUP_FIELD_MAP)
                
                # Map categories within group
                if "categories" in group:
                    converted_group["categories"] = [
                        cls.map_pre_category_data(category)
                        for category in group["categories"]
                    ]
                
                converted_groups.append(converted_group)
            
            converted["product_groups"] = converted_groups
        
        # Map totals
        if "totals" in parser_data:
            converted["totals"] = cls.map_pre_totals_data(parser_data["totals"])
        
        return converted
    
    @classmethod
    def convert_ap_parser_dict(cls, parser_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert complete Analisi Profittabilita parser output to unified model format
        
        Args:
            parser_data: Dictionary from analisi_profittabilita_parser.parse()
            
        Returns:
            Dictionary compatible with IndustrialQuotation model
        """
        converted = {}
        
        # Map project data
        if "project" in parser_data:
            converted["project"] = cls.map_ap_project_data(parser_data["project"])
        
        # Map product groups and categories
        if "product_groups" in parser_data:
            converted_groups = []
            
            for group in parser_data["product_groups"]:
                converted_group = cls.map_dict_fields(group, cls.AP_GROUP_FIELD_MAP)
                
                # Map categories within group
                if "categories" in group:
                    converted_group["categories"] = [
                        cls.map_ap_category_data(category)
                        for category in group["categories"]
                    ]
                
                converted_groups.append(converted_group)
            
            converted["product_groups"] = converted_groups
        
        # Map totals
        if "totals" in parser_data:
            converted["totals"] = cls.map_ap_totals_data(parser_data["totals"])
        
        return converted 
"""
Unified Data Models for Industrial Equipment Quotations
Pydantic models for parsing, validation, and data manipulation of quotation data
from both PRE files and Analisi Profittabilita files.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
import pandas as pd
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum

logger = logging.getLogger(__name__)

# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class CurrencyType(str, Enum):
    """Supported currency types"""
    EUR = "EUR"
    USD = "USD"

class CategoryType(str, Enum):
    """Category types for equipment classification"""
    EQUIPMENT = "EQUIPMENT"  # Non-installation categories
    INSTALLATION = "INSTALLATION"  # Installation categories (starting with 'E')

class ParserType(str, Enum):
    """Supported parser types for quotation files"""
    PRE_FILE_PARSER = "pre_file_parser"
    ANALISI_PROFITTABILITA_PARSER = "analisi_profittabilita_parser"

# =============================================================================
# BASE MODELS
# =============================================================================

class ProjectParameters(BaseModel):
    """
    Project calculation parameters used for cost and pricing calculations.
    These parameters affect the final quotation totals and margins.
    """
    doc_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Documentation fee percentage (0-1), applied to subtotal for admin costs"
    )
    pm_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Project management fee percentage (0-1), applied to subtotal for PM costs"
    )
    financial_costs: float = Field(
        default=0.0,
        ge=0.0,
        description="Fixed financial costs amount in project currency"
    )
    currency: CurrencyType = Field(
        default=CurrencyType.EUR,
        description="Base currency for all monetary values in the project"
    )
    exchange_rate: float = Field(
        default=1.0,
        gt=0.0,
        description="Exchange rate from base currency to target currency (default 1.0 for same currency)"
    )
    waste_disposal: float = Field(
        default=0.0,
        ge=0.0,
        description="Waste disposal costs amount in project currency"
    )
    warranty_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Warranty fee percentage (0-1), applied to subtotal for warranty coverage"
    )
    is_24h_service: bool = Field(
        default=False,
        description="Whether 24-hour service support is included in the project"
    )

    @field_validator('currency', mode='before')
    @classmethod
    def normalize_currency(cls, v):
        """
        Normalize currency input to handle common formatting issues from Excel parsing.
        
        This validator:
        - Strips whitespace
        - Converts to uppercase 
        - Handles None/empty values by defaulting to EUR
        - Maps common variants to standard currency codes
        """
        if v is None or v == "":
            return CurrencyType.EUR.value
        
        # Convert to string and normalize
        currency_str = str(v).strip().upper()
        
        # Handle common variants
        currency_mapping = {
            "EURO": "EUR",
            "€": "EUR",
            "EUROS": "EUR",
            "DOLLAR": "USD", 
            "DOLLARS": "USD",
            "$": "USD",
            "POUND": "GBP",
            "POUNDS": "GBP",
            "£": "GBP",
            "YEN": "JPY",
            "¥": "JPY"
        }
        
        normalized = currency_mapping.get(currency_str, currency_str)
        
        # Validate against supported currencies
        try:
            return CurrencyType(normalized).value
        except ValueError:
            # If invalid currency, log warning and default to EUR
            logger.warning(f"Invalid currency '{v}' normalized to '{normalized}', defaulting to EUR")
            return CurrencyType.EUR.value

class SalesInfo(BaseModel):
    """
    Sales team information and commission details for the project.
    Used for tracking sales performance and calculating commissions.
    """
    area_manager: Optional[str] = Field(
        default=None,
        description="Name of the area sales manager responsible for this region"
    )
    agent: Optional[str] = Field(
        default=None,
        description="Name of the sales agent handling this specific project"
    )
    commission_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Sales commission percentage (0-1) for this project"
    )
    author: Optional[str] = Field(
        default=None,
        description="Name of the person who created/authored this quotation"
    )

class ProjectInfo(BaseModel):
    """
    High-level project identification and configuration information.
    Contains basic project details and calculation parameters.
    """
    id: str = Field(
        description="Unique project identifier or quotation number"
    )
    customer: Optional[str] = Field(
        default=None,
        description="Customer name or company (used in PRE files)"
    )
    listino: Optional[str] = Field(
        default=None,
        description="Price list or catalog reference (used in Analisi Profittabilita files)"
    )
    parameters: ProjectParameters = Field(
        description="Project calculation parameters affecting costs and pricing"
    )
    sales_info: SalesInfo = Field(
        description="Sales team information and commission details"
    )

class QuotationItem(BaseModel):
    """
    Individual line item within a category representing a specific product or service.
    Contains detailed breakdown of quantities, prices, costs, and resource allocations.
    """
    # Basic identification fields
    position: str = Field(
        description="Line item position number or identifier within the category"
    )
    code: str = Field(
        description="Product or service code from the catalog or system"
    )
    cod_listino: Optional[str] = Field(
        default="",
        description="Price list code or catalog reference for this item"
    )
    description: str = Field(
        description="Detailed description of the product or service"
    )
    
    # Quantity and pricing fields
    quantity: float = Field(
        default=1.0,
        #ge=0.0,
        description="Quantity of items (pieces, hours, etc.)"
    )
    pricelist_unit_price: float = Field(
        default=0.0,
        #ge=0.0,
        description="Unit price from the official price list"
    )
    pricelist_total_price: float = Field(
        default=0.0,
        #ge=0.0,
        description="Total price from price list (quantity × unit price)"
    )
    
    # Cost fields
    unit_cost: float = Field(
        default=0.0,
        #ge=0.0,
        description="Internal unit cost for this item"
    )
    total_cost: float = Field(
        default=0.0,
        #ge=0.0,
        description="Total internal cost (quantity × unit cost)"
    )
    
    # Additional identification fields (mainly for Analisi Profittabilita)
    internal_code: Optional[str] = Field(
        default="",
        description="Internal system code or reference"
    )
    priority_order: Optional[int] = Field(
        default=0,
        description="Priority order for sorting and processing"
    )
    priority: Optional[int] = Field(
        default=0,
        description="Priority level for this item"
    )
    line_number: Optional[int] = Field(
        default=0,
        description="Sequential line number in the original document"
    )
    wbs: Optional[str] = Field(
        default="",
        description="Work Breakdown Structure code for project management"
    )
    total: Optional[float] = Field(
        default=0.0,
        description="Total amount for this line item"
    )
    
    # Material and Robot Engineering fields (UTM = Ufficio Tecnico Meccanico)
    mat: float = Field(default=0.0,  description="Material costs allocated to this item")
    utm_robot: float = Field(default=0.0,  description="Robot engineering costs (UTM)")
    utm_robot_h: float = Field(default=0.0,  description="Robot engineering hours (UTM)")
    utm_lgv: float = Field(default=0.0,  description="LGV (Laser Guided Vehicle) engineering costs")
    utm_lgv_h: float = Field(default=0.0,  description="LGV engineering hours")
    utm_intra: float = Field(default=0.0,  description="Intralogistics engineering costs")
    utm_intra_h: float = Field(default=0.0,  description="Intralogistics engineering hours")
    utm_layout: float = Field(default=0.0,  description="Layout design engineering costs")
    utm_layout_h: float = Field(default=0.0,  description="Layout design engineering hours")
    
    # Technical Engineering fields (UTE = Ufficio Tecnico Elettrico)
    ute: float = Field(default=0.0,  description="Electrical engineering costs (UTE)")
    ute_h: float = Field(default=0.0,  description="Electrical engineering hours (UTE)")
    ba: float = Field(default=0.0,  description="Business Analysis costs")
    ba_h: float = Field(default=0.0,  description="Business Analysis hours")
    
    # Software Development fields
    sw_pc: float = Field(default=0.0,  description="PC software development costs")
    sw_pc_h: float = Field(default=0.0,  description="PC software development hours")
    sw_plc: float = Field(default=0.0,  description="PLC software development costs")
    sw_plc_h: float = Field(default=0.0,  description="PLC software development hours")
    sw_lgv: float = Field(default=0.0,  description="LGV software development costs")
    sw_lgv_h: float = Field(default=0.0,  description="LGV software development hours")
    
    # Manufacturing fields (MTG = Montaggio)
    mtg_mec: float = Field(default=0.0,  description="Mechanical assembly costs")
    mtg_mec_h: float = Field(default=0.0,  description="Mechanical assembly hours")
    mtg_mec_intra: float = Field(default=0.0,  description="Intralogistics mechanical assembly costs")
    mtg_mec_intra_h: float = Field(default=0.0,  description="Intralogistics mechanical assembly hours")
    cab_ele: float = Field(default=0.0,  description="Electrical cabinet assembly costs")
    cab_ele_h: float = Field(default=0.0,  description="Electrical cabinet assembly hours")
    cab_ele_intra: float = Field(default=0.0,  description="Intralogistics electrical cabinet costs")
    cab_ele_intra_h: float = Field(default=0.0,  description="Intralogistics electrical cabinet hours")
    
    # Testing and Commissioning fields (COLL = Collaudo)
    coll_ba: float = Field(default=0.0,  description="Business Analysis testing costs")
    coll_ba_h: float = Field(default=0.0,  description="Business Analysis testing hours")
    coll_pc: float = Field(default=0.0,  description="PC software testing costs")
    coll_pc_h: float = Field(default=0.0,  description="PC software testing hours")
    coll_plc: float = Field(default=0.0,  description="PLC software testing costs")
    coll_plc_h: float = Field(default=0.0,  description="PLC software testing hours")
    coll_lgv: float = Field(default=0.0,  description="LGV system testing costs")
    coll_lgv_h: float = Field(default=0.0,  description="LGV system testing hours")
    
    # Project Management fields
    pm_cost: float = Field(default=0.0,  description="Project management costs allocated to this item")
    pm_h: float = Field(default=0.0,  description="Project management hours allocated to this item")
    spese_pm: float = Field(default=0.0,  description="Project management expenses (travel, etc.)")
    
    # Documentation fields
    document: float = Field(default=0.0,  description="Documentation preparation costs")
    document_h: float = Field(default=0.0,  description="Documentation preparation hours")
    
    # Logistics fields
    imballo: float = Field(default=0.0,  description="Packaging costs")
    stoccaggio: float = Field(default=0.0,  description="Storage and warehousing costs")
    trasporto: float = Field(default=0.0,  description="Transportation and shipping costs")
    
    # Field Installation fields
    site: float = Field(default=0.0,  description="On-site work costs")
    site_h: float = Field(default=0.0,  description="On-site work hours")
    install: float = Field(default=0.0,  description="Installation costs")
    install_h: float = Field(default=0.0,  description="Installation hours")
    
    # Field Commissioning fields (AV = Avviamento)
    av_pc: float = Field(default=0.0,  description="PC system commissioning costs")
    av_pc_h: float = Field(default=0.0,  description="PC system commissioning hours")
    av_plc: float = Field(default=0.0,  description="PLC system commissioning costs")
    av_plc_h: float = Field(default=0.0,  description="PLC system commissioning hours")
    av_lgv: float = Field(default=0.0,  description="LGV system commissioning costs")
    av_lgv_h: float = Field(default=0.0,  description="LGV system commissioning hours")
    
    # Additional cost fields
    spese_field: float = Field(default=0.0,  description="Field work expenses (travel, accommodation)")
    spese_varie: float = Field(default=0.0,  description="Miscellaneous expenses")
    after_sales: float = Field(default=0.0,  description="After-sales service costs")
    
    # Commission fields
    provvigioni_italia: float = Field(default=0.0,  description="Sales commissions for Italian market")
    provvigioni_estero: float = Field(default=0.0,  description="Sales commissions for international market")
    tesoretto: float = Field(default=0.0,  description="Special reserve or contingency fund")
    montaggio_bema_mbe_us: float = Field(default=0.0,  description="BEMA MBE-US assembly costs")

    @field_validator('pricelist_total_price')
    @classmethod
    def validate_pricelist_total(cls, v, info):
        """Validate that pricelist total equals quantity × unit price when provided"""
        if hasattr(info, 'data') and info.data:
            quantity = info.data.get('quantity', 0.0)
            pricelist_unit_price = info.data.get('pricelist_unit_price', 0.0)
            expected = quantity * pricelist_unit_price
            if v == 0.0 and expected > 0:
                return expected
        return v

    @field_validator('total_cost')
    @classmethod
    def validate_total_cost(cls, v, info):
        """Validate that total cost equals quantity × unit cost when provided"""
        if hasattr(info, 'data') and info.data:
            quantity = info.data.get('quantity', 0.0)
            unit_cost = info.data.get('unit_cost', 0.0)
            expected = quantity * unit_cost
            if v == 0.0 and expected > 0:
                return expected
        return v

class QuotationCategory(BaseModel):
    """
    Category grouping related items together (e.g., all robot components).
    Categories aggregate items and provide subtotals for different cost types.
    """
    category_id: str = Field(
        description="Unique identifier for this category (typically 4-character code)"
    )
    category_code: Optional[str] = Field(
        default="",
        description="Additional category code or reference"
    )
    category_name: str = Field(
        description="Human-readable name describing this category"
    )
    wbe: Optional[str] = Field(
        default="",
        description="Work Breakdown Element code for project tracking and SAP integration"
    )
    
    groups_count: float = Field(
        default=1.0,
        description="Group quantity for this category"
    )
    
    notes: Optional[str] = Field(
        default="",
        description="Notes for this category"
    )
    
    # Subtotal fields
    pricelist_subtotal: float = Field(
        default=0.0,
        ge=0.0,
        description="Sum of all pricelist prices for items in this category"
    )
    cost_subtotal: float = Field(
        default=0.0,
        ge=0.0,
        description="Sum of all internal costs for items in this category"
    )
    total_cost: float = Field(
        default=0.0,
        ge=0.0,
        description="Total cost for this category (usually equals cost_subtotal)"
    )
    offer_price: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Final offer price for this category (from VA21 integration)"
    )
    
    # Items in this category
    items: List[QuotationItem] = Field(
        default_factory=list,
        description="List of individual items belonging to this category"
    )
    
    margin_amount: Optional[float] = Field(
        default=None,
        description="Margin amount for this category"
    )
    
    margin_percentage: Optional[float] = Field( 
        default=None,
        description="Margin percentage for this category"
    )

    @property
    def category_type(self) -> CategoryType:
        """Determine if this is an equipment or installation category"""
        return CategoryType.INSTALLATION if self.category_id.startswith('E') else CategoryType.EQUIPMENT

    @property
    def calculated_pricelist_subtotal(self) -> float:
        """Calculate pricelist subtotal from items"""
        return sum(item.pricelist_total_price for item in self.items)

    @property
    def calculated_cost_subtotal(self) -> float:
        """Calculate cost subtotal from items"""
        return sum(item.total_cost for item in self.items)

    @model_validator(mode='before')
    @classmethod
    def calculate_subtotals(cls, values):
        """Auto-calculate subtotals if not provided"""
        if isinstance(values, dict):
            items = values.get('items', [])
            
            if values.get('pricelist_subtotal', 0.0) == 0.0 and items:
                values['pricelist_subtotal'] = sum(getattr(item, 'pricelist_total_price', 0.0) if hasattr(item, 'pricelist_total_price') else item.get('pricelist_total_price', 0.0) for item in items)
            
            if values.get('cost_subtotal', 0.0) == 0.0 and items:
                values['cost_subtotal'] = sum(getattr(item, 'total_cost', 0.0) if hasattr(item, 'total_cost') else item.get('total_cost', 0.0) for item in items)
            
            if values.get('total_cost', 0.0) == 0.0:
                values['total_cost'] = values.get('cost_subtotal', 0.0)
        
        return values

"""     @property
    def margin_amount(self) -> float:
   
        if self.offer_price is not None:
            return self.offer_price - self.cost_subtotal
        return self.pricelist_subtotal - self.cost_subtotal

    @property
    def margin_percentage(self) -> float:
   
        if self.offer_price is not None and self.offer_price > 0:
            # Use offer-based margin: margin% = 1 - (cost / offer)
            return (1 - (self.cost_subtotal / self.offer_price)) * 100
        elif self.pricelist_subtotal > 0:
            # Use pricelist-based margin: margin% = (pricelist - cost) / pricelist
            return ((self.pricelist_subtotal - self.cost_subtotal) / self.pricelist_subtotal) * 100
        return 0.0 
"""



class ProductGroup(BaseModel):
    """
    High-level grouping of related categories (e.g., all components for a specific system).
    Product groups organize the quotation into logical business units.
    """
    group_id: str = Field(
        description="Unique identifier for this product group (e.g., TXT-ROBOT-01)"
    )
    group_name: str = Field(
        description="Human-readable name describing this product group"
    )
    quantity: int = Field(
        default=1,
        ge=1,
        description="Quantity of this entire product group (usually 1 for unique systems)"
    )
    categories: List[QuotationCategory] = Field(
        default_factory=list,
        description="List of categories belonging to this product group"
    )

    @property
    def total_pricelist_value(self) -> float:
        """Total pricelist value across all categories"""
        return sum(cat.pricelist_subtotal for cat in self.categories)

    @property
    def total_cost_value(self) -> float:
        """Total cost value across all categories"""
        return sum(cat.cost_subtotal for cat in self.categories)

    @property
    def total_offer_value(self) -> float:
        """Total offer value across all categories (if available)"""
        return sum(cat.offer_price or 0.0 for cat in self.categories)

    @property
    def item_count(self) -> int:
        """Total number of items across all categories"""
        return sum(len(cat.items) for cat in self.categories)

class QuotationTotals(BaseModel):
    """
    Summary totals and calculations for the entire quotation.
    """

    total_pricelist: float = Field(
        default=0.0,
        ge=0.0,
        description="Final total pricelist"
    )
    
    total_cost: float = Field(
        default=0.0,
        ge=0.0,
        description="Total internal costs"
    )
    total_offer: float = Field(
        default=0.0,
        ge=0.0,
        description="Total offer price (from VA21 integration)"
    )

    offer_margin: float = Field(
        default=0.0,
        description="Offer-based margin amount (offer - cost)"
    )
    offer_margin_percentage: float = Field(
        default=0.0,
        description="Offer-based margin percentage: (1 - cost/offer) * 100"
    )



class IndustrialQuotation(BaseModel):
    """
    Complete industrial equipment quotation model.
    This is the root model that encompasses all quotation data from both PRE and Analisi Profittabilita files.
    
    Supports:
    - Full data validation
    - JSON serialization/deserialization
    - Pandas DataFrame conversion
    - LLM-friendly field descriptions
    - Database storage preparation
    """
    project: ProjectInfo = Field(
        description="Project identification and configuration information"
    )
    product_groups: List[ProductGroup] = Field(
        default_factory=list,
        description="List of product groups containing categorized quotation items"
    )
    totals: QuotationTotals = Field(
        description="Summary totals, margins, and financial calculations"
    )
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when this quotation model was created"
    )
    source_file: Optional[str] = Field(
        default=None,
        description="Path to the source Excel file that was parsed"
    )
    parser_type: ParserType = Field(
        default=None,
        description="Type of parser used (pre_file_parser or analisi_profittabilita_parser)"
    )

    model_config = {
        "validate_assignment": True,
        "use_enum_values": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

    pass
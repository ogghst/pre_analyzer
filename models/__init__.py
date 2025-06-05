"""
Models Package for Industrial Equipment Quotations
Provides unified Pydantic models and field mapping utilities for parsing quotation data.
"""

from .quotation_models import (
    # Main model classes
    IndustrialQuotation,
    ProjectInfo, 
    ProjectParameters,
    SalesInfo,
    ProductGroup,
    QuotationCategory,
    QuotationItem,
    QuotationTotals,
    
    # Enums
    CurrencyType,
    CategoryType,
    ParserType,
)

from .field_mappings import FieldMapper

__all__ = [
    # Main model classes
    "IndustrialQuotation",
    "ProjectInfo",
    "ProjectParameters", 
    "SalesInfo",
    "ProductGroup",
    "QuotationCategory",
    "QuotationItem",
    "QuotationTotals",
    
    # Enums
    "CurrencyType",
    "CategoryType",
    "ParserType",
    
    # Utilities
    "FieldMapper",
] 
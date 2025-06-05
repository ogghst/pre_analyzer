#!/usr/bin/env python3
"""
Direct PRE File Parser - Excel to IndustrialQuotation Model
Converts Excel files with PRE format directly to IndustrialQuotation objects
"""

import logging
import decimal
from typing import List, Optional, Any, Dict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from openpyxl import load_workbook

# Import unified models
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models.quotation_models import (
    IndustrialQuotation, ProjectInfo, ProjectParameters, SalesInfo,
    ProductGroup, QuotationCategory, QuotationItem, QuotationTotals,
    CurrencyType, CategoryType
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =============================================================================
# CONSTANTS
# =============================================================================

# Excel Column Indices (1-based)
class ExcelColumns:
    COD = 1
    CODICE = 3
    DENOMINAZIONE = 4
    QTA = 5
    LIST_UNIT = 6
    LISTINO = 7
    SUB_TOT_LISTINO = 8
    SUB_TOT_CODICE = 9
    TOTALE = 10
    GRUPPI = 11
    TOTALE_OFFERTA = 12
    VALUTA = 13
    TOTALE_CODICE = 14
    TOTALE_SCONTATO = 15
    NOTE = 16
    COD_LISTINO = 17
    TOTAL_DISCOUNTED = 18
    COSTO_UNITARIO = 19
    COSTO = 20
    SUB_TOT_COSTO = 21
    TOTALE_COSTO = 22

# Excel Row Constants
class ExcelRows:
    HEADER_ROW = 17
    DATA_START_ROW = 18

# Project Information Cell Positions (row, column)
class ProjectInfoCells:
    PROJECT_ID = (1, 1)  # Row 1, Column A
    CUSTOMER = (3, 7)    # Row 3, Column G
    DOC_PERCENTAGE = (8, 2)     # Row 8, Column B
    PM_PERCENTAGE = (9, 2)      # Row 9, Column B
    FINANCIAL_COSTS = (10, 2)   # Row 10, Column B
    CURRENCY = (11, 2)          # Row 11, Column B
    EXCHANGE_RATE = (12, 2)     # Row 12, Column B
    WASTE_DISPOSAL = (13, 2)    # Row 13, Column B
    WARRANTY_PERCENTAGE = (8, 11) # Row 8, Column K

# Identification Patterns
class IdentificationPatterns:
    GROUP_PREFIX = 'TXT-'
    CATEGORY_CODE_LENGTH = 4
    HEADER_CODE = 'COD'

# =============================================================================
# DIRECT PRE FILE PARSER
# =============================================================================

class DirectPreFileParser:
    """Direct parser for converting PRE Excel files to IndustrialQuotation objects"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.workbook = None
        self.ws = None
        
    def load_workbook(self) -> None:
        """Load the Excel workbook"""
        try:
            self.workbook = load_workbook(str(self.file_path), data_only=True)
            self.ws = self.workbook['OFFER1']
            logger.info(f"Loaded workbook with {self.ws.max_row} rows and {self.ws.max_column} columns")
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.file_path}")
        except Exception as e:
            raise Exception(f"Unable to load workbook: {str(e)}")
    
    def extract_project_info(self) -> ProjectInfo:
        """Extract project information and create ProjectInfo object"""
        # Extract basic project info
        project_id_cell = self.ws.cell(row=ProjectInfoCells.PROJECT_ID[0], column=ProjectInfoCells.PROJECT_ID[1])
        customer_cell = self.ws.cell(row=ProjectInfoCells.CUSTOMER[0], column=ProjectInfoCells.CUSTOMER[1])
        
        project_id = self._extract_after_colon(project_id_cell.value, "")
        customer = self._extract_after_colon(customer_cell.value, "")
        
        # Extract parameters
        doc_cell = self.ws.cell(row=ProjectInfoCells.DOC_PERCENTAGE[0], column=ProjectInfoCells.DOC_PERCENTAGE[1])
        pm_cell = self.ws.cell(row=ProjectInfoCells.PM_PERCENTAGE[0], column=ProjectInfoCells.PM_PERCENTAGE[1])
        financial_cell = self.ws.cell(row=ProjectInfoCells.FINANCIAL_COSTS[0], column=ProjectInfoCells.FINANCIAL_COSTS[1])
        currency_cell = self.ws.cell(row=ProjectInfoCells.CURRENCY[0], column=ProjectInfoCells.CURRENCY[1])
        exchange_cell = self.ws.cell(row=ProjectInfoCells.EXCHANGE_RATE[0], column=ProjectInfoCells.EXCHANGE_RATE[1])
        waste_cell = self.ws.cell(row=ProjectInfoCells.WASTE_DISPOSAL[0], column=ProjectInfoCells.WASTE_DISPOSAL[1])
        warranty_cell = self.ws.cell(row=ProjectInfoCells.WARRANTY_PERCENTAGE[0], column=ProjectInfoCells.WARRANTY_PERCENTAGE[1])
        
        # Create parameters object
        parameters = ProjectParameters(
            doc_percentage=self._safe_decimal(self._extract_after_colon(doc_cell.value)),
            pm_percentage=self._safe_decimal(self._extract_after_colon(pm_cell.value)),
            financial_costs=self._safe_decimal(self._extract_after_colon(financial_cell.value)),
            currency=self._extract_after_colon(currency_cell.value, "EUR"),
            exchange_rate=self._safe_decimal(self._extract_after_colon(exchange_cell.value), Decimal("1.0")),
            waste_disposal=self._safe_decimal(self._extract_after_colon(waste_cell.value)),
            warranty_percentage=self._safe_decimal(self._extract_after_colon(warranty_cell.value)),
            is_24h_service=False  # Default value, could be extracted if present
        )
        
        # Create sales info object (defaults for PRE files)
        sales_info = SalesInfo(
            area_manager=None,
            agent=None,
            commission_percentage=Decimal("0.0"),
            author=None
        )
        
        return ProjectInfo(
            id=project_id,
            customer=customer,
            parameters=parameters,
            sales_info=sales_info
        )
    
    def extract_product_groups(self) -> List[ProductGroup]:
        """Extract product groups, categories, and items directly as model objects"""
        product_groups = []
        current_group = None
        current_category = None
        
        # Start from data start row
        for row in range(ExcelRows.DATA_START_ROW, self.ws.max_row + 1):
            # Get cell values
            cod_val = self.ws.cell(row=row, column=ExcelColumns.COD).value
            codice_val = self.ws.cell(row=row, column=ExcelColumns.CODICE).value
            denominazione_val = self.ws.cell(row=row, column=ExcelColumns.DENOMINAZIONE).value
            qta_val = self.ws.cell(row=row, column=ExcelColumns.QTA).value
            listino_val = self.ws.cell(row=row, column=ExcelColumns.LIST_UNIT).value
            listino_tot_val = self.ws.cell(row=row, column=ExcelColumns.LISTINO).value
            sub_tot_listino_val = self.ws.cell(row=row, column=ExcelColumns.SUB_TOT_LISTINO).value
            sub_tot_codice_val = self.ws.cell(row=row, column=ExcelColumns.SUB_TOT_CODICE).value
            tot_val = self.ws.cell(row=row, column=ExcelColumns.TOTALE).value
            gruppi_val = self.ws.cell(row=row, column=ExcelColumns.GRUPPI).value
            tot_offer_val = self.ws.cell(row=row, column=ExcelColumns.TOTALE_OFFERTA).value
            note_val = self.ws.cell(row=row, column=ExcelColumns.NOTE).value
            cod_listino_val = self.ws.cell(row=row, column=ExcelColumns.COD_LISTINO).value
            costo_unitario_val = self.ws.cell(row=row, column=ExcelColumns.COSTO_UNITARIO).value
            costo_val = self.ws.cell(row=row, column=ExcelColumns.COSTO).value
            sub_tot_costo_val = self.ws.cell(row=row, column=ExcelColumns.SUB_TOT_COSTO).value
            tot_costo_val = self.ws.cell(row=row, column=ExcelColumns.TOTALE_COSTO).value
            
            # Check if this is a group header
            if codice_val and str(codice_val).startswith(IdentificationPatterns.GROUP_PREFIX):
                # Save previous group if exists
                if current_group:
                    product_groups.append(current_group)
                
                # Start new group
                current_group = ProductGroup(
                    group_id=str(codice_val),
                    group_name=str(denominazione_val) if denominazione_val else "",
                    quantity=self._safe_int(qta_val, 1),
                    categories=[]
                )
                current_category = None
                logger.info(f"Found group: {codice_val}")
                
            # Check if this is a category
            elif cod_val and len(str(cod_val).strip()) == IdentificationPatterns.CATEGORY_CODE_LENGTH and current_group:
                category_type = self._determine_category_type(str(cod_val))
                
                current_category = QuotationCategory(
                    category_id=str(cod_val),
                    category_name=str(denominazione_val) if denominazione_val else "",
                    items=[],
                    pricelist_subtotal=float(self._safe_decimal(sub_tot_listino_val)),
                    cost_subtotal=float(self._safe_decimal(sub_tot_costo_val)),
                    total_cost=float(self._safe_decimal(tot_costo_val)),
                    offer_price=float(self._safe_decimal(tot_offer_val)) if tot_offer_val else None
                )
                current_group.categories.append(current_category)
                logger.info(f"Found category: {cod_val}")
                
            # Check if this is an item
            elif (codice_val and denominazione_val and current_category 
                  and not str(codice_val).startswith(IdentificationPatterns.GROUP_PREFIX) 
                  and not str(codice_val).startswith(IdentificationPatterns.HEADER_CODE)):
                
                item = QuotationItem(
                    position=str(row),
                    code=str(codice_val),
                    description=str(denominazione_val),
                    quantity=float(self._safe_decimal(qta_val)),
                    pricelist_unit_price=float(self._safe_decimal(listino_val)),
                    pricelist_total_price=float(self._safe_decimal(listino_tot_val)),
                    unit_cost=float(self._safe_decimal(costo_unitario_val)),
                    total_cost=float(self._safe_decimal(costo_val))
                )
                
                current_category.items.append(item)
                logger.debug(f"Found item: {codice_val}")
        
        # Add the last group if exists
        if current_group:
            product_groups.append(current_group)
        
        return product_groups
    
    def calculate_totals(self, product_groups: List[ProductGroup], parameters: ProjectParameters) -> QuotationTotals:
        """Calculate total costs and fees"""
        total_pricelist = Decimal("0.0")
        total_cost = Decimal("0.0")
        total_offer = Decimal("0.0")
        offer_margin = Decimal("0.0")
        offer_margin_percentage = Decimal("0.0")
        
        # Sum up costs from all categories
        for group in product_groups:
            for category in group.categories:
                # Use offer_price if available, otherwise pricelist_subtotal
                category_pricelist  = Decimal(str(category.offer_price)) if category.offer_price is not None else Decimal("0.0")
                category_cost = Decimal(str(category.cost_subtotal)) if category.cost_subtotal is not None else Decimal("0.0")
                category_offer = Decimal(str(category.offer_price)) if category.offer_price is not None else Decimal("0.0")

                total_pricelist += category_pricelist
                total_cost += category_cost
                total_offer += category_offer
                offer_margin = total_offer - total_cost
                offer_margin_percentage = (offer_margin / total_cost) * 100
        
        return QuotationTotals(
            total_pricelist=float(self._round_decimal(total_pricelist)),
            total_cost=float(self._round_decimal(total_cost)),
            total_offer=float(self._round_decimal(total_offer)),
            offer_margin=float(self._round_decimal(offer_margin)),
            offer_margin_percentage=float(self._round_decimal(offer_margin_percentage))
        )
    
    def parse(self) -> IndustrialQuotation:
        """Main parsing method - returns IndustrialQuotation object directly"""
        logger.info(f"Starting direct parsing of PRE file: {self.file_path}")
        
        self.load_workbook()
        
        # Extract all sections as model objects
        project_info = self.extract_project_info()
        product_groups = self.extract_product_groups()
        totals = self.calculate_totals(product_groups, project_info.parameters)
        
        # Create final IndustrialQuotation object
        quotation = IndustrialQuotation(
            project=project_info,
            product_groups=product_groups,
            totals=totals,
            source_file=str(self.file_path),
            parser_type="direct_pre_file_parser"
        )
        
        logger.info(f"Direct parsing completed. Found {len(product_groups)} product groups")
        return quotation
    
    # Helper methods
    def _safe_decimal(self, value: Any, default: Decimal = None) -> Decimal:
        """Safely convert value to Decimal"""
        if value is None or value == "":
            return default if default is not None else Decimal("0.0")
        
        try:
            # Convert to string and clean up
            str_value = str(value).strip()
            
            # Handle empty strings after stripping
            if not str_value:
                return default if default is not None else Decimal("0.0")
            
            # Handle common non-numeric values
            if str_value.lower() in ['n/a', 'na', 'null', 'none', '-', '']:
                return default if default is not None else Decimal("0.0")
                
            # Remove currency symbols and common formatting
            str_value = str_value.replace('€', '').replace('$', '').replace(',', '').strip()
            
            # Handle percentage notation
            if str_value.endswith('%'):
                str_value = str_value[:-1]
                return Decimal(str_value) / Decimal("100")
            
            return Decimal(str_value)
            
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
            logger.debug(f"Could not convert '{value}' to Decimal: {e}")
            return default if default is not None else Decimal("0.0")
    
    def _safe_int(self, value: Any, default: int = 0) -> int:
        """Safely convert value to int"""
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def _round_decimal(self, value: Decimal) -> Decimal:
        """Round decimal to 2 places"""
        return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def _extract_after_colon(self, value: Any, default: str = "") -> str:
        """Extract text after colon, or return the value as string"""
        if value is None:
            return default
        
        str_value = str(value)
        if ':' in str_value:
            return str_value.split(':', 1)[1].strip()
        return str_value.strip()
    
    def _determine_category_type(self, category_id: str) -> CategoryType:
        """Determine category type based on category ID"""
        if category_id.startswith('E'):
            return CategoryType.INSTALLATION
        else:
            # All other categories (W, V, etc.) are considered equipment
            return CategoryType.EQUIPMENT

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def parse_pre_file_direct(file_path: str, output_path: Optional[str] = None) -> IndustrialQuotation:
    """
    Parse PRE Excel file directly to IndustrialQuotation object
    
    Args:
        file_path: Path to the Excel file
        output_path: Optional path to save JSON output
        
    Returns:
        IndustrialQuotation: Validated quotation model instance
    """
    parser = DirectPreFileParser(file_path)
    quotation = parser.parse()
    
    if output_path:
        quotation.save_json(output_path)
        logger.info(f"JSON output saved to {output_path}")
    
    return quotation

def validate_pre_file(file_path: str) -> Dict[str, Any]:
    """
    Validate PRE file and return validation results
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Dictionary with validation results
    """
    try:
        parser = DirectPreFileParser(file_path)
        quotation = parser.parse()
        
        # Run validation checks
        validation_results = quotation.validate_totals_consistency()
        summary_stats = quotation.get_summary_stats()
        
        return {
            "is_valid": True,
            "validation_results": validation_results,
            "summary_stats": summary_stats,
            "errors": []
        }
        
    except Exception as e:
        return {
            "is_valid": False,
            "validation_results": {},
            "summary_stats": {},
            "errors": [str(e)]
        }

if __name__ == "__main__":
    # Example usage
    input_file = "input/test_pre.xlsm"
    output_file = "output/quotation_direct.json"
    
    try:
        quotation = parse_pre_file_direct(input_file, output_file)
        stats = quotation.get_summary_stats()
        
        print("✅ Direct parsing completed successfully!")
        print(f"📋 Project ID: {stats['project_id']}")
        print(f"🏢 Customer: {quotation.project.customer}")
        print(f"📦 Product groups: {stats['total_groups']}")
        print(f"📂 Categories: {stats['total_categories']}")
        print(f"📄 Items: {stats['total_items']}")
        print(f"💵 Currency: {quotation.project.parameters.currency}")
        print(f"💰 Grand total pricelist: €{quotation.totals.total_pricelist:,.2f}")
        print(f"💰 Grand total cost: €{quotation.totals.total_cost:,.2f}")
        print(f"💰 Grand total offer: €{quotation.totals.total_offer:,.2f}")
        print(f"💰 Grand total offer margin: €{quotation.totals.offer_margin:,.2f}")
        print(f"💰 Grand total offer margin percentage: {quotation.totals.offer_margin_percentage:.2f}%")
        
        # Validate consistency
        validation = quotation.validate_totals_consistency()
        print(f"\n🔍 Validation results:")
        for check, is_valid in validation.items():
            status = "✅" if is_valid else "❌"
            print(f"   {status} {check}")
        
    except Exception as e:
        logger.error(f"Error parsing Excel file: {e}")
        raise 
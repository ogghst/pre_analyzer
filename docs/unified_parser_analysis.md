# Unified Parser Analysis: Data Extraction and Calculation Logic

## Overview

This document provides a comprehensive analysis of the unified parsing system for industrial equipment quotations. The system handles two main file types: **PRE files** and **Analisi Profittabilita files**, each with different Excel structures and data extraction requirements.

## System Architecture

### Core Components

1. **Unified Parser Interface** (`parsers/unified_parser.py`)
   - Automatically detects file type based on presence of `NEW_OFFER1` sheet
   - Routes to appropriate parser based on detection
   - Provides fallback parsing if primary parser fails

2. **Data Models** (`models/quotation_models.py`)
   - `IndustrialQuotation`: Root model encompassing all quotation data
   - `ProjectInfo`: Project identification and configuration
   - `ProductGroup`: High-level grouping of related categories
   - `QuotationCategory`: Category grouping related items
   - `QuotationItem`: Individual line items with detailed cost breakdown

3. **Direct Parsers**
   - `DirectPreFileParser`: Handles PRE file format
   - `DirectAnalisiProfittabilitaParser`: Handles Analisi Profittabilita format

## File Type Detection Logic

### Detection Process
The system determines file type by checking for the presence of the `NEW_OFFER1` sheet:

```python
# From unified_parser.py
def _detect_file_type(self) -> str:
    wb = load_workbook(self.file_path, read_only=True, data_only=True)
    sheet_names = [sheet_name.strip() for sheet_name in wb.sheetnames]
    if "NEW_OFFER1" in sheet_names:
        return 'analisi_profittabilita'
    else:
        return 'pre'
```

- **PRE Files**: Do not contain `NEW_OFFER1` sheet
- **Analisi Profittabilita Files**: Contain `NEW_OFFER1` sheet

## PRE File Data Extraction

### Excel Structure and Cell Mapping

#### Project Information Extraction
PRE files extract project metadata from specific cells:

| Data Field | Excel Location | Description |
|------------|----------------|-------------|
| Project ID | Row 1, Column A | Project identifier |
| Customer | Row 3, Column G | Customer name |
| Doc Percentage | Row 8, Column B | Documentation fee percentage |
| PM Percentage | Row 9, Column B | Project management percentage |
| Financial Costs | Row 10, Column B | Fixed financial costs |
| Currency | Row 11, Column B | Base currency |
| Exchange Rate | Row 12, Column B | Currency exchange rate |
| Waste Disposal | Row 13, Column B | Waste disposal costs |
| Warranty Percentage | Row 8, Column K | Warranty fee percentage |

#### Data Extraction Process
1. **Headers**: Start from row 17 (header row)
2. **Data**: Begin parsing from row 18
3. **Column Mapping**: Uses 1-based indexing for Excel columns

```python
# Column definitions from pre_file_parser_direct.py
class ExcelColumns:
    COD = 1                    # Category code
    CODICE = 3                 # Product code
    DENOMINAZIONE = 4          # Description
    QTA = 5                    # Quantity
    LIST_UNIT = 6             # Unit price from pricelist
    LISTINO = 7               # Total pricelist price
    COSTO_UNITARIO = 19       # Unit cost
    COSTO = 20                # Total cost
```

#### Hierarchical Data Structure
The parser identifies three levels of data:

1. **Product Groups**: Lines starting with `TXT-` prefix
2. **Categories**: 4-character codes in COD column
3. **Items**: All other lines with valid data

### MDC Sheet Integration
PRE files may contain MDC (latest available) sheets with additional financial data:

```python
# MDC columns from pre_file_parser_direct.py
class MDCColumns:
    DIRECT_COST_EUR = 4
    PRICELIST_EUR = 5
    OFFER_EUR = 6
    SALE_EUR = 7
    MARGIN_EUR = 16
    MARGIN_PERCENTAGE = 17
```

The MDC data is used to enhance category-level pricing and margin calculations.

## Analisi Profittabilita File Data Extraction

### Excel Structure and Cell Mapping

#### Project Information Extraction
Analisi Profittabilita files have simpler project metadata:

| Data Field | Excel Location | Description |
|------------|----------------|-------------|
| Project ID | Row 1, Column A | Project identifier |
| Listino | Row 2, Column A | Price list reference |

#### Comprehensive Column Mapping
Analisi Profittabilita files have 81 columns of detailed cost data:

```python
# Key columns from analisi_profittabilita_parser_direct.py
class ExcelColumns:
    COD = 1                    # Category code
    CODICE = 8                 # Product code
    DENOMINAZIONE = 10         # Description
    QTA = 11                   # Quantity
    LIST_UNIT = 13            # Unit price
    LISTINO_TOTALE = 14       # Total pricelist price
    COSTO_UNITARIO = 16       # Unit cost
    COSTO_TOTALE = 17         # Total cost
    
    # Engineering cost columns (22-40)
    MAT = 22                   # Material costs
    UTM_ROBOT = 23            # Robot engineering costs
    UTM_ROBOT_H = 24          # Robot engineering hours
    UTM_LGV = 25              # LGV engineering costs
    UTM_LGV_H = 26            # LGV engineering hours
    
    # Additional cost centers (41-81)
    PM_COST = 57              # Project management costs
    INSTALL = 67              # Installation costs
    AFTER_SALES = 77          # After-sales costs
```

#### Data Extraction Process
1. **Headers**: Row 3 contains column headers
2. **Data**: Parsing begins from row 4
3. **Priority Filter**: Only processes rows with priority values

### VA21 Sheet Integration
Analisi Profittabilita files may contain VA21 sheets with SAP-integrated offer prices:

```python
# VA21 columns from analisi_profittabilita_parser_direct.py
class VA21Columns:
    WBE = 4                    # Work Breakdown Element code
    OFFER_TOTAL = 25           # Final offer price
    COST_SUBTOTAL = 27         # Cost subtotal
    MARGIN_PERCENTAGE = 28     # Margin percentage
```

The VA21 data provides final offer prices that override calculated prices.

## Data Calculation Logic

### Category-Level Calculations

#### Pricelist Subtotal
```python
# Calculated as sum of all item pricelist totals
pricelist_subtotal = sum(item.pricelist_total_price for item in category.items)
```

#### Cost Subtotal
```python
# Calculated as sum of all item total costs
cost_subtotal = sum(item.total_cost for item in category.items)
```

#### Margin Calculations
```python
# Offer-based margin (when offer_price available)
margin_amount = offer_price - cost_subtotal
margin_percentage = (margin_amount / offer_price) * 100

# Pricelist-based margin (fallback)
margin_amount = pricelist_subtotal - cost_subtotal
margin_percentage = (margin_amount / pricelist_subtotal) * 100
```

### Total Calculations

#### Project-Level Totals
```python
# From calculate_totals method
total_pricelist = sum(category.pricelist_subtotal for all categories)
total_cost = sum(category.cost_subtotal for all categories)
total_offer = sum(category.offer_price for all categories where available)
offer_margin = total_offer - total_cost
offer_margin_percentage = (offer_margin / total_offer) * 100
```

## Excel Cell References by File Type

### PRE Files - Key Cell References

#### Project Configuration Cells
- **A1**: Project ID (format: "Project: [ID]")
- **G3**: Customer name (format: "Customer: [Name]")
- **B8**: Documentation percentage (decimal format)
- **B9**: Project management percentage (decimal format)
- **K8**: Warranty percentage (decimal format)

#### Data Structure Cells (Starting Row 18)
- **Column A**: Category codes (4 characters)
- **Column C**: Product codes (TXT- prefix for groups)
- **Column D**: Product descriptions
- **Column E**: Quantities
- **Column F**: Unit prices from pricelist
- **Column G**: Total pricelist prices
- **Column S**: Unit costs
- **Column T**: Total costs

### Analisi Profittabilita Files - Key Cell References

#### Project Configuration Cells
- **A1**: Project ID
- **A2**: Listino reference

#### Data Structure Cells (Starting Row 4)
- **Column A**: Category codes
- **Column H**: Product codes
- **Column J**: Product descriptions
- **Column K**: Quantities
- **Column M**: Unit prices
- **Column N**: Total pricelist prices
- **Column P**: Unit costs
- **Column Q**: Total costs

#### Cost Center Cells (Columns 22-81)
- **Column V (22)**: Material costs
- **Column W (23)**: Robot engineering costs
- **Column X (24)**: Robot engineering hours
- **Column Y (25)**: LGV engineering costs
- **Column Z (26)**: LGV engineering hours
- **... (continuing through Column CY for all 81 columns)**

## Data Validation and Error Handling

### Safe Data Extraction
The parsers implement robust error handling:

```python
def _safe_decimal(self, value: Any, default: Decimal = None) -> Decimal:
    """Safely convert value to Decimal with error handling"""
    if value is None or value == "":
        return default if default is not None else Decimal("0.0")
    
    try:
        str_value = str(value).strip()
        # Handle currency symbols and formatting
        str_value = str_value.replace('€', '').replace('$', '').replace(',', '').strip()
        return Decimal(str_value)
    except (ValueError, TypeError, decimal.InvalidOperation):
        return default if default is not None else Decimal("0.0")
```

### Data Consistency Validation
The models include validation to ensure data consistency:

```python
@field_validator('pricelist_total_price')
@classmethod
def validate_pricelist_total(cls, v, info):
    """Validate that pricelist total equals quantity × unit price"""
    if hasattr(info, 'data') and info.data:
        quantity = info.data.get('quantity', 0.0)
        unit_price = info.data.get('pricelist_unit_price', 0.0)
        expected = quantity * unit_price
        if v == 0.0 and expected > 0:
            return expected
    return v
```

## Cost Center Analysis

### UTM (Ufficio Tecnico Meccanico) Fields
- **UTM Robot**: Mechanical engineering costs for robot systems
- **UTM LGV**: Engineering costs for Laser Guided Vehicles
- **UTM Intra**: Intralogistics engineering costs
- **UTM Layout**: Layout design engineering costs

### Engineering Cost Centers
- **UTE**: Electrical engineering costs
- **BA**: Business Analysis costs
- **SW-PC**: PC software development costs
- **SW-PLC**: PLC software development costs
- **SW-LGV**: LGV software development costs

### Manufacturing Cost Centers
- **MTG-MEC**: Mechanical assembly costs
- **CAB-ELE**: Electrical cabinet assembly costs
- **COLL**: Testing and commissioning costs

### Field Operations
- **PM**: Project management costs
- **INSTALL**: Installation costs
- **AV**: Commissioning (Avviamento) costs
- **AFTER_SALES**: After-sales service costs

## Summary

The unified parser system provides a comprehensive solution for extracting and calculating data from industrial equipment quotations. It handles two distinct Excel formats with different structures, automatically detects file types, and provides consistent data models with robust error handling and validation.

The system's strength lies in its ability to:
1. Automatically detect and handle different file formats
2. Extract data from specific Excel cells with proper error handling
3. Calculate totals and margins at multiple levels (item, category, project)
4. Integrate additional data from supplementary sheets (MDC, VA21)
5. Provide detailed cost center analysis for engineering and manufacturing operations

This unified approach ensures consistent data processing regardless of the source file format, while maintaining the detailed cost breakdown necessary for industrial equipment quotation analysis.
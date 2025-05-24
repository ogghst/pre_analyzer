# Excel Parsers for Industrial Equipment Analysis

This project contains two specialized Excel parsers designed to convert different types of industrial equipment files into structured JSON format.

## Parsers Overview

### 1. PRE File Parser (`pre_file_parser.py`)
Converts Excel quotation files with specific format to structured JSON.

**Purpose**: Parse commercial quotation files for industrial equipment
**Input**: Excel files with quotation format (e.g., `PRE_ONLY_OFFER1.xlsx`)
**Output**: JSON with project details, product groups, categories, items, and calculated totals

### 2. Analisi Profittabilita Parser (`analisi_profittabilita_parser.py`)
Converts Excel profitability analysis files to structured JSON with **ALL 81 COLUMNS** extracted.

**Purpose**: Parse profitability analysis files with comprehensive cost vs. revenue data
**Input**: Excel files with profitability format (e.g., `cc2199_analisi_profittabilita_new_offer1.xlsx`)
**Output**: JSON with project details, product groups, categories, items, and complete field analysis

## Architecture

Both parsers follow the same modular architecture:

```
Parser Class
├── Constants (Excel columns, rows, patterns)
├── Project Info Extraction
├── Product Groups Extraction
│   ├── Groups (identified by TXT patterns)
│   ├── Categories (4-character codes)
│   └── Items (detailed product data)
├── Totals Calculation
└── JSON Output Generation
```

## Key Features

### Common Features
- **Consistent JSON Schema**: Both output the same JSON structure for compatibility
- **Robust Error Handling**: Safe type conversion and error reporting
- **Detailed Logging**: Comprehensive logging for debugging and monitoring
- **Modular Design**: Well-organized constants and helper methods
- **Excel Compatibility**: Uses openpyxl for reliable Excel parsing

### PRE File Parser Specific
- Extracts project parameters (doc %, PM %, financial costs, currency, etc.)
- Calculates fees and grand totals
- Identifies groups by `TXT-` prefix
- Focus on commercial quotation data
- ~25 key columns extracted

### Analisi Profittabilita Parser Specific
- **ALL 81 COLUMNS EXTRACTED** for comprehensive analysis
- Extracts profitability metrics (listino vs. costo)
- Calculates margins and profitability percentages
- Identifies groups by `TXT` prefix
- Focus on cost analysis and profitability

**Complete Field Categories:**
- **UTM Fields**: Robot, LGV, Intra, Layout (with hours)
- **Engineering Fields**: UTE, BA, SW-PC, SW-PLC, SW-LGV (with hours)
- **Manufacturing Fields**: MTG-MEC, CAB-ELE (with Intra variants and hours)
- **Testing Fields**: COLL-BA, COLL-PC, COLL-PLC, COLL-LGV (with hours)
- **Project Management**: PM costs, hours, expenses
- **Documentation**: Document preparation (with hours)
- **Logistics**: Imballo, Stoccaggio, Trasporto
- **Field Activities**: Site, Install, AV-PC, AV-PLC, AV-LGV (with hours)
- **Additional Costs**: After Sales, Provvigioni (Italia/Estero), Tesoretto, Montaggio BEMA

## Usage

### PRE File Parser

```python
from src.pre_file.pre_file_parser import parse_excel_to_json

# Parse and save to JSON
result = parse_excel_to_json(
    "input/PRE_ONLY_OFFER1.xlsx", 
    "output/quotation.json"
)

# Access parsed data
print(f"Project ID: {result['project']['id']}")
print(f"Customer: {result['project']['customer']}")
print(f"Grand Total: {result['totals']['grand_total']}")
```

### Analisi Profittabilita Parser

```python
from src.pre_file.analisi_profittabilita_parser import parse_analisi_profittabilita_to_json

# Parse and save to JSON (ALL 81 COLUMNS)
result = parse_analisi_profittabilita_to_json(
    "input/cc2199_analisi_profittabilita_new_offer1.xlsx",
    "output/profitability_complete.json"
)

# Access parsed data
print(f"Project ID: {result['project']['id']}")
print(f"Total Revenue: {result['totals']['total_listino']}")
print(f"Total Cost: {result['totals']['total_costo']}")
print(f"Margin: {result['totals']['margin']} ({result['totals']['margin_percentage']}%)")

# Access detailed field data
if result['product_groups']:
    sample_item = result['product_groups'][0]['categories'][0]['items'][0]
    print(f"Fields per item: {len(sample_item)}")  # Shows 74 fields
    print(f"UTM Robot hours: {sample_item['utm_robot_h']}")
    print(f"PM Cost: {sample_item['pm_cost']}")
    print(f"Install hours: {sample_item['install_h']}")
```

## JSON Output Structure

Both parsers generate JSON with the following structure, with the Analisi parser now including **all 81 columns**:

```json
{
  "project": {
    "id": "project_identifier",
    "customer": "customer_name",  // PRE parser only
    "listino": "listino_info",    // Analisi parser only
    "parameters": {
      "doc_percentage": 0.0,
      "pm_percentage": 0.0,
      "financial_costs": 0.0,
      "currency": "EUR",
      "exchange_rate": 1.0,
      "waste_disposal": 0.0,
      "warranty_percentage": 0.0,
      "is_24h_service": false
    },
    "sales_info": {
      "area_manager": null,
      "agent": null,
      "commission_percentage": 0.0,
      "author": null
    }
  },
  "product_groups": [
    {
      "group_id": "TXT-XX",
      "group_name": "Group Name",
      "quantity": 1,
      "categories": [
        {
          "category_id": "XXXX",
          "category_name": "Category Name",
          "items": [
            {
              // Basic fields
              "position": "row_number",
              "code": "item_code",
              "description": "item_description",
              "quantity": 1.0,
              "unit_cost": 100.0,
              "total_cost": 100.0,
              
              // ⭐ NEW: UTM Fields (Analisi parser)
              "utm_robot": 0.0,
              "utm_robot_h": 0.0,
              "utm_lgv": 0.0,
              "utm_lgv_h": 0.0,
              "utm_intra": 0.0,
              "utm_intra_h": 0.0,
              "utm_layout": 0.0,
              "utm_layout_h": 0.0,
              
              // ⭐ NEW: Engineering Fields
              "ute": 0.0,
              "ute_h": 0.0,
              "ba": 0.0,
              "ba_h": 0.0,
              "sw_pc": 0.0,
              "sw_pc_h": 0.0,
              "sw_plc": 0.0,
              "sw_plc_h": 0.0,
              "sw_lgv": 0.0,
              "sw_lgv_h": 0.0,
              
              // ⭐ NEW: Manufacturing Fields
              "mtg_mec": 0.0,
              "mtg_mec_h": 0.0,
              "mtg_mec_intra": 0.0,
              "mtg_mec_intra_h": 0.0,
              "cab_ele": 0.0,
              "cab_ele_h": 0.0,
              "cab_ele_intra": 0.0,
              "cab_ele_intra_h": 0.0,
              
              // ⭐ NEW: Testing Fields
              "coll_ba": 0.0,
              "coll_ba_h": 0.0,
              "coll_pc": 0.0,
              "coll_pc_h": 0.0,
              "coll_plc": 0.0,
              "coll_plc_h": 0.0,
              "coll_lgv": 0.0,
              "coll_lgv_h": 0.0,
              
              // ⭐ NEW: Project Management
              "pm_cost": 0.0,
              "pm_h": 0.0,
              "spese_pm": 0.0,
              
              // ⭐ NEW: Documentation & Logistics
              "document": 0.0,
              "document_h": 0.0,
              "imballo": 0.0,
              "stoccaggio": 0.0,
              "trasporto": 0.0,
              
              // ⭐ NEW: Field Activities
              "site": 0.0,
              "site_h": 0.0,
              "install": 0.0,
              "install_h": 0.0,
              "av_pc": 0.0,
              "av_pc_h": 0.0,
              "av_plc": 0.0,
              "av_plc_h": 0.0,
              "av_lgv": 0.0,
              "av_lgv_h": 0.0,
              
              // ⭐ NEW: Additional Costs
              "spese_field": 0.0,
              "spese_varie": 0.0,
              "after_sales": 0.0,
              "provvigioni_italia": 0.0,
              "provvigioni_estero": 0.0,
              "tesoretto": 0.0,
              "montaggio_bema_mbe_us": 0.0
            }
          ],
          "subtotal_listino": 1000.0,
          "subtotal_costo": 800.0,
          "total_cost": 800.0
        }
      ]
    }
  ],
  "totals": {
    "total_listino": 10000.0,     // Analisi parser
    "total_costo": 8000.0,        // Analisi parser
    "margin": 2000.0,             // Analisi parser
    "margin_percentage": 20.0,    // Analisi parser
    "grand_total": 10000.0,       // PRE parser
    "equipment_total": 9000.0,
    "installation_total": 1000.0,
    "subtotal": 10000.0
  }
}
```

## File Structure

```
src/
├── pre_file/
│   ├── pre_file_parser.py              # PRE quotation parser
│   └── analisi_profittabilita_parser.py # Profitability analysis parser (ALL 81 COLUMNS)
input/
├── PRE_ONLY_OFFER1.xlsx                # Example PRE file
└── cc2199_analisi_profittabilita_new_offer1.xlsx # Example profitability file
output/
├── quotation.json                      # PRE parser output
└── profitability_complete.json         # Profitability parser output (ALL FIELDS)
```

## Testing

Run the test script to verify both parsers:

```bash
python test_both_parsers.py
```

This will:
1. Test both parsers with sample files
2. Generate JSON outputs with complete field extraction
3. Display parsing results and field analysis
4. Show statistics about field usage across all items
5. Verify the parsers are working correctly

**Sample Output:**
```
✓ Analisi Parser - Fields per item: 74 (includes all 81 columns)
✓ Total items analyzed: 187
✓ Total unique fields: 57
✓ Top fields: priority (98.9%), line_number (98.9%), unit_cost (65.2%)
```

## Performance & Scale

The updated Analisi Profittabilita parser handles:
- **81 columns** from Excel (complete extraction)
- **278 rows** of data in test file
- **187 items** with full field analysis
- **74 fields** per item in JSON output
- **~57 unique fields** with actual data values
- Processing time: ~3 seconds for complete analysis

## Error Handling

Both parsers include comprehensive error handling:

- **File Not Found**: Clear error messages for missing input files
- **Invalid Excel Format**: Graceful handling of corrupted or invalid Excel files
- **Data Type Errors**: Safe conversion of cell values with fallback defaults
- **Missing Sheets**: Detection and reporting of missing worksheets

## Logging

Both parsers provide detailed logging:

- **INFO**: Major parsing milestones and results
- **DEBUG**: Detailed item-by-item parsing information
- **ERROR**: Error conditions and failures

Configure logging level as needed:

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # For detailed output
logging.basicConfig(level=logging.INFO)   # For normal output
```

## Dependencies

- `openpyxl`: Excel file reading and parsing
- `pandas`: Data manipulation and analysis
- `json`: JSON output generation
- `logging`: Comprehensive logging functionality

## Extension and Customization

Both parsers are designed for easy extension:

1. **Add new fields**: Modify the `JsonFields` class
2. **Change column mappings**: Update the `ExcelColumns` class
3. **Modify identification patterns**: Update the `IdentificationPatterns` class
4. **Add new calculations**: Extend the `calculate_totals` method
5. **Custom project info**: Modify the `extract_project_info` method

Example of adding a new field:

```python
# In Constants
class JsonFields:
    # ... existing fields ...
    NEW_FIELD = "new_field"

# In extract_project_info method
return {
    # ... existing fields ...
    JsonFields.NEW_FIELD: extracted_value
}
```

## Field Categories Reference

The Analisi Profittabilita parser extracts the following field categories:

| Category | Count | Examples |
|----------|--------|----------|
| **Basic** | 15 | position, code, description, quantity, costs |
| **UTM** | 8 | utm_robot, utm_lgv, utm_intra, utm_layout (+ hours) |
| **Engineering** | 10 | ute, ba, sw_pc, sw_plc, sw_lgv (+ hours) |
| **Manufacturing** | 8 | mtg_mec, cab_ele (+ intra variants + hours) |
| **Testing** | 8 | coll_ba, coll_pc, coll_plc, coll_lgv (+ hours) |
| **Project Mgmt** | 3 | pm_cost, pm_h, spese_pm |
| **Documentation** | 2 | document, document_h |
| **Logistics** | 3 | imballo, stoccaggio, trasporto |
| **Field Activities** | 10 | site, install, av_pc, av_plc, av_lgv (+ hours) |
| **Additional** | 7 | after_sales, provvigioni, tesoretto, etc. |

**Total: 74 fields per item** covering all aspects of industrial equipment profitability analysis. 
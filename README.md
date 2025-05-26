# Excel to JSON Parser for Industrial Equipment Quotations

This project provides a comprehensive Python solution for parsing Excel quotation files (PRE_ONLY_OFFER format) and converting them to structured JSON data according to a defined schema.

## Overview

The parser extracts data from complex Excel quotation files and converts them into a structured JSON format that includes:
- Project information and parameters
- Sales information 
- Product groups with hierarchical categories and items
- Calculated totals and fees

## Features

- ✅ **Complete Excel parsing** - Handles complex Excel structures with formulas
- ✅ **Schema validation** - Validates output against JSON schema
- ✅ **Hierarchical data** - Preserves group > category > item relationships
- ✅ **Calculation support** - Calculates totals, fees, and installation costs
- ✅ **Error handling** - Robust error handling and logging
- ✅ **Type safety** - Type hints and safe data conversion

## Project Structure

```
pre_analyzer/
├── input/                          # Input Excel files
│   └── PRE_ONLY_OFFER1.xlsx       # Sample quotation file
├── output/                         # Generated JSON outputs
│   └── quotation.json             # Parsed quotation data
├── src/
│   ├── utils/                      # Utility modules
│   └── widgets/                    # UI components
├── excel_to_json_parser.py         # Main parser implementation
├── validate_json_schema.py         # JSON schema validator
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd pre_analyzer
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```python
from excel_to_json_parser import parse_excel_to_json

# Parse Excel file to JSON
result = parse_excel_to_json("input/PRE_ONLY_OFFER1.xlsx", "output/quotation.json")

# Access parsed data
print(f"Project ID: {result['project']['id']}")
print(f"Customer: {result['project']['customer']}")
print(f"Grand Total: {result['totals']['grand_total']:,.2f}")
```

### Command Line Usage

```bash
# Parse Excel file
python excel_to_json_parser.py

# Validate generated JSON
python validate_json_schema.py
```

### Advanced Usage

```python
from excel_to_json_parser import ExcelQuotationParser

# Create parser instance
parser = ExcelQuotationParser("input/PRE_ONLY_OFFER1.xlsx")

# Parse with custom logic
result = parser.parse()

# Access specific sections
project_info = result['project']
product_groups = result['product_groups']
totals = result['totals']

# Process product groups
for group in product_groups:
    print(f"Group: {group['group_id']} - {group['group_name']}")
    for category in group['categories']:
        print(f"  Category: {category['category_id']} - {category['category_name']}")
        print(f"  Items: {len(category['items'])}")
        print(f"  Total: {category['total']:,.2f}")
```

## Data Structure

The parser extracts data into the following hierarchical structure:

### Project Information
- **Project ID**: Unique identifier (e.g., "PRE_LSU2300105_NEW_04_QS")
- **Customer**: Customer name
- **Parameters**: Pricing parameters (DOC %, PM %, exchange rate, etc.)
- **Sales Info**: Sales team information

### Product Groups
- **Groups**: High-level product groups (TXT-XX codes)
- **Categories**: Product categories within groups (4-letter codes like SWZZ, FAZZ)
- **Items**: Individual products with codes, descriptions, quantities, and prices

### Totals
- **Equipment Total**: Sum of all equipment costs
- **Installation Total**: Installation costs (typically 15% of equipment)
- **Fees**: Documentation, project management, and warranty fees
- **Grand Total**: Final total including all costs and fees

## JSON Schema

The output JSON conforms to a comprehensive schema that includes:

- **Type validation**: Ensures correct data types
- **Range validation**: Validates numeric ranges and constraints
- **Required fields**: Enforces mandatory fields
- **Hierarchical structure**: Maintains data relationships

### Key Schema Features

- Allows negative prices (for discounts/adjustments)
- Supports decimal quantities and prices
- Validates percentage ranges (0-1)
- Ensures non-negative totals
- Maintains referential integrity

## Excel File Format

The parser expects Excel files with the following structure:

### Header Section (Rows 1-16)
- **Row 1**: Project ID and Customer name
- **Rows 7-13**: Project parameters (DOC%, PM%, currency, etc.)
- **Rows 12-15**: Sales information

### Data Section (Starting Row 17)
- **Row 17**: Column headers
- **Row 18+**: Product data in hierarchical format
  - Groups: TXT-XX codes
  - Categories: 4-letter codes (SWZZ, FAZZ, etc.)
  - Items: Product codes with descriptions and pricing

### Supported Columns
- **COD**: Category codes
- **CODICE**: Product codes
- **DENOMINAZIONE**: Descriptions
- **QTA'**: Quantities
- **LIST.UNIT.**: Unit prices
- **Additional columns**: Various totals and calculations

## Error Handling

The parser includes comprehensive error handling:

- **File validation**: Checks file existence and format
- **Data validation**: Validates cell values and types
- **Schema validation**: Ensures output conforms to JSON schema
- **Logging**: Detailed logging for debugging
- **Graceful degradation**: Continues parsing when possible

## Validation

The `validate_json_schema.py` script provides:

- **Schema compliance**: Validates against JSON Schema Draft 07
- **Data integrity**: Checks relationships and constraints
- **Summary reporting**: Provides parsing statistics
- **Error details**: Detailed validation error messages

### Running Validation

```bash
python validate_json_schema.py
```

Output example:
```
🔍 VALIDATING QUOTATION JSON AGAINST SCHEMA
============================================================
✅ JSON file output/quotation.json is valid according to the schema

📊 VALIDATION SUMMARY:
Project ID: PRE_LSU2300105_NEW_04_QS
Customer: DrinkPAK II, LLC
Currency: Euro
Exchange Rate: 1.09
Number of Product Groups: 16
Total Items: 376
Equipment Total: 8,492,539.36
Installation Total: 1,273,880.90
Grand Total: 10,029,429.96

✅ Validation completed successfully!
```

## Dependencies

Key dependencies include:
- **pandas**: Excel file reading and data manipulation
- **openpyxl**: Excel file processing with formula support
- **jsonschema**: JSON schema validation
- **typing**: Type hints support

See `requirements.txt` for complete dependency list.

## Customization

### Adding New Excel Formats

To support additional Excel formats:

1. **Extend parser class**:
   ```python
   class CustomExcelParser(ExcelQuotationParser):
       def extract_project_info(self):
           # Custom extraction logic
           pass
   ```

2. **Update cell mappings**: Modify cell references for different layouts
3. **Add validation rules**: Update schema for new fields

### Custom Calculations

To add custom calculations:

1. **Override calculation methods**:
   ```python
   def calculate_totals(self, product_groups, parameters):
       # Custom calculation logic
       return custom_totals
   ```

2. **Update schema**: Add new fields to JSON schema
3. **Update validation**: Include new fields in validation

## Troubleshooting

### Common Issues

1. **File not found**: Ensure Excel file exists in `input/` directory
2. **Schema validation fails**: Check for negative prices or missing fields
3. **Parsing errors**: Enable debug logging for detailed error messages

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Excel File Issues

- Ensure Excel file is not corrupted
- Check for merged cells that might affect parsing
- Verify column headers match expected format

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Add tests for new functionality
4. Submit pull request with detailed description

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support or questions:
- Create an issue in the repository
- Contact the development team
- Review the troubleshooting section above

---

**Last Updated**: May 2025  
**Version**: 1.0.0 
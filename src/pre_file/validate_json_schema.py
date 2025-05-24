"""
JSON Schema Validator for Industrial Equipment Quotations
Validates the generated JSON against the specified schema
"""

import json
import jsonschema
from jsonschema import validate, ValidationError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the JSON schema as specified by the user
QUOTATION_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Industrial Equipment Quotation",
    "type": "object",
    "properties": {
        "project": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Project identifier (e.g., PRE_LSU2300105_NEW_04_QS)"
                },
                "customer": {
                    "type": "string",
                    "description": "Customer name"
                },
                "parameters": {
                    "type": "object",
                    "properties": {
                        "doc_percentage": {
                            "type": "number",
                            "description": "Document percentage fee",
                            "minimum": 0,
                            "maximum": 1
                        },
                        "pm_percentage": {
                            "type": "number",
                            "description": "Project management percentage",
                            "minimum": 0,
                            "maximum": 1
                        },
                        "financial_costs": {
                            "type": "number",
                            "description": "Financial costs percentage",
                            "minimum": 0,
                            "maximum": 1
                        },
                        "currency": {
                            "type": "string",
                            "description": "Base currency for pricing"
                        },
                        "exchange_rate": {
                            "type": "number",
                            "description": "Exchange rate (1 EUR = X)",
                            "minimum": 0
                        },
                        "waste_disposal": {
                            "type": "number",
                            "description": "Waste disposal percentage",
                            "minimum": 0,
                            "maximum": 1
                        },
                        "warranty_percentage": {
                            "type": "number",
                            "description": "Warranty percentage",
                            "minimum": 0,
                            "maximum": 1
                        },
                        "is_24h_service": {
                            "type": "boolean",
                            "description": "24-hour service availability"
                        }
                    },
                    "required": ["doc_percentage", "pm_percentage", "currency", "exchange_rate", "warranty_percentage"]
                },
                "sales_info": {
                    "type": "object",
                    "properties": {
                        "area_manager": {
                            "type": "string",
                            "description": "Area manager name"
                        },
                        "agent": {
                            "type": "string",
                            "description": "Sales agent name"
                        },
                        "commission_percentage": {
                            "type": "number",
                            "description": "Commission percentage",
                            "minimum": 0,
                            "maximum": 1
                        },
                        "author": {
                            "type": "string",
                            "description": "Quote author/compiler"
                        }
                    }
                }
            },
            "required": ["id", "customer", "parameters"]
        },
        "product_groups": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "group_id": {
                        "type": "string",
                        "description": "Group identifier (e.g., TXT-71)"
                    },
                    "group_name": {
                        "type": "string",
                        "description": "Group description"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Group quantity",
                        "minimum": 1
                    },
                    "discount_factor": {
                        "type": "number",
                        "description": "Discount factor applied to group",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 1
                    },
                    "installation": {
                        "type": "object",
                        "properties": {
                            "percentage": {
                                "type": "number",
                                "description": "Installation cost as percentage of equipment cost",
                                "minimum": 0,
                                "maximum": 1
                            },
                            "cost": {
                                "type": "number",
                                "description": "Calculated installation cost",
                                "minimum": 0
                            }
                        }
                    },
                    "categories": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "category_id": {
                                    "type": "string",
                                    "description": "Category identifier (e.g., SWZZ, FAZZ)"
                                },
                                "category_name": {
                                    "type": "string",
                                    "description": "Category description"
                                },
                                "items": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "position": {
                                                "type": "string",
                                                "description": "Item position number"
                                            },
                                            "code": {
                                                "type": "string",
                                                "description": "Product code"
                                            },
                                            "description": {
                                                "type": "string",
                                                "description": "Product description"
                                            },
                                            "quantity": {
                                                "type": "number",
                                                "description": "Item quantity",
                                                "minimum": 0
                                            },
                                            "unit_price": {
                                                "type": "number",
                                                "description": "Unit list price (can be negative for discounts)"
                                            },
                                            "line_total": {
                                                "type": "number",
                                                "description": "Line total (quantity × unit_price, can be negative for discounts)"
                                            }
                                        },
                                        "required": ["code", "description"]
                                    }
                                },
                                "subtotal_listino": {
                                    "type": "number",
                                    "description": "Category subtotal at list price",
                                    "minimum": 0
                                },
                                "subtotal_codice": {
                                    "type": "number",
                                    "description": "Category subtotal after discounts",
                                    "minimum": 0
                                },
                                "total": {
                                    "type": "number",
                                    "description": "Category total with ceiling rounding",
                                    "minimum": 0
                                }
                            },
                            "required": ["category_id", "category_name", "items"]
                        }
                    }
                },
                "required": ["group_id", "group_name", "categories"]
            }
        },
        "totals": {
            "type": "object",
            "properties": {
                "equipment_total": {
                    "type": "number",
                    "description": "Total equipment cost",
                    "minimum": 0
                },
                "installation_total": {
                    "type": "number",
                    "description": "Total installation cost",
                    "minimum": 0
                },
                "subtotal": {
                    "type": "number",
                    "description": "Subtotal before fees",
                    "minimum": 0
                },
                "doc_fee": {
                    "type": "number",
                    "description": "Documentation fee",
                    "minimum": 0
                },
                "pm_fee": {
                    "type": "number",
                    "description": "Project management fee",
                    "minimum": 0
                },
                "warranty_fee": {
                    "type": "number",
                    "description": "Warranty fee",
                    "minimum": 0
                },
                "grand_total": {
                    "type": "number",
                    "description": "Final total including all fees",
                    "minimum": 0
                }
            },
            "required": ["equipment_total", "installation_total", "grand_total"]
        }
    },
    "required": ["project", "product_groups", "totals"]
}


def validate_quotation_json(json_file_path: str) -> bool:
    """
    Validate a quotation JSON file against the schema
    
    Args:
        json_file_path: Path to the JSON file to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Load the JSON data
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate against schema
        validate(instance=data, schema=QUOTATION_SCHEMA)
        
        logger.info(f"✅ JSON file {json_file_path} is valid according to the schema")
        
        # Print some summary statistics
        print("\n📊 VALIDATION SUMMARY:")
        print(f"Project ID: {data['project']['id']}")
        print(f"Customer: {data['project']['customer']}")
        print(f"Currency: {data['project']['parameters']['currency']}")
        print(f"Exchange Rate: {data['project']['parameters']['exchange_rate']}")
        print(f"Number of Product Groups: {len(data['product_groups'])}")
        
        total_items = sum(len(cat['items']) for group in data['product_groups'] for cat in group['categories'])
        print(f"Total Items: {total_items}")
        
        print(f"Equipment Total: {data['totals']['equipment_total']:,.2f}")
        print(f"Installation Total: {data['totals']['installation_total']:,.2f}")
        print(f"Grand Total: {data['totals']['grand_total']:,.2f}")
        
        return True
        
    except ValidationError as e:
        logger.error(f"❌ JSON validation failed: {e.message}")
        logger.error(f"Failed at path: {' -> '.join(str(x) for x in e.absolute_path)}")
        return False
        
    except FileNotFoundError:
        logger.error(f"❌ File not found: {json_file_path}")
        return False
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON format: {e}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    # Test with the generated JSON file
    json_file = "output/quotation.json"
    
    print("🔍 VALIDATING QUOTATION JSON AGAINST SCHEMA")
    print("=" * 60)
    
    is_valid = validate_quotation_json(json_file)
    
    if is_valid:
        print("\n✅ Validation completed successfully!")
    else:
        print("\n❌ Validation failed!")
        exit(1) 
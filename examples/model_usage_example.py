"""
Comprehensive Example: Using the Unified Quotation Model System

This example demonstrates:
1. Parsing different file types with automatic detection
2. Data validation and consistency checking
3. JSON serialization/deserialization
4. Pandas DataFrame conversion for analysis
5. LLM-friendly data access
6. Cross-parser compatibility
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from models import IndustrialQuotation, CurrencyType, CategoryType
from parsers.unified_parser import parse_quotation_file, analyze_quotation_file

# Configure logging to file with detailed formatting
log_file = "output/model_usage_example.log"

def setup_logging():
    """Setup logging configuration"""
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    
    # Clear any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup file handler
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Setup console handler for errors only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler, console_handler],
        force=True
    )
    
    return logging.getLogger(__name__)

# Setup logging and get logger
logger = setup_logging()

def demonstrate_unified_parsing():
    """Demonstrate parsing different file types with the unified interface"""
    logger.info("=" * 80)
    logger.info("UNIFIED PARSING DEMONSTRATION")
    logger.info("=" * 80)
    
    # Example file paths (update these to your actual files)
    example_files = [
        "input/test_pre.xlsm",  # PRE file
        "input/test_ap.xlsm",  # AP file
    ]
    
    for file_path in example_files:
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            continue
            
        logger.info(f"Analyzing file: {Path(file_path).name}")
        
        # Analyze file and get recommendations
        analysis = analyze_quotation_file(file_path)
        logger.info(f"Parser recommendation: {analysis['parser_recommendations']['recommended_parser']}")
        logger.info(f"Confidence scores:")
        logger.info(f"   - PRE: {analysis['parser_recommendations']['pre_confidence']}%")
        logger.info(f"   - Analisi Profittabilita: {analysis['parser_recommendations']['analisi_profittabilita_confidence']}%")
        
        try:
            # Parse to unified model
            logger.info("Parsing with unified interface...")
            quotation = parse_quotation_file(file_path)
            
            # Show summary stats
            stats = quotation.get_summary_stats()
            logger.info("Successfully parsed!")
            logger.info(f"   - Project ID: {stats['project_id']}")
            logger.info(f"   - Total groups: {stats['total_groups']}")
            logger.info(f"   - Total categories: {stats['total_categories']}")
            logger.info(f"   - Total items: {stats['total_items']}")
            logger.info(f"   - Total value: €{stats['total_listino']:,.2f}")
            logger.info(f"   - Has offer prices: {stats['has_offer_prices']}")
            
        except Exception as e:
            logger.error(f"Failed to parse: {e}", exc_info=True)

def demonstrate_model_validation():
    """Demonstrate data validation and consistency checking"""
    logger.info("=" * 80)
    logger.info("MODEL VALIDATION DEMONSTRATION")
    logger.info("=" * 80)
    
    # Create a sample quotation programmatically
    from models import ProjectInfo, ProjectParameters, SalesInfo, ProductGroup, QuotationCategory, QuotationItem, QuotationTotals
    
    # Create project info
    project = ProjectInfo(
        id="TEST-2024-001",
        customer="Test Customer Inc.",
        parameters=ProjectParameters(
            doc_percentage=0.02,
            pm_percentage=0.05,
            currency=CurrencyType.EUR,
            warranty_percentage=0.01
        ),
        sales_info=SalesInfo(
            area_manager="John Doe",
            commission_percentage=0.03
        )
    )
    
    # Create sample items
    item1 = QuotationItem(
        position="1",
        code="ROBOT-001", 
        description="Industrial Robot Unit",
        quantity=2.0,
        pricelist_unit_price=50000.0,
        pricelist_total_price=100000.0,  # Will validate against quantity × unit_price
        unit_cost=35000.0,
        total_cost=70000.0,
        utm_robot=5000.0,  # Engineering costs
        sw_pc=2000.0       # Software costs
    )
    
    # Create category
    category = QuotationCategory(
        category_id="ROBO",
        category_name="Robotics Systems",
        items=[item1],
        offer_price=95000.0  # Special offer price
    )
    
    # Create product group
    group = ProductGroup(
        group_id="TXT-ROBOTICS",
        group_name="Complete Robotics Solution",
        categories=[category]
    )
    
    # Create totals
    totals = QuotationTotals(
        total_listino=100000.0,
        total_cost=70000.0,
        total_offer=95000.0,
        margin=30000.0,
        margin_percentage=30.0,
        offer_margin=25000.0,
        offer_margin_percentage=26.32
    )
    
    # Create complete quotation
    quotation = IndustrialQuotation(
        project=project,
        product_groups=[group],
        totals=totals,
        parser_type="manual_creation"
    )
    
    logger.info("Created sample quotation programmatically")
    
    # Validate consistency
    validation_results = quotation.validate_totals_consistency()
    logger.info("Validation results:")
    for check, is_valid in validation_results.items():
        if is_valid:
            logger.info(f"   ✓ {check}: {is_valid}")
        else:
            logger.warning(f"   ✗ {check}: {is_valid}")
    
    # Show calculated properties
    logger.info("Category calculations:")
    cat = quotation.product_groups[0].categories[0]
    logger.info(f"   - Type: {cat.category_type}")
    logger.info(f"   - Calculated pricelist: €{cat.calculated_pricelist_subtotal:,.2f}")
    logger.info(f"   - Calculated cost: €{cat.calculated_cost_subtotal:,.2f}")
    logger.info(f"   - Margin amount: €{cat.margin_amount:,.2f}")
    logger.info(f"   - Margin percentage: {cat.margin_percentage:.2f}%")

def demonstrate_json_serialization():
    """Demonstrate JSON serialization and deserialization"""
    logger.info("=" * 80)
    logger.info("JSON SERIALIZATION DEMONSTRATION")
    logger.info("=" * 80)
    
    # Parse a file to get a quotation
    test_file = "input/test_pre.xlsm"
    if not os.path.exists(test_file):
        logger.warning(f"Test file not found: {test_file}")
        return
    
    try:
        # Parse quotation
        quotation = parse_quotation_file(test_file)
        logger.info("Parsed quotation for JSON demo")
        
        # Save to JSON
        json_output = "output/quotation_model_example.json"
        quotation.save_json(json_output)
        logger.info(f"Saved to JSON: {json_output}")
        
        # Load from JSON
        loaded_quotation = IndustrialQuotation.load_json(json_output)
        logger.info("Successfully loaded from JSON")
        
        # Verify they're equivalent
        original_stats = quotation.get_summary_stats()
        loaded_stats = loaded_quotation.get_summary_stats()
        
        logger.info("Comparing original vs loaded:")
        items_match = original_stats['total_items'] == loaded_stats['total_items']
        total_match = abs(original_stats['total_listino'] - loaded_stats['total_listino']) < 0.01
        logger.info(f"   - Items match: {items_match}")
        logger.info(f"   - Total matches: {total_match}")
        
        if not items_match or not total_match:
            logger.warning("Data integrity check failed during JSON roundtrip")
        
        # Show JSON size
        json_size = os.path.getsize(json_output)
        logger.info(f"JSON file size: {json_size:,} bytes")
        
    except Exception as e:
        logger.error(f"JSON serialization failed: {e}", exc_info=True)

def demonstrate_pandas_conversion():
    """Demonstrate pandas DataFrame conversion and analysis"""
    logger.info("=" * 80)
    logger.info("PANDAS DATAFRAME CONVERSION DEMONSTRATION")
    logger.info("=" * 80)
    
    test_file = "input/test_pre.xlsm"
    if not os.path.exists(test_file):
        logger.warning(f"Test file not found: {test_file}")
        return
    
    try:
        # Parse quotation
        quotation = parse_quotation_file(test_file)
        logger.info("Parsed quotation for pandas demo")
        
        # Convert to different DataFrames
        items_df = quotation.to_items_dataframe()
        categories_df = quotation.to_categories_dataframe()
        groups_df = quotation.to_groups_dataframe()
        
        logger.info("Created DataFrames:")
        logger.info(f"   - Items DataFrame: {items_df.shape[0]} rows × {items_df.shape[1]} columns")
        logger.info(f"   - Categories DataFrame: {categories_df.shape[0]} rows × {categories_df.shape[1]} columns")
        logger.info(f"   - Groups DataFrame: {groups_df.shape[0]} rows × {groups_df.shape[1]} columns")
        
        # Show sample analysis
        if not items_df.empty:
            logger.info("Sample analysis:")
            logger.info(f"   - Total quantity: {items_df['quantity'].sum():.2f}")
            logger.info(f"   - Average unit price: €{items_df['pricelist_unit_price'].mean():,.2f}")
            logger.info(f"   - Most expensive item: €{items_df['pricelist_unit_price'].max():,.2f}")
            
            # Engineering cost analysis
            engineering_cols = [col for col in items_df.columns if any(x in col for x in ['utm_', 'ute_', 'sw_', 'ba_'])]
            if engineering_cols:
                total_engineering = items_df[engineering_cols].sum().sum()
                logger.info(f"   - Total engineering costs: €{total_engineering:,.2f}")
            
            logger.debug(f"Engineering columns found: {engineering_cols}")
        else:
            logger.warning("Items DataFrame is empty")
        
        # Save DataFrames to CSV for external analysis
        items_df.to_csv("output/items_analysis.csv", index=False)
        categories_df.to_csv("output/categories_analysis.csv", index=False)
        logger.info("Saved DataFrames to CSV files")
        
    except Exception as e:
        logger.error(f"Pandas conversion failed: {e}", exc_info=True)

def demonstrate_llm_integration():
    """Demonstrate LLM-friendly data access and descriptions"""
    logger.info("=" * 80)
    logger.info("LLM INTEGRATION DEMONSTRATION")
    logger.info("=" * 80)
    
    # Show field descriptions for LLM tools
    from models.quotation_models import QuotationItem
    
    logger.info("Field descriptions for LLM tools:")
    logger.info("   QuotationItem fields with descriptions:")
    
    # Get field information from Pydantic model (v2 compatible)
    field_count = 0
    # Use model_fields for Pydantic v2, fallback to __fields__ for v1
    if hasattr(QuotationItem, 'model_fields'):
        model_fields = QuotationItem.model_fields
    else:
        model_fields = getattr(QuotationItem, '__fields__', {})
    
    for field_name, field_info in model_fields.items():
        # Handle both Pydantic v1 and v2
        if hasattr(field_info, 'description'):
            description = field_info.description or 'No description'
        else:
            description = getattr(field_info, 'field_info', {}).get('description', 'No description')
        
        # Get field type (v2 compatible)
        if hasattr(field_info, 'annotation'):
            field_type = str(field_info.annotation).replace('typing.', '')
        elif hasattr(field_info, 'type_'):
            field_type = str(field_info.type_).replace('typing.', '')
        else:
            field_type = 'Unknown'
            
        logger.debug(f"     - {field_name} ({field_type}): {description}")
        field_count += 1
        
        # Only show first few fields in INFO, rest in DEBUG
        if field_count <= 3:
            logger.info(f"     - {field_name} ({field_type}): {description}")
        elif field_count == 4:
            remaining_fields = len(model_fields) - 3
            logger.info(f"     ... and {remaining_fields} more fields (see debug log)")
    
    logger.info("Model provides structured access for LLMs:")
    logger.info("   - All fields have detailed descriptions")
    logger.info("   - Data is validated and consistent")
    logger.info("   - Easy to convert to different formats")
    logger.info("   - Built-in analysis methods")

def main():
    """Run all demonstrations"""
    logger.info("INDUSTRIAL QUOTATION UNIFIED MODEL SYSTEM DEMONSTRATION")
    logger.info("=" * 80)
    logger.info(f"Logging to file: {log_file}")
    logger.info("=" * 80)
    
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    
    try:
        # Run all demonstrations
        logger.info("Starting demonstration sequence...")
        demonstrate_unified_parsing()
        demonstrate_model_validation()
        demonstrate_json_serialization()
        demonstrate_pandas_conversion()
        demonstrate_llm_integration()
        
        logger.info("=" * 80)
        logger.info("DEMONSTRATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info("Key benefits of the unified model system:")
        logger.info("   ✓ Consistent data structure across different file types")
        logger.info("   ✓ Automatic validation and error detection")
        logger.info("   ✓ JSON serialization for storage and transmission")
        logger.info("   ✓ Pandas integration for data analysis")
        logger.info("   ✓ LLM-friendly field descriptions")
        logger.info("   ✓ Type safety and IDE support")
        logger.info("   ✓ Extensible for future file formats")
        
        # Log completion summary
        logger.info("=" * 80)
        logger.info(f"Complete log saved to: {log_file}")
        logger.info("Check the output/ directory for generated files:")
        logger.info("   - quotation_model_example.json")
        logger.info("   - items_analysis.csv")
        logger.info("   - categories_analysis.csv")
        logger.info("=" * 80)
        
        # Print completion message to console
        print(f"✅ Demonstration completed successfully!")
        print(f"📋 Full log saved to: {log_file}")
        print(f"📁 Check output/ directory for generated files")
        
    except Exception as e:
        logger.error(f"Demonstration failed: {e}", exc_info=True)
        print(f"❌ Demonstration failed. Check log file: {log_file}")

if __name__ == "__main__":
    main() 
"""
Test script for the Unified Comparator
This script tests the basic functionality of the unified comparator
"""

import sys
import os
import tempfile
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from models.quotation_models import IndustrialQuotation, ProjectInfo, ProjectParameters, SalesInfo, QuotationTotals, ProductGroup, QuotationCategory, QuotationItem
from components.analyzers.unified_comparator import UnifiedComparator

def create_test_quotation(name: str, items_count: int = 5) -> IndustrialQuotation:
    """Create a test quotation for testing purposes"""
    
    # Create project info
    project = ProjectInfo(
        id=f"TEST-{name}-001",
        customer=f"Test Customer {name}",
        listino=f"Listino {name}",
        parameters=ProjectParameters(),
        sales_info=SalesInfo()
    )
    
    # Create totals
    totals = QuotationTotals(
        total_pricelist=10000.0,
        total_cost=8000.0,
        total_offer=9500.0
    )
    
    # Create product groups
    product_groups = []
    
    for group_idx in range(2):
        categories = []
        
        for cat_idx in range(2):
            items = []
            
            for item_idx in range(items_count // 4):
                item = QuotationItem(
                    position=f"{group_idx+1}.{cat_idx+1}.{item_idx+1}",
                    code=f"ITEM-{name}-{group_idx+1}-{cat_idx+1}-{item_idx+1}",
                    description=f"Test item {item_idx+1} for {name}",
                    quantity=1.0,
                    pricelist_unit_price=100.0 * (item_idx + 1),
                    pricelist_total_price=100.0 * (item_idx + 1),
                    unit_cost=80.0 * (item_idx + 1),
                    total_cost=80.0 * (item_idx + 1)
                )
                items.append(item)
            
            category = QuotationCategory(
                category_id=f"CAT-{name}-{group_idx+1}-{cat_idx+1}",
                category_name=f"Category {cat_idx+1}",
                wbe=f"WBE-{name}-{group_idx+1}-{cat_idx+1}",
                items=items
            )
            categories.append(category)
        
        group = ProductGroup(
            group_id=f"GROUP-{name}-{group_idx+1}",
            group_name=f"Product Group {group_idx+1}",
            categories=categories
        )
        product_groups.append(group)
    
    return IndustrialQuotation(
        project=project,
        product_groups=product_groups,
        totals=totals
    )

def test_unified_comparator():
    """Test the unified comparator with sample data"""
    
    print("🧪 Testing Unified Comparator...")
    
    # Create two test quotations
    first_quotation = create_test_quotation("FIRST", 8)
    second_quotation = create_test_quotation("SECOND", 6)
    
    # Add some differences to the second quotation
    # Modify some items
    for group in second_quotation.product_groups:
        for category in group.categories:
            for item in category.items:
                if "ITEM-SECOND-1-1-1" in item.code:
                    item.pricelist_unit_price = 150.0
                    item.pricelist_total_price = 150.0
                elif "ITEM-SECOND-2-1-1" in item.code:
                    item.description = "Modified description"
    
    # Remove one item from second quotation
    if second_quotation.product_groups and second_quotation.product_groups[0].categories:
        second_quotation.product_groups[0].categories[0].items = second_quotation.product_groups[0].categories[0].items[:-1]
    
    # Add one item to first quotation
    new_item = QuotationItem(
        position="1.1.5",
        code="ITEM-FIRST-NEW-001",
        description="New item in first quotation",
        quantity=1.0,
        pricelist_unit_price=200.0,
        pricelist_total_price=200.0,
        unit_cost=160.0,
        total_cost=160.0
    )
    if first_quotation.product_groups and first_quotation.product_groups[0].categories:
        first_quotation.product_groups[0].categories[0].items.append(new_item)
    
    # Create comparator
    comparator = UnifiedComparator(
        first_quotation=first_quotation,
        second_quotation=second_quotation,
        first_name="Test First File",
        second_name="Test Second File"
    )
    
    # Test analysis results
    print(f"✅ First quotation items: {len(comparator.first_items_map)}")
    print(f"✅ Second quotation items: {len(comparator.second_items_map)}")
    print(f"✅ Total comparisons: {len(comparator.item_comparisons)}")
    
    # Test comparison results
    matches = len([c for c in comparator.item_comparisons if c.result_type.value == 'match'])
    missing_in_second = len([c for c in comparator.item_comparisons if c.result_type.value == 'missing_in_second'])
    missing_in_first = len([c for c in comparator.item_comparisons if c.result_type.value == 'missing_in_first'])
    value_mismatches = len([c for c in comparator.item_comparisons if c.result_type.value == 'value_mismatch'])
    
    print(f"✅ Matches: {matches}")
    print(f"✅ Missing in second: {missing_in_second}")
    print(f"✅ Missing in first: {missing_in_first}")
    print(f"✅ Value mismatches: {value_mismatches}")
    
    # Test financial analysis
    print(f"✅ First total: €{comparator.pricelist_analysis['first_total_listino']:,.2f}")
    print(f"✅ Second total: €{comparator.pricelist_analysis['second_total_listino']:,.2f}")
    print(f"✅ Difference: €{comparator.pricelist_analysis['listino_difference']:,.2f}")
    
    # Test WBE analysis
    print(f"✅ WBE impacts: {len(comparator.wbe_impacts)}")
    
    # Test views
    views = comparator.get_comparison_views()
    print(f"✅ Available views: {len(views)}")
    for view in views:
        print(f"  - {view}")
    
    print("✅ All tests passed!")
    
    return comparator

if __name__ == "__main__":
    comparator = test_unified_comparator()
    
    # Save test results
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            'first_quotation': comparator.first_quotation.to_parser_dict(),
            'second_quotation': comparator.second_quotation.to_parser_dict(),
            'analysis': comparator.pricelist_analysis
        }, f, indent=2)
        print(f"📄 Test results saved to: {f.name}") 
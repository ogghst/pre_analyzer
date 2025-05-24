"""
Example Usage of Excel to JSON Parser
Demonstrates various ways to use the parser and work with the generated JSON data
"""

import json
from pre_file_parser import parse_excel_to_json, PreFileParser
from validate_json_schema import validate_quotation_json

def full_structure_example():
    """Display the complete hierarchical structure"""
    print("\n🏗️ FULL HIERARCHICAL STRUCTURE")
    print("=" * 50)
    
    # Load the parsed data
    with open("output/quotation.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Display project information
    project = data['project']
    print("📋 PROJECT")
    print(f"├── ID: {project['id']}")
    print(f"├── Customer: {project['customer']}")
    print("├── Parameters:")
    params = project['parameters']
    print(f"│   ├── DOC Percentage: {params['doc_percentage']:.3%}")
    print(f"│   ├── PM Percentage: {params['pm_percentage']:.3%}")
    print(f"│   ├── Financial Costs: {params['financial_costs']:.3%}")
    print(f"│   ├── Currency: {params['currency']}")
    print(f"│   ├── Exchange Rate: {params['exchange_rate']}")
    print(f"│   ├── Waste Disposal: {params['waste_disposal']:.3%}")
    print(f"│   ├── Warranty Percentage: {params['warranty_percentage']:.3%}")
    print(f"│   └── 24h Service: {params['is_24h_service']}")
    print("└── Sales Info:")
    sales = project['sales_info']
    print(f"    ├── Area Manager: {sales['area_manager'] or 'N/A'}")
    print(f"    ├── Agent: {sales['agent'] or 'N/A'}")
    print(f"    ├── Commission: {sales['commission_percentage']:.3%}")
    print(f"    └── Author: {sales['author'] or 'N/A'}")
    
    print(f"\n📦 PRODUCT GROUPS ({len(data['product_groups'])} groups)")
    
    # Display all product groups with their hierarchical structure
    for group_idx, group in enumerate(data['product_groups'], 1):
        is_last_group = group_idx == len(data['product_groups'])
        group_prefix = "└──" if is_last_group else "├──"
        continue_prefix = "   " if is_last_group else "│  "
        
        # Calculate group totals
        group_total = sum(cat['total'] for cat in group['categories'])
        total_items = sum(len(cat['items']) for cat in group['categories'])
        
        print(f"{group_prefix} {group['group_id']}: {group['group_name']}")
        print(f"{continue_prefix} ├── Quantity: {group['quantity']}")
        print(f"{continue_prefix} ├── Total Value: €{group_total:,.2f}")
        print(f"{continue_prefix} ├── Total Items: {total_items}")
        print(f"{continue_prefix} └── Categories ({len(group['categories'])}):")
        
        # Display categories within each group
        for cat_idx, category in enumerate(group['categories'], 1):
            is_last_category = cat_idx == len(group['categories'])
            cat_prefix = f"{continue_prefix}     └──" if is_last_category else f"{continue_prefix}     ├──"
            cat_continue = f"{continue_prefix}        " if is_last_category else f"{continue_prefix}     │  "
            
            print(f"{cat_prefix} {category['category_id']}: {category['category_name']}")
            print(f"{cat_continue} ├── Items: {len(category['items'])}")
            print(f"{cat_continue} ├── Subtotal Listino: €{category['subtotal_listino']:,.2f}")
            print(f"{cat_continue} ├── Subtotal Codice: €{category['subtotal_codice']:,.2f}")
            print(f"{cat_continue} ├── Total: €{category['total']:,.2f}")
            
            # Show top 5 items by value in each category
            items_with_value = [item for item in category['items'] if item['pricelist_total_price'] > 0]
            top_items = sorted(items_with_value, key=lambda x: x['pricelist_total_price'], reverse=True)[:5]
            
            if top_items:
                print(f"{cat_continue} └── Top Items:")
                for item_idx, item in enumerate(top_items, 1):
                    is_last_item = item_idx == len(top_items)
                    item_prefix = f"{cat_continue}     └──" if is_last_item else f"{cat_continue}     ├──"
                    
                    # Truncate long descriptions
                    desc = item['description'][:40] + "..." if len(item['description']) > 40 else item['description']
                    print(f"{item_prefix} {item['code']}: {desc} (€{item['pricelist_total_price']:,.2f})")
            else:
                print(f"{cat_continue} └── No items with value")
        
        print()  # Add spacing between groups
    
    # Display totals
    totals = data['totals']
    print("💰 TOTALS")
    print(f"├── Equipment Total: €{totals['equipment_total']:,.2f}")
    print(f"├── Installation Total: €{totals['installation_total']:,.2f}")
    print(f"├── Subtotal: €{totals['subtotal']:,.2f}")
    print(f"├── DOC Fee: €{totals['doc_fee']:,.2f}")
    print(f"├── PM Fee: €{totals['pm_fee']:,.2f}")
    print(f"├── Warranty Fee: €{totals['warranty_fee']:,.2f}")
    print(f"└── GRAND TOTAL: €{totals['grand_total']:,.2f}")
    
    # Display summary statistics
    print(f"\n📊 SUMMARY STATISTICS")
    all_items = []
    for group in data['product_groups']:
        for category in group['categories']:
            all_items.extend(category['items'])
    
    items_with_value = [item for item in all_items if item['pricelist_total_price'] > 0]
    items_with_negative = [item for item in all_items if item['pricelist_total_price'] < 0]
    
    print(f"├── Total Groups: {len(data['product_groups'])}")
    print(f"├── Total Categories: {sum(len(group['categories']) for group in data['product_groups'])}")
    print(f"├── Total Items: {len(all_items)}")
    print(f"├── Items with Positive Value: {len(items_with_value)}")
    print(f"├── Items with Negative Value (Discounts): {len(items_with_negative)}")
    print(f"├── Items with Zero Value: {len(all_items) - len(items_with_value) - len(items_with_negative)}")
    
    if items_with_value:
        avg_item_value = sum(item['pricelist_total_price'] for item in items_with_value) / len(items_with_value)
        max_item = max(items_with_value, key=lambda x: x['pricelist_total_price'])
        min_item = min(items_with_value, key=lambda x: x['pricelist_total_price'])
        
        print(f"├── Average Item Value: €{avg_item_value:,.2f}")
        print(f"├── Highest Value Item: {max_item['code']} (€{max_item['pricelist_total_price']:,.2f})")
        print(f"└── Lowest Value Item: {min_item['code']} (€{min_item['pricelist_total_price']:,.2f})")
    else:
        print(f"└── No items with positive value found")

def basic_example():
    """Basic usage example"""
    print("🔄 BASIC USAGE EXAMPLE")
    print("=" * 50)
    
    # Simple one-line parsing
    result = parse_excel_to_json("input/PRE_ONLY_OFFER1.xlsx", "output/example_output.json")
    
    print(f"✅ Parsed successfully!")
    print(f"📁 Project ID: {result['project']['id']}")
    print(f"👤 Customer: {result['project']['customer']}")
    print(f"💰 Grand Total: €{result['totals']['grand_total']:,.2f}")
    print(f"📦 Product Groups: {len(result['product_groups'])}")


def detailed_example():
    """Detailed usage with manual parser control"""
    print("\n🔧 DETAILED USAGE EXAMPLE")
    print("=" * 50)
    
    # Create parser instance for more control
    parser = PreFileParser("input/PRE_ONLY_OFFER1.xlsx")
    result = parser.parse()
    
    # Access project information
    project = result['project']
    print(f"📋 Project Information:")
    print(f"   ID: {project['id']}")
    print(f"   Customer: {project['customer']}")
    print(f"   Currency: {project['parameters']['currency']}")
    print(f"   Exchange Rate: {project['parameters']['exchange_rate']}")
    print(f"   DOC %: {project['parameters']['doc_percentage']:.3%}")
    print(f"   PM %: {project['parameters']['pm_percentage']:.3%}")
    
    # Analyze product groups
    print(f"\n📦 Product Groups Analysis:")
    for i, group in enumerate(result['product_groups'], 1):
        print(f"   {i}. {group['group_id']}: {group['group_name']}")
        print(f"      Categories: {len(group['categories'])}")
        
        total_items = sum(len(cat['items']) for cat in group['categories'])
        group_total = sum(cat['total'] for cat in group['categories'])
        
        print(f"      Items: {total_items}")
        print(f"      Total: €{group_total:,.2f}")
        
        # Show top categories by value
        sorted_categories = sorted(group['categories'], key=lambda x: x['total'], reverse=True)
        if sorted_categories:
            top_cat = sorted_categories[0]
            print(f"      Top Category: {top_cat['category_id']} (€{top_cat['total']:,.2f})")
    
    # Show totals breakdown
    totals = result['totals']
    print(f"\n💰 Financial Breakdown:")
    print(f"   Equipment Total: €{totals['equipment_total']:,.2f}")
    print(f"   Installation Total: €{totals['installation_total']:,.2f}")
    print(f"   Subtotal: €{totals['subtotal']:,.2f}")
    print(f"   DOC Fee: €{totals['doc_fee']:,.2f}")
    print(f"   PM Fee: €{totals['pm_fee']:,.2f}")
    print(f"   Warranty Fee: €{totals['warranty_fee']:,.2f}")
    print(f"   GRAND TOTAL: €{totals['grand_total']:,.2f}")


def category_analysis_example():
    """Example of analyzing categories and items"""
    print("\n📊 CATEGORY ANALYSIS EXAMPLE")
    print("=" * 50)
    
    # Load the parsed data
    with open("output/quotation.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find most expensive categories
    all_categories = []
    for group in data['product_groups']:
        for category in group['categories']:
            all_categories.append({
                'group_id': group['group_id'],
                'group_name': group['group_name'],
                'category_id': category['category_id'],
                'category_name': category['category_name'],
                'total': category['total'],
                'item_count': len(category['items'])
            })
    
    # Sort by total value
    top_categories = sorted(all_categories, key=lambda x: x['total'], reverse=True)
    
    print("🔝 Top 5 Most Expensive Categories:")
    for i, cat in enumerate(top_categories[:5], 1):
        print(f"   {i}. {cat['category_id']} - {cat['category_name'][:50]}...")
        print(f"      Group: {cat['group_id']}")
        print(f"      Value: €{cat['total']:,.2f}")
        print(f"      Items: {cat['item_count']}")
        print()
    
    # Find categories with most items
    by_item_count = sorted(all_categories, key=lambda x: x['item_count'], reverse=True)
    
    print("📋 Categories with Most Items:")
    for i, cat in enumerate(by_item_count[:3], 1):
        print(f"   {i}. {cat['category_id']} - {cat['item_count']} items (€{cat['total']:,.2f})")


def item_analysis_example():
    """Example of analyzing individual items"""
    print("\n🔍 ITEM ANALYSIS EXAMPLE")
    print("=" * 50)
    
    # Load the parsed data
    with open("output/quotation.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Collect all items with their totals
    all_items = []
    for group in data['product_groups']:
        for category in group['categories']:
            for item in category['items']:
                if item['pricelist_total_price'] > 0:  # Only items with positive value
                    all_items.append({
                        'group_id': group['group_id'],
                        'category_id': category['category_id'],
                        'code': item['code'],
                        'description': item['description'],
                        'quantity': item['quantity'],
                        'pricelist_unit_price': item['pricelist_unit_price'],
                        'pricelist_total_price': item['pricelist_total_price']
                    })
    
    # Sort by value
    top_items = sorted(all_items, key=lambda x: x['pricelist_total_price'], reverse=True)
    
    print("💎 Top 10 Most Expensive Items:")
    for i, item in enumerate(top_items[:10], 1):
        print(f"   {i}. {item['code']}")
        print(f"      Description: {item['description'][:60]}...")
        print(f"      Group/Category: {item['group_id']}/{item['category_id']}")
        print(f"      Quantity: {item['quantity']}")
        print(f"      Pricelist Unit : €{item['pricelist_unit_price']:,.2f}")
        print(f"      Pricelist Total : €{item['pricelist_total_price']:,.2f}")
        print()
    
    # Statistics
    total_items = len(all_items)
    total_value = sum(item['pricelist_total_price'] for item in all_items)
    avg_value = total_value / total_items if total_items > 0 else 0
    
    print("📈 Item Statistics:")
    print(f"   Total Items with Value: {total_items}")
    print(f"   Total Value: €{total_value:,.2f}")
    print(f"   Average Item Value: €{avg_value:,.2f}")


def main():
    """Run all examples"""
    print("🚀 EXCEL TO JSON PARSER - USAGE EXAMPLES")
    print("=" * 60)
    
    try:
        # Run examples in sequence
        basic_example()
        detailed_example()
        full_structure_example()  # Add the new hierarchical structure display
        category_analysis_example()
        item_analysis_example()
        
        print("\n🎯 ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("Check the generated files:")
        print("   - output/quotation.json (main output)")
        print("   - output/example_output.json (basic example)")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
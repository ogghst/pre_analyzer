#!/usr/bin/env python3
"""
Test script to demonstrate both parsers working together
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from pre_file.pre_file_parser import parse_excel_to_json
from pre_file.analisi_profittabilita_parser import parse_analisi_profittabilita_to_json

def test_both_parsers():
    """Test both parsers and compare outputs"""
    print("=" * 80)
    print("TESTING BOTH PARSERS")
    print("=" * 80)
    
    # Test PRE file parser
    print("\n1. Testing PRE File Parser:")
    print("-" * 40)
    try:
        pre_result = parse_excel_to_json(
            "input/PRE_ONLY_OFFER1.xlsx", 
            "output/pre_test.json"
        )
        print(f"✓ PRE Parser - Project ID: {pre_result['project']['id']}")
        print(f"✓ PRE Parser - Customer: {pre_result['project']['customer']}")
        print(f"✓ PRE Parser - Groups: {len(pre_result['product_groups'])}")
        print(f"✓ PRE Parser - Grand Total: {pre_result['totals']['grand_total']}")
        
    except Exception as e:
        print(f"✗ PRE Parser failed: {e}")
    
    # Test Analisi Profittabilita parser (Complete with 81 columns)
    print("\n2. Testing Analisi Profittabilita Parser (Complete - 81 columns):")
    print("-" * 70)
    try:
        analisi_result = parse_analisi_profittabilita_to_json(
            "input/cc2199_analisi_profittabilita_new_offer1.xlsx",
            "output/analisi_test_complete.json"
        )
        print(f"✓ Analisi Parser - Project ID: {analisi_result['project']['id']}")
        print(f"✓ Analisi Parser - Listino: {analisi_result['project']['listino']}")
        print(f"✓ Analisi Parser - Groups: {len(analisi_result['product_groups'])}")
        print(f"✓ Analisi Parser - Total Listino: {analisi_result['totals']['total_listino']}")
        print(f"✓ Analisi Parser - Total Costo: {analisi_result['totals']['total_costo']}")
        print(f"✓ Analisi Parser - Margin: {analisi_result['totals']['margin']} ({analisi_result['totals']['margin_percentage']}%)")
        
        # Show field count from a sample item
        if analisi_result['product_groups']:
            first_group = analisi_result['product_groups'][0]
            if first_group['categories']:
                first_category = first_group['categories'][0]
                if first_category['items']:
                    sample_item = first_category['items'][0]
                    print(f"✓ Analisi Parser - Fields per item: {len(sample_item)} (includes all 81 columns)")
                    
                    # Count non-zero fields
                    non_zero_fields = sum(1 for k, v in sample_item.items() 
                                        if isinstance(v, (int, float)) and v != 0)
                    print(f"✓ Analisi Parser - Non-zero fields in sample: {non_zero_fields}")
                    
                    # Show sample of new fields with values
                    print(f"✓ Sample additional fields:")
                    sample_fields = ['utm_robot', 'pm_cost', 'install', 'after_sales', 'spese_pm', 'document']
                    for field in sample_fields:
                        if field in sample_item:
                            print(f"    {field}: {sample_item[field]}")
        
    except Exception as e:
        print(f"✗ Analisi Parser failed: {e}")
    
    print("\n" + "=" * 80)
    print("PARSER COMPARISON & CAPABILITIES")
    print("=" * 80)
    
    print("\nPRE File Parser Features:")
    print("• Parses quotation files with specific format")
    print("• Extracts project parameters (doc %, PM %, financial costs, etc.)")
    print("• Identifies groups by 'TXT-' prefix")
    print("• Calculates fees and grand totals")
    print("• Focus on commercial quotations")
    print("• ~25 key columns extracted")
    
    print("\nAnalisi Profittabilita Parser Features (UPDATED):")
    print("• Parses profitability analysis files")
    print("• Extracts project ID and listino information")
    print("• Identifies groups by 'TXT' prefix")
    print("• Includes cost analysis (listino vs costo)")
    print("• Calculates margins and profitability metrics")
    print("• ALL 81 COLUMNS EXTRACTED including:")
    print("  - UTM fields (Robot, LGV, Intra, Layout)")
    print("  - Engineering fields (UTE, BA, SW-PC, SW-PLC, SW-LGV)")
    print("  - Manufacturing fields (MTG-MEC, CAB-ELE)")
    print("  - Testing fields (COLL-BA, COLL-PC, COLL-PLC, COLL-LGV)")
    print("  - Project management (PM costs, hours, expenses)")
    print("  - Logistics (Document, Imballo, Stoccaggio, Trasporto)")
    print("  - Field activities (Site, Install, AV-PC, AV-PLC, AV-LGV)")
    print("  - Additional costs (After Sales, Provvigioni, Tesoretto)")
    
    print("\nCommon Architecture:")
    print("• Both use same JSON schema structure")
    print("• Similar constant organization")
    print("• Same error handling patterns")
    print("• Consistent logging approach")
    print("• Modular design with separate classes")
    print("• Complete field extraction for comprehensive analysis")

def show_field_analysis():
    """Show detailed field analysis of the complete parser"""
    print("\n" + "=" * 80)
    print("COMPLETE FIELD ANALYSIS")
    print("=" * 80)
    
    try:
        import json
        with open('output/analisi_test_complete.json', 'r') as f:
            data = json.load(f)
        
        # Analyze field usage
        field_usage = {}
        total_items = 0
        
        for group in data['product_groups']:
            for category in group['categories']:
                for item in category['items']:
                    total_items += 1
                    for k, v in item.items():
                        if isinstance(v, (int, float)) and v != 0:
                            field_usage[k] = field_usage.get(k, 0) + 1
        
        print(f"Total items analyzed: {total_items}")
        print(f"Total unique fields: {len(field_usage)}")
        print(f"\nTop 15 most used fields (with non-zero values):")
        
        sorted_fields = sorted(field_usage.items(), key=lambda x: x[1], reverse=True)
        for field, count in sorted_fields[:15]:
            percentage = (count / total_items) * 100
            print(f"  {field:<20}: {count:3d} items ({percentage:5.1f}%)")
        
        # Show field categories
        utm_fields = [f for f, _ in sorted_fields if 'utm' in f]
        engineering_fields = [f for f, _ in sorted_fields if f.startswith(('ute', 'ba', 'sw_'))]
        manufacturing_fields = [f for f, _ in sorted_fields if f.startswith(('mtg_', 'cab_'))]
        
        print(f"\nField categories with data:")
        print(f"  UTM fields: {len(utm_fields)}")
        print(f"  Engineering fields: {len(engineering_fields)}")
        print(f"  Manufacturing fields: {len(manufacturing_fields)}")
        
    except Exception as e:
        print(f"Could not perform field analysis: {e}")

if __name__ == "__main__":
    test_both_parsers()
    show_field_analysis() 
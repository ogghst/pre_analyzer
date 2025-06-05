#!/usr/bin/env python3
"""
Test script for both direct parsers
Demonstrates parsing PRE and Analisi Profittabilita files directly to IndustrialQuotation objects
"""

from parsers.pre_file_parser_direct import parse_pre_file_direct
from parsers.analisi_profittabilita_parser_direct import parse_analisi_profittabilita_direct
import time

def test_both_parsers():
    """Test both direct parsers with example files"""
    
    print("🚀 Testing Both Direct Parsers")
    print("=" * 60)
    
    # Test files
    pre_file = "input/test_pre.xlsm"
    ap_file = "input/test_ap.xlsm"
    
    try:
        # Test PRE direct parser
        print("📁 Testing PRE Direct Parser...")
        start_time = time.time()
        
        pre_quotation = parse_pre_file_direct(pre_file, "output/test_pre_direct.json")
        pre_stats = pre_quotation.get_summary_stats()
        
        pre_time = time.time() - start_time
        
        print(f"✅ PRE parsing completed in {pre_time:.2f} seconds")
        print(f"   - Project: {pre_stats['project_id']}")
        print(f"   - Groups: {pre_stats['total_groups']}")
        print(f"   - Items: {pre_stats['total_items']}")
        print(f"   - Total: €{pre_quotation.totals.total_pricelist:,.2f}")
        
        # Test AP direct parser  
        print("\n📁 Testing Analisi Profittabilita Direct Parser...")
        start_time = time.time()
        
        ap_quotation = parse_analisi_profittabilita_direct(ap_file, "output/test_ap_direct.json")
        ap_stats = ap_quotation.get_summary_stats()
        
        ap_time = time.time() - start_time
        
        print(f"✅ AP parsing completed in {ap_time:.2f} seconds")
        print(f"   - Project: {ap_stats['project_id']}")
        print(f"   - Groups: {ap_stats['total_groups']}")
        print(f"   - Items: {ap_stats['total_items']}")
        print(f"   - Total: €{ap_quotation.totals.total_pricelist:,.2f}")
        
        # Summary comparison
        print(f"\n📊 Performance Summary:")
        print(f"   - PRE parsing: {pre_time:.2f}s")
        print(f"   - AP parsing: {ap_time:.2f}s")
        print(f"   - Total time: {pre_time + ap_time:.2f}s")
        
        print(f"\n🎯 Data Summary:")
        print(f"   - PRE file: {pre_stats['total_items']} items")
        print(f"   - AP file: {ap_stats['total_items']} items")
        print(f"   - Total items processed: {pre_stats['total_items'] + ap_stats['total_items']}")
        
        # Validation checks
        print(f"\n🔍 Validation Summary:")
        pre_validation = pre_quotation.validate_totals_consistency()
        ap_validation = ap_quotation.validate_totals_consistency()
        
        pre_valid = all(pre_validation.values())
        ap_valid = all(ap_validation.values())
        
        print(f"   - PRE validation: {'✅ Passed' if pre_valid else '❌ Failed'}")
        print(f"   - AP validation: {'✅ Passed' if ap_valid else '❌ Failed'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_both_parsers()
    print(f"\n{'✅ All tests completed successfully!' if success else '❌ Tests failed'}") 
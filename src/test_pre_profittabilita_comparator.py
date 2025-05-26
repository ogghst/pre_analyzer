"""
Test script for PRE vs Analisi Profittabilita Cross-Comparator
Simple validation of the new functionality
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import plotly
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        # Add current directory to path for local imports
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from components.analyzers.pre_profittabilita_comparator import PreProfittabilitaComparator
        print("✅ PreProfittabilitaComparator imported successfully")
    except ImportError as e:
        print(f"❌ PreProfittabilitaComparator import failed: {e}")
        return False
    
    try:
        from pre_profittabilita_comparator_app import PreProfittabilitaComparatorApp
        print("✅ PreProfittabilitaComparatorApp imported successfully")
    except ImportError as e:
        print(f"❌ PreProfittabilitaComparatorApp import failed: {e}")
        return False
    
    return True

def test_class_instantiation():
    """Test if classes can be instantiated"""
    print("\n🔍 Testing class instantiation...")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Test comparator with dummy data
        from components.analyzers.pre_profittabilita_comparator import PreProfittabilitaComparator
        
        dummy_pre_data = {
            "project": {"id": "TEST_PRE", "customer": "Test Customer"},
            "product_groups": [],
            "totals": {"grand_total": 1000.0}
        }
        
        dummy_prof_data = {
            "project": {"id": "TEST_PROF", "listino": "Test Listino"},
            "product_groups": [],
            "totals": {"total_listino": 1000.0, "total_costo": 800.0}
        }
        
        comparator = PreProfittabilitaComparator(dummy_pre_data, dummy_prof_data)
        print("✅ PreProfittabilitaComparator instantiated successfully")
        
        # Test basic methods
        views = comparator.get_comparison_views()
        print(f"✅ Available views: {len(views)} views")
        
        return True
        
    except Exception as e:
        print(f"❌ Class instantiation failed: {e}")
        return False

def test_file_existence():
    """Test if all required files exist"""
    print("\n🔍 Testing file existence...")
    
    required_files = [
        "components/analyzers/pre_profittabilita_comparator.py",
        "pre_profittabilita_comparator_app.py",
        "run_pre_profittabilita_comparator.py",
        "run_pre_profittabilita_comparator.bat",
        "README_PRE_PROFITTABILITA_COMPARATOR.md"
    ]
    
    all_exist = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def main():
    """Main test function"""
    print("=" * 70)
    print("PRE vs Analisi Profittabilita Cross-Comparator - Test Suite")
    print("=" * 70)
    
    # Run tests
    imports_ok = test_imports()
    files_ok = test_file_existence()
    instantiation_ok = test_class_instantiation()
    
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    print(f"📦 Imports Test: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"📁 Files Test: {'✅ PASS' if files_ok else '❌ FAIL'}")
    print(f"🏗️ Instantiation Test: {'✅ PASS' if instantiation_ok else '❌ FAIL'}")
    
    overall_success = imports_ok and files_ok and instantiation_ok
    
    print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS - Ready to use!' if overall_success else '❌ ISSUES DETECTED'}")
    
    if overall_success:
        print("\n🚀 You can now run the cross-comparator using:")
        print("   • Windows: run_pre_profittabilita_comparator.bat")
        print("   • Python: python run_pre_profittabilita_comparator.py")
        print("\n📋 The tool provides comprehensive analysis including:")
        print("   • Data consistency validation")
        print("   • WBE impact analysis")
        print("   • Financial impact assessment")
        print("   • Project structure comparison")
        print("   • Missing items analysis")
        print("   • Detailed item-by-item comparison")
    else:
        print("\n🔧 Please resolve the issues above before using the tool.")
    
    print("=" * 70)

if __name__ == "__main__":
    main() 
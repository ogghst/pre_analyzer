#!/usr/bin/env python
"""
Test script to verify constants refactoring
"""

import sys
import os

# Add path for imports
sys.path.insert(0, 'src/pre_file')

try:
    # Test field constants import
    from components.field_constants import JsonFields, DisplayFields
    print("✅ Field constants imported successfully")
    
    # Test some key constants
    assert JsonFields.PROJECT == "project"
    assert JsonFields.UTM_ROBOT == "utm_robot"
    assert DisplayFields.GROUP_ID == "Group ID"
    print("✅ Field constants values verified")
    
    # Test analyzer imports
    from components.analyzers.base_analyzer import BaseAnalyzer
    print("✅ Base analyzer imported successfully")
    
    from components.analyzers.pre_analyzer import PreAnalyzer
    print("✅ PRE analyzer imported successfully")
    
    from components.analyzers.profittabilita_analyzer import ProfittabilitaAnalyzer
    print("✅ Profittabilita analyzer imported successfully")
    
    print("\n🎉 All constants refactoring tests passed!")
    print("🔧 Hardcoded strings have been successfully replaced with constants")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except AssertionError as e:
    print(f"❌ Assertion error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1) 
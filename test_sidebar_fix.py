"""
Test script to verify the sidebar column fix
"""

import streamlit as st
import sys
import os

# Add path for imports
current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, 'src', 'pre_file')
sys.path.insert(0, src_dir)

from components.file_processor import render_file_upload_component, render_file_metrics, FileType

def test_sidebar_upload():
    """Test the file upload component in sidebar context"""
    st.title("🧪 Sidebar Column Fix Test")
    
    with st.sidebar:
        st.header("Testing Sidebar Upload")
        try:
            # This should not raise the column error anymore
            data, file_type = render_file_upload_component()
            st.success("✅ Sidebar upload component works!")
            
            if data and file_type:
                st.info(f"Data loaded: {file_type.value}")
            
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    # Test metrics in main area
    st.header("Testing Main Area Metrics")
    
    # Simulate some test data
    test_data = {
        'product_groups': [
            {'categories': [{'items': [1, 2, 3]}]},
            {'categories': [{'items': [4, 5]}]}
        ],
        'totals': {
            'grand_total': 50000,
            'total_listino': 45000
        }
    }
    
    try:
        render_file_metrics(test_data, FileType.PRE_FILE)
        st.success("✅ Main area metrics work!")
    except Exception as e:
        st.error(f"❌ Metrics error: {e}")

if __name__ == "__main__":
    test_sidebar_upload() 
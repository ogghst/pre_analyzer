"""
Example usage of the Unified Comparator
This example shows how to compare two quotation files using the unified parser and comparator
"""

import streamlit as st
import sys
import os

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from parsers.unified_parser import parse_quotation_file
from components.analyzers.unified_comparator import UnifiedComparator

def main():
    st.title("🔄 Unified Quotation Comparator Example")
    
    st.markdown("""
    This example demonstrates how to use the Unified Comparator to compare two quotation files.
    
    The comparator works with any two files that can be parsed by the unified parser:
    - PRE files
    - Analisi Profittabilita files
    - Any combination of the above
    """)
    
    # File upload section
    st.header("📁 Upload Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("First File")
        first_file = st.file_uploader(
            "Upload first quotation file (Excel)",
            type=['xlsx', 'xls'],
            key="first_file"
        )
        
        if first_file:
            st.success(f"✅ Uploaded: {first_file.name}")
    
    with col2:
        st.subheader("Second File")
        second_file = st.file_uploader(
            "Upload second quotation file (Excel)",
            type=['xlsx', 'xls'],
            key="second_file"
        )
        
        if second_file:
            st.success(f"✅ Uploaded: {second_file.name}")
    
    # Comparison section
    if first_file and second_file:
        st.header("🔍 Comparison Analysis")
        
        try:
            # Parse both files
            with st.spinner("Parsing first file..."):
                first_quotation = parse_quotation_file(first_file.name)
            
            with st.spinner("Parsing second file..."):
                second_quotation = parse_quotation_file(second_file.name)
            
            # Create comparator
            comparator = UnifiedComparator(
                first_quotation=first_quotation,
                second_quotation=second_quotation,
                first_name=first_file.name,
                second_name=second_file.name
            )
            
            # Display comparison views
            st.subheader("📊 Analysis Views")
            
            view = st.selectbox(
                "Select analysis view",
                comparator.get_comparison_views()
            )
            
            # Display selected view
            if view == "Executive Summary":
                comparator.display_executive_summary()
            elif view == "Data Consistency Check":
                comparator.display_data_consistency_check()
            elif view == "WBE Impact Analysis":
                comparator.display_wbe_impact_analysis()
            elif view == "Pricelist Comparison":
                comparator.display_pricelist_comparison()
            elif view == "Missing Items Analysis":
                comparator.display_missing_items_analysis()
            elif view == "Detailed Item Comparison":
                comparator.display_detailed_item_comparison()
            else:
                st.info("This view is not yet implemented.")
            
            # Show file information
            st.subheader("📋 File Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**First File:** {first_file.name}")
                st.write(f"**Project ID:** {first_quotation.project.id}")
                st.write(f"**Total Items:** {len(comparator.first_items_map)}")
                st.write(f"**Total Value:** €{first_quotation.totals.total_pricelist:,.2f}")
            
            with col2:
                st.write(f"**Second File:** {second_file.name}")
                st.write(f"**Project ID:** {second_quotation.project.id}")
                st.write(f"**Total Items:** {len(comparator.second_items_map)}")
                st.write(f"**Total Value:** €{second_quotation.totals.total_pricelist:,.2f}")
        
        except Exception as e:
            st.error(f"❌ Error during comparison: {str(e)}")
            st.exception(e)
    
    else:
        st.info("👆 Please upload both files to start the comparison.")
    
    # Usage instructions
    st.header("📖 Usage Instructions")
    
    st.markdown("""
    ### How to use the Unified Comparator:
    
    1. **Upload Files**: Upload two Excel quotation files (PRE or Analisi Profittabilita)
    2. **Automatic Parsing**: The unified parser will automatically detect file types
    3. **Select Analysis**: Choose from various comparison views
    4. **Review Results**: Analyze differences, missing items, and financial impact
    
    ### Available Analysis Views:
    
    - **Executive Summary**: High-level overview of differences and recommendations
    - **Data Consistency Check**: Detailed analysis of item-by-item consistency
    - **WBE Impact Analysis**: How changes affect Work Breakdown Elements
    - **Pricelist Comparison**: Financial comparison by product groups
    - **Missing Items Analysis**: Items present in one file but not the other
    - **Detailed Item Comparison**: Comprehensive item-by-item comparison with filtering
    
    ### Key Features:
    
    - ✅ **Automatic file type detection**
    - ✅ **NumberColumn formatting for better readability**
    - ✅ **Interactive charts and visualizations**
    - ✅ **Export functionality for detailed analysis**
    - ✅ **WBE impact analysis for project management**
    - ✅ **Financial impact assessment**
    """)

if __name__ == "__main__":
    main() 
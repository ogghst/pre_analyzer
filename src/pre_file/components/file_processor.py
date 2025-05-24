"""
File Processor Component
Handles file upload, detection, and processing with appropriate parsers
"""

import streamlit as st
import os
import tempfile
import sys
from typing import Dict, Any, Optional, Tuple
from enum import Enum

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from pre_file_parser import parse_excel_to_json
from analisi_profittabilita_parser import parse_analisi_profittabilita_to_json


class FileType(Enum):
    """Enumeration of supported file types"""
    PRE_FILE = "pre_file"
    ANALISI_PROFITTABILITA = "analisi_profittabilita"
    UNKNOWN = "unknown"


class FileProcessor:
    """Handles file processing with automatic type detection and parsing"""
    
    def __init__(self):
        self.current_file_type = None
        self.current_data = None
        self.file_info = {}
    
    def detect_file_type(self, filename: str, file_content=None) -> FileType:
        """
        Detect file type based on filename patterns and content
        
        Args:
            filename: Name of the uploaded file
            file_content: Optional file content for analysis
            
        Returns:
            FileType: Detected file type
        """
        filename_lower = filename.lower()
        
        # Check filename patterns
        if "pre_" in filename_lower or "pre-" in filename_lower:
            return FileType.PRE_FILE
        elif "analisi" in filename_lower and "profittabilita" in filename_lower:
            return FileType.ANALISI_PROFITTABILITA
        elif "profittabilita" in filename_lower:
            return FileType.ANALISI_PROFITTABILITA
        elif "offer" in filename_lower:
            # Could be either, let user choose or default to PRE
            return FileType.PRE_FILE
        
        return FileType.UNKNOWN
    
    def process_file(self, uploaded_file, file_type: Optional[FileType] = None) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Process uploaded file with appropriate parser
        
        Args:
            uploaded_file: Streamlit uploaded file object
            file_type: Optional file type override
            
        Returns:
            Tuple[bool, Optional[Dict], str]: (success, data, message)
        """
        try:
            # Auto-detect file type if not specified
            if file_type is None:
                file_type = self.detect_file_type(uploaded_file.name)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                temp_file_path = tmp_file.name
            
            try:
                # Process based on file type
                if file_type == FileType.PRE_FILE:
                    data = parse_excel_to_json(temp_file_path)
                    success_msg = "✅ PRE quotation file processed successfully!"
                    
                elif file_type == FileType.ANALISI_PROFITTABILITA:
                    data = parse_analisi_profittabilita_to_json(temp_file_path)
                    success_msg = "✅ Analisi Profittabilita file processed successfully!"
                    
                else:
                    return False, None, f"❌ Unsupported file type. Please upload a PRE quotation or Analisi Profittabilita file."
                
                # Store results
                self.current_file_type = file_type
                self.current_data = data
                self.file_info = {
                    'name': uploaded_file.name,
                    'size': uploaded_file.size,
                    'type': file_type.value
                }
                
                return True, data, success_msg
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            error_msg = f"❌ Error processing file: {str(e)}"
            return False, None, error_msg
    
    def get_file_info(self) -> Dict[str, Any]:
        """Get information about the currently processed file"""
        return self.file_info.copy()
    
    def get_current_data(self) -> Optional[Dict[str, Any]]:
        """Get the currently processed data"""
        return self.current_data
    
    def get_current_file_type(self) -> Optional[FileType]:
        """Get the current file type"""
        return self.current_file_type
    
    def is_data_loaded(self) -> bool:
        """Check if data is currently loaded"""
        return self.current_data is not None
    
    def clear_data(self):
        """Clear current data and reset processor"""
        self.current_file_type = None
        self.current_data = None
        self.file_info = {}


def render_file_upload_component() -> Tuple[Optional[Dict[str, Any]], Optional[FileType]]:
    """
    Render file upload component with type detection (sidebar-safe)
    
    Returns:
        Tuple[Optional[Dict], Optional[FileType]]: (processed_data, file_type)
    """
    st.header("📁 File Upload")
    
    # Initialize processor in session state
    if 'file_processor' not in st.session_state:
        st.session_state.file_processor = FileProcessor()
    
    processor = st.session_state.file_processor
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Excel File",
        type=['xlsx', 'xls'],
        help="Upload a PRE quotation file or Analisi Profittabilita file",
        key="file_uploader"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.info(f"📄 **File:** {uploaded_file.name} ({uploaded_file.size:,} bytes)")
        
        # Auto-detect file type
        detected_type = processor.detect_file_type(uploaded_file.name)
        
        # File type display mapping
        file_type_display_map = {
            FileType.PRE_FILE: "PRE Quotation File",
            FileType.ANALISI_PROFITTABILITA: "Analisi Profittabilita File",
            FileType.UNKNOWN: "Unknown File Type"
        }
        
        if detected_type == FileType.UNKNOWN:
            st.warning("⚠️ Could not auto-detect file type. Please select manually:")
            file_type_selection = st.selectbox(
                "File Type",
                options=[FileType.PRE_FILE, FileType.ANALISI_PROFITTABILITA],
                format_func=lambda x: file_type_display_map.get(x, "Unknown"),
                key="file_type_selector"
            )
        else:
            # Safe access to file type display
            file_type_display = file_type_display_map.get(detected_type, f"Detected: {detected_type.value}")
            st.success(f"🎯 **Detected Type:** {file_type_display}")
            file_type_selection = detected_type
        
        # Process button
        if st.button("🚀 Process File", type="primary", use_container_width=True):
            with st.spinner("Processing file..."):
                success, data, message = processor.process_file(uploaded_file, file_type_selection)
                
                if success:
                    st.success(message)
                    return data, file_type_selection
                else:
                    st.error(message)
                    return None, None
    
    # Show current status
    if processor.is_data_loaded():
        file_info = processor.get_file_info()
        current_type = processor.get_current_file_type()
        
        # Safe display of current file type
        type_display = "Unknown"
        if current_type == FileType.PRE_FILE:
            type_display = "PRE Quotation"
        elif current_type == FileType.ANALISI_PROFITTABILITA:
            type_display = "Analisi Profittabilita"
        
        st.success(f"✅ **Current File:** {file_info.get('name', 'Unknown')} ({type_display})")
        return processor.get_current_data(), processor.get_current_file_type()
    
    return None, None


def render_file_metrics(data: Optional[Dict[str, Any]], file_type: Optional[FileType]):
    """
    Render file processing metrics in the main area (uses columns)
    
    Args:
        data: Processed data
        file_type: Type of file processed
    """
    if data and file_type:
        st.subheader("📊 File Processing Summary")
        
        # Display basic stats using columns (safe in main area)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            groups_count = len(data.get('product_groups', []))
            st.metric("Product Groups", groups_count)
        
        with col2:
            if file_type == FileType.PRE_FILE:
                total = data.get('totals', {}).get('grand_total', 0)
                st.metric("Grand Total", f"€{total:,.2f}")
            else:
                total = data.get('totals', {}).get('total_listino', 0)
                st.metric("Total Listino", f"€{total:,.2f}")
        
        with col3:
            total_items = sum(
                len(cat.get('items', [])) 
                for group in data.get('product_groups', []) 
                for cat in group.get('categories', [])
            )
            st.metric("Total Items", total_items) 
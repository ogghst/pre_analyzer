import streamlit as st
import pandas as pd
import os
import sys
import logging
import uuid
from datetime import datetime

# Import utility functions
from utils.excel_processor import (
    save_uploaded_file,
    process_data,
)

# Import widget functions
from widgets.data_tables import (
    show_data_tables,
    show_comparison_tables
)
from widgets.detail_comparison_viz import create_detail_comparison_viz
from widgets.summary_comparison_viz import create_summary_comparison_viz
from widgets.single_file_viz import create_visualizations

# Import display names
from config import SUMMARY_FIELD_DISPLAY_NAMES, DETAIL_FIELD_DISPLAY_NAMES

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_page():
    """Configure the Streamlit page layout and title"""
    st.set_page_config(
        page_title="PRE Excel Data Analyzer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("PRE Excel Data Analyzer")
    st.markdown("""
    This application allows you to upload one or more Excel files and analyze the extracted data.
    You can view individual files or compare multiple files to identify differences.
    """)

def main():
    """Main application function"""
    # Set up the page
    setup_page()
    
    # Initialize session state for file storage
    if 'files' not in st.session_state:
        st.session_state.files = {}
    
    # Sidebar for file upload and options
    with st.sidebar:
        st.header("Upload Data")
        uploaded_files = st.file_uploader("Choose Excel files", type=['xlsx', 'xls', 'xlsm'], accept_multiple_files=True)
        
        if uploaded_files:
            # Process each uploaded file
            for uploaded_file in uploaded_files:
                # Generate a unique identifier for this file
                file_id = str(uuid.uuid4())
                file_name = uploaded_file.name
                
                # Check if we've already processed this file
                existing_ids = [fid for fid, fdata in st.session_state.files.items() 
                               if fdata['name'] == file_name]
                
                if not existing_ids:
                    # Save file temporarily
                    with st.spinner(f"Processing {file_name}..."):
                        file_path = save_uploaded_file(uploaded_file)
                        
                        if file_path:
                            # Process the file
                            detail_df, summary_df = process_data(file_path)
                            
                            # Store in session state
                            st.session_state.files[file_id] = {
                                'name': file_name,
                                'path': file_path,
                                'detail_df': detail_df,
                                'summary_df': summary_df,
                                'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            
                            # Clean up temporary file
                            try:
                                os.unlink(file_path)
                            except:
                                pass
                else:
                    st.info(f"File {file_name} already uploaded.")
        
        st.divider()
        
        # Options section
        st.header("Options")
        show_tables = st.checkbox("Show Data Tables", value=True)
        show_viz = st.checkbox("Show Visualizations", value=True)
        
        # Clear files button
        if st.button("Clear All Files"):
            st.session_state.files = {}
            st.experimental_rerun()
    
    # Main area - File selection and viewing
    if st.session_state.files:
        st.header("Uploaded Files")
        
        # Display the list of uploaded files
        file_table = []
        for file_id, file_data in st.session_state.files.items():
            file_table.append({
                "ID": file_id,
                "Filename": file_data['name'],
                f"{DETAIL_FIELD_DISPLAY_NAMES.get('wbe_item_code', 'Detail Items')}": len(file_data['detail_df']),
                f"{SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_code', 'Summary Items')}": len(file_data['summary_df']),
                "Upload Time": file_data['upload_time']
            })
        
        st.dataframe(pd.DataFrame(file_table).set_index("ID"), use_container_width=True)
        
        # Analysis mode selection
        st.subheader("Analysis Mode")
        analysis_mode = st.radio(
            "Choose analysis mode:",
            options=["Single File Analysis", "File Comparison"],
            horizontal=True,
            index=0
        )
        
        if analysis_mode == "Single File Analysis":
            # Single file selection
            file_ids = list(st.session_state.files.keys())
            file_names = [st.session_state.files[fid]['name'] for fid in file_ids]
            
            selected_idx = st.selectbox(
                "Select a file to analyze:",
                range(len(file_ids)),
                format_func=lambda i: file_names[i]
            )
            
            selected_file_id = file_ids[selected_idx]
            selected_file_data = st.session_state.files[selected_file_id]
            
            # Display single file data
            if show_tables:
                show_data_tables(
                    selected_file_data['detail_df'],
                    selected_file_data['summary_df'],
                    selected_file_data['name']
                )
            
            if show_viz:
                create_visualizations(
                    selected_file_data['detail_df'],
                    selected_file_data['summary_df'],
                    selected_file_data['name']
                )
        
        else:  # File Comparison mode
            if len(st.session_state.files) < 2:
                st.warning("You need at least 2 files to use comparison mode.")
            else:
                # File selection for comparison
                file_ids = list(st.session_state.files.keys())
                file_names = [st.session_state.files[fid]['name'] for fid in file_ids]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_idx1 = st.selectbox(
                        "Select first file:",
                        range(len(file_ids)),
                        format_func=lambda i: file_names[i],
                        key="file1"
                    )
                
                with col2:
                    # Create a list excluding the first selection
                    remaining_indices = [i for i in range(len(file_ids)) if i != selected_idx1]
                    selected_idx2 = st.selectbox(
                        "Select second file:",
                        remaining_indices,
                        format_func=lambda i: file_names[i],
                        key="file2"
                    )
                
                selected_file_id1 = file_ids[selected_idx1]
                selected_file_id2 = file_ids[selected_idx2]
                
                file1_data = st.session_state.files[selected_file_id1]
                file2_data = st.session_state.files[selected_file_id2]
                
                # Display comparison
                if show_tables:
                    show_comparison_tables(file1_data, file2_data)
                
                if show_viz:
                    # Create tabs for different types of visualizations
                    viz_tabs = st.tabs(["Summary Comparison", "Detail Comparison"])
                    
                    with viz_tabs[0]:
                        create_summary_comparison_viz(file1_data, file2_data)
                    
                    with viz_tabs[1]:
                        create_detail_comparison_viz(file1_data, file2_data)
    else:
        # Show instructions when no files are uploaded
        st.info("Please upload Excel files using the sidebar to get started.")
        
        # Sample visualizations or placeholder
        st.markdown("""
        ## What you can do with this app
        
        1. **Upload Multiple Excel Files**: Upload multiple PRE Excel files to extract and compare data.
        2. **View Individual Files**: Explore each file's data in interactive tables and charts.
        3. **Compare Files**: Select any two files to see differences in both tabular and graphical format.
        4. **Download Results**: Export processed data as CSV files for further analysis.
        
        The app supports comparison of:
        - Items present in one file but not the other
        - Differences in prices, quantities, and other numeric values
        - Distribution differences across item types and groups
        """)

if __name__ == "__main__":
    main() 
# 📊 Unified Excel Analysis & Comparison Tool

## Overview

The Unified Excel Analysis & Comparison Tool is a comprehensive Streamlit application that combines both single-file analysis and dual-file comparison capabilities for industrial equipment quotations and profitability files. This integrated solution provides a seamless user experience for analyzing PRE quotation files and Analisi Profittabilita files.

## 🎯 Key Features

### Operation Modes

The application offers four main operation modes:

1. **📊 Analyze PRE File** - Single file analysis for PRE quotation files
2. **💹 Analyze Analisi Profittabilita** - Single file analysis for profitability files
3. **🔄 Compare Two PRE Files** - Side-by-side comparison of PRE quotation files
4. **⚖️ Compare Two Profittabilita Files** - Advanced comparison of profitability files

### Analysis Features

#### PRE File Analysis
- **Project Summary**: Overview of project parameters and customer information
- **Financial Analysis**: Detailed breakdown of equipment, installation, and fee calculations
- **Tree Structure**: Hierarchical visualization of product groups and categories
- **Groups Analysis**: Analysis of product groups with cost breakdowns
- **Categories Analysis**: Detailed category-level analysis with visualizations
- **Items Analysis**: Item-level details with specifications and costs

#### Profittabilita File Analysis
- **Project Summary**: Comprehensive project overview with 81+ data fields
- **Profitability Analysis**: Margin analysis and cost effectiveness metrics
- **UTM Analysis**: Time tracking analysis for manufacturing processes
- **WBE Analysis**: Work Breakdown Element analysis with cost aggregation
- **Field Analysis**: Usage statistics and field completeness analysis
- **Tree Structure**: Hierarchical view of work elements and categories

### Comparison Features

#### PRE File Comparison
- **Project Comparison**: Side-by-side parameter comparison
- **Financial Comparison**: Detailed financial difference analysis
- **Groups Comparison**: Product group differences with visual charts
- **Categories Comparison**: Category-level comparison with impact analysis
- **Items Comparison**: Item-by-item difference detection
- **Summary Report**: Automated insights and recommendations

#### Profittabilita File Comparison
- **Project Comparison**: Comprehensive project parameter comparison
- **Profitability Comparison**: Margin and cost analysis differences
- **WBE Comparison**: Work Breakdown Element comparison with threshold filtering
- **Cost Elements Comparison**: Detailed cost category analysis (Material, UTM, Engineering, etc.)
- **UTM Comparison**: Manufacturing time comparison with distribution charts
- **Engineering Comparison**: UTE, BA, and software component analysis
- **Types Comparison**: Equipment type classification and comparison
- **Summary Report**: Automated difference detection with financial impact analysis

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- Required packages (install via `pip install -r requirements.txt`):
  - streamlit
  - pandas
  - plotly
  - openpyxl
  - numpy

### Installation

1. Clone or download the project
2. Navigate to the `src` directory
3. Install dependencies: `pip install -r ../requirements.txt`

### Running the Application

#### 🟢 Method 1: Direct Streamlit Command (RECOMMENDED)
```bash
cd src
streamlit run scope_of_supply_analyzer.py
```
This is the most reliable method as it lets Streamlit handle port selection automatically.

#### 🟡 Method 2: Simple Python Runner
```bash
cd src
python run_simple.py
```

#### 🟡 Method 3: Simple Windows Batch File
```bash
cd src
run_simple.bat
```

#### 🔴 Method 4: Advanced Python Runner (May have port issues on Windows)
```bash
cd src
python run_unified_app.py
```

#### 🔴 Method 5: Advanced Windows Batch File (May have port issues on Windows)
```bash
cd src
run_unified_app.bat
```

The application will open in your default web browser. Streamlit will display the URL in the terminal.

## 📋 How to Use

### 1. Select Operation Mode

Upon launching the application, you'll see a welcome screen with four operation options in the sidebar:

- Choose your desired operation mode using the radio button selector
- Each mode has different file upload requirements and analysis capabilities

### 2. Upload Files

#### For Analysis Modes (Single File):
- Click "Choose file" in the sidebar
- Select your Excel file (.xlsx, .xls, .xlsm)
- The application will automatically process the file upon upload

#### For Comparison Modes (Two Files):
- Upload the first file using "Choose first file"
- Upload the second file using "Choose second file"
- Both files must be uploaded before comparison can begin

### 3. Navigate Analysis Views

#### Analysis Mode:
- Use the sidebar navigation to explore different analysis views
- Each view provides specific insights into your data
- Views adapt based on file type (PRE vs Profittabilita)

#### Comparison Mode:
- Select comparison views from the sidebar radio buttons
- Each view highlights different aspects of the file differences
- Visual charts and tables show side-by-side comparisons

### 4. Export Results

- In analysis mode, use the export section to download processed data as JSON
- Comparison results can be explored interactively within the application

### 5. Reset and Start Over

- Use the "🔄 Reset Analysis" button to clear all data and return to the initial state
- This allows you to switch between different operation modes or load new files

## 📊 Status Indicators

The sidebar includes a status section that shows:

### Analysis Mode:
- **File**: ✅ Loaded / ❌ Not loaded
- **Analysis**: ✅ Ready / ❌ Not ready

### Comparison Mode:
- **File 1**: ✅ Loaded / ❌ Not loaded
- **File 2**: ✅ Loaded / ❌ Not loaded
- **Comparison**: ✅ Ready / ❌ Not ready

## 🔧 Technical Architecture

### Components

- **scope_of_supply_analyzer.py**: Main application controller with unified interface
- **components/file_processor.py**: File upload and processing logic
- **components/ui_components.py**: Reusable UI elements
- **components/analyzers/**: Analysis and comparison classes
  - `pre_analyzer.py`: PRE file analysis
  - `profittabilita_analyzer.py`: Profitability file analysis
  - `pre_comparator.py`: PRE file comparison
  - `profittabilita_comparator.py`: Profitability file comparison
- **parsers/**: File parsing logic
  - `pre_file_parser.py`: PRE file parsing
  - `analisi_profittabilita_parser.py`: Profitability file parsing

### Session State Management

The application uses Streamlit session state to maintain:
- Current operation mode
- Loaded data and file types
- View selections and navigation state
- Analyzer and comparator instances

## 🎨 User Interface Features

### Responsive Design
- Wide layout for optimal screen utilization
- Sidebar-based navigation and controls
- Expandable sections for detailed information

### Visual Elements
- Color-coded status indicators
- Progress spinners during file processing
- Interactive charts and visualizations
- Comprehensive data tables with sorting and filtering

### Error Handling
- Graceful error messages with detailed information
- File format validation
- Automatic retry mechanisms for file processing

## 🔍 Troubleshooting

### Common Issues

1. **Port Permission Errors on Windows (Error 10013)**
   - **Solution 1**: Use the direct Streamlit command: `streamlit run scope_of_supply_analyzer.py`
   - **Solution 2**: Run Command Prompt as Administrator
   - **Solution 3**: Try a specific port: `streamlit run scope_of_supply_analyzer.py --server.port 8502`
   - **Solution 4**: Restart your computer to clear port locks

2. **Import Errors**
   - Ensure you're running from the `src` directory
   - Check that all required packages are installed: `pip install -r ../requirements.txt`
   - Verify Python path configuration

3. **File Processing Errors**
   - Verify file format (Excel .xlsx, .xls, .xlsm)
   - Check file structure matches expected format
   - Ensure file is not corrupted or password-protected

4. **Memory Issues with Large Files**
   - Close other applications to free memory
   - Try processing smaller file sections
   - Consider upgrading system memory

5. **Application Won't Start**
   - Check if another Streamlit app is running
   - Kill Python processes: `taskkill /f /im python.exe` (Windows)
   - Try different port: `streamlit run scope_of_supply_analyzer.py --server.port 8502`

### Debug Information

The application includes debug information in the sidebar showing:
- Session state variables
- Current operation mode
- Loaded data status
- Error details when issues occur

### Windows-Specific Solutions

If you encounter port permission errors on Windows:

1. **Use the basic command**:
   ```bash
   cd src
   streamlit run scope_of_supply_analyzer.py
   ```

2. **Try with a specific port**:
   ```bash
   streamlit run scope_of_supply_analyzer.py --server.port 8502
   ```

3. **Run as Administrator**:
   - Right-click Command Prompt or PowerShell
   - Select "Run as administrator"
   - Navigate to the src directory and run the command

4. **Alternative launch methods**:
   ```bash
   # Let Streamlit choose the port automatically
   python -m streamlit run scope_of_supply_analyzer.py
   
   # Or use the simple runner
   python run_simple.py
   ```

## 📈 Performance Considerations

### File Size Limits
- Recommended maximum file size: 50MB
- Large files may require additional processing time
- Memory usage scales with file complexity

### Browser Compatibility
- Tested with Chrome, Firefox, Edge
- JavaScript must be enabled
- Recommended minimum screen resolution: 1024x768

## 🔄 Updates and Maintenance

### Version History
- v1.0: Initial unified application release
- Integrated analysis and comparison capabilities
- Comprehensive error handling and user feedback

### Future Enhancements
- Additional file format support
- Enhanced visualization options
- Batch processing capabilities
- Advanced filtering and search features

## 📞 Support

For technical support or feature requests:

1. **First, try the direct method**: `streamlit run scope_of_supply_analyzer.py`
2. Check this documentation, especially the troubleshooting section
3. Review error messages and debug information
4. Verify file format and structure requirements
5. Contact the development team with specific error details

## 💡 Quick Start Guide

**If you just want to run the application quickly:**

1. Open Command Prompt or PowerShell
2. Navigate to the `src` directory
3. Run: `streamlit run scope_of_supply_analyzer.py`
4. The application will open in your browser
5. Select your operation mode and upload your files

---

**Note**: This unified application replaces the separate analysis and comparison tools, providing a single interface for all Excel analysis and comparison needs. The direct Streamlit command is the most reliable way to launch the application. 
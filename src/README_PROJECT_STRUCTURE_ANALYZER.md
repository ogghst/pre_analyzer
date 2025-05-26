# 🏗️ Project Structure Analyzer

**Comprehensive Project Structure Analysis Tool for Industrial Equipment Files**

The Project Structure Analyzer is a unified application that provides comprehensive analysis, comparison, and cross-validation capabilities for industrial equipment project files, specifically PRE quotations and Analisi Profittabilita elaborations.

## 🎯 Overview

This tool addresses the critical need for quality assurance and validation in industrial project management by providing:

- **Single File Analysis**: Deep dive into individual PRE or Profittabilita files
- **File Comparison**: Side-by-side comparison of similar file types
- **Cross-File Analysis**: Advanced cross-validation between PRE quotations and Profittabilita elaborations
- **Performance Optimization**: Intelligent caching to prevent re-parsing on view changes
- **WBE Impact Assessment**: Specialized analysis for Work Breakdown Element impacts

## 📋 Available Operations

### 📊 Single File Analysis

#### PRE File Analysis
- **Project Summary**: Overview of quotation parameters and structure
- **Tree Structure**: Hierarchical visualization of product groups and categories
- **Groups Analysis**: Detailed breakdown by product groups
- **Categories Analysis**: Category-level analysis with metrics
- **Items Analysis**: Individual item examination with filtering
- **Financial Analysis**: Margin calculations, cost breakdowns, and profitability metrics

#### Analisi Profittabilita Analysis
- **Project Summary**: Overview of profitability structure and WBE organization
- **Tree Structure**: Hierarchical view of WBE and cost elements
- **Groups Analysis**: Product group breakdown with profitability metrics
- **Categories Analysis**: Category-level profitability analysis
- **Items Analysis**: Item-level cost and margin analysis
- **Profitability Analysis**: Comprehensive margin and cost analysis
- **UTM Analysis**: Manufacturing time tracking and analysis
- **WBE Analysis**: Work Breakdown Element cost aggregation
- **Field Analysis**: Usage statistics and data completeness metrics

### 🔄 File Comparison

#### PRE File Comparison
- **Project Comparison**: High-level project parameter comparison
- **Financial Comparison**: Detailed financial difference analysis
- **Groups Comparison**: Product group variance analysis
- **Categories Comparison**: Category-level change detection
- **Items Comparison**: Item-by-item comparison with configurable thresholds
- **Summary Report**: Automated insights and recommendations

#### Profittabilita File Comparison
- **Project Comparison**: Project-level profitability comparison
- **Profitability Comparison**: Margin and cost variance analysis
- **Groups Comparison**: Product group profitability changes
- **Categories Comparison**: Category-level profitability variance
- **Items Comparison**: Item-level cost and margin comparison
- **WBE Comparison**: Work Breakdown Element comparison
- **Cost Elements Comparison**: Detailed cost component analysis
- **UTM Comparison**: Manufacturing time variance analysis
- **Engineering Comparison**: Engineering cost comparison
- **Types Comparison**: Equipment type analysis
- **Summary Report**: Comprehensive comparison insights

### 🔗 Cross-File Analysis (PRE vs Profittabilita)

#### Executive Summary
- High-level metrics and key performance indicators
- Risk assessment and recommendations
- Critical issue identification
- Project health overview

#### Data Consistency Check
- Item-by-item validation between files
- Missing item identification
- Data integrity verification
- Consistency statistics and metrics

#### WBE Impact Analysis
- Work Breakdown Element impact assessment
- Margin change analysis by WBE
- Risk categorization for WBEs
- Cost variance tracking

#### Pricelist Comparison
- Financial comparison by product groups
- Visual charts and trend analysis
- Variance detection and categorization
- Impact assessment on project profitability

#### Missing Items Analysis
- Bidirectional analysis of missing items
- Impact assessment of missing elements
- Recommendations for data completion
- Export capabilities for missing item lists

#### Financial Impact Assessment
- Comprehensive financial risk evaluation
- Automated risk categorization
- Visual impact representation
- Variance threshold analysis

#### Project Structure Analysis
- Structure mapping between PRE and Profittabilita
- Consistency metrics and coverage analysis
- Complexity indicators
- Structural optimization recommendations

#### Detailed Item Comparison
- Granular item-by-item analysis
- Advanced filtering and sorting capabilities
- Export functionality for detailed reports
- Custom comparison criteria

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** with pip
- **Required packages**: streamlit, pandas, plotly, openpyxl, xlrd
- **Supported file formats**: .xlsx, .xls, .xlsm

### Installation

1. **Clone or download** the project files
2. **Navigate** to the `src` directory
3. **Install dependencies** (if not already installed):
   ```bash
   pip install streamlit pandas plotly openpyxl xlrd
   ```

### Launch Options

#### Option 1: Simple Launcher (Recommended)
```bash
# Windows
run_project_analyzer.bat

# Python (any OS)
python run_project_analyzer.py
```

#### Option 2: Direct Streamlit Launch
```bash
streamlit run scope_of_supply_analyzer.py
```

#### Option 3: Alternative Entry Point
```bash
python streamlit_app.py
```

## 🎮 How to Use

### 1. Select Operation Mode
- Choose from 5 available operation modes in the sidebar
- Each mode provides specialized functionality for different analysis needs

### 2. Upload Files
- **Single File Analysis**: Upload one file of the appropriate type
- **File Comparison**: Upload two files of the same type
- **Cross-File Analysis**: Upload one PRE file and one Profittabilita file

### 3. Explore Analysis
- Navigate through different analysis views using the sidebar menu
- Each view provides specialized insights and visualizations
- Use interactive filters and controls to customize the analysis

### 4. Export Results
- Download processed data as CSV files (analysis mode)
- Export detailed comparison reports
- Save visualizations and charts

### 5. Reset and Switch
- Use the reset button to start over with new files
- Switch between operation modes without restarting the application

## ✨ Key Features

### Performance Optimization
- **Intelligent Caching**: Files are parsed once and cached for subsequent view changes
- **Analyzer Caching**: Analysis objects are cached to prevent re-computation
- **Session State Management**: Efficient state management for smooth user experience

### Advanced Analytics
- **Configurable Thresholds**: Customize difference detection sensitivity
- **Visual Comparisons**: Interactive charts and graphs using Plotly
- **Statistical Analysis**: Comprehensive metrics and statistical insights
- **Risk Assessment**: Automated risk categorization and alerts

### User Experience
- **Intuitive Interface**: Clean, modern UI with logical navigation
- **Real-time Feedback**: Progress indicators and status updates
- **Error Handling**: Comprehensive error handling with helpful messages
- **Responsive Design**: Works well on different screen sizes

### Export Capabilities
- **CSV Downloads**: Export detailed data for further analysis
- **Report Generation**: Automated summary reports
- **Chart Export**: Save visualizations for presentations
- **Filtered Data**: Export only relevant subsets of data

## 📊 Supported File Types

### PRE Quotation Files
- Standard quotation structure with project parameters
- Product groups, categories, and items hierarchy
- Financial data including costs, margins, and pricing
- Customer and project information

### Analisi Profittabilita Files
- 81+ column profitability analysis format
- Work Breakdown Element (WBE) structure
- UTM (Unità di Tempo Macchina) time tracking
- Cost elements and engineering data
- Manufacturing and equipment type information

## 🔧 Technical Architecture

### Modular Design
- **`scope_of_supply_analyzer.py`**: Main unified application controller
- **`components/file_processor.py`**: File upload and parsing logic
- **`components/ui_components.py`**: Reusable UI elements and styling
- **`components/analyzers/`**: Analysis and comparison engines
- **`parsers/`**: File format processors

### Analysis Engines
- **`pre_analyzer.py`**: PRE quotation analysis
- **`profittabilita_analyzer.py`**: Analisi Profittabilita analysis
- **`pre_comparator.py`**: PRE file comparison
- **`profittabilita_comparator.py`**: Profitability file comparison
- **`pre_profittabilita_comparator.py`**: Cross-file comparison

### File Parsers
- **`pre_file_parser.py`**: PRE file parsing and data extraction
- **`analisi_profittabilita_parser.py`**: Profitability file parsing

## 🛠️ Troubleshooting

### Common Issues

#### Import Errors
- Ensure all required packages are installed
- Check Python version compatibility (3.8+)
- Verify file paths and directory structure

#### File Processing Errors
- Ensure files are in supported formats (.xlsx, .xls, .xlsm)
- Check file structure matches expected format
- Verify files are not corrupted or password-protected

#### Performance Issues
- Large files may take time to process initially
- Subsequent view changes should be fast due to caching
- Consider closing other applications if memory is limited

#### Browser Issues
- Try refreshing the browser page
- Clear browser cache if experiencing display issues
- Use a modern browser (Chrome, Firefox, Edge)

### Getting Help

If you encounter issues:

1. **Check the console output** for error messages
2. **Verify file formats** match the expected structure
3. **Try with smaller test files** to isolate issues
4. **Check system requirements** and dependencies

## 📈 Performance Tips

### For Large Files
- Allow extra time for initial file processing
- Use the caching benefits for multiple view explorations
- Consider analyzing subsets of data for very large files

### For Multiple Analyses
- Keep the application running to benefit from caching
- Use the reset function only when switching to completely different files
- Take advantage of the unified interface to switch between operation modes

### For Best Results
- Ensure files follow the expected structure and format
- Use consistent naming conventions in your files
- Regularly update to the latest version for performance improvements

## 🎯 Use Cases

### Quality Assurance
- Validate data consistency between quotation and elaboration phases
- Identify missing or mismatched items before project submission
- Ensure financial accuracy across project documents

### Project Management
- Track changes between different versions of project files
- Assess impact of modifications on project profitability
- Monitor WBE cost allocation and margin distribution

### Financial Analysis
- Analyze project profitability and cost structure
- Identify high-risk elements requiring attention
- Compare financial performance across different projects

### Process Optimization
- Identify structural inconsistencies for process improvement
- Optimize WBE organization for better cost tracking
- Streamline data flow between quotation and elaboration phases

---

**🎉 Ready to analyze your project structure? Launch the application and start exploring!** 
# Analisi Profittabilita File Comparator

A specialized tool for comparing two Analisi Profittabilita files and analyzing differences in Work Breakdown Elements (WBE), cost components, UTM elements, and equipment types.

## 🎯 Overview

The Analisi Profittabilita Comparator is designed specifically for analyzing differences between two profitability analysis files. It provides comprehensive insights into:

- **WBE (Work Breakdown Elements)** comparison and analysis
- **Cost Elements** breakdown including UTM, UTE, Engineering, Manufacturing costs
- **UTM Time Tracking** differences (Robot, LGV, Intra, Layout)
- **Engineering Components** analysis (UTE, BA, Software PC/PLC/LGV)
- **Equipment Types** and categories comparison
- **Financial Impact** analysis with margin calculations

## 🚀 Quick Start

### Method 1: Windows Batch File (Recommended for Windows)
```bash
# Double-click or run from command prompt
run_profittabilita_comparator.bat
```

### Method 2: Python Runner Script
```bash
python run_profittabilita_comparator.py
```

### Method 3: Direct Streamlit Launch
```bash
streamlit run profittabilita_comparator_app.py --server.port 8502
```

## 📋 Requirements

### Python Dependencies
```
streamlit>=1.28.0
pandas>=1.5.0
plotly>=5.15.0
openpyxl>=3.1.0
numpy>=1.24.0
```

### Install Dependencies
```bash
pip install streamlit pandas plotly openpyxl numpy
```

## 🔍 Comparison Views

### 1. Project Comparison
- Side-by-side project parameters
- Financial totals comparison
- Currency and exchange rate differences
- Structural overview (groups, items count)

### 2. Profitability Comparison
- Cost vs. margin analysis
- Profitability metrics comparison table
- Interactive pie charts for both files
- Margin difference visualization

### 3. WBE Comparison
- Work Breakdown Elements analysis
- Common vs. unique WBE identification
- Cost differences by WBE
- Interactive threshold filtering
- Top differences visualization

### 4. Cost Elements Comparison
- Comprehensive cost breakdown analysis:
  - **Material Costs**
  - **UTM Costs** (Robot, LGV, Intra, Layout)
  - **Engineering Costs** (UTE, BA)
  - **Software Costs** (PC, PLC, LGV)
  - **Manufacturing Costs** (Mechanical, Electrical)
  - **Testing Costs** (Collaudo)
  - **Project Management**
  - **Installation, Documentation, After Sales**

### 5. UTM Comparison
- Focus on UTM time tracking elements:
  - UTM Robot
  - UTM LGV
  - UTM Intra
  - UTM Layout
- Side-by-side distribution charts
- Difference analysis with visual indicators

### 6. Engineering Comparison
- Engineering costs breakdown:
  - UTE (Engineering hours)
  - BA (Business Analysis)
  - Software PC
  - Software PLC
  - Software LGV
- Grouped bar chart comparisons

### 7. Types Comparison
- Equipment and category types analysis
- Group types identification and comparison
- Category types breakdown
- Common vs. unique types highlighting

### 8. Summary Report
- Executive summary with key metrics
- Structural comparison overview
- Cost analysis summary
- Key insights and automated recommendations
- Action items and next steps

## 🎨 Key Features

### Interactive Filtering
- **Cost threshold filtering** for WBE comparison
- **Significance thresholds** for highlighting important differences
- **Dynamic charts** that update based on selections

### Visual Analytics
- **Side-by-side charts** for easy comparison
- **Pie charts** for cost composition analysis
- **Bar charts** for categorical comparisons
- **Color-coded differences** (red/blue scale for positive/negative changes)
- **Gauge charts** for margin analysis

### Smart Analysis
- **Automated difference detection** with configurable thresholds
- **Financial impact calculation** for all cost elements
- **Equipment type extraction** from naming conventions
- **Margin percentage analysis** with benchmark comparisons

### Export and Reporting
- **Comprehensive summary reports** with actionable insights
- **Data tables** with sortable columns
- **Visual charts** for presentation purposes

## 🏗️ Technical Architecture

### Data Flow
```
Analisi Profittabilita Files (.xlsx)
    ↓
analisi_profittabilita_parser.py (parsing)
    ↓
ProfittabilitaComparator (analysis)
    ↓
Streamlit UI Components (visualization)
    ↓
Interactive Web Interface
```

### Core Components

#### ProfittabilitaComparator Class
- **Data Processing**: Extracts and structures WBE, cost elements, and type data
- **Comparison Logic**: Identifies differences with configurable thresholds
- **Financial Analysis**: Calculates margins, differences, and impacts
- **Visualization**: Generates charts and tables for each comparison view

#### Cost Element Extraction
The comparator analyzes these cost categories:
- **Material**: Direct material costs (MAT field)
- **UTM Elements**: Time tracking costs for Robot, LGV, Intra, Layout
- **Engineering**: UTE and BA engineering costs
- **Software**: PC, PLC, and LGV software development costs
- **Manufacturing**: Mechanical and Electrical manufacturing costs
- **Testing**: Various testing and validation costs (Collaudo)
- **Project Management**: PM costs and hours
- **Others**: Installation, Documentation, After Sales

#### WBE Analysis
- **WBE Identification**: Extracts Work Breakdown Elements from categories
- **Financial Aggregation**: Sums costs and margins by WBE
- **Difference Detection**: Identifies unique and common WBEs
- **Impact Analysis**: Calculates financial impact of WBE differences

#### Types Classification
Equipment types are automatically classified based on naming patterns:
- **Robot/AGV**: Robotic and automated guided vehicle systems
- **Conveyor**: Conveyor and belt systems
- **Storage**: Warehouse and storage systems
- **Software**: Software components and applications
- **Mechanical**: Mechanical systems and components
- **Electrical**: Electrical systems and components
- **Installation**: Installation and setup services
- **Service**: Maintenance and service components
- **Other**: Unclassified components

## 🔧 Configuration

### Port Configuration
The application runs on port 8502 by default to avoid conflicts with the main PRE analyzer (port 8501).

### Threshold Settings
- **Cost difference threshold**: €1,000 (configurable via slider in WBE comparison)
- **Percentage difference threshold**: 0.1% for margin comparisons
- **Significance threshold**: €100 for cost element differences

### Chart Settings
- **Color scheme**: Red-Blue diverging scale for differences
- **Chart height**: 400-500px for optimal viewing
- **Interactive features**: Hover tooltips, zoom, pan

## 🚨 Troubleshooting

### Common Issues

#### 1. File Upload Errors
```
Error: "Error processing file"
```
**Solution**:
- Ensure file is a valid Analisi Profittabilita Excel file
- Check file format (.xlsx, .xls, .xlsm)
- Verify file is not corrupted or password-protected

#### 2. Parser Import Error
```
Error: "No module named 'analisi_profittabilita_parser'"
```
**Solution**:
- Ensure `analisi_profittabilita_parser.py` exists in the same directory
- Check that the parser module is properly configured

#### 3. Missing Dependencies
```
Error: "No module named 'plotly'"
```
**Solution**:
```bash
pip install plotly streamlit pandas openpyxl numpy
```

#### 4. Port Already in Use
```
Error: "Port 8502 is already in use"
```
**Solution**:
- Change port in runner script or use different port:
```bash
streamlit run profittabilita_comparator_app.py --server.port 8503
```

#### 5. Streamlit Not Found
```
Error: "streamlit is not recognized"
```
**Solution**:
- Use Python module approach:
```bash
python -m streamlit run profittabilita_comparator_app.py
```

### Performance Optimization

For large files (>1000 items):
- Use cost threshold filtering to focus on significant differences
- Process files incrementally if memory issues occur
- Consider data aggregation for initial overview

## 📝 Usage Examples

### Example 1: Basic Comparison
1. Launch the application
2. Upload two Analisi Profittabilita files
3. Start with "Project Comparison" for overview
4. Navigate to "WBE Comparison" for detailed analysis
5. Use "Summary Report" for final insights

### Example 2: Cost Analysis Focus
1. Upload files and go to "Cost Elements Comparison"
2. Review the pie charts for major cost distribution differences
3. Check "UTM Comparison" for time tracking differences
4. Analyze "Engineering Comparison" for development cost changes

### Example 3: Threshold-Based Analysis
1. Go to "WBE Comparison"
2. Adjust the cost difference threshold slider
3. Focus on WBEs with significant cost impacts
4. Export findings to summary report

## 🤝 Integration

### With Main PRE Analyzer
The Profittabilita Comparator can be accessed from the main PRE analyzer interface via the dedicated button, providing seamless workflow integration.

### With Existing Parsers
Uses the same parsing infrastructure as the main analyzer, ensuring consistency in data interpretation and field mapping.

## 📈 Future Enhancements

Planned features for future versions:
- **Export to PDF/Excel** functionality
- **Batch comparison** for multiple file pairs
- **Historical trend analysis** across multiple versions
- **Custom threshold profiles** for different analysis scenarios
- **API integration** for automated comparison workflows
- **Advanced filtering** by equipment type, cost category, or WBE
- **Collaboration features** for team analysis and commenting

---

## 📞 Support

For technical support or feature requests:
1. Check this documentation for common solutions
2. Review the troubleshooting section
3. Ensure all dependencies are properly installed
4. Verify file formats and data structure compliance

The Analisi Profittabilita Comparator is designed to provide comprehensive insights into cost structure differences and support data-driven decision making in profitability analysis. 
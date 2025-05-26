# PRE File Comparator 🔄

A powerful Streamlit application for comparing two PRE quotation files and analyzing differences in project parameters, financial breakdowns, groups, categories, and items.

## 📋 Overview

The PRE File Comparator is designed to help users identify differences between two versions of PRE quotation files. It provides comprehensive analysis across multiple dimensions including:

- Project parameters comparison
- Financial breakdown analysis
- Product groups comparison
- Categories analysis
- Items statistics
- Summary reports with insights and recommendations

## 🚀 Quick Start

### Prerequisites
Make sure you have Streamlit installed:
```bash
pip install streamlit
```

### Running the Comparator

**Option 1: Use the runner script (Recommended)**
```bash
cd src/pre_file
python run_comparator.py
```

**Option 2: Windows batch file (Windows users)**
```cmd
cd src/pre_file
run_comparator.bat
```

**Option 3: Direct Streamlit command**
```bash
cd src/pre_file
streamlit run pre_comparator_app.py
```

**Option 4: Python module method (if streamlit command not in PATH)**
```bash
cd src/pre_file
python -m streamlit run pre_comparator_app.py
```

**Option 5: From any directory**
```bash
# From the project root
cd src/pre_file && python -m streamlit run pre_comparator_app.py
```

The application will automatically open in your default browser at `http://localhost:8501`

### Using the Comparator

1. **Upload Files**: Use the sidebar to upload two PRE quotation files (.xlsx, .xls, or .xlsm)
2. **Select Views**: Choose from different comparison views in the sidebar navigation
3. **Analyze**: Review the differences and insights provided by each comparison view

## 🔍 Comparison Views

### 1. Project Comparison
- Side-by-side comparison of project parameters
- Key metrics comparison (currency, exchange rates, percentages)
- Structural differences (number of groups, items)
- Financial totals comparison

### 2. Financial Comparison
- Detailed financial breakdown comparison
- Side-by-side pie charts
- Difference visualization (absolute and percentage)
- Financial impact analysis

### 3. Groups Comparison
- Product groups analysis
- Common vs unique groups identification
- Value differences visualization
- Group-level statistics

### 4. Categories Comparison
- Category-level analysis
- Filterable differences by value threshold
- Top differences visualization
- Category uniqueness analysis

### 5. Items Comparison
- High-level items statistics
- Total counts and values comparison
- Average and maximum item values
- Statistical differences summary

### 6. Summary Report
- Executive summary with key metrics
- Structural comparison overview
- Automated insights and recommendations
- Key differences highlighting

## 📊 Features

### ✅ Visual Components
- **Side-by-side metrics**: Easy comparison of key values
- **Interactive charts**: Plotly-powered visualizations
- **Difference highlighting**: Clear identification of changes
- **Progress indicators**: Real-time processing feedback

### ✅ Analysis Capabilities
- **Automatic difference detection**: Smart identification of changes
- **Financial impact analysis**: Understand monetary implications
- **Threshold filtering**: Focus on significant differences
- **Statistical summaries**: Comprehensive data overview

### ✅ User Experience
- **Intuitive interface**: Clean, modern design
- **Error handling**: Robust error reporting and recovery
- **Status indicators**: Clear feedback on upload and processing status
- **Responsive design**: Works on different screen sizes

## 🏗️ Architecture

### Components Structure

```
src/pre_file/
├── components/
│   ├── analyzers/
│   │   ├── pre_comparator.py      # Main comparator class
│   │   ├── pre_analyzer.py        # Single file analyzer
│   │   ├── base_analyzer.py       # Base analyzer interface
│   │   └── __init__.py            # Package exports
│   ├── file_processor.py          # File handling utilities
│   ├── ui_components.py           # UI component library
│   └── field_constants.py         # Field name constants
├── pre_comparator_app.py          # Main comparator application
├── run_comparator.py              # Runner script
└── README_COMPARATOR.md           # This documentation
```

### Key Classes

#### `PreComparator`
The main comparator class that handles:
- Data initialization for two files
- Comparison view management
- Difference calculation and analysis
- Visualization rendering

#### `PreComparatorApp`
The Streamlit application class that manages:
- File upload and processing
- Navigation and state management
- UI rendering and error handling
- User interaction flow

## 🔧 Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **NumPy**: Numerical computations
- **Custom parsers**: PRE file parsing utilities

### Data Processing
1. **File Upload**: Streamlit file uploader with validation
2. **Parsing**: Custom PRE parser converts Excel to structured JSON
3. **Comparison**: Field-by-field comparison with difference calculation
4. **Visualization**: Dynamic chart generation based on data differences

### Error Handling
- File format validation
- Parsing error recovery
- Missing data handling
- User-friendly error messages

## 💡 Usage Tips

### Best Practices
1. **File Naming**: Use descriptive names for easier identification
2. **Version Control**: Compare files with clear version differences
3. **Focus Areas**: Use threshold filtering to focus on significant changes
4. **Export Results**: Take screenshots or notes for documentation

### Common Use Cases
- **Version Comparison**: Compare different versions of the same quotation
- **Proposal Analysis**: Analyze changes between initial and final proposals
- **Quality Assurance**: Verify that updates were applied correctly
- **Financial Review**: Understand cost implications of changes

### Troubleshooting

#### Common Issues

**"Streamlit is not installed" error:**
```bash
pip install streamlit
```

**"Could not find pre_comparator_app.py" error:**
Make sure you're in the correct directory:
```bash
cd src/pre_file
```

**File upload errors:**
- Ensure files are genuine PRE quotation files (.xlsx, .xls, .xlsm)
- Check file size (very large files may take longer to process)

**Browser issues:**
- Try refreshing the page
- Clear browser cache
- Try a different browser
- Check if the URL is `http://localhost:8501`

**Application doesn't start:**
- Check if port 8501 is already in use
- Try running with a different port: `streamlit run pre_comparator_app.py --server.port 8502`

## 🛠️ Customization

### Adding New Comparison Views
To add a new comparison view:

1. Add the view name to `get_comparison_views()` in `PreComparator`
2. Implement the display method (e.g., `display_new_view()`)
3. Add the view case in `render_comparison_view()` in `PreComparatorApp`

### Modifying Visualizations
Charts can be customized by modifying the Plotly configurations in the respective display methods.

### Extending Analysis
Add new analysis methods to the `PreComparator` class following the existing pattern.

## 📝 Contributing

When contributing to the comparator:

1. Follow the existing code structure and naming conventions
2. Add appropriate error handling for new features
3. Include docstrings for new methods
4. Test with various PRE file formats
5. Update this documentation for new features

## 🔗 Related Files

- **Single File Analysis**: Use `streamlit_app_refactored.py` for analyzing individual files
- **Parser Documentation**: See `README.md` for PRE file parsing details
- **Field Constants**: Reference `field_constants.py` for available data fields

## 📞 Support

For issues or questions:
1. Check the error messages and details in the Streamlit interface
2. Verify file formats and structure are correct
3. Review this troubleshooting section
4. Check existing code comments and docstrings
5. Ensure all dependencies are properly installed

### Getting Help

If you encounter issues:
1. **Check the terminal output** for error messages
2. **Look at the Streamlit interface** for error details (often in expandable sections)
3. **Verify your files** are properly formatted PRE quotation files
4. **Check your environment** has all required dependencies installed 
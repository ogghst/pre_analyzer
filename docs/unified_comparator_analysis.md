# Unified Comparator Analysis

## Overview

The Unified Comparator is a comprehensive comparison tool that can analyze two quotation files parsed by the unified parser. It provides detailed analysis of differences, missing items, financial impact, and WBE (Work Breakdown Element) structure changes.

## Features

### 🔄 Universal Compatibility
- Works with any combination of PRE files and Analisi Profittabilita files
- Automatic file type detection via unified parser
- Handles different data structures seamlessly

### 📊 Comprehensive Analysis Views

#### 1. Executive Summary
- High-level overview of differences and recommendations
- Key metrics and financial impact summary
- Actionable recommendations based on analysis

#### 2. Data Consistency Check
- Item-by-item consistency analysis
- Visual pie chart of comparison results
- Detailed issues table with export functionality
- NumberColumn formatting for better readability

#### 3. WBE Impact Analysis
- Analysis of how changes affect Work Breakdown Elements
- Visual charts showing listino and margin impact
- High-impact WBE alerts (>10% margin changes)
- Detailed breakdown of items added, removed, and modified

#### 4. Pricelist Comparison
- Financial comparison by product groups
- Interactive bar charts and visualizations
- Percentage difference calculations
- Group-by-group analysis

#### 5. Missing Items Analysis
- Items present in one file but not the other
- Total value calculations for missing items
- Export functionality for detailed analysis
- Separate analysis for each file

#### 6. Detailed Item Comparison
- Comprehensive item-by-item comparison
- Advanced filtering by status, WBE, and other criteria
- Sortable results with multiple options
- Export functionality for filtered results

### 💰 Financial Analysis
- Total value comparisons
- Percentage difference calculations
- Margin impact analysis
- Cost structure analysis

### 📈 Visual Analytics
- Interactive Plotly charts
- Color-coded visualizations
- Scatter plots for margin analysis
- Bar charts for value comparisons

## Usage

### Basic Usage

```python
from parsers.unified_parser import parse_quotation_file
from components.analyzers.unified_comparator import UnifiedComparator

# Parse two files
first_quotation = parse_quotation_file("first_file.xlsx")
second_quotation = parse_quotation_file("second_file.xlsx")

# Create comparator
comparator = UnifiedComparator(
    first_quotation=first_quotation,
    second_quotation=second_quotation,
    first_name="First File",
    second_name="Second File"
)

# Display analysis
comparator.display_executive_summary()
comparator.display_data_consistency_check()
comparator.display_wbe_impact_analysis()
```

### Streamlit Integration

```python
import streamlit as st
from components.analyzers.unified_comparator import UnifiedComparator

# File upload
first_file = st.file_uploader("Upload first file", type=['xlsx', 'xls'])
second_file = st.file_uploader("Upload second file", type=['xlsx', 'xls'])

if first_file and second_file:
    # Parse files
    first_quotation = parse_quotation_file(first_file.name)
    second_quotation = parse_quotation_file(second_file.name)
    
    # Create comparator
    comparator = UnifiedComparator(
        first_quotation=first_quotation,
        second_quotation=second_quotation,
        first_name=first_file.name,
        second_name=second_file.name
    )
    
    # Display views
    view = st.selectbox("Select view", comparator.get_comparison_views())
    
    if view == "Executive Summary":
        comparator.display_executive_summary()
    elif view == "Data Consistency Check":
        comparator.display_data_consistency_check()
    # ... other views
```

## Key Features

### NumberColumn Formatting
All numeric columns in tables are formatted using Streamlit's NumberColumn for better readability:
- Currency values: `€%.2f`
- Percentages: `%.2f%%`
- Integers: `%d`
- Quantities: `%.2f`

### Export Functionality
- CSV export for detailed analysis
- Filtered results export
- Missing items export
- Issues export

### Interactive Filtering
- Filter by comparison status
- Filter by WBE
- Sort by various criteria
- Real-time filtering

### Visual Analytics
- Pie charts for comparison results
- Bar charts for value comparisons
- Scatter plots for margin analysis
- Color-coded visualizations

## Comparison Logic

### Item Matching
- Items are matched by their unique codes
- Automatic detection of missing items
- Value comparison with tolerance for rounding differences

### Financial Analysis
- Total value calculations
- Percentage difference analysis
- Margin impact assessment
- Cost structure comparison

### WBE Impact
- Work Breakdown Element analysis
- Items added, removed, and modified
- Financial impact on each WBE
- Margin percentage changes

## Error Handling

The comparator includes robust error handling:
- Safe float conversion for numeric values
- Graceful handling of missing data
- Clear error messages for debugging
- Fallback values for missing fields

## Performance

- Efficient item mapping for fast lookups
- Optimized data structures
- Minimal memory usage
- Fast comparison algorithms

## Example Output

### Executive Summary
```
📊 Unified Quotation Comparison - Executive Summary

Data Consistency: 45/67 (67.2% match)
Items Missing in Second: 12 (Items to add)
Items with Differences: 10 (Items to review)
WBEs Affected: 3 out of 8 total

💰 Financial Impact Summary
First File Total: €125,000.00
Second File Total: €118,500.00
Difference: €6,500.00 (+5.5%)

🎯 Key Recommendations
• Add 12 missing items to Second File
• Review and reconcile 10 items with value differences
• Investigate significant financial difference of 5.5%
```

## Integration

The Unified Comparator integrates seamlessly with:
- Unified Parser for file parsing
- Streamlit for web interface
- Plotly for visualizations
- Pandas for data manipulation
- Export functionality for detailed analysis

## Future Enhancements

- Additional visualization types
- More detailed financial analysis
- Batch comparison capabilities
- Advanced filtering options
- Custom comparison criteria 
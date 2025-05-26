# 📊 Excel Quotation Analyzer - Streamlit Application

Interactive web application for processing and visualizing industrial equipment quotations from Excel files.

## 🚀 Quick Start

### Option 1: Using the Launcher Script
```bash
cd src/pre_file
python run_app.py
```

### Option 2: Direct Streamlit Command
```bash
cd src/pre_file
streamlit run streamlit_app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 🌟 Features

### 📤 File Upload & Processing
- **Drag & Drop Interface**: Easy file upload with visual feedback
- **Format Support**: Excel files (`.xlsx`, `.xls`) in PRE_ONLY_OFFER format
- **Real-time Processing**: Live progress indicators during file processing
- **Error Handling**: Comprehensive error messages and troubleshooting

### 🌳 Interactive Tree Structure
- **Hierarchical View**: Expandable tree showing Groups → Categories → Items
- **Value Visualization**: Each level shows associated monetary values
- **Quick Navigation**: Click to expand/collapse sections
- **Search Integration**: Find specific items or categories quickly

### 📊 Data Tables & Analytics

#### Groups Analysis
- **Summary Table**: Overview of all product groups with key metrics
- **Interactive Filters**: Filter by value ranges and group types
- **Sorting**: Multi-column sorting capabilities
- **Export Options**: Download filtered data as CSV/Excel

#### Categories Analysis
- **Detailed View**: Category-level breakdown with subtotals
- **Cross-Group Comparison**: Compare categories across different groups
- **Value Tracking**: Monitor `total_offer` values and trends
- **Item Count Analysis**: Analyze item distribution per category

#### Items Analysis
- **Comprehensive Item View**: All items with full details
- **Advanced Search**: Search by description, code, or category
- **Price Range Filtering**: Filter by unit price or total price
- **Performance Metrics**: Average prices, top items, distributions

### 📈 Interactive Visualizations (Plotly)

#### Group-Level Charts
- **Bar Charts**: Total offer values by group with interactive hover
- **Pie Charts**: Distribution of values across groups
- **Treemap**: Hierarchical visualization of group values
- **Waterfall Charts**: Financial flow analysis

#### Category-Level Charts
- **Horizontal Bar Charts**: Top categories by value
- **Stacked Charts**: Categories grouped by product groups
- **Scatter Plots**: Items count vs. total offer relationships
- **Color-coded Visualizations**: Easy identification of high-value categories

#### Item-Level Charts
- **Top Items Analysis**: Highest value items with interactive details
- **Price Distribution**: Histograms showing price ranges
- **Quantity vs. Price**: Scatter plots for correlation analysis
- **Trend Analysis**: Time-based price trends (if applicable)

#### Financial Charts
- **Cost Breakdown**: Equipment vs. Installation vs. Fees
- **Waterfall Analysis**: Step-by-step financial calculations
- **Group Financial Comparison**: Cost analysis by product group
- **ROI Visualizations**: Profit margin and cost efficiency metrics

### 💰 Financial Analysis Dashboard
- **Real-time Calculations**: Live updates of totals and fees
- **Multi-currency Support**: Handle different currencies and exchange rates
- **Fee Breakdown**: DOC, PM, and warranty fee analysis
- **Profit Margins**: Equipment cost vs. final pricing analysis

## 🎯 Application Sections

### 1. Project Summary
- **Key Metrics**: Project ID, customer, currency, exchange rates
- **Financial Overview**: Equipment, installation, fees, and grand totals
- **Quick Stats**: Number of groups, categories, items
- **Parameter Display**: DOC%, PM%, and other pricing parameters

### 2. Tree Structure
- **Interactive Hierarchy**: Expandable tree with Groups → Categories → Items
- **Value Display**: Shows monetary values at each level
- **Quick Stats**: Item counts and totals per section
- **Visual Indicators**: Icons and colors for different item types

### 3. Groups Analysis
- **Summary Table**: Complete group overview with filtering
- **Bar Chart**: Total offer values by group
- **Pie Chart**: Value distribution across groups  
- **Treemap**: Hierarchical value visualization

### 4. Categories Analysis
- **Filtered Tables**: Advanced filtering by group and value
- **Top Categories**: Highest value categories with details
- **Group Comparison**: Stacked charts comparing categories
- **Correlation Analysis**: Items count vs. value relationships

### 5. Items Analysis
- **Advanced Search**: Multi-criteria filtering and search
- **Top Items Display**: Highest value items with full details
- **Price Distribution**: Statistical analysis of pricing
- **Performance Charts**: Various analytical visualizations

### 6. Financial Analysis
- **Cost Breakdown**: Detailed financial component analysis
- **Waterfall Charts**: Step-by-step cost calculation visualization
- **Group Financial**: Equipment vs. installation cost analysis
- **Fee Analysis**: Detailed breakdown of all fees and charges

## 🛠️ Technical Features

### Performance Optimizations
- **Lazy Loading**: Large datasets loaded on demand
- **Caching**: `@st.cache_data` for expensive operations
- **Sampling**: Large item lists sampled for better performance
- **Efficient Filtering**: Client-side filtering for responsive UI

### User Experience
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Theme**: Automatic theme detection
- **Keyboard Shortcuts**: Quick navigation and actions
- **Progress Indicators**: Real-time feedback during processing

### Data Export
- **JSON Download**: Complete processed data export
- **CSV Export**: Individual table downloads
- **Chart Export**: Save visualizations as images
- **Report Generation**: Automated summary reports

## 📋 Data Requirements

### Excel File Format
The application expects Excel files with the following structure:

#### Project Information (Rows 1-16)
- **Row 1**: Project ID and Customer
- **Rows 7-13**: Pricing parameters (DOC%, PM%, etc.)
- **Row 11**: Currency information
- **Row 12**: Exchange rate

#### Data Section (Row 17+)
- **Row 17**: Column headers
- **Row 18+**: Hierarchical product data
  - **Groups**: TXT-XX format codes
  - **Categories**: 4-letter codes (SWZZ, FAZZ, etc.)
  - **Items**: Product codes with full descriptions

#### Required Columns
- **COD**: Category identification codes
- **CODICE**: Product/item codes
- **DENOMINAZIONE**: Descriptions
- **QTA**: Quantities
- **LIST.UNIT**: Unit prices
- **LISTINO**: Total prices
- **TOTALE OFFERTA**: Offer totals (focus field)

## 🎨 Customization

### Styling
The application includes custom CSS for:
- **Color Themes**: Professional color schemes
- **Typography**: Enhanced readability
- **Layout**: Optimized spacing and alignment
- **Interactive Elements**: Hover effects and transitions

### Chart Configurations
- **Color Palettes**: Professional Plotly color schemes
- **Chart Types**: Bar, pie, scatter, treemap, waterfall
- **Interactive Features**: Zoom, pan, hover, selection
- **Export Options**: PNG, SVG, PDF formats

## 🐛 Troubleshooting

### Common Issues

#### File Upload Problems
- **Large Files**: Check file size limits (default: 200MB)
- **Format Issues**: Ensure Excel file is not corrupted
- **Encoding**: Verify proper character encoding in descriptions

#### Performance Issues
- **Large Datasets**: Use filtering to reduce displayed data
- **Memory Usage**: Close other browser tabs if needed
- **Cache Issues**: Clear browser cache if experiencing problems

#### Chart Display Issues
- **Browser Compatibility**: Use modern browsers (Chrome, Firefox, Safari)
- **JavaScript**: Ensure JavaScript is enabled
- **Plotly Issues**: Refresh page if charts don't load

### Error Messages
- **File Processing Errors**: Check Excel file format and structure
- **Data Validation Errors**: Verify required columns are present
- **Memory Errors**: Reduce dataset size or restart application

## 🔧 Development

### Project Structure
```
src/pre_file/
├── streamlit_app.py          # Main Streamlit application
├── pre_file_parser.py        # Excel parsing logic
├── validate_json_schema.py   # Data validation
├── run_app.py               # Application launcher
├── STREAMLIT_README.md      # This documentation
└── example_usage.py         # Usage examples
```

### Dependencies
- **streamlit**: Web application framework
- **plotly**: Interactive visualizations
- **pandas**: Data manipulation and analysis
- **openpyxl**: Excel file processing
- **jsonschema**: Data validation
- **numpy**: Numerical computations

### Extension Points
- **Custom Charts**: Add new Plotly visualizations
- **Data Filters**: Implement additional filtering logic
- **Export Formats**: Add new export options
- **Validation Rules**: Extend data validation

## 📞 Support

### Getting Help
1. **Documentation**: Check this README for common solutions
2. **Error Logs**: Check Streamlit terminal output for errors
3. **Sample Files**: Use provided sample Excel files for testing
4. **Code Comments**: Review inline code documentation

### Contributing
1. **Fork Repository**: Create your own copy
2. **Feature Branch**: Create branch for new features
3. **Testing**: Test with various Excel file formats
4. **Pull Request**: Submit changes with detailed description

---

**🎯 Happy Analyzing!** 

This application provides a comprehensive solution for Excel quotation analysis with modern web interface and powerful visualization capabilities. 
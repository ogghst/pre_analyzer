# PRE Excel Data Analyzer

This Streamlit application allows you to analyze and visualize data from PRE Excel files. It extracts both detailed and summary data, presenting them in interactive tables and visualizations.

## Features

- Upload PRE Excel files (.xlsx, .xls, .xlsm)
- Extract detailed data and MDC summary data
- View data in interactive tables
- Visualize data with dynamic charts and graphs
- Download processed data as CSV files

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

To start the application, run:

```bash
cd pre_enc
streamlit run app.py
```

The application will start and open in your default web browser at `http://localhost:8501`.

## How to Use

1. **Upload Data**: Use the sidebar to upload your PRE Excel file
2. **View Data**: The application will automatically extract and display the data in tables
3. **Explore Visualizations**: Switch between tabs to view different visualizations
4. **Download Results**: Use the download buttons to save processed data as CSV files

## Data Types

The application processes two types of data from your Excel files:

1. **Detail Data**: Hierarchical WBE items with group, type, and subtype information
2. **Summary Data**: From the MDC sheet, containing code, description, quantity, and various price fields

## Customization

You can customize the application behavior using the checkboxes in the sidebar:

- **Show Data Tables**: Toggle the display of data tables
- **Show Visualizations**: Toggle the display of charts and graphs 
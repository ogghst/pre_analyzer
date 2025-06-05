"""
Pytest configuration and shared fixtures for pre_analyzer tests
"""

import pytest
import os
import sys
import tempfile
from unittest.mock import Mock
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def project_root_path():
    """Fixture providing the project root path"""
    return project_root

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_excel_file():
    """Create a mock Excel file for testing"""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
        temp_file.write(b'mock excel content')
        yield temp_file.name
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)

@pytest.fixture
def sample_quotation_data():
    """Sample quotation data for testing"""
    return {
        'project_info': {
            'project_name': 'Test Project',
            'customer_name': 'Test Customer',
            'quotation_number': 'Q-12345',
            'created_date': '2024-01-15'
        },
        'sales_info': {
            'sales_person': 'John Doe',
            'customer_code': 'CUST001',
            'currency': 'EUR'
        },
        'items': [
            {
                'description': 'Test Item 1',
                'quantity': 10,
                'unit_price': 100.0,
                'total_price': 1000.0
            },
            {
                'description': 'Test Item 2', 
                'quantity': 5,
                'unit_price': 200.0,
                'total_price': 1000.0
            }
        ],
        'totals': {
            'subtotal': 2000.0,
            'total': 2000.0
        }
    }

@pytest.fixture
def mock_industrial_quotation():
    """Mock IndustrialQuotation model for testing"""
    from models import IndustrialQuotation
    
    mock_quotation = Mock(spec=IndustrialQuotation)
    mock_quotation.project_info = Mock()
    mock_quotation.project_info.project_name = "Test Project"
    mock_quotation.project_info.customer_name = "Test Customer"
    mock_quotation.sales_info = Mock()
    mock_quotation.sales_info.currency = "EUR"
    mock_quotation.items = []
    mock_quotation.totals = Mock()
    mock_quotation.totals.total = 1000.0
    mock_quotation.save_json = Mock()
    mock_quotation.to_json = Mock(return_value='{"test": "data"}')
    
    return mock_quotation

# Configure logging for tests
import logging
logging.getLogger().setLevel(logging.WARNING)  # Reduce noise in test output 
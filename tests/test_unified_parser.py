"""
Test suite for UnifiedQuotationParser
Tests file type detection, parsing logic, error handling, and fallback mechanisms
"""

import pytest
import os
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile

# Add project root to path for imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from parsers.unified_parser import UnifiedQuotationParser, parse_quotation_file, analyze_quotation_file
from models import IndustrialQuotation


class TestUnifiedQuotationParser:
    """Test cases for UnifiedQuotationParser class"""
    
    @pytest.fixture
    def mock_quotation_model(self):
        """Mock IndustrialQuotation model for testing"""
        mock_model = Mock(spec=IndustrialQuotation)
        mock_model.project_info = Mock()
        mock_model.project_info.project_name = "Test Project"
        mock_model.save_json = Mock()
        return mock_model
    
    @pytest.fixture
    def temp_excel_file(self):
        """Create a temporary Excel file for testing"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            temp_file.write(b'dummy excel content')
            yield temp_file.name
        os.unlink(temp_file.name)
    
    def test_file_type_detection_pre_files(self):
        """Test detection of PRE file types"""
        test_cases = [
            "PRE_12345_quotation.xlsx",
            "pre_offer_document.xlsx", 
            "OFFER1_project_123.xlsx",
            "offer1_manufacturing.xlsx"
        ]
        
        for filename in test_cases:
            with patch('os.path.exists', return_value=True):
                parser = UnifiedQuotationParser(filename)
                assert parser.detected_type == 'pre', f"Failed to detect PRE for {filename}"
    
    def test_file_type_detection_analisi_profittabilita_files(self):
        """Test detection of Analisi Profittabilita file types"""
        test_cases = [
            "Analisi profitabilita_project.xlsx",
            "analisi_profittabilita_2024.xlsx",
            "profitability_analysis.xlsx", 
            "Tabella riassuntiva SAP_data.xlsx",
            "comprehensive_analysis.xlsx"  # Changed from NEW_OFFER1 which contains OFFER1 (PRE indicator)
        ]
        
        for filename in test_cases:
            with patch('os.path.exists', return_value=True):
                parser = UnifiedQuotationParser(filename)
                assert parser.detected_type == 'analisi_profittabilita', f"Failed to detect AP for {filename}"
    
    def test_file_type_detection_unknown_defaults_to_ap(self):
        """Test that unknown file types default to analisi_profittabilita"""
        unknown_files = [
            "random_quotation.xlsx",
            "project_2024.xlsx",
            "unknown_format.xlsx"
        ]
        
        for filename in unknown_files:
            with patch('os.path.exists', return_value=True):
                parser = UnifiedQuotationParser(filename)
                assert parser.detected_type == 'analisi_profittabilita'
    
    @patch('parsers.unified_parser.PreFileParser')
    def test_parse_pre_file_success(self, mock_pre_parser_class, mock_quotation_model):
        """Test successful parsing of PRE file"""
        # Setup mocks
        mock_parser_instance = Mock()
        mock_parser_instance.parse_to_model.return_value = mock_quotation_model
        mock_pre_parser_class.return_value = mock_parser_instance
        
        # Test parsing
        with patch('os.path.exists', return_value=True):
            parser = UnifiedQuotationParser("PRE_test.xlsx")
            result = parser.parse()
        
        # Assertions
        mock_pre_parser_class.assert_called_once_with("PRE_test.xlsx")
        mock_parser_instance.parse_to_model.assert_called_once()
        assert result == mock_quotation_model
    
    @patch('parsers.unified_parser.AnalisiProfittabilitaParser')
    def test_parse_ap_file_success(self, mock_ap_parser_class, mock_quotation_model):
        """Test successful parsing of Analisi Profittabilita file"""
        # Setup mocks
        mock_parser_instance = Mock()
        mock_parser_instance.parse_to_model.return_value = mock_quotation_model
        mock_ap_parser_class.return_value = mock_parser_instance
        
        # Test parsing
        with patch('os.path.exists', return_value=True):
            parser = UnifiedQuotationParser("analisi_profittabilita_test.xlsx")
            result = parser.parse()
        
        # Assertions
        mock_ap_parser_class.assert_called_once_with("analisi_profittabilita_test.xlsx")
        mock_parser_instance.parse_to_model.assert_called_once()
        assert result == mock_quotation_model
    
    @patch('parsers.unified_parser.PreFileParser')
    @patch('parsers.unified_parser.AnalisiProfittabilitaParser')
    def test_parse_fallback_mechanism(self, mock_ap_parser_class, mock_pre_parser_class, mock_quotation_model):
        """Test fallback parsing when primary parser fails"""
        # Setup: PRE parser fails, AP parser succeeds
        mock_pre_instance = Mock()
        mock_pre_instance.parse_to_model.side_effect = Exception("PRE parsing failed")
        mock_pre_parser_class.return_value = mock_pre_instance
        
        mock_ap_instance = Mock()
        mock_ap_instance.parse_to_model.return_value = mock_quotation_model
        mock_ap_parser_class.return_value = mock_ap_instance
        
        # Test parsing PRE file that falls back to AP parser
        with patch('os.path.exists', return_value=True):
            parser = UnifiedQuotationParser("PRE_test.xlsx")
            result = parser.parse()
        
        # Assertions
        mock_pre_parser_class.assert_called_once_with("PRE_test.xlsx")
        mock_ap_parser_class.assert_called_once_with("PRE_test.xlsx")
        assert result == mock_quotation_model
    
    @patch('parsers.unified_parser.PreFileParser')
    @patch('parsers.unified_parser.AnalisiProfittabilitaParser')
    def test_parse_both_parsers_fail(self, mock_ap_parser_class, mock_pre_parser_class):
        """Test exception when both parsers fail"""
        # Setup: Both parsers fail
        mock_pre_instance = Mock()
        mock_pre_instance.parse_to_model.side_effect = Exception("PRE parsing failed")
        mock_pre_parser_class.return_value = mock_pre_instance
        
        mock_ap_instance = Mock()
        mock_ap_instance.parse_to_model.side_effect = Exception("AP parsing failed")
        mock_ap_parser_class.return_value = mock_ap_instance
        
        # Test parsing fails completely
        with patch('os.path.exists', return_value=True):
            parser = UnifiedQuotationParser("PRE_test.xlsx")
            with pytest.raises(Exception) as exc_info:
                parser.parse()
        
        assert "Could not parse" in str(exc_info.value)
        assert "PRE parsing failed" in str(exc_info.value)
        assert "AP parsing failed" in str(exc_info.value)
    
    def test_parse_and_save(self, temp_excel_file, mock_quotation_model):
        """Test parsing and saving to JSON"""
        with patch.object(UnifiedQuotationParser, 'parse', return_value=mock_quotation_model):
            parser = UnifiedQuotationParser(temp_excel_file)
            
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_json:
                result = parser.parse_and_save(temp_json.name)
            
            # Cleanup
            if os.path.exists(temp_json.name):
                os.unlink(temp_json.name)
            
            # Assertions
            mock_quotation_model.save_json.assert_called_once_with(temp_json.name)
            assert result == mock_quotation_model
    
    def test_get_parser_recommendations_pre(self):
        """Test parser recommendations for PRE files"""
        with patch('os.path.exists', return_value=True):
            parser = UnifiedQuotationParser("PRE_offer1_project.xlsx")
            recommendations = parser.get_parser_recommendations()
        
        assert recommendations['recommended_parser'] == 'pre'
        assert recommendations['pre_confidence'] > recommendations['analisi_profittabilita_confidence']
        assert recommendations['detected_type'] == 'pre'
        assert recommendations['pre_score'] > 0
    
    def test_get_parser_recommendations_ap(self):
        """Test parser recommendations for AP files"""
        with patch('os.path.exists', return_value=True):
            parser = UnifiedQuotationParser("analisi_profittabilita_va21_sap.xlsx")
            recommendations = parser.get_parser_recommendations()
        
        assert recommendations['recommended_parser'] == 'analisi_profittabilita'
        assert recommendations['analisi_profittabilita_confidence'] > recommendations['pre_confidence']
        assert recommendations['detected_type'] == 'analisi_profittabilita'
        assert recommendations['ap_score'] > 0
    
    def test_get_parser_recommendations_unknown_file(self):
        """Test parser recommendations for unknown files"""
        with patch('os.path.exists', return_value=True):
            parser = UnifiedQuotationParser("unknown_file.xlsx")
            recommendations = parser.get_parser_recommendations()
        
        # Should have equal confidence for unknown files
        assert recommendations['pre_confidence'] == 50.0
        assert recommendations['analisi_profittabilita_confidence'] == 50.0
        assert recommendations['recommended_parser'] == 'analisi_profittabilita'  # Default


class TestUnifiedParserFunctions:
    """Test cases for module-level functions"""
    
    @pytest.fixture
    def mock_quotation_model(self):
        """Mock IndustrialQuotation model for testing"""
        mock_model = Mock(spec=IndustrialQuotation)
        mock_model.project_info = Mock()
        mock_model.project_info.project_name = "Test Project"
        return mock_model
    
    @patch('parsers.unified_parser.parse_pre_to_model')
    def test_parse_quotation_file_force_pre(self, mock_parse_pre, mock_quotation_model):
        """Test forcing PRE parser"""
        mock_parse_pre.return_value = mock_quotation_model
        
        result = parse_quotation_file("test.xlsx", force_parser='pre')
        
        mock_parse_pre.assert_called_once_with("test.xlsx", None)
        assert result == mock_quotation_model
    
    @patch('parsers.unified_parser.parse_analisi_profittabilita_to_model')
    def test_parse_quotation_file_force_ap(self, mock_parse_ap, mock_quotation_model):
        """Test forcing AP parser"""
        mock_parse_ap.return_value = mock_quotation_model
        
        result = parse_quotation_file("test.xlsx", force_parser='analisi_profittabilita')
        
        mock_parse_ap.assert_called_once_with("test.xlsx", None)
        assert result == mock_quotation_model
    
    def test_parse_quotation_file_invalid_force_parser(self):
        """Test invalid forced parser type"""
        with pytest.raises(ValueError) as exc_info:
            parse_quotation_file("test.xlsx", force_parser='invalid')
        
        assert "Invalid forced parser type: invalid" in str(exc_info.value)
    
    @patch('parsers.unified_parser.UnifiedQuotationParser')
    def test_parse_quotation_file_auto_detect(self, mock_parser_class, mock_quotation_model):
        """Test automatic file type detection"""
        mock_parser_instance = Mock()
        mock_parser_instance.parse.return_value = mock_quotation_model
        mock_parser_class.return_value = mock_parser_instance
        
        result = parse_quotation_file("test.xlsx")
        
        mock_parser_class.assert_called_once_with("test.xlsx")
        mock_parser_instance.parse.assert_called_once()
        assert result == mock_quotation_model
    
    @patch('parsers.unified_parser.UnifiedQuotationParser')
    def test_parse_quotation_file_with_output(self, mock_parser_class, mock_quotation_model):
        """Test parsing with JSON output"""
        mock_parser_instance = Mock()
        mock_parser_instance.parse_and_save.return_value = mock_quotation_model
        mock_parser_class.return_value = mock_parser_instance
        
        result = parse_quotation_file("test.xlsx", output_path="output.json")
        
        mock_parser_class.assert_called_once_with("test.xlsx")
        mock_parser_instance.parse_and_save.assert_called_once_with("output.json")
        assert result == mock_quotation_model
    
    @patch('parsers.unified_parser.UnifiedQuotationParser')
    @patch('os.path.getsize')
    @patch('os.path.exists')
    def test_analyze_quotation_file(self, mock_exists, mock_getsize, mock_parser_class):
        """Test quotation file analysis"""
        # Setup mocks
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        
        mock_parser_instance = Mock()
        mock_parser_instance.file_name = "test.xlsx"
        mock_parser_instance.get_parser_recommendations.return_value = {
            'recommended_parser': 'pre',
            'pre_confidence': 75.0,
            'analisi_profittabilita_confidence': 25.0
        }
        mock_parser_class.return_value = mock_parser_instance
        
        # Test analysis
        result = analyze_quotation_file("test.xlsx")
        
        # Assertions
        assert 'file_info' in result
        assert 'parser_recommendations' in result
        assert result['file_info']['file_name'] == "test.xlsx"
        assert result['file_info']['file_size'] == 1024
        assert result['file_info']['exists'] is True
        assert result['parser_recommendations']['recommended_parser'] == 'pre'


class TestIntegration:
    """Integration tests for the unified parser"""
    
    def test_end_to_end_workflow(self):
        """Test complete parsing workflow with mocked components"""
        mock_quotation = Mock(spec=IndustrialQuotation)
        mock_quotation.project = Mock()
        mock_quotation.project.id = "Integration Test"
        
        with patch('parsers.unified_parser.PreFileParser') as mock_parser_class:
            mock_parser_instance = Mock()
            mock_parser_instance.parse_to_model.return_value = mock_quotation
            mock_parser_class.return_value = mock_parser_instance
            
            # Test the complete workflow
            with patch('os.path.exists', return_value=True):
                parser = UnifiedQuotationParser("PRE_integration_test.xlsx")
                
                # Test detection
                assert parser.detected_type == 'pre'
                
                # Test recommendations
                recommendations = parser.get_parser_recommendations()
                assert recommendations['recommended_parser'] == 'pre'
                
                # Test parsing
                result = parser.parse()
                assert result == mock_quotation
    
    def test_error_resilience(self):
        """Test error handling and resilience"""
        with patch('parsers.unified_parser.PreFileParser') as mock_pre:
            with patch('parsers.unified_parser.AnalisiProfittabilitaParser') as mock_ap:
                # Both parsers raise different exceptions
                mock_pre.return_value.parse_to_model.side_effect = ValueError("Invalid PRE format")
                mock_ap.return_value.parse_to_model.side_effect = KeyError("Missing AP data")
                
                with patch('os.path.exists', return_value=True):
                    parser = UnifiedQuotationParser("PRE_error_test.xlsx")
                    
                    with pytest.raises(Exception) as exc_info:
                        parser.parse()
                    
                    # Should contain both error messages
                    error_msg = str(exc_info.value)
                    assert "Invalid PRE format" in error_msg
                    assert "Missing AP data" in error_msg


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"]) 
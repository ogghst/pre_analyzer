"""
Manager for IndustrialQuotation objects.
This class provides methods for data processing, serialization, and analysis
of IndustrialQuotation data models.
"""
from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Dict, Any, Union

import json
import pandas as pd

from models.quotation_models import IndustrialQuotation, ParserType

if TYPE_CHECKING:
    from models.quotation_models import IndustrialQuotation, ParserType

logger = logging.getLogger(__name__)

class IndustrialQuotationManager:
    """
    Manages operations on IndustrialQuotation objects, separating logic from the data model.
    """
    def __init__(self, quotation: IndustrialQuotation):
        """
        Initialize the manager with a quotation object.
        Args:
            quotation: An IndustrialQuotation instance.
        """
        self.quotation = quotation

    # =============================================================================
    # PANDAS CONVERSION METHODS
    # =============================================================================

    def to_items_dataframe(self) -> pd.DataFrame:
        """
        Convert all items to a flat pandas DataFrame for analysis.

        Returns:
            DataFrame with one row per item, including group and category information
        """
        items_data = []

        for group in self.quotation.product_groups:
            for category in group.categories:
                for item in category.items:
                    item_dict = item.model_dump()
                    # Add group and category context
                    item_dict.update({
                        'group_id': group.group_id,
                        'group_name': group.group_name,
                        'group_quantity': group.quantity,
                        'category_id': category.category_id,
                        'category_name': category.category_name,
                        'category_wbe': category.wbe,
                        'category_offer_price': category.offer_price,
                        'category_type': category.category_type.value
                    })
                    items_data.append(item_dict)

        return pd.DataFrame(items_data)

    def to_categories_dataframe(self) -> pd.DataFrame:
        """
        Convert all categories to a pandas DataFrame for analysis.

        Returns:
            DataFrame with one row per category, including calculated metrics
        """
        categories_data = []

        for group in self.quotation.product_groups:
            for category in group.categories:
                cat_dict = category.model_dump(exclude={'items'})
                # Add group context and calculated fields
                cat_dict.update({
                    'group_id': group.group_id,
                    'group_name': group.group_name,
                    'group_quantity': group.quantity,
                    'category_type': category.category_type.value,
                    'calculated_pricelist_subtotal': category.calculated_pricelist_subtotal,
                    'calculated_cost_subtotal': category.calculated_cost_subtotal,
                    'margin_amount': category.margin_amount,
                    'margin_percentage': category.margin_percentage,
                    'item_count': len(category.items)
                })
                categories_data.append(cat_dict)

        return pd.DataFrame(categories_data)

    def to_groups_dataframe(self) -> pd.DataFrame:
        """
        Convert all product groups to a pandas DataFrame for analysis.

        Returns:
            DataFrame with one row per product group, including aggregated metrics
        """
        groups_data = []

        for group in self.quotation.product_groups:
            group_dict = group.model_dump(exclude={'categories'})
            # Add calculated fields
            group_dict.update({
                'total_pricelist_value': group.total_pricelist_value,
                'total_cost_value': group.total_cost_value,
                'total_offer_value': group.total_offer_value,
                'item_count': group.item_count,
                'category_count': len(group.categories)
            })
            groups_data.append(group_dict)

        return pd.DataFrame(groups_data)

    # =============================================================================
    # JSON SERIALIZATION METHODS
    # =============================================================================

    def to_json(self, indent: int = 2) -> str:
        """
        Serialize the quotation to JSON string.

        Args:
            indent: JSON indentation level

        Returns:
            JSON string representation
        """
        return self.quotation.model_dump_json(indent=indent)

    def save_json(self, filepath: str, indent: int = 2) -> None:
        """
        Save quotation to JSON file.

        Args:
            filepath: Path to save the JSON file
            indent: JSON indentation level
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json(indent=indent))
        logger.info(f"Quotation saved to JSON file: {filepath}")

    # =============================================================================
    # ANALYSIS AND VALIDATION METHODS
    # =============================================================================

    def validate_totals_consistency(self) -> Dict[str, bool]:
        """
        Validate that calculated totals match the stored totals.

        Returns:
            Dictionary with validation results for different total types
        """
        actual_total_listino = sum(cat.pricelist_subtotal for group in self.quotation.product_groups for cat in group.categories)
        actual_total_cost = sum(cat.cost_subtotal for group in self.quotation.product_groups for cat in group.categories)
        actual_total_offer = sum(cat.offer_price or 0.0 for group in self.quotation.product_groups for cat in group.categories)

        tolerance = 0.01  # Allow small rounding differences

        return {
            'total_listino_valid': abs(self.quotation.totals.total_pricelist - actual_total_listino) <= tolerance,
            'total_costo_valid': abs(self.quotation.totals.total_cost - actual_total_cost) <= tolerance,
            'total_offer_valid': abs(self.quotation.totals.total_offer - actual_total_offer) <= tolerance
        }

    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics for the quotation.

        Returns:
            Dictionary with key metrics and statistics
        """
        return {
            'project_id': self.quotation.project.id,
            'total_groups': len(self.quotation.product_groups),
            'total_categories': sum(len(group.categories) for group in self.quotation.product_groups),
            'total_items': sum(group.item_count for group in self.quotation.product_groups),
            'total_listino': self.quotation.totals.total_pricelist,
            'total_cost': self.quotation.totals.total_cost,
            'total_offer': self.quotation.totals.total_offer,
            'margin_percentage': self.quotation.totals.offer_margin_percentage,
            'offer_margin_percentage': self.quotation.totals.offer_margin_percentage,
            'currency': self.quotation.project.parameters.currency,
            'has_offer_prices': any(
                cat.offer_price is not None and cat.offer_price > 0
                for group in self.quotation.product_groups for cat in group.categories
            ),
            'validation_results': self.validate_totals_consistency()
        }

    def to_parser_dict(self) -> Dict[str, Any]:
        """
        Convert back to parser-compatible dictionary format.

        Returns:
            Dictionary compatible with original parser output format
        """
        return {
            'project': self.quotation.project.model_dump(),
            'product_groups': [group.model_dump() for group in self.quotation.product_groups],
            'totals': self.quotation.totals.model_dump()
        }

    # =============================================================================
    # FACTORY METHODS FOR PARSER INTEGRATION
    # =============================================================================

    @staticmethod
    def from_json(json_str: str) -> 'IndustrialQuotation':
        """
        Deserialize quotation from JSON string.

        Args:
            json_str: JSON string to parse

        Returns:
            IndustrialQuotation instance
        """
        return IndustrialQuotation.model_validate_json(json_str)

    @staticmethod
    def load_json(filepath: str) -> 'IndustrialQuotation':
        """
        Load quotation from JSON file.

        Args:
            filepath: Path to the JSON file

        Returns:
            IndustrialQuotation instance
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return IndustrialQuotationManager.from_json(f.read())

    @staticmethod
    def from_parser_dict(data: Dict[str, Any], source_file: str = None, parser_type: Union[str, ParserType] = None) -> 'IndustrialQuotation':
        """
        Create IndustrialQuotation from parser output dictionary.

        Args:
            data: Dictionary from pre_file_parser or analisi_profittabilita_parser
            source_file: Source Excel file path
            parser_type: Type of parser used (string or ParserType enum)

        Returns:
            IndustrialQuotation instance
        """
        # Convert string to ParserType if needed
        if isinstance(parser_type, str):
            try:
                parser_type = ParserType(parser_type)
            except ValueError:
                # If invalid string, try to match common patterns
                if 'pre' in parser_type.lower():
                    parser_type = ParserType.PRE_FILE_PARSER
                elif 'analisi' in parser_type.lower():
                    parser_type = ParserType.ANALISI_PROFITTABILITA_PARSER
                else:
                    logger.warning(f"Unknown parser_type '{parser_type}', defaulting to PRE_FILE_PARSER")
                    parser_type = ParserType.PRE_FILE_PARSER

        # If parser_type is still None, default to PRE_FILE_PARSER
        if parser_type is None:
            parser_type = ParserType.PRE_FILE_PARSER

        # Convert the parser dict to our model structure
        quotation_data = {
            'project': data.get('project', {}),
            'product_groups': data.get('product_groups', []),
            'totals': data.get('totals', {}),
            'source_file': source_file,
            'parser_type': parser_type
        }

        return IndustrialQuotation(**quotation_data)

from typing import List, Any


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float with error handling.
    
    Args:
        value: Value to convert to float
        default: Default value to return if conversion fails
        
    Returns:
        Float value or default if conversion fails
    """
    try:
        if value is None or value == '':
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_format_currency(value: Any, italian_style: bool = False, decimals: int = 0) -> str:
    """
    Safely format a currency value to EUR format with error handling.
    
    Args:
        value: Numeric value to format as currency
        italian_style: If True, use Italian number formatting (. for thousands, , for decimals)
        decimals: Number of decimal places to show
        
    Returns:
        Formatted currency string
    """
    try:
        safe_value = safe_float(value, 0.0)
        if italian_style:
            # Italian style: € 1.234,56
            formatted = f"€ {safe_value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            # Standard style: €1,234 (no decimals) or €1,234.56 (with decimals)
            if decimals == 0:
                formatted = f"€{safe_value:,.0f}"
            else:
                formatted = f"€{safe_value:,.{decimals}f}"
        return formatted
    except (ValueError, TypeError):
        return "€0"


def safe_format_percentage(value: Any, decimals: int = 1) -> str:
    """
    Safely format a percentage value with error handling.
    
    Args:
        value: Numeric value to format as percentage
        decimals: Number of decimal places to show
        
    Returns:
        Formatted percentage string
    """
    try:
        safe_value = safe_float(value, 0.0)
        return f"{safe_value:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0.0%"


def safe_format_number(value: Any, decimals: int = 0, show_sign: bool = False) -> str:
    """
    Safely format a numeric value with thousands separators.
    
    Args:
        value: Numeric value to format
        decimals: Number of decimal places to show
        show_sign: If True, show + sign for positive numbers
        
    Returns:
        Formatted number string
    """
    try:
        safe_value = safe_float(value, 0.0)
        if show_sign:
            return f"{safe_value:+,.{decimals}f}"
        else:
            return f"{safe_value:,.{decimals}f}"
    except (ValueError, TypeError):
        return "0"


def format_currency_values(values: List[float], italian_style: bool = False, decimals: int = 2) -> List[str]:
    """
    Format a list of currency values to EUR format.
    
    Args:
        values: List of numeric values to format as currency
        italian_style: If True, use Italian number formatting
        decimals: Number of decimal places to show
        
    Returns:
        List of formatted currency strings
    """
    return [safe_format_currency(value, italian_style, decimals) for value in values]


def format_currency_value(value: float, italian_style: bool = False, decimals: int = 2) -> str:
    """
    Format a single currency value to EUR format (legacy function for backward compatibility).
    
    Args:
        value: Numeric value to format as currency
        italian_style: If True, use Italian number formatting
        decimals: Number of decimal places to show
        
    Returns:
        Formatted currency string
    """
    return safe_format_currency(value, italian_style, decimals)


def parse_currency_string(currency_str: str) -> float:
    """
    Parse a formatted currency string back to a float value.
    
    Args:
        currency_str: Formatted currency string (e.g., "€1,234.56" or "€ 1.234,56")
        
    Returns:
        Float value extracted from the currency string
    """
    try:
        # Remove currency symbol and spaces
        cleaned = str(currency_str).replace('€', '').replace(' ', '')
        
        # Handle both standard and Italian formatting
        if ',' in cleaned and '.' in cleaned:
            # Determine which is thousands separator vs decimal separator
            last_comma = cleaned.rfind(',')
            last_dot = cleaned.rfind('.')
            
            if last_comma > last_dot:
                # Italian style: 1.234,56 (dot=thousands, comma=decimal)
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                # Standard style: 1,234.56 (comma=thousands, dot=decimal)
                cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Only comma - could be thousands or decimal separator
            comma_pos = cleaned.rfind(',')
            if len(cleaned) - comma_pos == 3:  # If 2 digits after comma, it's decimal
                cleaned = cleaned.replace(',', '.')
            else:  # Otherwise it's thousands separator
                cleaned = cleaned.replace(',', '')
        
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0




from typing import List


def format_currency_values(values: List[float]) -> List[str]:
    """
    Format a list of currency values to EUR format in Italian style.
    
    Args:
        values: Dictionary values containing float numbers to format
        
    Returns:
        Dictionary values with formatted currency strings
    """
    return [f"€ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") for value in values]

def format_currency_value(value: float) -> str:
    """
    Format a single currency value to EUR format in Italian style.
    
    Args:
        value: Float number to format   

    Returns:
        Formatted currency string
    """
    return f"€ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")




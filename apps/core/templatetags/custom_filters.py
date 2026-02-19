from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def rupiah(value):
    """
    Format number to Indonesian Rupiah format.
    Example: 1000000 -> 1.000.000
    """
    if value is None:
        return "0"
    try:
        # Convert string to float first if it's a string number
        if isinstance(value, str):
            value = float(value)
        
        # Check if it's an integer-like float
        if value == int(value):
            value = int(value)
            
        # Format with thousand separator
        # We replace comma with dot since intcomma uses comma
        s = f"{value:,}".replace(",", ".")
        return s
    except (ValueError, TypeError):
        return value

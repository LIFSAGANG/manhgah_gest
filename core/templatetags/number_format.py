from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def format_amount(value, decimals=2):
    if value in (None, ''):
        return ''
    try:
        amount = Decimal(str(value))
        decimals = int(decimals)
    except (InvalidOperation, TypeError, ValueError):
        return value

    formatted = f"{amount:,.{decimals}f}"
    return formatted.replace(',', ' ')

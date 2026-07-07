from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def format_amount(value, decimals=0):
    if value in (None, ''):
        return ''
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return value

    # En comptabilité, les affichages sont normalisés en entier.
    amount = amount.quantize(Decimal('1'))
    if amount == 0:
        return ''

    formatted = f"{int(amount):,}"
    return formatted.replace(',', ' ')

import re


def format_phone_number(phone: str) -> str:
    """Format to +998XXXXXXXXX"""
    digits = re.sub(r'\D', '', phone)

    if digits.startswith('998'):
        return '+' + digits
    elif len(digits) == 9:
        return '+998' + digits
    else:
        return '+998' + digits


def validate_uzbek_phone(phone: str) -> bool:
    """Validate Uzbekistan phone number"""
    clean = re.sub(r'[^\d+]', '', phone)
    return bool(re.match(r'^\+998\d{9}', clean))

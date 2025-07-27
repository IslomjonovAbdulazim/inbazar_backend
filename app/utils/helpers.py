import re
from typing import Optional


def format_phone_number(phone: str) -> str:
    """Format phone number to international format"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)

    # Add + if not present
    if not digits.startswith('998'):  # Uzbekistan code
        if len(digits) == 9:
            digits = '998' + digits

    return '+' + digits


def validate_phone_number(phone: str) -> bool:
    """Validate Uzbekistan phone number"""
    formatted = format_phone_number(phone)
    # Uzbekistan phone numbers: +998XXXXXXXXX (13 digits total)
    return re.match(r'^\+998\d{9}$', formatted) is not None


def generate_supabase_url(bucket: str, filename: str) -> str:
    """Generate Supabase storage URL"""
    from app.config import settings
    return f"{settings.supabase_url}/storage/v1/object/public/{bucket}/{filename}"


def extract_filename_from_url(url: str) -> Optional[str]:
    """Extract filename from URL"""
    try:
        return url.split('/')[-1]
    except:
        return None
from typing import Optional
from app.config import settings

# Try to import bot database functions
try:
    from app.database import SessionLocal
    from app.crud.bot_user import verify_otp_code as verify_otp_db, get_bot_user_by_phone

    BOT_DB_AVAILABLE = True
except ImportError:
    BOT_DB_AVAILABLE = False


def verify_otp_code_sync(phone_number: str, code: str) -> bool:
    """Verify OTP code using PostgreSQL database"""
    if not BOT_DB_AVAILABLE:
        print("Bot DB not available, using fallback")
        # Fallback: accept any 6-digit code for testing
        return code.isdigit() and len(code) == 6

    db = SessionLocal()
    try:
        # Format phone number
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number

        print(f"Verifying OTP for {phone_number} with code {code}")
        result = verify_otp_db(db, phone_number, code)
        print(f"OTP verification result: {result}")
        return result
    except Exception as e:
        print(f"Error in sync OTP verification: {e}")
        return False
    finally:
        db.close()


def get_user_by_phone_sync(phone_number: str) -> Optional[dict]:
    """Get user info from bot database by phone number"""
    if not BOT_DB_AVAILABLE:
        return None

    db = SessionLocal()
    try:
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number

        print(f"Looking up user by phone: {phone_number}")
        bot_user = get_bot_user_by_phone(db, phone_number)

        if bot_user:
            user_data = {
                'telegram_id': bot_user.telegram_id,
                'username': bot_user.username,
                'first_name': bot_user.first_name,
                'last_name': bot_user.last_name,
                'phone_number': bot_user.phone_number
            }
            print(f"Found user: {user_data}")
            return user_data
        else:
            print("No user found for phone number")
            return None

    except Exception as e:
        print(f"Error getting user by phone: {e}")
        return None
    finally:
        db.close()


def get_telegram_bot_url() -> str:
    """Get Telegram bot URL for user to start conversation"""
    return f"https://t.me/{settings.telegram_bot_username}"
import httpx
import random
import string
from typing import Dict, Optional
from app.config import settings

# In-memory storage for OTP codes (in production, use Redis)
otp_storage: Dict[str, str] = {}


def generate_otp_code() -> str:
    """Generate a 6-digit OTP code"""
    return ''.join(random.choices(string.digits, k=6))


async def send_otp_via_telegram(phone_number: str, telegram_id: str) -> bool:
    """Send OTP code via Telegram bot"""
    try:
        otp_code = generate_otp_code()

        # Store OTP code temporarily (5 minutes)
        otp_storage[phone_number] = otp_code

        # Send message via Telegram Bot API
        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"

        message = f"🔐 Your verification code: {otp_code}\n\nEnter this code in the app to complete login."

        payload = {
            "chat_id": telegram_id,
            "text": message
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            return response.status_code == 200

    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False


def verify_otp_code(phone_number: str, code: str) -> bool:
    """Verify OTP code"""
    stored_code = otp_storage.get(phone_number)
    if stored_code and stored_code == code:
        # Remove used OTP
        del otp_storage[phone_number]
        return True
    return False


def get_telegram_bot_url() -> str:
    """Get Telegram bot URL for user to start conversation"""
    return f"https://t.me/{settings.telegram_bot_username}"


# Telegram webhook handler (for receiving user messages)
async def handle_telegram_webhook(update: dict) -> Optional[str]:
    """Handle incoming Telegram webhook for phone verification"""
    try:
        message = update.get("message", {})
        contact = message.get("contact")

        if contact:
            phone_number = contact.get("phone_number")
            telegram_id = str(message.get("from", {}).get("id"))

            if phone_number and telegram_id:
                # Send OTP code
                success = await send_otp_via_telegram(phone_number, telegram_id)
                if success:
                    return "✅ Verification code sent! Please check the app."
                else:
                    return "❌ Failed to send verification code. Please try again."

        return "📱 Please share your phone number using the button below."

    except Exception as e:
        print(f"Error handling Telegram webhook: {e}")
        return "❌ Something went wrong. Please try again."
import random
import string
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.crud.bot_user import create_or_update_bot_user, store_otp_code, get_bot_user_by_telegram_id
from app.bot.utils import format_phone_number, validate_uzbek_phone


def get_contact_keyboard():
    """Always show the same contact button"""
    contact_button = KeyboardButton("📱 Tasdiqlash kodini olish", request_contact=True)
    return ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show contact button"""
    await update.message.reply_text(
        "📱 Telefon raqamingizni tasdiqlash uchun pastdagi tugmani bosing:",
        reply_markup=get_contact_keyboard()
    )


async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle contact - send OTP with security checks"""
    user = update.effective_user
    contact = update.message.contact

    # SECURITY CHECK 1: Must be user's own contact
    if contact.user_id != user.id:
        await update.message.reply_text(
            "❌ Xavfsizlik: Faqat o'z kontaktingizni ulashing!\n\n"
            "📱 Boshqa odamning kontaktini ulash taqiqlangan.",
            reply_markup=get_contact_keyboard()
        )
        return

    # SECURITY CHECK 2: Contact must have user_id (real Telegram contact)
    if not contact.user_id:
        await update.message.reply_text(
            "❌ Noto'g'ri kontakt turi. Iltimos, Telegram kontaktingizni ulashing.",
            reply_markup=get_contact_keyboard()
        )
        return

    # SECURITY CHECK 3: Telegram user ID must match exactly
    if str(contact.user_id) != str(user.id):
        await update.message.reply_text(
            "❌ Xavfsizlik xatosi: Kontakt egasi mos kelmaydi.\n\n"
            "📱 Faqat o'zingizning kontaktingizni ulashingiz mumkin.",
            reply_markup=get_contact_keyboard()
        )
        return

    phone_number = format_phone_number(contact.phone_number)

    # SECURITY CHECK 4: Must be Uzbekistan number
    if not validate_uzbek_phone(phone_number):
        await update.message.reply_text(
            "❌ Faqat O'zbekiston raqamlari qabul qilinadi: +998XXXXXXXXX\n\n"
            "📱 To'g'ri O'zbekiston raqamini ulashing.",
            reply_markup=get_contact_keyboard()
        )
        return

    # SECURITY CHECK 5: Check if this phone is already registered to another Telegram user
    db = SessionLocal()
    try:
        from app.crud.bot_user import get_bot_user_by_phone
        existing_user = get_bot_user_by_phone(db, phone_number)

        if existing_user and existing_user.telegram_id != str(user.id):
            await update.message.reply_text(
                "❌ Bu raqam boshqa foydalanuvchi tomonidan ro'yxatdan o'tkazilgan.\n\n"
                "📱 O'zingizning raqamingizni ulashing.",
                reply_markup=get_contact_keyboard()
            )
            return
    finally:
        pass

    # Generate 6-digit OTP
    otp_code = ''.join(random.choices(string.digits, k=6))

    # Save to database
    try:
        store_otp_code(db, phone_number, otp_code)
        create_or_update_bot_user(
            db=db,
            telegram_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=phone_number
        )

        # Send OTP
        await update.message.reply_text(
            f"✅ Kod: **{otp_code}**\n\n"
            f"📱 Raqam: {phone_number}\n"
            f"⏰ 5 daqiqada tugaydi",
            parse_mode='Markdown',
            reply_markup=get_contact_keyboard()
        )

    except Exception as e:
        await update.message.reply_text(
            "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.",
            reply_markup=get_contact_keyboard()
        )
        print(f"Error storing OTP: {e}")
    finally:
        db.close()


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Any text -> remind to use button or show active code"""
    user = update.effective_user

    # Check if user has active OTP
    db = SessionLocal()
    try:
        bot_user = get_bot_user_by_telegram_id(db, str(user.id))

        if bot_user and bot_user.phone_number:
            # Check for active OTP
            from app.models.bot_user import OTPCode
            from datetime import datetime

            active_otp = db.query(OTPCode).filter(
                OTPCode.phone_number == bot_user.phone_number,
                OTPCode.expires_at > datetime.utcnow()
            ).first()

            if active_otp:
                await update.message.reply_text(
                    f"✅ Faol kodingiz bor: **{active_otp.code}**\n\n"
                    f"📱 Raqam: {bot_user.phone_number}",
                    parse_mode='Markdown',
                    reply_markup=get_contact_keyboard()
                )
                return
    except Exception as e:
        print(f"Error checking active OTP: {e}")
    finally:
        db.close()

    # Default: remind to use button
    await update.message.reply_text(
        "📱 Tasdiqlash kodi olish uchun pastdagi tugmani bosing:",
        reply_markup=get_contact_keyboard()
    )
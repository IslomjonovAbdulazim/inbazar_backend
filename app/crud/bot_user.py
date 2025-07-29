from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta, timezone
from app.models.bot_user import BotUser, OTPCode


def get_bot_user_by_telegram_id(db: Session, telegram_id: str) -> Optional[BotUser]:
    return db.query(BotUser).filter(BotUser.telegram_id == telegram_id).first()


def get_bot_user_by_phone(db: Session, phone_number: str) -> Optional[BotUser]:
    return db.query(BotUser).filter(BotUser.phone_number == phone_number).first()


def create_or_update_bot_user(
        db: Session,
        telegram_id: str,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone_number: Optional[str] = None
) -> BotUser:
    bot_user = get_bot_user_by_telegram_id(db, telegram_id)

    if bot_user:
        # Update existing user
        if username is not None:
            bot_user.username = username
        if first_name is not None:
            bot_user.first_name = first_name
        if last_name is not None:
            bot_user.last_name = last_name
        if phone_number is not None:
            bot_user.phone_number = phone_number
        db.commit()
        db.refresh(bot_user)
    else:
        # Create new user
        bot_user = BotUser(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )
        db.add(bot_user)
        db.commit()
        db.refresh(bot_user)

    return bot_user


def store_otp_code(db: Session, phone_number: str, code: str, expires_minutes: int = 5) -> bool:
    try:
        # Use timezone-aware datetime
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

        # Delete any existing OTP for this phone number
        db.query(OTPCode).filter(OTPCode.phone_number == phone_number).delete()

        # Create new OTP
        otp_code = OTPCode(
            phone_number=phone_number,
            code=code,
            expires_at=expires_at
        )

        db.add(otp_code)
        db.commit()
        return True

    except Exception as e:
        print(f"Error storing OTP: {e}")
        db.rollback()
        return False


def verify_otp_code(db: Session, phone_number: str, code: str) -> bool:
    try:
        # Get OTP code
        otp_record = db.query(OTPCode).filter(
            OTPCode.phone_number == phone_number,
            OTPCode.code == code
        ).first()

        if not otp_record:
            print(f"No OTP found for {phone_number} with code {code}")
            return False

        # Use timezone-aware datetime for comparison
        now = datetime.now(timezone.utc)

        # Check if expired
        if now > otp_record.expires_at:
            print(f"OTP expired for {phone_number}")
            # Clean up expired code
            db.delete(otp_record)
            db.commit()
            return False

        print(f"OTP verified successfully for {phone_number}")
        # Valid OTP - remove it
        db.delete(otp_record)
        db.commit()
        return True

    except Exception as e:
        print(f"Error verifying OTP: {e}")
        db.rollback()
        return False
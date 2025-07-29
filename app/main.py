import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.api.routes import auth, users, products, categories, admin

# Try to import bot
try:
    from app.bot.main import bot_instance

    BOT_AVAILABLE = True
    print("✅ Bot fayllari topildi")
except ImportError as e:
    print(f"⚠️  Bot fayllari topilmadi: {e}")
    print("📝 Bot yaratish uchun: python simple_setup_bot.py")
    BOT_AVAILABLE = False
    bot_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 InBazar API ishga tushirilmoqda...")

    # Only start bot if enabled and available
    should_start_bot = (
        BOT_AVAILABLE and
        bot_instance and
        getattr(settings, 'enable_bot', True)  # Default to True if not set
    )

    if should_start_bot:
        try:
            print("🤖 Starting Telegram bot...")
            await bot_instance.start_bot()
        except Exception as e:
            print(f"❌ Bot ishga tushmadi: {e}")
            print("💡 Bot conflicts can happen if another instance is running")

    yield

    # Shutdown
    if should_start_bot and bot_instance:
        try:
            await bot_instance.stop_bot()
        except Exception as e:
            print(f"❌ Bot to'xtatishda xatolik: {e}")


# Create FastAPI app
app = FastAPI(
    title="InBazar API",
    description="InBazar Kiyim Do'koni API",
    version="1.0.0",
    lifespan=lifespan if BOT_AVAILABLE else None
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # literally all origins
    allow_credentials=False, # required for `*` to work
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


@app.get("/")
def root():
    return {
        "message": "InBazar API",
        "status": "ishlayapti",
        "bot": "mavjud" if BOT_AVAILABLE else "mavjud_emas"
    }


@app.get("/health")
def health():
    return {"status": "sog'lom"}


@app.get("/bot/status")
def bot_status():
    if not BOT_AVAILABLE:
        return {"bot": "mavjud_emas", "setup": "python simple_setup_bot.py"}

    return {
        "bot": "ishlayapti" if (bot_instance and bot_instance.application) else "to'xtagan",
        "username": settings.telegram_bot_username
    }


@app.get("/debug/otp/{phone_number}")
def debug_otp(phone_number: str, db: Session = Depends(get_db)):
    """Debug endpoint to check OTP codes"""
    try:
        from app.models.bot_user import OTPCode
        from datetime import datetime, timezone

        # Format phone number
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number

        # Get all OTP codes for this phone
        otps = db.query(OTPCode).filter(OTPCode.phone_number == phone_number).all()

        now = datetime.now(timezone.utc)

        result = {
            "phone_number": phone_number,
            "current_time": now.isoformat(),
            "otp_codes": []
        }

        for otp in otps:
            result["otp_codes"].append({
                "code": otp.code,
                "created_at": otp.created_at.isoformat(),
                "expires_at": otp.expires_at.isoformat(),
                "is_expired": now > otp.expires_at,
                "time_remaining": str(otp.expires_at - now) if now < otp.expires_at else "expired"
            })

        return result

    except Exception as e:
        return {"error": str(e)}
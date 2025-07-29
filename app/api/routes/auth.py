from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import RequestCodeRequest, RequestCodeResponse, VerifyCodeRequest, TokenResponse
from app.core.telegram import get_telegram_bot_url, verify_otp_code_sync, get_user_by_phone_sync
from app.core.auth import create_access_token
from app.crud import user as user_crud

router = APIRouter()


@router.post("/request-code", response_model=RequestCodeResponse)
async def request_verification_code(request: RequestCodeRequest):
    """Start Telegram OTP verification flow"""
    telegram_url = get_telegram_bot_url()

    return RequestCodeResponse(
        message="Please open Telegram bot and share your phone number to receive verification code.",
        telegram_url=telegram_url
    )


@router.post("/verify-code", response_model=TokenResponse)
async def verify_code(
        request: VerifyCodeRequest,
        db: Session = Depends(get_db)
):
    """Verify OTP code and return access token"""

    # Verify OTP code
    if not verify_otp_code_sync(request.phone_number, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )

    # Check if user exists in main database
    user = user_crud.get_user_by_phone(db, request.phone_number)

    if not user:
        # Try to get user info from bot database and auto-create
        bot_user = get_user_by_phone_sync(request.phone_number)

        if bot_user:
            # Auto-create user from bot data
            from app.schemas.user import UserCreate

            user_data = UserCreate(
                telegram_id=bot_user['telegram_id'],
                phone_number=bot_user['phone_number'],
                full_name=f"{bot_user['first_name'] or ''} {bot_user['last_name'] or ''}".strip(),
                telegram_username=bot_user['username']
            )

            user = user_crud.create_user(db, user_data)
        else:
            # For testing, create a dummy user
            # TODO: Remove this when bot is integrated
            from app.schemas.user import UserCreate

            user_data = UserCreate(
                telegram_id="123456789",  # Dummy telegram ID
                phone_number=request.phone_number,
                full_name="Test User",
                telegram_username=None
            )

            user = user_crud.create_user(db, user_data)

    # Create access token
    access_token = create_access_token(data={"sub": user.telegram_id})

    return TokenResponse(access_token=access_token)
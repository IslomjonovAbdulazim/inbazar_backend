from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import auth, users, products, categories, admin

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Backend API for Clothing Shop with Telegram authentication",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "message": "Clothing Shop API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Health check for monitoring"""
    return {"status": "healthy"}


# Telegram webhook endpoint (for receiving messages from bot)
@app.post("/webhook/telegram")
async def telegram_webhook(update: dict):
    """Handle Telegram webhook for bot interactions"""
    from app.core.telegram import handle_telegram_webhook

    response = await handle_telegram_webhook(update)

    if response:
        # Send response back to user
        return {
            "method": "sendMessage",
            "chat_id": update.get("message", {}).get("chat", {}).get("id"),
            "text": response
        }

    return {"ok": True}
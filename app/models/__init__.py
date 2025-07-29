# Import all models here
from .user import User
from .product import Product
from .category import Category

# Import bot models if they exist
try:
    from .bot_user import BotUser, OTPCode
except ImportError:
    # Bot models not available yet
    pass
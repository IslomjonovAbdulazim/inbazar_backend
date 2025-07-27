# 🧵 Clothing Shop Backend

FastAPI backend for a clothing shop mobile app with Telegram-based authentication.

## 🚀 Features

- **Telegram Authentication**: OTP verification via Telegram bot
- **Product Catalog**: Browse, filter, and search clothing items
- **User Interactions**: Like, bookmark, and track product clicks
- **Admin Panel**: Manage products and categories
- **Supabase Storage**: Image hosting and management
- **PostgreSQL**: Robust data storage

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- Telegram Bot Token
- Supabase account

## 🛠 Installation

1. **Clone and setup**:
   ```bash
   git clone <your-repo>
   cd clothing-shop-backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Database setup**:
   ```bash
   # Create database tables
   python -c "from app.database import engine; from app.models import *; Base.metadata.create_all(bind=engine)"
   ```

4. **Run the application**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 🔧 Configuration

Update `.env` file with your credentials:

- `DATABASE_URL`: PostgreSQL connection string
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_BOT_USERNAME`: Your bot username (without @)
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key
- `SECRET_KEY`: JWT secret key
- `ADMIN_TELEGRAM_ID`: Admin user's Telegram ID

## 📱 Telegram Bot Setup

1. Create bot with [@BotFather](https://t.me/botfather)
2. Set webhook URL: `https://your-domain.com/webhook/telegram`
3. Configure bot commands and menu

## 🚀 Deployment

### Railway Deployment

1. Connect GitHub repository to Railway
2. Add environment variables in Railway dashboard
3. Deploy automatically on push

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📖 API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🏗 Project Structure

```
app/
├── api/
│   ├── routes/          # API endpoints
│   └── deps.py          # Dependencies
├── core/
│   ├── auth.py          # JWT authentication
│   └── telegram.py      # Telegram bot logic
├── crud/                # Database operations
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── utils/               # Helper functions
├── config.py            # Settings
├── database.py          # DB connection
└── main.py              # FastAPI app
```

## 🔐 Authentication Flow

1. User enters phone number in app
2. App calls `/auth/request-code`
3. User opens Telegram bot and shares contact
4. Bot sends 6-digit OTP code
5. User enters code in app
6. App calls `/auth/verify-code` → receives JWT token
7. Use JWT token for authenticated requests

## 👨‍💻 Development

```bash
# Install dev dependencies
pip install pytest httpx

# Run tests
pytest

# Format code
black app/
isort app/

# Type checking
mypy app/
```

## 📝 License

MIT License - feel free to use for your projects!
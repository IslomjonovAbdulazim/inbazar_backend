import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from app.config import settings
from app.bot.handlers import start_handler, contact_handler, text_handler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


class TelegramBot:
    def __init__(self):
        self.application = None

    async def start_bot(self):
        """Start the bot."""
        # Create the Application
        self.application = Application.builder().token(settings.telegram_bot_token).build()

        # Add handlers
        self.application.add_handler(CommandHandler("start", start_handler))
        self.application.add_handler(MessageHandler(filters.CONTACT, contact_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

        # Add error handler
        self.application.add_error_handler(error_handler)

        # Initialize and start polling
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

        print(f"🤖 Bot @{settings.telegram_bot_username} is running...")

    async def stop_bot(self):
        """Stop the bot."""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            print("🤖 Bot stopped.")


# Global bot instance
bot_instance = TelegramBot()


async def run_bot():
    """Run the bot (for standalone execution)."""
    try:
        await bot_instance.start_bot()
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down bot...")
        await bot_instance.stop_bot()


def main():
    """Main entry point for standalone bot execution."""
    asyncio.run(run_bot())


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Setup script for the Telegram bot.
Run this to create the bot directory structure and install dependencies.
"""

import os
import subprocess
import sys


def create_bot_structure():
    """Create bot directory structure"""
    bot_dir = "bot"

    # Create bot directory if it doesn't exist
    if not os.path.exists(bot_dir):
        os.makedirs(bot_dir)
        print(f"✅ Created {bot_dir}/ directory")

    # Create __init__.py file
    init_file = os.path.join(bot_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write('"""Telegram Bot for InBazar Clothing Shop"""\n')
        print(f"✅ Created {init_file}")


def install_bot_dependencies():
    """Install bot dependencies"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot==20.7", "aiosqlite==0.19.0",
                               "python-dotenv==1.0.0"])
        print("✅ Bot dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")


def main():
    print("🤖 Setting up Telegram Bot for InBazar...")

    create_bot_structure()
    install_bot_dependencies()

    print("\n🎉 Bot setup complete!")
    print("\n📝 Next steps:")
    print("1. Make sure you have the bot files in the bot/ directory")
    print("2. Update your .env file with TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_USERNAME")
    print("3. Run the bot: python bot/main.py")
    print("4. Set webhook URL in @BotFather if needed")


if __name__ == "__main__":
    main()
import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

def require_env(env_item) -> str:
    item = os.getenv(env_item)
    if not item:
        raise ValueError(f"{env_item} was not set!")
    return item

ALLOWED_USER = int(require_env("ALLOWED_USER"))
TELEGRAM_BOT_TOKEN = require_env("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.effective_message.reply_html(
        f"Hi {user.mention_html()}!"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(update.effective_message.text)

def main() -> None:
    allowed_user = filters.User(user_id=ALLOWED_USER)
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start, filters=allowed_user))
    application.add_handler(MessageHandler(allowed_user & filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()

if __name__ == "__main__":
    main()
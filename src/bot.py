import logging
import os

from dotenv import load_dotenv
from openai import APIConnectionError, APIError, AsyncOpenAI, RateLimitError
from telegram import Update, constants
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from transcriber import Transcriber

load_dotenv()

def require_env(env_item: str) -> str:
    item = os.getenv(env_item)
    if not item:
        raise ValueError(f"{env_item} was not set!")
    return item

ALLOWED_USER = int(require_env("ALLOWED_USER"))
TELEGRAM_BOT_TOKEN = require_env("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = require_env("OPENAI_API_KEY")
MAX_BYTES = 20 * 1024 * 1024
MIN_SECONDS = 1
MAX_SECONDS = 1500

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=OPENAI_API_KEY, max_retries=2, timeout=60)
transcriber = Transcriber(client=client)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.effective_message.reply_html(
        f"Hi {user.mention_html()}!"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(update.effective_message.text)

async def audio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    voice = update.effective_message.voice

    if voice.duration < MIN_SECONDS:
        await update.effective_message.reply_text("The audio is too short, please try again!")
        return

    if voice.duration > MAX_SECONDS:
        await update.effective_message.reply_text(f"The audio is too long. Max duration is {MAX_SECONDS} sec, please try again!")
        return

    if voice.file_size and voice.file_size > MAX_BYTES:
        await update.effective_message.reply_text("The file is too big!")
        return

    try:
        tg_file = await context.bot.get_file(voice.file_id)
    except BadRequest:
        await update.effective_message.reply_text("Couldn't download the file!")
        return

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=constants.ChatAction.TYPING
    )

    try:
        audio_bytes = bytes(await tg_file.download_as_bytearray())
        if not audio_bytes:
            await update.effective_message.reply_text("The audio came up empty! Try again!")
            return
        transcribed_message = await transcriber.transcribe(audio_bytes)
    except RateLimitError:
        await update.effective_message.reply_text("OpenAI is busy or out of credit, check your balance or try again in a minute.")
        logger.exception("Rate Limit Error")
        return
    except APIConnectionError:
        await update.effective_message.reply_text("API Connection Error!")
        logger.exception("API Connection Error")
        return
    except APIError:
        await update.effective_message.reply_text("OpenAI rejected the API key, check .env")
        logger.exception("API Error")
        return
    except Exception:
        await update.effective_message.reply_text("Something went wrong!")
        logger.exception("Something went wrong")
        return

    if not transcribed_message.strip():
        await update.effective_message.reply_text("There are no words in your message, please try again!")
        logger.warning("The audio message was empty!")
        return
    await update.effective_message.reply_text(transcribed_message)



def main() -> None:
    allowed_user = filters.User(user_id=ALLOWED_USER)
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start, filters=allowed_user))
    application.add_handler(MessageHandler(allowed_user & filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(MessageHandler(allowed_user & filters.VOICE, audio_handler))

    application.run_polling()

if __name__ == "__main__":
    main()
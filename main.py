
import logging
import os

from dotenv import load_dotenv
from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)

# Avoid excessively verbose HTTP request logs.
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def post_init(app: Application) -> None:
    """Register commands shown in Telegram's command menu."""
    await app.bot.set_my_commands([
        BotCommand("start", "Start the assistant"),
        BotCommand("help", "Show available commands"),
        BotCommand("ping", "Check whether the bot is online"),
    ])


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.effective_message:
        await update.effective_message.reply_text(
            "Hi! I'm your personal Telegram assistant.\n\n"
            "Try /help to see what I can do."
        )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.effective_message:
        await update.effective_message.reply_text(
            "Available commands:\n"
            "/start - Start the assistant\n"
            "/help - Show this help message\n"
            "/ping - Check bot status\n\n"
            "You can also send me a text message."
        )


async def ping(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.effective_message:
        await update.effective_message.reply_text("Pong! I'm online.")


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = update.effective_message

    if not message or not message.text:
        return

    text = message.text.strip()
    normalised = text.casefold()

    # Temporary rule-based responses.
    if normalised in {"hi", "hello", "hey"}:
        reply = "Hello! How can I help you today?"
    elif "your name" in normalised:
        reply = "I'm your personal Telegram assistant."
    else:
        reply = (
            "I received your message:\n\n"
            f"{text}\n\n"
            "I'm currently using basic rules. "
            "An AI model can be connected in the next step."
        )

    await message.reply_text(reply)


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    logger.error(
        "Exception while processing an update",
        exc_info=context.error,
    )


def main() -> None:
    if not TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing. Check your .env file."
        )

    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )
    app.add_error_handler(error_handler)

    logger.info("Starting Telegram assistant...")
    app.run_polling()


if __name__ == "__main__":
    main()
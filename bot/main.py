import logging
import os
from json import load

from dotenv import load_dotenv
from telegram import ForceReply, Message, Update, User
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from websockets.sync.client import connect

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

load_dotenv()

if not os.getenv("TELEGRAM_BOT_TOKEN"):
    # os.environ["TELEGRAM_BOT_TOKEN"] = (
    #     open("/run/secrets/TELEGRAM_BOT_TOKEN").read().strip()
    # )
    logger.info("Loading bot configuration from /run/secrets/bot_config")

    os.environ.update(load(open("/run/secrets/bot_config")))

    logger.info("Bot configuration loaded successfully.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user: User = update.effective_user
    message: Message = update.message

    if user.id != int(os.getenv("TELEGRAM_BOT_OWNER_ID", "0")):
        logger.info(f"{os.getenv('TELEGRAM_BOT_OWNER_ID', '0') = }, {type(user.id) = }")
        logger.info(f"Unauthorized access attempt by user {user.id} ({user.username})")
        await message.reply_text("You are not authorized to use this bot.")
        return

    await message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")  # type: ignore


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Connect to agent, send the message and reply with the response."""
    if not update.message or not update.message.text:
        logger.error("No message found in the update.")
        return

    with connect("ws://agent:80/chat") as websocket:
        websocket.send(update.message.text)
        response = str(websocket.recv())
        await update.message.reply_text(response)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()  # type: ignore

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

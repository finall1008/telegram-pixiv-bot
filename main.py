import logging

from telegram.ext import ApplicationBuilder, CommandHandler, InlineQueryHandler

from commands import send_illust, send_illust_file, start
from config import config
from inline import inline_answer

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger("pixiv_bot")


if __name__ == "__main__":
    application = ApplicationBuilder().token(config.TOKEN).build()

    application.add_handler(CommandHandler("getpic", send_illust))
    application.add_handler(CommandHandler("getfile", send_illust_file))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(InlineQueryHandler(inline_answer))

    application.run_polling()

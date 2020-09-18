import logging

from telegram.ext import CommandHandler, Updater

from commands import start, send_illust
from config import config

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger("pixiv_bot")


if __name__ == "__main__":
    updater = Updater(token=config.TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    commands = [("start", "检查运行状态"), ("getpic", "使用 id 获取 pixiv 图片预览及详情")]
    updater.bot.set_my_commands(commands)

    dispatcher.add_handler(CommandHandler("getpic", send_illust))
    dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()
    logger.info(f"Bot @{updater.bot.get_me().username} 已启动")
    updater.idle()

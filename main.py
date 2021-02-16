import logging

from telegram.ext import CommandHandler, Updater

from commands import start, send_illust, send_illust_file
from config import config

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger("pixiv_bot")


if __name__ == "__main__":
    updater = Updater(token=config.TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    commands = [
        ("start", "检查运行状态"),
        ("getpic", "使用 id 获取 pixiv 插画预览及详情"),
        ("getfile", "使用 id 获取 pixiv 插画原图。在非私聊中默认发送第一张，加上 all 参数解除限制")
    ]
    updater.bot.set_my_commands(commands)

    dispatcher.add_handler(CommandHandler(
        "getpic", send_illust, run_async=True))
    dispatcher.add_handler(CommandHandler(
        "getfile", send_illust_file, run_async=True))
    dispatcher.add_handler(CommandHandler("start", start, run_async=True))

    updater.start_polling()
    logger.info(f"Bot @{updater.bot.get_me().username} 已启动")
    updater.idle()

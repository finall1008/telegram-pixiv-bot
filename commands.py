import logging
import os
from io import BytesIO

from telegram import Bot, ParseMode, Update, InputFile, InputMediaPhoto
from telegram.ext.dispatcher import run_async

from illust import Illust
from utilities import origin_link_button
from config import config
from errors import IllustInitError


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger("pixiv_bot")


def start(update, context):
    update.effective_message.reply_text(
        "一个简单的 Pixiv 返图机器人。\nBy @finall_1008\n源代码：https://github.com/finall1008/telegram-pixiv-bot")


def send_illust(update: Update, context):
    try:
        illust_id = int(context.args[0])
    except:
        update.effective_message.reply_text("用法：/getpic $pixiv_id")
        return

    try:
        illust = Illust(illust_id)
    except IllustInitError:
        return

    illust.download()

    images = illust.get_downloaded_images()

    if len(images) > 1:
        bot = Bot(config.TOKEN)
        bot.send_media_group(chat_id=update.effective_chat.id, media=[
                             InputMediaPhoto(BytesIO(image)) for image in images])
        update.effective_message.reply_text(text=str(illust),
                                            reply_markup=origin_link_button(
                                                illust_id),
                                            disable_web_page_preview=True,
                                            parse_mode=ParseMode.HTML)
    else:
        update.effective_message.reply_photo(photo=BytesIO(images[0]),
                                             caption=str(illust),
                                             reply_markup=origin_link_button(
                                                 illust_id),
                                             parse_mode=ParseMode.HTML)

    logger.info(f"成功发送 {illust.id}")


def send_illust_file(update: Update, context):
    try:
        illust_id = int(context.args[0])
    except:
        update.effective_message.reply_text("用法：/getfile $pixiv_id")
        return

    force_send_all = False
    try:
        arg1 = str(context.args[1])
    except:
        pass
    else:
        if arg1 == "all":
            force_send_all = True

    try:
        illust = Illust(illust_id)
    except IllustInitError:
        return

    illust.download_original()

    images = illust.get_downloaded_images()

    if force_send_all or len(images) > 1 and update.effective_chat.type == "private":
        page = 0
        for image in images:
            update.effective_message.reply_document(InputFile(BytesIO(image)))
            page = page + 1
    else:
        update.effective_message.reply_document(InputFile(BytesIO(images[0])))

    logger.info(f"成功发送 {illust.id} 原始文件")

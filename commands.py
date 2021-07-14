import logging
from io import BytesIO

from telegram import ParseMode, Update, InputFile, InputMediaPhoto
from telegram.ext import CallbackContext

from illust import Illust
from utilities import origin_link_button, get_illust_id
from errors import IllustInitError


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger("pixiv_bot")


def start(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        "一个简单的 Pixiv 返图机器人，请通过指令或 inline 来使用。\nBy @finall_1008\n源代码：https://github.com/finall1008/telegram-pixiv-bot")


def send_illust(update: Update, context: CallbackContext):
    illust_id = get_illust_id(context.args[0])
    if illust_id == -1:
        update.effective_message.reply_text("用法：/getpic *Pixiv ID 或链接*")
        return

    try:
        illust = Illust(illust_id)
    except IllustInitError:
        return

    illust.download()

    images = illust.get_downloaded_images()

    if len(images) > 1:
        context.bot.send_media_group(chat_id=update.effective_chat.id, media=[
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


def send_illust_file(update: Update, context: CallbackContext):
    illust_id = get_illust_id(context.args[0])
    if illust_id == -1:
        update.effective_message.reply_text("用法：/getfile *Pixiv ID 或链接*")
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

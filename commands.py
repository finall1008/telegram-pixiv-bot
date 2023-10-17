import logging
from io import BytesIO

from telegram import InputFile, InputMediaPhoto, Update
from telegram.ext import ContextTypes

from errors import IllustInitError
from illust import Illust
from utilities import get_illust_id, origin_link_button

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger("pixiv_bot")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message:
        await update.effective_message.reply_text(
            "一个简单的 Pixiv 返图机器人，请通过指令或 inline 来使用。\nBy @finall_1008\n源代码：https://github.com/finall1008/telegram-pixiv-bot"
        )


async def send_illust(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not update.effective_message or not update.effective_chat:
        return

    illust_id = get_illust_id(context.args[0])
    if not illust_id:
        await update.effective_message.reply_text("用法：/getpic *Pixiv ID 或链接*")
        return

    try:
        illust = await Illust(illust_id).init()
    except IllustInitError:
        return

    images = await illust.download_original()
    if not images:
        logger.exception(f"{update.effective_chat} 请求的 {illust_id} 下载错误")
        return

    r18 = illust.is_r18()

    if len(images) > 1:
        await context.bot.send_media_group(
            chat_id=update.effective_chat.id,
            media=[
                InputMediaPhoto(BytesIO(image[1]), has_spoiler=r18) for image in images
            ],
        )
        await update.effective_message.reply_text(
            text=str(illust),
            reply_markup=origin_link_button(illust_id),
            disable_web_page_preview=True,
            parse_mode="HTML",
        )
    else:
        await update.effective_message.reply_photo(
            photo=BytesIO(images[0][1]),
            caption=str(illust),
            reply_markup=origin_link_button(illust_id),
            parse_mode="HTML",
            has_spoiler=r18,
        )

    logger.info(f"成功发送 {illust.id}")


async def send_illust_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not update.effective_message or not update.effective_chat:
        return

    illust_id = get_illust_id(context.args[0])
    if not illust_id:
        await update.effective_message.reply_text("用法：/getfile *Pixiv ID 或链接*")
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
        illust = await Illust(illust_id).init()
    except IllustInitError:
        return

    images = await illust.download_original()
    if not images:
        logger.exception(f"{update.effective_chat} 请求的 {illust_id} 下载错误")
        return

    if force_send_all or (len(images) > 1 and update.effective_chat.type == "private"):
        page = 0
        for i, (ext, image) in enumerate(images):
            file = InputFile(BytesIO(image), filename=f"{illust_id}_{i}{ext}")
            await update.effective_message.reply_document(file)
            page = page + 1
    else:
        file = InputFile(BytesIO(images[0][1]), filename=f"image{images[0][0]}")
        await update.effective_message.reply_document(file)

    logger.info(f"成功发送 {illust.id} 原始文件")

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
    CallbackContext
)
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    Bot,
    ParseMode
)
from telegram.ext.dispatcher import run_async
from pixivpy_async import AppPixivAPI
import os
from os.path import join, getsize
import json
import sys
import logging
import asyncio

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger("pixiv_bot")


def origin_link(_id: int):
    return InlineKeyboardMarkup([[InlineKeyboardButton(text="原链接", url=f"https://www.pixiv.net/artworks/{_id}")]])


def start(update, context):
    update.effective_message.reply_text(
        "一个简单的 Pixiv 返图机器人。\nBy @finall_1008\n源代码：https://github.com/finall1008/telegram-pixiv-bot")


def parse_tags_text(tags: list) -> str:
    text = str()
    for tag in tags:
        text = text + \
            f"[{tag.name}\({tag.translated_name}\)](https://www.pixiv.net/tags/{tag.name}/artworks) "
    return text


async def download_single_pic(url: str, _id: int, size: str, page: int, aapi: AppPixivAPI):
    url_basename = os.path.basename(url)
    extension = os.path.splitext(url_basename)[1]
    name = f"{_id}_p{page}_{size}{extension}"
    try:
        os.mkdir(f"{DOWNLOAD_PATH}/{_id}")
    except FileExistsError:
        pass
    await aapi.download(url, path=DOWNLOAD_PATH + "/" + str(_id), name=name)
    logger.info(f"成功下载 {name}")


def download_pic(urls: list, _id: int, size: str, aapi: AppPixivAPI):
    page = 0
    loop = asyncio.new_event_loop()
    tasks = list()
    for url in urls:
        tasks.append(download_single_pic(url, _id, size, page, aapi))
        # download_single_pic(url, _id, size, page, aapi)
        page = page + 1
    loop.run_until_complete(asyncio.gather(*tasks, loop=loop))
    loop.close()
    logger.info(f"成功下载 {_id} 全部图片")


async def parse_illust_info_msg(illust_id: int, aapi: AppPixivAPI):
    json_result = await aapi.illust_detail(illust_id)
    info = json_result.illust
    caption = str()
    if info.caption != "":
        caption = "\n" + info.caption
    msg_text = f"**标题：**{info.title}\n**作者：**[{info.user.name}](https://www.pixiv.net/users/{info.user.id}){caption}\n**标签：**{parse_tags_text(info.tags)}"
    logger.info(msg_text)

    if info.page_count == 1:
        illust_urls = [info.image_urls.large]
    else:
        illust_urls = [page.image_urls.large for page in info.meta_pages]
    return illust_urls, illust_id, msg_text


def get_dir_size(dir):
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([getsize(join(root, name)) for name in files])
    return size


@run_async
def send_illust_info(update, context):
    if get_dir_size(DOWNLOAD_PATH) >= DOWNLOAD_SIZE:
        for sub_dir in os.listdir(DOWNLOAD_PATH):
            for filename in os.listdir(f"{DOWNLOAD_PATH}/{sub_dir}"):
                os.remove(f"{DOWNLOAD_PATH}/{sub_dir}/" + filename)
            os.removedirs(sub_dir)
        logger.info("已清除下载目录")

    illust_id = int(context.args[0])
    # msg_text = parse_illust_info_msg(illust_id, aapi)
    loop = asyncio.new_event_loop()
    illust_urls, illust_id, msg_text = loop.run_until_complete(
        parse_illust_info_msg(illust_id, aapi))
    loop.close()
    download_pic(illust_urls, illust_id, "large", aapi)
    file_dirs = [DOWNLOAD_PATH+f"/{illust_id}/" +
                 filename for filename in os.listdir(DOWNLOAD_PATH+f"/{illust_id}")]
    if len(file_dirs) == 1:
        update.effective_message.reply_photo(photo=open(file_dirs[0], 'rb'),
                                             caption=msg_text, reply_markup=origin_link(illust_id), parse_mode=ParseMode.MARKDOWN_V2)
    else:
        bot = Bot(TOKEN)
        for file_dir in file_dirs:
            bot.send_photo(chat_id=update.effective_chat.id,
                           photo=open(file_dir, 'rb'))
        update.effective_message.reply_text(text=msg_text,
                                            reply_markup=origin_link(
                                                illust_id),
                                            parse_mode=ParseMode.MARKDOWN_V2,
                                            disable_web_page_preview=True)


async def init_appapi(aapi: AppPixivAPI):
    try:
        await aapi.login(username=USERNAME, password=PASSWORD)
    except:
        logger.exception("Pixiv 登陆失败")
        sys.exit(1)
    logger.info("成功登录 Pixiv")
    aapi.set_accept_language("zh-CN")


if __name__ == "__main__":
    with open('config.json', 'r') as file:
        config = json.load(file)

    try:
        TOKEN = config["token"]
    except:
        logger.exception(f"非法的 token")
        sys.exit(1)

    try:
        USERNAME = config["username"]
    except:
        logger.exception(f"非法的用户名")
        sys.exit(1)

    try:
        PASSWORD = config["password"]
    except:
        logger.exception(f"非法的密码")
        sys.exit(1)

    try:
        DOWNLOAD_PATH = config["download_path"]
    except:
        logger.info("非法的下载路径，使用当前目录/Download")
        try:
            os.mkdir("Download")
        except FileExistsError:
            pass
        DOWNLOAD_PATH = os.curdir+"/Download"
    else:
        try:
            os.mkdir(DOWNLOAD_PATH)
        except FileExistsError:
            pass

    try:
        DOWNLOAD_SIZE = config["download_size"]
    except:
        logger.exception(f"非法的下载路径大小")
        sys.exit(1)

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    aapi = AppPixivAPI()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(init_appapi(aapi))
    loop.close()

    commands = [("start", "检查运行状态"), ("getpic", "使用 id 获取 pixiv 图片预览及详情")]
    updater.bot.set_my_commands(commands)

    dispatcher.add_handler(CommandHandler("getpic", send_illust_info))

    updater.start_polling()
    logger.info(f"Bot @{updater.bot.get_me().username} 已启动")
    updater.idle()

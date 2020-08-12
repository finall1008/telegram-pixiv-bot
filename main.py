from telegram.ext import (
    CommandHandler,
    Updater,
)
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    Bot,
    ParseMode,
    InputMediaPhoto
)
from telegram.ext.dispatcher import run_async
from telegram.error import NetworkError
from pixivpy_async import AppPixivAPI
import os
from os.path import join, getsize
import json
import sys
import logging
import asyncio
from bs4 import BeautifulSoup

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
        if tag.translated_name:
            translated_name = f"({tag.translated_name})"
        else:
            translated_name = ""
        text = text + \
            f"<a href=\"https://www.pixiv.net/tags/{tag.name}/artworks\">{tag.name}{translated_name}</a> "
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
        soup = BeautifulSoup(info.caption, "html.parser")
        caption = "\n" + soup.get_text()
    msg_text = f"<b>标题：</b>{info.title}\n<b>作者：</b><a href=\"https://www.pixiv.net/users/{info.user.id}\">{info.user.name}</a>{caption}\n<b>标签：</b>{parse_tags_text(info.tags)}"
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
    loop = asyncio.new_event_loop()
    login_result = loop.run_until_complete(init_appapi(aapi))
    loop.close()
    if not login_result:
        return

    if get_dir_size(DOWNLOAD_PATH) >= DOWNLOAD_SIZE:
        for sub_dir in os.listdir(DOWNLOAD_PATH):
            for filename in os.listdir(f"{DOWNLOAD_PATH}/{sub_dir}"):
                os.remove(f"{DOWNLOAD_PATH}/{sub_dir}/" + filename)
            os.removedirs(sub_dir)
        logger.info("已清除下载目录")

    try:
        illust_id = int(context.args[0])
    except:
        update.effective_message.reply_text("用法：/getpic $pixiv_id")
        return
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
                                             caption=msg_text,
                                             reply_markup=origin_link(
                                                 illust_id),
                                             parse_mode=ParseMode.HTML)
    else:
        bot = Bot(TOKEN)
        tmp_sub_file_group = list()
        tmp_size = 0
        sub_file_groups = list()
        for file_dir in file_dirs:
            if tmp_size + os.path.getsize(file_dir) <= 5242880 and len(tmp_sub_file_group) + 1 <= 10:
                tmp_sub_file_group.append(InputMediaPhoto(media=open(file_dir, 'rb'),
                                                          caption=msg_text,
                                                          parse_mode=ParseMode.HTML))
            else:
                sub_file_groups.append(tmp_sub_file_group)
                tmp_sub_file_group = [InputMediaPhoto(media=open(file_dir, 'rb'),
                                                      caption=msg_text,
                                                      parse_mode=ParseMode.HTML)]
                tmp_size = os.path.getsize(file_dir)
        sub_file_groups.append(tmp_sub_file_group)
        for sub_file_group in sub_file_groups:
            bot.send_media_group(chat_id=update.effective_chat.id,
                                 media=sub_file_group)
        update.effective_message.reply_text(text=msg_text,
                                            reply_markup=origin_link(
                                                illust_id),
                                            disable_web_page_preview=True,
                                            parse_mode=ParseMode.HTML)


async def init_appapi(aapi: AppPixivAPI):
    try:
        await aapi.login(username=USERNAME, password=PASSWORD)
    except:
        logger.exception("Pixiv 登陆失败")
        return False
    logger.info("成功登录 Pixiv")
    aapi.set_accept_language("zh-CN")
    return True


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
        if DOWNLOAD_PATH == "":
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
            except:
                logger.exception("下载路径不可用")
                sys.exit(1)

    try:
        DOWNLOAD_SIZE = config["download_size"]
    except:
        logger.exception(f"非法的下载路径大小")
        sys.exit(1)

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    aapi = AppPixivAPI()
    # loop = asyncio.new_event_loop()
    # loop.run_until_complete(init_appapi(aapi))
    # loop.close()

    commands = [("start", "检查运行状态"), ("getpic", "使用 id 获取 pixiv 图片预览及详情")]
    updater.bot.set_my_commands(commands)

    dispatcher.add_handler(CommandHandler("getpic", send_illust_info))
    dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()
    logger.info(f"Bot @{updater.bot.get_me().username} 已启动")
    updater.idle()

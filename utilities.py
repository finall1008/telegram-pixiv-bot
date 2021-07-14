import os
from os.path import getsize, join
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_dir_size(dir) -> int:
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([getsize(join(root, name)) for name in files])
    return size


def origin_link_button(_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(text="原链接", url=f"https://www.pixiv.net/artworks/{_id}")]])


def get_illust_id(text: str) -> int:
    try:
        illust_id = int(text)
    except:
        pass
    else:
        return illust_id if len(text) >= 7 else -1

    reg = r"pixiv.net"
    if re.search(reg, text):
        try:
            return int(re.search(r"[1-9][0-9]{7,}", text).group())
        except:
            return -1
    else:
        return -1

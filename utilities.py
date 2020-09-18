import os
from os.path import getsize, join

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_dir_size(dir) -> int:
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([getsize(join(root, name)) for name in files])
    return size


def origin_link_button(_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(text="原链接", url=f"https://www.pixiv.net/artworks/{_id}")]])

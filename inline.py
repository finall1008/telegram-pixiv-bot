import logging
from uuid import uuid4

from telegram.parsemode import ParseMode
from telegram.inline.inputtextmessagecontent import InputTextMessageContent
from telegram import Update, InlineQueryResultPhoto, InlineQueryResultArticle
from telegram.ext import CallbackContext

from illust import Illust
from utilities import get_illust_id, origin_link_button


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger("pixiv_bot")


def inline_answer(update: Update, context: CallbackContext):
    query = update.inline_query.query
    if not query:
        return

    illust_id = get_illust_id(query)
    if illust_id == -1:
        context.bot.answer_inline_query(
            update.inline_query.id,
            [InlineQueryResultArticle(
                id=str(uuid4()),
                title="输入错误，请输入 Pixiv ID 或链接",
                input_message_content=InputTextMessageContent(
                    "输入错误，请输入 Pixiv ID 或链接")
            )]
        )
        return
    print(illust_id)

    try:
        illust = Illust(illust_id)
    except:
        return

    results = []
    for index in range(len(illust.mid_urls)):
        results.append(
            InlineQueryResultPhoto(
                id=str(uuid4()),
                caption=str(illust),
                reply_markup=origin_link_button(illust_id),
                title=illust_id,
                description=str(illust),
                photo_url=illust.mid_urls[index],
                thumb_url=illust.thumb_urls[index],
                parse_mode=ParseMode.HTML
            )
        )

    context.bot.answer_inline_query(update.inline_query.id, results)

    logger.info(f"成功返回 inline 结果 {illust.id}")

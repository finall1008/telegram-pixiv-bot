import logging
from uuid import uuid4

from telegram import (
    Update,
    InlineQueryResultPhoto,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.ext import ContextTypes

from illust import Illust
from utilities import get_illust_id, origin_link_button


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger("pixiv_bot")


async def inline_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.inline_query:
        return
    query = update.inline_query.query
    if not query:
        return

    illust_id = get_illust_id(query)
    if not illust_id:
        await context.bot.answer_inline_query(
            update.inline_query.id,
            [
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="输入错误，请输入 Pixiv ID 或链接",
                    input_message_content=InputTextMessageContent(
                        "输入错误，请输入 Pixiv ID 或链接"
                    ),
                )
            ],
        )
        return

    try:
        illust = await Illust(illust_id).init()
    except:
        return

    results = []
    for index in range(len(illust.mid_urls)):
        results.append(
            InlineQueryResultPhoto(
                id=str(uuid4()),
                caption=str(illust),
                reply_markup=origin_link_button(illust_id),
                title=str(illust_id),
                description=str(illust),
                photo_url=illust.mid_urls[index],
                thumbnail_url=illust.thumb_urls[index],
                parse_mode="HTML",
            )
        )

    await context.bot.answer_inline_query(
        update.inline_query.id, results, cache_time=600
    )

    logger.info(f"成功返回 inline 结果 {illust.id}")

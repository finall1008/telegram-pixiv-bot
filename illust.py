import asyncio
import logging
from typing import Self

from bs4 import BeautifulSoup
from pixivpy_async import AppPixivAPI

from config import config
from errors import DownloadError, GetInfoError, LoginError

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger("pixiv_bot")


class Illust:
    aapi = AppPixivAPI(env=True)

    async def init_appapi(self) -> bool:
        try:
            await self.aapi.login(refresh_token=config.REFRESH_TOKEN)
        except:
            return False
        self.aapi.set_accept_language("zh-CN")
        return True

    async def get_info(self) -> bool:
        try:
            json_result = await self.aapi.illust_detail(self.id)
        except:
            return False

        info = json_result.illust
        if not info:
            return False

        self.caption = str()
        if info.caption != "":
            soup = BeautifulSoup(info.caption, "html.parser")
            self.caption = "\n" + soup.get_text()

        self.title = info.title
        self.author = (info.user.name, info.user.id)

        self.tags = [(tag.name, tag.translated_name) for tag in info.tags]

        if info.page_count == 1:
            self.thumb_urls = [info.image_urls.square_medium]
            self.mid_urls = [info.image_urls.medium]
            self.urls = [info.image_urls.large]
            self.original_urls = [info.meta_single_page.original_image_url]
        else:
            self.thumb_urls = [
                page.image_urls.square_medium for page in info.meta_pages
            ]
            self.mid_urls = [page.image_urls.medium for page in info.meta_pages]
            self.urls = [page.image_urls.large for page in info.meta_pages]
            self.original_urls = [page.image_urls.original for page in info.meta_pages]

        return True

    def __init__(self, illust_id: int) -> None:
        self.caption: str
        self.title: str
        self.author: tuple[str, int]
        self.tags: list[tuple[str, str]]
        self.thumb_urls: list[str]
        self.mid_urls: list[str]
        self.urls: list[str]
        self.original_urls: list[str]
        self.id: int = illust_id
        self.__images: list[tuple[int, bytes]] = list()

    async def init(self) -> Self:
        login_result = await self.init_appapi()
        if not login_result:
            logger.exception("Pixiv 登录失败")
            raise LoginError()
        logger.info("Pixiv 登录成功")

        get_info_result = await self.get_info()
        if not get_info_result:
            logger.exception("插画信息获取失败")
            raise GetInfoError()

        return self

    def __str__(self):
        tags_text = str()
        for tag in self.tags:
            tags_text = (
                tags_text
                + f'<a href="https://www.pixiv.net/tags/{tag[0]}/artworks">{tag[0]}</a>'
            )
            if tag[1]:
                tags_text = tags_text + f" ({tag[1]})"
            tags_text = tags_text + ", "

        return f'<b>标题：</b>{self.title}\n<b>作者：</b><a href="https://www.pixiv.net/users/{self.author[1]}">{self.author[0]}</a>\n<b>简介：</b>{self.caption}\n<b>标签：</b>{tags_text}'

    async def __download_single_image(
        self, url: str, size_hint: str, page_hint: int
    ) -> None:
        tp: str
        content: bytes
        try:
            result = []
            #! aapi.down 是一个返回 AsyncGenerator 的 Coroutine，类型检查有误
            async for v in await self.aapi.down(url, "https://app-api.pixiv.net/", True):  # type: ignore
                result.append(v)
            tp, content = result
        except:
            logger.exception(f"{self.id} {size_hint} 第 {page_hint} 张下载错误")
            raise DownloadError

        if tp is not None and tp.find("image") != -1:
            self.__images.append((page_hint, content))
        else:
            logger.exception(f"{self.id} {size_hint} 第 {page_hint} 张下载错误")
            raise DownloadError

        logger.info(f"成功下载 {self.id} {size_hint} 第 {page_hint} 张")

    async def __download_images(self, original: bool = False) -> None:
        page = 0

        if not original:
            urls = self.urls
            size_hint = "large"
        else:
            urls = self.original_urls
            size_hint = "original"

        tasks = list()
        for url in urls:
            tasks.append(self.__download_single_image(url, size_hint, page))
            page = page + 1

        try:
            await asyncio.gather(*tasks)
        except DownloadError:
            pass

        logger.info(f"成功下载 {self.id} 全部 {size_hint} 图片")

    async def download(self) -> list[bytes]:
        await self.__download_images()
        return self.get_downloaded_images()

    async def download_original(self) -> list[bytes]:
        await self.__download_images(True)
        return self.get_downloaded_images()

    def get_downloaded_images(self) -> list[bytes]:
        if not len(self.__images):
            return []

        self.__images.sort(key=lambda elem: elem[0])

        return [elem[1] for elem in self.__images[:9]]

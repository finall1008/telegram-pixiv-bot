import asyncio
import logging

from bs4 import BeautifulSoup
from pixivpy_async import AppPixivAPI
from pixivpy_async.net import Net

from config import config
from errors import DownloadError, GetInfoError, LoginError

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger("pixiv_bot")


class Illust:

    aapi = AppPixivAPI()

    def __init__(self, illust_id: int):
        async def init_appapi() -> bool:
            try:
                await self.aapi.login(username=config.USERNAME, password=config.PASSWORD)
            except:
                return False
            self.aapi.set_accept_language("zh-CN")
            return True

        async def get_info() -> bool:
            try:
                json_result = await self.aapi.illust_detail(self.id)
            except:
                return False

            info = json_result.illust

            self.caption = str()
            if info.caption != "":
                soup = BeautifulSoup(info.caption, "html.parser")
                self.caption = "\n" + soup.get_text()

            self.title = info.title
            self.author = (info.user.name, info.user.id)

            self.tags = [(tag.name, tag.translated_name) for tag in info.tags]

            if info.page_count == 1:
                self.urls = [info.image_urls.large]
            else:
                self.urls = [
                    page.image_urls.large for page in info.meta_pages]

            return True

        loop = asyncio.new_event_loop()
        login_result = loop.run_until_complete(init_appapi())
        loop.close()
        if not login_result:
            logger.exception("Pixiv 登录失败")
            raise LoginError
        logger.info("Pixiv 登录成功")

        self.id: int = illust_id

        self.__images: list = list()

        loop = asyncio.new_event_loop()
        get_info_result = loop.run_until_complete(get_info())
        loop.close()
        if not get_info_result:
            logger.exception("插画信息获取失败")
            raise GetInfoError

    def __str__(self):
        tags_text = str()
        for tag in self.tags:
            tags_text = tags_text + \
                f"<a href=\"https://www.pixiv.net/tags/{tag[0]}/artworks\">{tag[0]}</a>"
            if tag[1]:
                tags_text = tags_text + f" ({tag[1]})"
            tags_text = tags_text+", "

        return f"<b>标题：</b>{self.title}\n<b>作者：</b><a href=\"https://www.pixiv.net/users/{self.author[1]}\">{self.author[0]}</a>\n<b>简介：</b>{self.caption}\n<b>标签：</b>{tags_text}"

    async def __download_single_image(self, url: str, size_hint: str, page_hint: int):
        try:
            content, type = await self.aapi.down(url, "https://app-api.pixiv.net/")
        except:
            logger.exception(f"{self.id} {size_hint} 第 {page_hint} 张下载错误")
            raise DownloadError

        if type is not None and type.find("image") != -1:
            self.__images.append(content)
        else:
            logger.exception(f"{self.id} {size_hint} 第 {page_hint} 张下载错误")
            raise DownloadError

        logger.info(f"成功下载 {self.id} {size_hint} 第 {page_hint} 张")

    def download(self):
        page = 0
        loop = asyncio.new_event_loop()

        tasks = list()
        for url in self.urls:
            tasks.append(self.__download_single_image(url, "large", page))
            page = page + 1

        try:
            loop.run_until_complete(asyncio.gather(*tasks, loop=loop))
        except DownloadError:
            pass
        finally:
            loop.close()

        logger.info(f"成功下载 {self.id} 全部 Large 图片")

    def get_downloaded_images(self):
        if not len(self.__images):
            return None

        return self.__images[:9] if len(self.__images) > 10 else self.__images

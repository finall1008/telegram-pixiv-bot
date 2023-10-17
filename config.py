import json
import logging
import sys
from typing import TypedDict

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger("pixiv_bot")


class ConfigDict(TypedDict):
    token: str
    refresh_token: str


class Config:
    def __init__(self):
        with open("config.json", "r") as file:
            config: ConfigDict = json.load(file)

        try:
            self.TOKEN = config["token"]
        except:
            logger.exception(f"非法的 token")
            sys.exit(1)

        try:
            self.REFRESH_TOKEN = config["refresh_token"]
        except:
            logger.exception(f"非法的 refresh_token。如果您不知道这是什么，请查看文档")
            sys.exit(1)


config = Config()

# telegram-pixiv-bot
[![Require: Python 3.8](https://img.shields.io/badge/Python-3.8-blue)](https://www.python.org/)
[![Require: python-telegram-bot >= 12.8](https://img.shields.io/badge/python--telegram--bot-%3E%3D%2012.6.1-blue)](https://github.com/python-telegram-bot/python-telegram-bot)


一个简单的 Pixiv 返图机器人。

## 部署

```shell
git clone https://github.com/finall1008/telegram-pixiv-bot
cd telegram-pixiv-bot
pip install -r requirements.txt
# 编辑 config.json
python main.py
```

## 使用

在群组中或与机器人私聊：`/getpic $pixiv_id`

## 配置

~~`download_path`: 图片下载路径，未指定则使用当前路径/Download~~

~~`download_size`: 下载目录大小，默认为 500 MB，超过该大小则会自动清空该目录~~

新版本不再下载文件到本地目录，以上配置项目不再需要

## Licence

![GitHub](https://img.shields.io/github/license/finall1008/telegram-pixiv-bot)
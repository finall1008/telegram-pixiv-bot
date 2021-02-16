# telegram-pixiv-bot
[![Require: Python 3.8](https://img.shields.io/badge/Python-3.8-blue)](https://www.python.org/)
[![Require: python-telegram-bot >= 13.2](https://img.shields.io/badge/python--telegram--bot-%3E%3D%2013.2-blue)](https://github.com/python-telegram-bot/python-telegram-bot)


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

在群组中或与机器人私聊：

- `/getpic $pixiv_id`：获取插画全部分 P 的预览和详情，包括标题、作者、简介和标签
- `/getfile $pixiv_id (all)`：获取插画的原始图片。在群聊中默认只发送第一张，增加 `all` 参数来解除这个限制

## 配置

`refresh_token`：Pixiv 登录必须使用的参数。请参考[此处](https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362)获取，或者，参考[本人翻译的中文版本](docs/get_refresh_token.md)。

## Licence

![GitHub](https://img.shields.io/github/license/finall1008/telegram-pixiv-bot)

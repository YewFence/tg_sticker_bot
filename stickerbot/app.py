"""
应用装配与启动

- 负责：日志配置、创建 Application、注册各类 Handler、启动轮询
- 保留自原始 main.py 的注释：
- 开启日志，这在调试时非常有用
- run_polling() 会开始不断地从 Telegram "拉取" 新消息
"""

import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from .config import API_TOKEN
from .handlers.start import start
from .handlers.mention import mention_reply
from .handlers.stickers import sticker_echo
from .handlers.get import get_sticker_set


def build_application():
    # 开启日志，这在调试时非常有用
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # 创建 Application
    application = ApplicationBuilder().token(API_TOKEN).build()

    # 注册处理器 (Handlers)
    # 告诉机器人，当收到 /start 命令时，调用 start 函数启动
    application.add_handler(CommandHandler('start', start))

    # 当文本中出现 @机器人 时，给出使用提示
    application.add_handler(MessageHandler(
        filters.TEXT & (~filters.COMMAND), mention_reply))

    # 告诉机器人，当收到“贴纸”消息时，调用 sticker_echo 函数
    # 仅在私聊中生效：限制为 ChatType.PRIVATE
    application.add_handler(
        MessageHandler(
            filters.Sticker.ALL & filters.ChatType.PRIVATE,
            sticker_echo
        )
    )

    # 告诉机器人，当收到 /get 命令时，调用 get_sticker_set 函数
    application.add_handler(CommandHandler('get', get_sticker_set))

    return application


def run() -> None:
    application = build_application()
    # 启动机器人
    # run_polling() 会开始不断地从 Telegram "拉取" 新消息
    print("Bot启动中... 按 Ctrl+C 停止")
    application.run_polling()

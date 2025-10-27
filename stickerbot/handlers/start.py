"""
/start 命令处理器。

- 1. 定义 /start 命令的处理函数
- 当用户发送 /start 时，机器人回复这条消息
"""

from textwrap import dedent
from telegram import Update
from telegram.ext import ContextTypes
from ..utils.bot import send_message


# 1. 定义 /start 命令的处理函数
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """当用户发送 /start 时，机器人回复这条消息"""
    # update 对象包含了这条消息的所有信息，比如是谁发的
    user = update.effective_user
    raw_message = f"""
                你好, {user.first_name}! 欢迎你！
                在私聊里发给我一个表情包，我会告诉你它的信息然后把它发回给你！
                使用/get命令去‘回复’某个贴纸，我会批量下载它的表情包集。"""
    message = dedent(raw_message)  # 去除多余的缩进
    send_message(context, text=message)

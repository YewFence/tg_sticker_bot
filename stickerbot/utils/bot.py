"""
与 Bot 相关的通用工具。

- 获取并缓存机器人的用户名发送消息等辅助功能
- 发送消息的封装,带有错误处理
"""

import logging
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# 辅助：获取并缓存机器人的用户名，避免每次都请求 get_me


async def get_bot_username(context: ContextTypes.DEFAULT_TYPE) -> str:
    bot_data = context.application.bot_data
    username = bot_data.get("bot_username")
    if username:
        return username
    me = await context.bot.get_me()
    username = me.username or ""
    bot_data["bot_username"] = username
    logger.info(f"Bot username 缓存为: @{username}")
    return username


async def send_message(context: ContextTypes.DEFAULT_TYPE, text: str, **kwargs):
    try:
        message = await context.bot.send_message(
            chat_id=context.effective_chat.id,
            text=text,
            **kwargs
        )
    except Exception as e:
        logger.error(f"发送消息时出错: {e}")

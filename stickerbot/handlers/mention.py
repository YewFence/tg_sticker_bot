"""
@ 提示处理器。

- 当在群聊中有人 @机器人 时，给出提示信息。
- 仅在文本消息中处理，忽略命令消息，避免与其他指令冲突。
"""

import logging
from telegram.ext import ContextTypes
from telegram import Update

from ..utils.bot import get_bot_username

logger = logging.getLogger(__name__)


async def mention_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """当在群聊中有人 @机器人 时，给出提示信息。
    仅在文本消息中处理，忽略命令消息，避免与其他指令冲突。
    """
    message = update.effective_message
    if not message:
        return
    # 忽略命令，避免在 /get@botname 这类命令时重复响应
    if message.text and message.text.startswith("/"):
        return

    text = (message.text or message.caption or "").casefold()
    if not text:
        return
    
    username = await get_bot_username(context)
    if not username:
        return

    at_me = f"@{username}".casefold()
    if at_me not in text:
        return
    # 提示信息，可按需调整
    hint = (
        "👋 我在呢！\n"
        "用 /get 去‘回复’某个贴纸，我会批量下载它的表情包集。"
    )
    await message.reply_text(hint)


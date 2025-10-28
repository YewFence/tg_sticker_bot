"""
贴纸处理相关：
- 打印贴纸/贴纸集信息
- 回显贴纸
"""

import logging
import pprint
from telegram import Update
from telegram.ext import ContextTypes
from ..utils.bot import send_message

logger = logging.getLogger(__name__)


def _print_sticker_set_info(sticker) -> None:
    """辅助函数：格式化贴纸集信息为字符串并打印"""
    # 1. 转换成字典
    sticker_as_dict = sticker.to_dict()
    # 2. (核心) 使用 pprint.pformat() 把它格式化成一个漂亮的字符串
    #    indent=2 表示用2个空格来缩进
    pretty_string = pprint.pformat(sticker_as_dict, indent=2)
    # 3. 用 logger.info() 打印这个格式化后的字符串
    logger.info(f"--- Stickers ---\n{pretty_string}")


async def sticker_echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """响应用户发送的贴纸消息"""
    try:
        # 1. 获取收到的贴纸对象
        sticker_received = update.message.sticker
        sticker_set_name = sticker_received.set_name or ""
        if sticker_set_name:
            # 2. 如果它属于一个表情包集，获取表情包集信息
            sticker_set = await context.bot.get_sticker_set(sticker_set_name)
            # 3. 打印表情包集信息
            _print_sticker_set_info(sticker_set)
            sticker_count = len(sticker_set.stickers)
            sticker_message = f"属于表情包集: {sticker_set_name}，它包含 {sticker_count} 个表情包。"
        else:
            # 2. 如果不属于任何表情包集，返回提示信息
            sticker_message = "但是它不属于任何表情包集捏。"

        # 3. 编辑回复信息
        message = f"我收到了你的表情包！它的id是: {sticker_received.file_id}\n{sticker_message}"
        # 4. 发送回复
        send_message(context, text=message)
        # 5. 把贴纸发回去
        await context.bot.send_sticker(
            chat_id=update.effective_chat.id,
            sticker=sticker_received.file_id
        )
        send_message(context, text="这是我给你回传的表情包！它真有意思，对吧？")
    except Exception as e:
        logger.error(f"处理贴纸时出错: {e}")
        send_message(context, text="坏了，我好像没法处理这个表情包诶。")


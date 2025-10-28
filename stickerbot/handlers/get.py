"""
/get 命令处理器：
- 要求在群聊中用 /get 去"回复"一条包含贴纸的消息
- 下载该贴纸所属的整个表情包集
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from ..utils.downloader import download_sticker_set_files
from ..utils.bot import send_message

logger = logging.getLogger(__name__)


async def get_sticker_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """响应get命令里回复消息中的贴纸"""
    logger.info("收到了 /get 命令，开始检查...")
        
    # 4. 关键检查：这条 /get 命令是否在 '回复' 另一条消息？
    replied_message = update.message.reply_to_message
    
    if not replied_message:
        # 如果没有回复任何消息
        send_message(context, text="⚠️ 使用方法错误！\n请用 /get 这条命令去回复一个你想下载的表情包。")
        return

    # 5. 关键检查：被回复的那条消息是不是一个表情包？
    sticker_received = replied_message.sticker
    if not sticker_received:
        # 如果回复了，但回复的不是表情包
        send_message(context, text="⚠️ 你回复的不是一个表情包哦！\n请用 /get 回复一个表情包。")
        return

    # 获取表情包集信息
    set_name = sticker_received.set_name
    if not set_name:
        send_message(context,text="这个贴纸不属于公开表情包集，暂时无法批量下载。")
        return
    sticker_set = await context.bot.get_sticker_set(set_name)
    # 6. 关键步骤：下载贴纸
    await download_sticker_set_files(sticker_set, update, context)


"""
贴纸处理相关：
- 打印贴纸/贴纸集信息
- 回显贴纸
- 下载整个贴纸集
"""

import os
import logging
import pprint
from telegram import Update
from telegram.ext import ContextTypes
from ..config import DOWNLOAD_DIR
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


async def download_sticker_set_files(sticker_set, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """辅助函数：下载贴纸集中的所有贴纸文件"""
    title = sticker_set.title
    set_name = sticker_set.name
    total_stickers = len(sticker_set.stickers)
    logger.info(f"准备下载表情包集: {title} (名称: {set_name})，共 {total_stickers} 张表情。")
    # 1. 创建一个下载目录
    # 用 set_name 作为文件夹名，因为它唯一且合法
    download_dir = os.path.join(DOWNLOAD_DIR, set_name)
    # 检查文件夹是否存在，如果不存在，就创建它
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        logger.info(f"创建了新目录: {download_dir}")
    # 提示信息
    send_message(context, text=f"开始下载 {title} (共 {total_stickers} 张)... 这可能需要一点时间。")
    # 2. 遍历包里的所有表情（下载整个集合）
    download_count = 0
    for i, sticker_in_set in enumerate(sticker_set.stickers):
        file_id = sticker_in_set.file_id
        # 3. 获取文件对象
        file = await context.bot.get_file(file_id)
        # 打印看看 file 对象长什么样
        logger.info(f"文件对象长这样: {pprint.pformat(file.to_dict())}")
        # 只取最后的文件名
        file_name = os.path.basename(file.file_path)
        local_path = os.path.join(download_dir, file_name)

        # 下载并保存
        await file.download_to_drive(custom_path=local_path)

        download_count += 1
        # 每下载10个，在日志里说一声
        if (download_count % 10 == 0) or (download_count == total_stickers):
            logger.info(f"已下载 {download_count} / {total_stickers} 张...")

    # 6. 全部下载完成后，给用户一个最终回复
    send_message(context, text=f"✅ 下载完成！\n包名: {title}\n总共 {download_count} 张表情已保存到服务器。")


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


"""
下载贴纸集相关工具函数
"""

import os
import logging
import pprint
from telegram import Update
from telegram.ext import ContextTypes
from ..config import DOWNLOAD_DIR, TEST_MODE, DOWNLOAD_LIMIT
from .bot import send_message

logger = logging.getLogger(__name__)


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
        if TEST_MODE and i >= DOWNLOAD_LIMIT:
            logger.info(f"测试模式下，已达到下载上限 {DOWNLOAD_LIMIT}，停止下载。")
            break
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

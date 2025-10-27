import logging
import pprint
import os
from textwrap import dedent
from dotenv import load_dotenv  # 导入 load_dotenv 用于加载环境变量
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# 加载 .env 文件中的环境变量
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR") or "sticker_downloads"

# 开启日志，这在调试时非常有用
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 1. 定义 /start 命令的处理函数
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """当用户发送 /start 时，机器人回复这条消息"""
    # update 对象包含了这条消息的所有信息，比如是谁发的
    user = update.effective_user
    raw_message = f"""
                你好, {user.first_name}! 欢迎使用！
                试着发给我一条消息，我会复述它。
                或者发给我一个表情包，我会告诉你它的信息然后把它发回给你！"""
    message = dedent(raw_message)  # 去除多余的缩进
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )

async def echo_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """复述用户发送的文本消息"""
    text_received = update.message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"我收到了: {text_received}"
    )

def _print_sticker_set_info(sticker) -> None:
    """辅助函数：格式化贴纸集信息为字符串并打印"""
    # ---- 这是最优雅的方式 ----
    # 1. 转换成字典
    sticker_as_dict = sticker.to_dict()
    # 2. (核心) 使用 pprint.pformat() 把它格式化成一个漂亮的字符串
    #    indent=2 表示用2个空格来缩进
    pretty_string = pprint.pformat(sticker_as_dict, indent=2)
    # 3. 用 logger.info() 打印这个格式化后的字符串
    logger.info(f"--- Sticker (Pretty Printed) ---\n{pretty_string}")

async def _download_sticker_set_files(sticker_set, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """辅助函数：下载贴纸集中的所有贴纸文件"""
    title = sticker_set.title
    set_name = sticker_set.name
    total_stickers = len(sticker_set.stickers)
    logger.info(f"准备下载表情包集: {title} (名称: {set_name})，共 {total_stickers} 张表情。")
    # 1. 创建一个下载目录
    # 我们用 set_name 作为文件夹名，因为它唯一且合法
    download_dir = os.path.join(DOWNLOAD_DIR, set_name)
    # 检查文件夹是否存在，如果不存在，就创建它
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        logger.info(f"创建了新目录: {download_dir}")
    # 先回复用户，告诉他我们要开始下载了，避免超时
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"开始下载 {title} (共 {total_stickers} 张)... 这可能需要一点时间。"
    )
    # 2. 遍历包里的所有表情
    # (我们可以设置一个计数器，只下载前几个作为测试)
    download_count = 0
    for i, sticker_in_set in enumerate(sticker_set.stickers):
        # (可选) 测试时，只下载前5个
        if i >= 5: 
           break 
        # 3. 获取 file_id
        file_id = sticker_in_set.file_id
        # 4. (核心) 第一步：获取文件对象
        file = await context.bot.get_file(file_id)
        
        # (可选) 打印看看 file 对象长什么样
        logger.info(f"文件对象长这样: {pprint.pformat(file.to_dict())}")
        
        # 5. (核心) 第二步：下载！
        # 我们需要构建一个本地保存路径
        # file.file_path 会告诉我们原始文件名，通常是 .webp
        # 比如: "stickers/file_6.webp"
        # 我们只取最后的文件名
        file_name = os.path.basename(file.file_path) 
        local_path = os.path.join(download_dir, file_name)
        
        # 执行下载并保存
        await file.download_to_drive(custom_path=local_path)
        download_count += 1
        
        # 每下载10个，在日志里说一声
        if (download_count % 10 == 0) or (download_count == total_stickers):
            logger.info(f"已下载 {download_count} / {total_stickers} 张...")

    # 6. (新增) 全部下载完成后，给用户一个最终回复
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ 下载完成！\n包名: {title}\n总共 {download_count} 张表情已保存到服务器的 {download_dir} 文件夹。"
    )

async def sticker_echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """响应用户发送的贴纸消息"""
    sticker_received = update.message.sticker
    try:
        sticker_set_name = sticker_received.set_name or ""
        if sticker_set_name:
            sticker_set = await context.bot.get_sticker_set(sticker_set_name)
            _print_sticker_set_info(sticker_set)
            sticker_count = len(sticker_set.stickers)
            sticker_message = f"属于表情包集: {sticker_set_name}，它包含 {sticker_count} 个表情包。"
        else:
            sticker_message = "但是它不属于任何表情包集捏。"
        message = f"我收到了你的表情包！它的id是: {sticker_received.file_id}\n{sticker_message}"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
        await context.bot.send_sticker(
            chat_id=update.effective_chat.id,
            sticker=sticker_received.file_id
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="这是我给你回传的表情包！它真有意思，对吧？"
        )
        if sticker_set_name:
            await _download_sticker_set_files(sticker_set, update, context)
    except Exception as e:
        logger.error(f"处理贴纸时出错: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="坏了，我好像没法处理这个表情包诶。"
        )

if __name__ == '__main__':
    # 创建 Application
    application = ApplicationBuilder().token(API_TOKEN).build()
    
    # 注册处理器 (Handlers)
    # 告诉机器人，当收到 /start 命令时，调用 start 函数启动
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    # 告诉机器人，当收到“文本”消息时，调用 echo_text 函数
    # filters.TEXT & (~filters.COMMAND) 表示：只处理文本消息，并且排除掉命令
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo_text)
    application.add_handler(echo_handler)

    # 告诉机器人，当收到“贴纸”消息时，调用 sticker_echo 函数
    # 和text不一样的filter用法
    sticker_handler = MessageHandler(filters.Sticker.ALL, sticker_echo)
    application.add_handler(sticker_handler)

    # 启动机器人
    # run_polling() 会开始不断地从 Telegram "拉取" 新消息
    print("机器人启动中... 按 Ctrl+C 停止")
    application.run_polling()
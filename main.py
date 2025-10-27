import logging
import os
from textwrap import dedent
from dotenv import load_dotenv  # 导入 load_dotenv 用于加载环境变量
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# 加载 .env 文件中的环境变量
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

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

async def sticker_echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """响应用户发送的贴纸消息"""
    sticker_received = update.message.sticker
    message = f"我收到了你的表情包！它的id是: {sticker_received.file_id}，属于表情包集: {sticker_received.set_name}"
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
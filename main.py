import logging
import os  # 导入 os 模块
from dotenv import load_dotenv  # 导入 load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# 加载 .env 文件中的环境变量
load_dotenv()
# 把这里 'YOUR_API_TOKEN' 替换成你自己的 Token
API_TOKEN = os.getenv("API_TOKEN")

# (可选) 开启日志，这在调试时非常有用
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
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"你好, {user.first_name}! 欢迎使用！\n"
             f"试着发给我一条消息，我会复述它。"
    )

# 2. 定义处理普通文本消息的函数 (回声)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """复述用户发送的文本消息"""
    text_received = update.message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"我收到了: {text_received}"
    )

if __name__ == '__main__':
    # 3. 创建 Application
    # ApplicationBuilder 会帮我们设置好一切
    application = ApplicationBuilder().token(API_TOKEN).build()
    
    # 4. 注册处理器 (Handlers)
    # 告诉机器人，当收到 /start 命令时，调用 start 函数
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    # 告诉机器人，当收到“文本”消息时，调用 echo 函数
    # filters.TEXT & (~filters.COMMAND) 表示：只处理文本消息，并且排除掉命令
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)

    # 5. 启动机器人
    # run_polling() 会开始不断地从 Telegram "拉取" 新消息
    print("机器人启动中... 按 Ctrl+C 停止")
    application.run_polling()
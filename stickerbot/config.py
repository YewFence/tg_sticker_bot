"""
配置模块

- 加载 .env 文件中的环境变量
- 提供可复用的 API_TOKEN 和 DOWNLOAD_DIR
"""

import os
from dotenv import load_dotenv  # 导入 load_dotenv 用于加载环境变量

# 加载 .env 文件中的环境变量
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR") or "sticker_downloads"
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
DOWNLOAD_LIMIT = 5  # 测试模式下的下载上限

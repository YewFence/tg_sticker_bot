# TG 表情包图片下载 Bot

来自于AptS:1547的奇思妙想  
一个基于 python-telegram-bot 的简易 Telegram 机器人，用于：
- 在“群聊”中，通过命令 /get 去“回复某个贴纸”，即可批量下载该贴纸所属的整个表情包集；
- 在“私聊”中，发送贴纸可查看其所属表情包集信息并回传贴纸；
- 在群里被 @ 时，给出如何使用的提示。


## 功能一览

- /start：欢迎与使用说明
- 被 @ 提示：在群聊 @ 机器人时，提示如何下载
- 贴纸回显（仅私聊）：发送贴纸，机器人回显并展示基础信息
- /get（群聊）：对“某条贴纸消息”使用 /get（即用 /get 去回复那条贴纸），机器人会下载该贴纸所属表情包集的全部贴纸
- 下载目录：默认保存到本地的 `sticker_downloads/<set_name>/`


## 运行环境与依赖

- Python：建议 3.10+（实话说我自己用的3.13，没试过其他版本（逃

安装示例（Windows PowerShell）：

```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```


## 必要配置

在项目根目录将 `.env.example` 更改为 `.env` 后修改：

```env
API_TOKEN=123456789:ABCDEF_your_token_here
```

其他可选配置详见 `.env.example` 中的注释

## 运行

```pwsh
python .\main.py
```

启动后终端会显示“Bot启动中...”，此时即可在 Telegram 中与机器人交互。

## 或者：使用Docker

### 构建 Docker 镜像

在项目根目录运行以下命令来构建 Docker 镜像：

```bash
docker build -t tg_sticker_bot .
```

### 运行 Docker 容器

运行以下命令来启动 Docker 容器：

```bash
docker run -d --name tg_sticker_bot_container -v $(pwd)/sticker_downloads:/app/sticker_downloads tg_sticker_bot
```

对于 PowerShell 用户，可以使用以下命令：

```pwsh
docker run -d --name tg_sticker_bot_container -v ${PWD}/sticker_downloads:/app/sticker_downloads tg_sticker_bot
```

这将会在后台运行机器人，并将 `sticker_downloads` 目录挂载到容器中，以便你可以访问下载的贴纸。


## 使用方式

1) 私聊贴纸回显（仅私聊）：
- 打开与你的机器人的私聊，发送任意贴纸
- 机器人会回显贴纸，并告知其所属表情包集（若有）

2) 群聊整包下载（核心场景）：
- 在群里找到一条“贴纸消息”
- 使用 /get 命令去“回复”这条贴纸消息（长按/右键回复，输入 /get 并发送）
- 机器人会：
	- 先提示“开始下载 … 共 N 张”
	- 然后将整个表情包集下载到服务器中的DOWNLOAD_DIR目录（默认为项目文件夹下的 `sticker_downloads/<set_name>/`）
	- 完成后告诉你共下载了多少张

3) 被 @ 时提示：
- 在群里 @ 机器人用户名（例如 `@YourBotName`），它会回复一段使用说明

隐私模式说明：
- 即便开启了“隐私模式”，机器人也能接收到“命令消息”及其 `reply_to_message`，因此“用 /get 回复贴纸”的方式在群聊中可正常工作
- 如果你希望机器人在群里读取更多类型的消息，可在 BotFather 里关闭隐私模式，但本项目的推荐用法不依赖此设置


## 项目结构

```
tg_sticker_bot/
├─ main.py                 # 极简入口：调用 stickerbot.run()
├─ stickerbot/             # 机器人业务包
│  ├─ __init__.py          # 暴露 run()/build_application()
│  ├─ app.py               # 日志、Application 构建、注册 Handler、run_polling
│  ├─ config.py            # 加载 .env，导出 API_TOKEN、DOWNLOAD_DIR
│  ├─ handlers/            # 各类处理器
│  │  ├─ start.py          # /start 欢迎
│  │  ├─ mention.py        # 被 @ 提示
│  │  ├─ stickers.py       # 贴纸回显与整包下载核心逻辑
│  │  └─ get_set.py        # /get（群里回复贴纸以下载整包）
│  └─ utils/
│     └─ bot.py            # get_bot_username 缓存工具
└─ sticker_downloads/      # 下载输出目录（可自定义）
```


## 实现要点

- 仅私聊触发贴纸回显：`filters.Sticker.ALL & filters.ChatType.PRIVATE`
- 群聊整包下载通过命令触发：用户“用 /get 去回复一条贴纸消息”，机器人通过 `update.message.reply_to_message` 拿到那张贴纸
- 下载文件名沿用 Telegram 文件名


## 常见问题（FAQ）

1) 报错 AttributeError: module 'telegram.ext.filters' has no attribute 'STICKER'
- 解决：本项目使用 v20 的过滤器写法，应使用 `filters.Sticker.ALL`，不应该使用旧版常量 `filters.STICKER`

2) 群里为什么机器人看不到我的普通消息？
- 因为默认“隐私模式”下机器人只接收命令/被 @ 的消息
- 本项目的群聊交互设计是用命令（/get）+“回复贴纸”，因此不受此限制

3) 大集合/网络不稳会不会中断？
- 我觉得会（，没了解过，这个Bot的健壮性我觉得应该不是很好（逃

4) 动图/视频贴纸能下载吗？
- 可以，但是需要注意机器人会按 Telegram 源文件原样保存（.webp/.tgs/.webm 等）。

## 开发提示

- 主要入口：`stickerbot/app.py`（注册 Handler 与运行）
- 配置：`.env`（`API_TOKEN` 必填）
- 若要拓展功能（如进度消息编辑、命名规范、重试机制），建议在 `handlers/stickers.py` 中实现，或者自己新开一个模块

## TODO
- 保存方式：考虑自动上传云盘/放进QQ群文件


—— 祝使用愉快 🙂

## License
MIT License © YewFence
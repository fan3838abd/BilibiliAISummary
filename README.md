# Bilibili AI Summary

使用AI自动总结Bilibili视频字幕的工具。

## 功能特性

- 使用 `yt-dlp` 下载Bilibili视频字幕
- 调用AI API对字幕进行智能总结
- 生成结构化的Markdown文档

## 环境要求

- Python 3.11.13
- cookies.txt 文件（用于访问Bilibili）

## 安装

1. 克隆项目
```bash
git clone <repository-url>
cd BilibiliAISummary
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 准备cookies文件
   
   程序需要cookies文件来访问Bilibili视频字幕。获取方法如下：
   
   **方法一：从浏览器提取（推荐）**
   
   1. 在Firefox浏览器中登录Bilibili网站
   2. 使用yt-dlp从浏览器提取cookies：
      ```bash
      yt-dlp --list-subs --cookies-from-browser firefox https://www.bilibili.com/video/BV1JMSsBZEc3 --cookies cookies.txt
      ```
      注意：将URL替换为任意Bilibili视频链接即可
   3. 将生成的 `cookies.txt` 文件放到项目根目录
   
   **方法二：手动导出**
   
   - 使用浏览器扩展（如Cookie-Editor）导出Bilibili的cookies
   - 保存为Netscape格式的 `cookies.txt` 文件
   - 放到项目根目录
   
   **注意事项：**
   - cookies文件需要定期更新（通常有效期较长）
   - 如果下载字幕失败，可能是cookies已过期，需要重新获取

4. 配置环境变量
   - 复制 `.env.example` 为 `.env`（如果存在）
   - 或在项目根目录创建 `.env` 文件，内容如下：
     ```env
     AI_API_URL=https://aihubmix.com/v1/chat/completions
     AI_API_KEY=your_api_key_here
     AI_MODEL=gpt-4o-mini
     ```
   - 将 `your_api_key_here` 替换为你的实际API密钥
   - 注意：`.env` 文件已添加到 `.gitignore`，不会被提交到版本控制

## 使用方法

### 基本用法

```bash
python src/main.py <bilibili_video_url>
```

### 完整参数

```bash
python src/main.py <bilibili_video_url> [选项]

选项:
  --cookies PATH      Cookies文件路径（默认: cookies.txt）
  --api-key KEY      AI API密钥（优先使用，会覆盖.env中的配置）
  --model MODEL      AI模型名称（优先使用，会覆盖.env中的配置）
  --output DIR       输出目录（默认: output/）
```

### 示例

```bash
# 使用默认配置
python src/main.py https://www.bilibili.com/video/BV1234567890

# 指定API密钥
python src/main.py https://www.bilibili.com/video/BV1234567890 --api-key your_key

# 指定输出目录
python src/main.py https://www.bilibili.com/video/BV1234567890 --output ./summaries
```

## 项目结构

```
BilibiliAISummary/
├── src/                 # 源代码
│   ├── downloader.py   # 字幕下载模块
│   ├── summarizer.py   # AI总结模块
│   └── main.py         # 主程序入口
├── config/             # 配置模块
│   └── settings.py     # 配置管理
├── utils/              # 工具模块
│   └── logger.py       # 日志工具
├── output/             # 输出目录（自动创建）
├── cookies.txt         # Bilibili cookies文件
├── .env                # 环境变量配置（需自行创建）
├── .env.example        # 环境变量配置示例（如果存在）
├── requirements.txt    # 依赖列表
└── README.md          # 说明文档
```

## 输出

程序会在 `output/` 目录下为每次处理创建一个时间戳命名的子目录，所有相关文件都保存在该子目录中：

```
output/
├── YYYYMMDD_HHMMSS/          # 时间戳子目录
│   ├── 视频标题.ai-zh.srt     # 中文字幕文件
│   ├── 视频标题.ai-en.srt     # 英文字幕文件（如果有）
│   └── 视频标题.md            # AI总结文件
└── ...
```

每个视频的处理结果（字幕文件和总结文件）都保存在独立的子目录中，便于管理和查找。

### 输出示例

查看实际输出效果：[输出Demo](https://github.com/fan3838abd/BilibiliAISummary/tree/main/output/20251210_214001)

## 注意事项

1. 确保 `cookies.txt` 文件有效，否则可能无法下载字幕
2. AI API密钥需要有效，否则无法生成总结
3. 网络连接需要稳定，下载字幕和调用API都需要网络
4. 字幕下载依赖yt-dlp，如果下载失败请检查视频URL和cookies

## 许可证

MIT License


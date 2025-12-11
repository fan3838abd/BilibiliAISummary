"""配置管理"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()


class Settings:
    """应用配置"""
    
    # 项目根目录
    BASE_DIR = Path(__file__).parent.parent
    
    # Cookies文件路径
    COOKIES_FILE = BASE_DIR / "cookies.txt"
    
    # 输出目录
    OUTPUT_DIR = BASE_DIR / "output"
    
    # AI API配置
    AI_API_URL = os.getenv("AI_API_URL", "https://aihubmix.com/v1/chat/completions")
    AI_API_KEY = os.getenv("AI_API_KEY", "")
    AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")
    
    # yt-dlp配置
    YT_DLP_SUBTITLE_LANG = "zh-CN,zh,en"  # 优先中文字幕
    
    @classmethod
    def ensure_output_dir(cls):
        """确保输出目录存在"""
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate_cookies(cls) -> bool:
        """验证cookies文件是否存在"""
        return cls.COOKIES_FILE.exists() and cls.COOKIES_FILE.is_file()


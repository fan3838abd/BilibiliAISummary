"""简洁的日志工具"""
import logging
import sys
from pathlib import Path


def setup_logger(name: str = "BilibiliAISummary", level: int = logging.INFO) -> logging.Logger:
    """设置并返回日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 控制台输出格式：简洁
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    
    logger.addHandler(console_handler)
    return logger


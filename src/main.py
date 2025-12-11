"""主程序入口"""
import argparse
import re
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import Settings
from utils.logger import setup_logger
from src.downloader import SubtitleDownloader
from src.summarizer import AISummarizer

logger = setup_logger()


def save_summary(summary: str, video_title: str, sub_dir: Path) -> Path:
    """
    保存总结到Markdown文件
    
    Args:
        summary: 总结内容
        video_title: 视频标题
        sub_dir: 输出子目录（与字幕文件在同一目录）
    
    Returns:
        保存的文件路径
    """
    # 确保子目录存在
    sub_dir.mkdir(parents=True, exist_ok=True)
    
    # 清理文件名中的特殊字符（保留中文、英文、数字、空格、横线、下划线）
    safe_title = re.sub(r'[<>:"/\\|?*]', '', video_title).strip()
    safe_title = safe_title[:50]  # 限制长度
    
    # 生成文件名：标题.md
    filename = f"{safe_title}.md" if safe_title else "summary.md"
    output_file = sub_dir / filename
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    return output_file


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Bilibili视频AI总结工具 - 下载字幕并使用AI生成总结"
    )
    parser.add_argument(
        "url",
        help="Bilibili视频URL"
    )
    parser.add_argument(
        "--cookies",
        type=str,
        help=f"Cookies文件路径（默认: {Settings.COOKIES_FILE}）"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="AI API密钥（也可通过环境变量AI_API_KEY设置）"
    )
    parser.add_argument(
        "--model",
        type=str,
        help=f"AI模型名称（默认: {Settings.AI_MODEL}）"
    )
    parser.add_argument(
        "--output",
        type=str,
        help=f"输出目录（默认: {Settings.OUTPUT_DIR}）"
    )
    
    args = parser.parse_args()
    
    try:
        # 配置设置
        if args.cookies:
            Settings.COOKIES_FILE = Path(args.cookies)
        if args.api_key:
            Settings.AI_API_KEY = args.api_key
        if args.model:
            Settings.AI_MODEL = args.model
        if args.output:
            Settings.OUTPUT_DIR = Path(args.output)
        
        # 验证cookies文件
        if not Settings.validate_cookies():
            logger.error(f"Cookies文件不存在: {Settings.COOKIES_FILE}")
            logger.info("请确保cookies.txt文件存在于项目根目录")
            sys.exit(1)
        
        # 验证API密钥
        if not Settings.AI_API_KEY:
            logger.error("AI_API_KEY未设置")
            logger.info("请通过环境变量AI_API_KEY或--api-key参数设置")
            sys.exit(1)
        
        # 步骤1: 下载字幕
        logger.info("=" * 50)
        logger.info("步骤1: 下载字幕")
        logger.info("=" * 50)
        
        downloader = SubtitleDownloader()
        subtitle_text, video_title, sub_dir = downloader.download_subtitle(args.url)
        
        if not subtitle_text or not sub_dir:
            logger.error("字幕下载失败，程序退出")
            sys.exit(1)
        
        # 步骤2: AI总结
        logger.info("=" * 50)
        logger.info("步骤2: AI总结")
        logger.info("=" * 50)
        
        summarizer = AISummarizer()
        summary = summarizer.summarize(subtitle_text, video_title or "")
        
        if not summary:
            logger.error("AI总结失败，程序退出")
            sys.exit(1)
        
        # 步骤3: 保存结果
        logger.info("=" * 50)
        logger.info("步骤3: 保存结果")
        logger.info("=" * 50)
        
        output_file = save_summary(summary, video_title or "summary", sub_dir)
        logger.info(f"总结已保存到: {output_file}")
        
        logger.info("=" * 50)
        logger.info("完成！")
        logger.info("=" * 50)
        
    except KeyboardInterrupt:
        logger.info("\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()


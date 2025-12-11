"""使用yt-dlp下载Bilibili视频字幕"""
import json
import re
from pathlib import Path
from typing import Optional, Tuple
import yt_dlp
from config.settings import Settings
from utils.logger import setup_logger

logger = setup_logger()


class SubtitleDownloader:
    """字幕下载器"""
    
    def __init__(self, cookies_file: Optional[Path] = None):
        """
        初始化下载器
        
        Args:
            cookies_file: cookies文件路径，默认使用Settings中的配置
        """
        self.cookies_file = cookies_file or Settings.COOKIES_FILE
        if not self.cookies_file.exists():
            raise FileNotFoundError(f"Cookies文件不存在: {self.cookies_file}")
    
    def download_subtitle(self, video_url: str, output_dir: Optional[Path] = None) -> Tuple[Optional[str], Optional[str], Optional[Path]]:
        """
        下载视频字幕
        
        Args:
            video_url: Bilibili视频URL
            output_dir: 输出目录，默认使用Settings中的配置
        
        Returns:
            (字幕文本内容, 视频标题, 子目录路径) 元组，如果下载失败返回 (None, None, None)
        """
        output_dir = output_dir or Settings.OUTPUT_DIR
        Settings.ensure_output_dir()
        
        # 创建子目录（使用时间戳）
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sub_dir = output_dir / timestamp
        sub_dir.mkdir(exist_ok=True)
        logger.info(f"创建输出子目录: {sub_dir}")
        
        try:
            logger.info(f"开始下载字幕: {video_url}")
            logger.info(f"输出目录: {output_dir}")
            logger.info(f"Cookies文件: {self.cookies_file}")
            
            # 先获取视频信息，确定可用字幕
            temp_opts = {
                'skip_download': True,
                'cookiefile': str(self.cookies_file),
                'quiet': False,
            }
            
            with yt_dlp.YoutubeDL(temp_opts) as ydl:
                logger.info("正在获取视频信息...")
                info = ydl.extract_info(video_url, download=False)
                video_title = info.get('title', 'unknown')
                logger.info(f"视频标题: {video_title}")
                
                # 检查可用的字幕 - 尝试多个可能的字段
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})
                
                # 调试：打印所有包含 'sub' 的键
                logger.debug("=" * 50)
                logger.debug("视频信息中所有包含 'sub' 的键:")
                for key in info.keys():
                    if 'sub' in key.lower() or 'caption' in key.lower():
                        logger.debug(f"  {key}: {type(info[key])}")
                logger.debug("=" * 50)
                
                # 如果 subtitles 和 automatic_captions 都为空，尝试直接下载看看
                if not subtitles and not automatic_captions:
                    logger.warning("在视频信息中未找到字幕，尝试直接下载字幕...")
                    # 打印完整的 info 字典结构（仅键名）
                    logger.debug(f"视频信息的所有键: {list(info.keys())}")
                    
                    # 尝试使用 writesubtitles 参数重新获取
                    temp_opts_with_subs = {
                        'skip_download': True,
                        'cookiefile': str(self.cookies_file),
                        'writesubtitles': True,
                        'writeautomaticsub': True,
                        'subtitleslangs': ['ai-zh', 'zh-CN', 'zh', 'ai-en', 'en'],
                        'quiet': False,
                    }
                    logger.info("使用字幕参数重新获取信息...")
                    ydl2 = yt_dlp.YoutubeDL(temp_opts_with_subs)
                    info2 = ydl2.extract_info(video_url, download=False)
                    subtitles = info2.get('subtitles', {})
                    automatic_captions = info2.get('automatic_captions', {})
                
                logger.info("=" * 50)
                logger.info("可用字幕信息:")
                if subtitles:
                    logger.info(f"手动字幕: {list(subtitles.keys())}")
                    for lang, subs in subtitles.items():
                        logger.info(f"  {lang}: {[s.get('ext', 'unknown') for s in subs]}")
                else:
                    logger.info("未找到手动字幕")
                
                if automatic_captions:
                    logger.info(f"自动字幕: {list(automatic_captions.keys())}")
                    for lang, subs in automatic_captions.items():
                        logger.info(f"  {lang}: {[s.get('ext', 'unknown') for s in subs]}")
                else:
                    logger.info("未找到自动字幕")
                logger.info("=" * 50)
                
                # 动态选择字幕语言和格式
                available_langs = list(subtitles.keys()) + list(automatic_captions.keys())
                selected_lang = None
                selected_format = None
                
                if available_langs:
                    # 优先选择中文字幕
                    preferred_langs = ['ai-zh', 'zh-CN', 'zh', 'ai-en', 'en', 'ai-ja', 'ja']
                    for pref_lang in preferred_langs:
                        if pref_lang in available_langs:
                            selected_lang = pref_lang
                            break
                    
                    # 如果没找到优先语言，使用第一个可用语言
                    if not selected_lang and available_langs:
                        selected_lang = available_langs[0]
                    
                    if selected_lang:
                        # 获取该语言可用的格式
                        lang_subs = subtitles.get(selected_lang) or automatic_captions.get(selected_lang)
                        if lang_subs:
                            # 优先选择 srt，其次 vtt
                            preferred_formats = ['srt', 'vtt', 'ass', 'ssa']
                            for pref_format in preferred_formats:
                                if any(s.get('ext') == pref_format for s in lang_subs):
                                    selected_format = pref_format
                                    break
                
                if not selected_lang:
                    # 即使信息中没有字幕，也尝试下载常见语言的字幕
                    logger.warning("信息中未找到字幕，尝试下载常见语言字幕...")
                    selected_lang = 'ai-zh'  # 默认尝试中文字幕
                    selected_format = 'srt'  # 默认使用 srt 格式
                    logger.info(f"将尝试下载: {selected_lang} ({selected_format})")
                else:
                    logger.info(f"选择字幕: {selected_lang} ({selected_format or 'auto'})")
            
            # 配置yt-dlp选项，使用选定的语言和格式
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': [selected_lang, 'zh-CN', 'zh', 'ai-en', 'en'],  # 尝试多个语言
                'skip_download': True,
                'outtmpl': str(sub_dir / '%(title)s.%(ext)s'),
                'cookiefile': str(self.cookies_file),
                'verbose': True,  # 启用详细日志
            }
            
            # 如果指定了格式，使用指定格式；否则让yt-dlp自动选择
            if selected_format:
                ydl_opts['subtitlesformat'] = selected_format
            else:
                # 不指定格式，让yt-dlp自动选择可用格式
                ydl_opts['subtitlesformat'] = 'srt/vtt/ass/ssa'
            
            # 下载字幕
            logger.info("开始下载字幕文件...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                
                # 列出输出子目录中的所有文件
                logger.info(f"输出子目录中的文件:")
                for file in sub_dir.iterdir():
                    if file.is_file():
                        logger.info(f"  - {file.name} ({file.stat().st_size} bytes)")
                
                # 查找下载的字幕文件
                subtitle_file = self._find_subtitle_file(sub_dir, video_title)
                
                if subtitle_file:
                    logger.info(f"找到字幕文件: {subtitle_file}")
                    # 读取并解析字幕内容
                    subtitle_text = self._parse_subtitle(subtitle_file)
                    logger.info(f"字幕下载成功，共 {len(subtitle_text)} 字符")
                    return subtitle_text, video_title, sub_dir
                else:
                    logger.warning("未找到字幕文件")
                    logger.warning(f"已搜索目录: {sub_dir}")
                    logger.warning(f"视频标题: {video_title}")
                    return None, None, None
                    
        except Exception as e:
            logger.error(f"下载字幕失败: {str(e)}")
            return None, None, None
    
    def _find_subtitle_file(self, output_dir: Path, video_title: str) -> Optional[Path]:
        """查找字幕文件"""
        # 清理标题中的特殊字符，用于匹配文件名
        safe_title = re.sub(r'[<>:"/\\|?*]', '', video_title)
        logger.info(f"搜索字幕文件，清理后的标题: {safe_title}")
        
        # 查找.vtt文件
        for ext in ['.vtt', '.srt']:
            pattern = f"{safe_title}*{ext}"
            logger.info(f"搜索模式: {pattern}")
            matches = list(output_dir.glob(pattern))
            if matches:
                logger.info(f"找到匹配文件: {[str(m) for m in matches]}")
                return matches[0]
        
        # 如果没找到，尝试查找所有.vtt文件（可能是自动生成的文件名）
        logger.info("未找到精确匹配，搜索所有.vtt文件...")
        vtt_files = list(output_dir.glob("*.vtt"))
        srt_files = list(output_dir.glob("*.srt"))
        all_subtitle_files = vtt_files + srt_files
        
        if all_subtitle_files:
            logger.info(f"找到字幕文件: {[str(f) for f in all_subtitle_files]}")
            # 返回最新的文件
            return max(all_subtitle_files, key=lambda p: p.stat().st_mtime)
        
        logger.warning("未找到任何字幕文件")
        return None
    
    def _parse_subtitle(self, subtitle_file: Path) -> str:
        """
        解析字幕文件（VTT或SRT格式），提取纯文本
        
        Args:
            subtitle_file: 字幕文件路径
        
        Returns:
            纯文本字幕内容
        """
        try:
            file_ext = subtitle_file.suffix.lower()
            logger.info(f"解析字幕文件: {subtitle_file.name} (格式: {file_ext})")
            
            with open(subtitle_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if file_ext == '.vtt':
                # 解析VTT格式
                # 移除WEBVTT头部
                content = re.sub(r'WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
                # 移除时间戳行 (格式: 00:00:00.000 --> 00:00:00.000)
                content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}.*?\n', '\n', content)
            elif file_ext == '.srt':
                # 解析SRT格式
                # SRT格式: 序号\n时间戳\n文本\n空行
                # 移除序号行和时间戳行
                lines = content.split('\n')
                text_lines = []
                skip_next = False
                for i, line in enumerate(lines):
                    line = line.strip()
                    # 跳过空行
                    if not line:
                        skip_next = False
                        continue
                    # 跳过序号行（纯数字）
                    if re.match(r'^\d+$', line):
                        skip_next = True
                        continue
                    # 跳过时间戳行
                    if skip_next and re.match(r'\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,.]\d{3}', line):
                        skip_next = False
                        continue
                    # 收集文本行
                    if not skip_next:
                        text_lines.append(line)
                content = '\n'.join(text_lines)
            else:
                # 其他格式，尝试通用解析
                logger.warning(f"未知字幕格式: {file_ext}，尝试通用解析")
            
            # 移除HTML标签
            content = re.sub(r'<[^>]+>', '', content)
            
            # 移除多余的空行
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            # 清理每行，移除前后空格
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            return '\n'.join(lines)
            
        except Exception as e:
            logger.error(f"解析字幕文件失败: {str(e)}")
            raise


"""使用AI API对字幕进行总结"""
import json
import requests
from typing import Optional
from config.settings import Settings
from utils.logger import setup_logger

logger = setup_logger()


class AISummarizer:
    """AI总结器"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        初始化总结器
        
        Args:
            api_key: API密钥，默认使用Settings中的配置
            model: 模型名称，默认使用Settings中的配置
        """
        self.api_key = api_key or Settings.AI_API_KEY
        self.model = model or Settings.AI_MODEL
        self.api_url = Settings.AI_API_URL
        
        if not self.api_key:
            raise ValueError("AI_API_KEY未设置，请设置环境变量或传入参数")
    
    def summarize(self, subtitle_text: str, video_title: str = "") -> Optional[str]:
        """
        对字幕进行总结
        
        Args:
            subtitle_text: 字幕文本
            video_title: 视频标题（可选）
        
        Returns:
            总结内容，如果失败返回None
        """
        if not subtitle_text or not subtitle_text.strip():
            logger.warning("字幕内容为空")
            return None
        
        # 构建提示词
        prompt = self._build_prompt(subtitle_text, video_title)
        
        try:
            logger.info("开始调用AI API进行总结...")
            
            response = requests.post(
                url=self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                timeout=120  # 2分钟超时
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 提取回复内容
            summary = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            if summary:
                logger.info("AI总结完成")
                return summary
            else:
                logger.warning("AI返回内容为空")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"总结过程出错: {str(e)}")
            return None
    
    def _build_prompt(self, subtitle_text: str, video_title: str) -> str:
        """构建AI提示词"""
        title_part = f"视频标题：{video_title}\n\n" if video_title else ""
        
        prompt = f"""请对以下Bilibili视频字幕进行总结，生成一份结构化的Markdown文档。

{title_part}字幕内容：

{subtitle_text}

请按照以下要求生成总结：
1. 提取视频的核心内容和要点
2. 使用Markdown格式，包含标题、段落、列表等
3. 总结要简洁明了，突出重点
4. 如果字幕内容较长，可以分章节总结
5. 保持中文输出

请开始总结："""
        
        return prompt


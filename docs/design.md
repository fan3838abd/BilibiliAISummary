## 项目简介

使用yt-dlb下载bilibili视频字幕

然后用大语言模型对字幕进行总结

最后得到视频总结的md文档

## 技术分析

使用`python`开发本项目，最终的输出是一份`.md`文件

yt-dlb需要指定cookies.txt文件

## 相关接口

### 大语言模型接口

```python
import requests
import json

response = requests.post(
  url="https://aihubmix.com/v1/chat/completions",
  headers={
    "Authorization": "Bearer <AIHUBMIX_API_KEY>",
    "Content-Type": "application/json",
  },
  data=json.dumps({
    "model": "gpt-4o-mini", # 替换模型 id
    "messages": [
      {
        "role": "user",
        "content": "What is the meaning of life?"
      }
    ]
  })
)
```

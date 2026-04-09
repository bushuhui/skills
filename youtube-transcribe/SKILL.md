---
name: youtube-transcribe
description: 自动提取 YouTube 视频字幕并保存到知识库。支持自动生成字幕、多语言支持、自动格式化 Markdown。Use when the user wants to extract YouTube video subtitles or save video content to knowledge base.
---

# youtube-transcribe Skill

自动提取 YouTube 视频字幕并保存到知识库。

## 输入
- `youtube_url`: YouTube 视频 URL 或 ID（字符串）
- `output_dir`: 输出目录（可选，默认：Clippings/YouTube-Transcripts/）
- `languages`: 语言优先级（可选，默认：zh-CN,en）

## 输出
- `success`: 是否成功（布尔值）
- `video_id`: 视频 ID（字符串）
- `title`: 视频标题（字符串）
- `language`: 字幕语言（字符串）
- `snippet_count`: 字幕片段数量（整数）
- `output_path`: 保存路径（字符串）
- `error`: 错误信息（如有）

## 依赖
- youtube-transcript-api (Python)
- 安装：`pip install youtube-transcript-api`

## 示例

### Feishu 群聊
```
@AI 助手 转写这个视频：https://www.youtube.com/watch?v=JqFUbl-OVzc
```

### 命令行
```bash
openclaw skill run youtube-transcribe --url "JqFUbl-OVzc"
```

### API
```typescript
const result = await openclaw.skills.run('youtube-transcribe', {
  url: 'https://www.youtube.com/watch?v=JqFUbl-OVzc',
  output_dir: 'Clippings/202603/'
});
```

## 特性
- ✅ 支持手动上传字幕
- ✅ 支持自动生成字幕
- ✅ 多语言支持
- ✅ 自动格式化 Markdown
- ✅ 自动保存到知识库
- ✅ WebDAV 自动同步

## 限制
- 视频必须有字幕轨道
- 部分视频可能禁用字幕
- 仅用于学习、研究目的

## 相关文件
- 主程序：`youtube_transcribe.py`
- 依赖：`requirements.txt`

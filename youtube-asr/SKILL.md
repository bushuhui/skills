---
name: youtube-asr
description: YouTube 视频音频自动转写技能。使用 CDP 导出 Chrome cookies，yt-dlp 下载音频，调用 ASR API 转写（Qwen/Qwen3-ASR-1.7B），支持保存到知识库。Use when the user wants to transcribe YouTube video audio to text via ASR.
---

## 技能描述

**功能**: 自动下载 YouTube 视频音频并转写为文字

**流程**:
1. CDP 导出 Chrome cookies（Netscape 格式）
2. yt-dlp 下载音频（带 cookies + JS runtime）
3. 调用 ASR API 转写（Qwen/Qwen3-ASR-1.7B）
4. 保存结果到知识库

**适用场景**:
- YouTube 教程视频转文字
- 会议录像整理
- 播客内容归档
- 外语视频中文字幕

---

## 快速使用

### 方式 1: 自然语言调用

```
帮我转写这个 YouTube 视频：https://www.youtube.com/watch?v=xxx

保存 YouTube 视频内容到知识库：https://www.youtube.com/watch?v=xxx
```

### 方式 2: 命令行调用

```bash
# 基础用法
python youtube_asr.py https://www.youtube.com/watch?v=xxx

# 指定输出文件
python youtube_asr.py https://www.youtube.com/watch?v=xxx /path/to/output.txt

# 保存到知识库
python youtube_asr.py https://www.youtube.com/watch?v=xxx --save-to-obsidian
```

---

## 前置条件

### 1. 安装依赖

```bash
# Python 依赖
pip install puppeteer-core requests

# yt-dlp（确保已安装）
which yt-dlp  # 应该输出路径

# Node.js（yt-dlp 需要）
node --version

# Chrome Remote Debugging（必须已启动）
# Chrome 启动参数：--remote-debugging-port=9222
```

### 2. Chrome Remote Debugging

```bash
# Linux
google-chrome --remote-debugging-port=9222
```

### 3. yt-dlp 配置

```bash
yt-dlp --version  # 应该是最新版本
yt-dlp -U         # 更新
```

---

## 使用示例

### 示例 1: 基础转写

```bash
python youtube_asr.py https://www.youtube.com/watch?v=aZT9d8qrirY
```

### 示例 2: 保存到 Obsidian

```bash
python youtube_asr.py https://www.youtube.com/watch?v=xxx --save-to-obsidian
```

输出位置: `/home/bushuhui/data-all/note/bushuhui/Clippings/YYYYMM/DDDD.md`

### 示例 3: 指定输出文件

```bash
python youtube_asr.py https://www.youtube.com/watch?v=xxx /path/to/output.txt
```

---

## 注意事项

### Chrome Cookies

- 必须使用 CDP 导出
- YouTube 有反爬虫机制，需要登录态
- cookies 会过期，每次下载前重新导出

### yt-dlp 参数

```bash
--cookies /tmp/youtube_cookies.txt    # 使用导出的 cookies
--js-runtimes node                     # JS runtime（处理 n 参数）
--remote-components ejs:github         # 远程 challenge solver
```

缺少这些参数会导致 `403 Forbidden`、`n parameter` 错误、`PO Token` 错误。

### 代理配置

ASR API 调用必须禁用代理：
```python
session = requests.Session()
session.trust_env = False
```

### 超时设置

```python
timeout=600  # 10 分钟超时，长视频需要较长时间
```

### 临时文件

会自动清理：
- `/tmp/youtube_cookies.txt`
- `/tmp/youtube_<video_id>.mp3`

---

## 故障排查

### "Cannot connect to Chrome"
Chrome 未启动或端口不对。检查 `ps aux | grep chrome`，启动时加 `--remote-debugging-port=9222`。

### "yt-dlp: 403 Forbidden"
cookies 过期或缺失。重新运行脚本（会自动重新导出）。

### "n parameter" 错误
yt-dlp 缺少 JS runtime，确保参数 `--js-runtimes node --remote-components ejs:github`。

### "API error: 401"
ASR API Token 无效。检查环境变量 `YOUTUBE_ASR_API_TOKEN`。

### 转写超时
视频太长，增加 `timeout` 值或使用更短片段。

---

## 性能指标

| 指标 | 值 |
|------|-----|
| **下载速度** | ~1-5 MB/s（取决于网络） |
| **转写速度** | ~1-2 分钟/10 分钟音频 |
| **准确率** | 中文 ~95%，英文 ~98% |
| **支持语言** | 中文、英文、日文、韩文等 |

---

## 相关文件

- 主程序：`youtube_asr.py`

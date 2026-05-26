---
name: youtube-asr
description: YouTube 视频音频自动转写技能。使用 CDP 导出 Chrome cookies，yt-dlp 下载音频，调用 ASR API 转写（Qwen/Qwen3-ASR-1.7B），支持保存到知识库。Use when the user wants to transcribe YouTube video audio to text via ASR.
---

## 技能描述

**功能**: 自动下载视频音频并转写为文字

**支持平台**: YouTube、Bilibili、小红书 (Xiaohongshu / xhslink.com)

**通用流程**:
1. yt-dlp 下载音频（YouTube 需要 cookies，Bilibili 通常不需要）
2. 调用 ASR API 转写（Qwen/Qwen3-ASR-1.7B）
3. 保存结果到知识库

**适用场景**:
- 教程视频转文字
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

### 小红书 (Xiaohongshu / xhslink.com)

小红书视频通过 xhslink.com 短链接分享。**yt-dlp 直接支持，无需 cookies**：

```bash
# 1. yt-dlp 下载视频（自动跟随短链接重定向）
yt-dlp "http://xhslink.com/o/XXXXX"

# 2. 提取音频
ffmpeg -y -i video.mp4 -q:a 0 -map a audio.mp3

# 3. ASR 转写
python3 scripts/pi_llm_server_skill.py transcribe "audio.mp3"
```

**注意**：
- xhslink.com 短链接会自动重定向到 xiaohongshu.com，yt-dlp 能正确识别并提取视频
- 无需 cookies 或登录态
- 如果链接是完整 xiaohongshu.com URL 而非短链接，CDP 浏览器会报 "IP at risk" 错误 → 此时尝试用 yt-dlp 直接下载，或注明平台限制

### Bilibili

B站视频使用相同音频转写流程，但有不同特点：

```bash
# 1. yt-dlp 下载音频（B站无需 cookies 即可下载音频）
yt-dlp -x --audio-format mp3 -o "output.%(ext)s" "https://www.bilibili.com/video/BVxxxxx/"

# 2. 字幕获取
# B站字幕需要登录态（cookies），否则 yt-dlp 会跳过字幕
# 推荐方案：直接下载音频 → ASR 转写（不依赖平台字幕）
```

**B站特有问题**：
- yt-dlp 下载音频无需 cookies，但字幕需要登录
- `--write-sub --all-subs` 在无 cookies 时只会下载弹幕（danmaku.xml）
- B站 API 字幕接口 `api.bilibili.com/x/player/v2?cid=<cid>&bvid=<bvid>` 可能超时
- 短链接 `b23.tv/xxx` 需先通过浏览器访问获取真实 BV 号

**⚠️ yt-dlp 下载失败兜底方案**（2026-05-26 实测确认）：
yt-dlp 有时会返回 `ERROR: No video formats found!`（BV1UfGo6GEVR、BV1KoGE6cE53 均遇到过）。此时需用 **CDP + API 直接下载**：

```python
import requests, re, subprocess, json

# 1. 通过 CDP 获取 B站 cookies
result = subprocess.run(
    ['node', '<web-access-skill-dir>/scripts/cdp-cli.mjs', 'eval', '<targetId>', 'document.cookie'],
    capture_output=True, text=True
)
cookie_str = result.stdout.strip()

# 2. 调用 Bilibili playurl API 获取音频 URL
headers = {'Cookie': cookie_str, 'User-Agent': 'Mozilla/5.0', 'Referer': f'https://www.bilibili.com/video/{bvid}/'}
r = requests.get('https://api.bilibili.com/x/player/playurl', params={
    'bvid': bvid, 'cid': cid, 'qn': 80, 'fnval': 16, 'fourk': 1
}, headers=headers)
dash = r.json()['data']['dash']
audio_url = max(dash['audio'], key=lambda x: x.get('bandwidth', 0))['baseUrl']

# 3. 下载音频（必须提取 Host header，CDN 会验证）
headers2 = {**headers, 'Referer': 'https://www.bilibili.com/', 'Origin': 'https://www.bilibili.com'}
host_match = re.search(r'https://([^/]+)', audio_url)
if host_match:
    headers2['Host'] = host_match.group(1)
resp = requests.get(audio_url, headers=headers2, timeout=180)
with open('audio.m4s', 'wb') as f:
    f.write(resp.content)
```

**关键点**：
- mcdn CDN URL 需要携带 `Host` header（从 URL 中解析域名），否则可能返回空内容
- 下载的是 `.m4s` 格式，需 `ffmpeg -i audio.m4s -q:a 0 -map a audio.mp3` 转换
- 视频流同样可通过 `dash['video']` 获取

- **最佳实践**：浏览器打开页面获取信息 → 尝试 yt-dlp 下载 → 失败则 API 兜底 → ffmpeg 转 mp3 → pi-llm-server ASR 转写

详见 `references/bilibili-asr-notes.md`。

ASR API 调用必须禁用代理：
```python
session = requests.Session()
session.trust_env = False
```

### 超时设置

ASR API 短音频 `timeout=600`，**长音频（>10 分钟）不应直接调用 API**，应使用 `pi-llm-server` 的 `split_transcribe.py` 分段转写（详见 pi-llm-server skill）。

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
视频太长。**长音频（>20 分钟）直接调用 API 必定超时。** 使用 `split_transcribe.py` 分段转写（详见 pi-llm-server skill）。

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

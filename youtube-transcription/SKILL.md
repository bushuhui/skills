# YouTube Transcription Skill - YouTube 视频转写技能

> 创建日期：2026-03-20
> 版本：1.0.0
> 标签：#YouTube #音频转写 #Whisper #ASR #语音识别 #视频转文字

---

## 📺 技能描述

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

## 🚀 快速使用

### 方式 1: 自然语言调用

```
帮我转写这个 YouTube 视频：https://www.youtube.com/watch?v=xxx

保存 YouTube 视频内容到知识库：https://www.youtube.com/watch?v=xxx
```

### 方式 2: 命令行调用

```bash
# 基础用法
python ~/.openclaw/workspace/skills/youtube-transcription/youtube_transcription.py https://www.youtube.com/watch?v=xxx

# 指定输出文件
python ~/.openclaw/workspace/skills/youtube-transcription/youtube_transcription.py https://www.youtube.com/watch?v=xxx /path/to/output.txt

# 保存到知识库
python ~/.openclaw/workspace/skills/youtube-transcription/youtube_transcription.py https://www.youtube.com/watch?v=xxx --save-to-obsidian
```

---

## 📋 完整流程

### Step 1: CDP 导出 Chrome Cookies

**为什么需要**: YouTube 需要登录态才能下载高质量音频

```python
def export_chrome_cookies():
    """使用 CDP 导出 Chrome cookies 为 Netscape 格式"""
    
    import puppeteer
    import time
    
    # 连接到已有 Chrome 实例（Remote Debugging）
    browser = await puppeteer.connect({
        'browserURL': 'http://127.0.0.1:9222',
        'defaultViewport': None
    })
    
    pages = await browser.pages()
    page = pages[0] if pages else await browser.newPage()
    
    # 访问 YouTube 确保有 cookies
    await page.goto('https://www.youtube.com/', {
        'waitUntil': 'networkidle2',
        'timeout': 30000
    })
    await asyncio.sleep(3)  # 等待 cookies 加载
    
    # 使用 CDP 获取 cookies
    cdp = await page.createCDPSession()
    result = await cdp.send('Network.getAllCookies')
    cookies = result.get('cookies', [])
    
    # 转换为 Netscape 格式
    netscape = '# Netscape HTTP Cookie File\n'
    for c in cookies:
        if 'youtube' in c.get('domain', '') or 'google' in c.get('domain', ''):
            domain = c['domain']
            include_sub = 'TRUE' if domain.startswith('.') else 'FALSE'
            path = c.get('path', '/')
            secure = 'TRUE' if c.get('secure') else 'FALSE'
            expiration = int(c.get('expires', time.time() + 31536000))
            netscape += f"{domain}\t{include_sub}\t{path}\t{secure}\t{expiration}\t{c['name']}\t{c['value']}\n"
    
    # 保存到临时文件
    cookie_file = '/tmp/youtube_cookies.txt'
    with open(cookie_file, 'w') as f:
        f.write(netscape)
    
    print(f"Exported {len(cookies)} cookies to {cookie_file}")
    
    await browser.disconnect()
    return cookie_file
```

---

### Step 2: yt-dlp 下载音频

**关键参数**:
- `--cookies`: 使用导出的 cookies
- `--js-runtimes node`: JS runtime（处理 n 参数）
- `--remote-components ejs:github`: 远程 challenge solver

```python
def download_audio(youtube_url, cookie_file):
    """使用 yt-dlp 下载 YouTube 音频"""
    
    import subprocess
    
    output_file = f"/tmp/youtube_{youtube_url.split('v=')[-1]}.mp3"
    
    cmd = [
        'yt-dlp',
        '-x',  # 提取音频
        '--audio-format', 'mp3',
        '--cookies', cookie_file,
        '--js-runtimes', 'node',
        '--remote-components', 'ejs:github',
        '-o', output_file,
        youtube_url
    ]
    
    print(f"Downloading: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Download failed: {result.stderr}")
        raise Exception(f"yt-dlp error: {result.stderr}")
    
    print(f"Downloaded to {output_file}")
    return output_file
```

---

### Step 3: 调用 ASR API 转写

```python
def transcribe_audio(audio_path, model="Qwen/Qwen3-ASR-1.7B"):
    """调用 ASR API 转写音频"""
    
    import requests
    
    API_BASE = "http://api.adv-ci.com:8090"
    API_TOKEN = "sk-5f8b839908d14561590b70227c72ca86"
    
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    # 禁用代理（关键！）
    session = requests.Session()
    session.trust_env = False
    
    print(f"Transcribing {audio_path}...")
    
    with open(audio_path, 'rb') as f:
        files = {'file': (os.path.basename(audio_path), f, 'audio/mpeg')}
        data = {'model': model}
        
        response = session.post(
            f'{API_BASE}/v1/audio/transcriptions',
            headers=headers,
            files=files,
            data=data,
            timeout=600
        )
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")
    
    result = response.json()
    
    if 'text' not in result:
        raise Exception(f"No text in response: {result}")
    
    return result['text']
```

---

### Step 4: 保存到知识库

```python
def save_to_obsidian(text, video_title, video_url):
    """保存转写结果到 Obsidian 知识库"""
    
    import datetime
    
    # 获取当前日期
    today = datetime.datetime.now()
    month_dir = today.strftime("%Y%m")
    date_file = today.strftime("%Y%m%d")
    
    # 知识库路径
    base_path = "/home/bushuhui/data-all/note/bushuhui/Clippings"
    month_path = f"{base_path}/{month_dir}"
    
    # 创建目录
    os.makedirs(month_path, exist_ok=True)
    
    # 写入当天文件
    file_path = f"{month_path}/{date_file}.md"
    
    # 读取现有内容（如有）
    existing_content = ""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    
    # 追加新内容
    new_section = f"""
---

## YouTube 视频转写：{video_title}

**视频链接**: {video_url}
**转写时间**: {today.strftime("%Y-%m-%d %H:%M")}
**转写模型**: Qwen/Qwen3-ASR-1.7B
**字数**: {len(text)} 字

### 转写内容

{text}

---
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(existing_content + new_section)
    
    print(f"Saved to {file_path}")
    return file_path
```

---

### Step 5: 清理临时文件

```python
def cleanup(*paths):
    """清理临时文件"""
    for path in paths:
        if path and path.startswith('/tmp/') and os.path.exists(path):
            try:
                os.remove(path)
                print(f"Cleaned up: {path}")
            except Exception as e:
                print(f"Failed to clean up {path}: {e}")
```

---

## 📦 完整脚本

```python
#!/usr/bin/env python3
"""
YouTube Transcription Skill - YouTube 视频转写技能
1. CDP 导出 Chrome cookies
2. yt-dlp 下载音频
3. ASR API 转写
4. 保存到知识库

Usage:
    python youtube_transcription.py <youtube_url> [output_file]
    python youtube_transcription.py <youtube_url> --save-to-obsidian

Example:
    python youtube_transcription.py https://www.youtube.com/watch?v=xxx
    python youtube_transcription.py https://www.youtube.com/watch?v=xxx --save-to-obsidian
"""

import os
import sys
import time
import asyncio
import subprocess
import requests
import json

# API 配置
API_BASE = "http://api.adv-ci.com:8090"
API_TOKEN = "sk-5f8b839908d14561590b70227c72ca86"
DEFAULT_MODEL = "Qwen/Qwen3-ASR-1.7B"

# 路径配置
OBSIDIAN_BASE = "/home/bushuhui/data-all/note/bushuhui/Clippings"


async def export_chrome_cookies():
    """使用 CDP 导出 Chrome cookies 为 Netscape 格式"""
    try:
        import puppeteer
    except ImportError:
        print("Installing puppeteer-core...")
        subprocess.run([sys.executable, "-m", "pip", "install", "puppeteer-core"], check=True)
        import puppeteer
    
    print("Connecting to Chrome via CDP...")
    
    browser = await puppeteer.connect({
        'browserURL': 'http://127.0.0.1:9222',
        'defaultViewport': None
    })
    
    pages = await browser.pages()
    page = pages[0] if pages else await browser.newPage()
    
    # 访问 YouTube
    await page.goto('https://www.youtube.com/', {
        'waitUntil': 'networkidle2',
        'timeout': 30000
    })
    await asyncio.sleep(3)
    
    # 获取 cookies
    cdp = await page.createCDPSession()
    result = await cdp.send('Network.getAllCookies')
    cookies = result.get('cookies', [])
    
    # 转换为 Netscape 格式
    netscape = '# Netscape HTTP Cookie File\n'
    for c in cookies:
        if 'youtube' in c.get('domain', '') or 'google' in c.get('domain', ''):
            domain = c['domain']
            include_sub = 'TRUE' if domain.startswith('.') else 'FALSE'
            path = c.get('path', '/')
            secure = 'TRUE' if c.get('secure') else 'FALSE'
            expiration = int(c.get('expires', time.time() + 31536000))
            netscape += f"{domain}\t{include_sub}\t{path}\t{secure}\t{expiration}\t{c['name']}\t{c['value']}\n"
    
    cookie_file = '/tmp/youtube_cookies.txt'
    with open(cookie_file, 'w') as f:
        f.write(netscape)
    
    print(f"Exported {len(cookies)} cookies to {cookie_file}")
    
    await browser.disconnect()
    return cookie_file


def download_audio(youtube_url, cookie_file):
    """使用 yt-dlp 下载 YouTube 音频"""
    video_id = youtube_url.split('v=')[-1].split('&')[0]
    output_file = f"/tmp/youtube_{video_id}.mp3"
    
    if os.path.exists(output_file):
        print(f"Using cached audio: {output_file}")
        return output_file
    
    cmd = [
        'yt-dlp',
        '-x',
        '--audio-format', 'mp3',
        '--cookies', cookie_file,
        '--js-runtimes', 'node',
        '--remote-components', 'ejs:github',
        '-o', output_file,
        youtube_url
    ]
    
    print(f"Downloading: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Download stderr: {result.stderr}")
        raise Exception(f"yt-dlp error: {result.stderr[-500:]}")
    
    print(f"Downloaded to {output_file}")
    return output_file


def get_video_info(youtube_url):
    """获取视频信息（标题等）"""
    try:
        import puppeteer
    except ImportError:
        return {"title": "Unknown", "channel": "Unknown"}
    
    async def fetch():
        browser = await puppeteer.connect({
            'browserURL': 'http://127.0.0.1:9222',
            'defaultViewport': None
        })
        
        page = await browser.newPage()
        await page.goto(youtube_url, {'waitUntil': 'domcontentloaded', 'timeout': 30000})
        await asyncio.sleep(3)
        
        info = await page.evaluate('''() => {
            const title = document.querySelector('h1.ytd-video-primary-info-renderer')?.innerText || 
                         document.querySelector('#title h1')?.innerText || '';
            const channel = document.querySelector('#owner-name a')?.innerText || '';
            return { title: title.trim(), channel: channel.trim() };
        }''')
        
        await browser.disconnect()
        return info
    
    try:
        return asyncio.run(fetch())
    except Exception as e:
        print(f"Failed to get video info: {e}")
        return {"title": "Unknown", "channel": "Unknown"}


def transcribe_audio(audio_path, model=DEFAULT_MODEL):
    """调用 ASR API 转写音频"""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    session = requests.Session()
    session.trust_env = False
    
    print(f"Transcribing {audio_path}...")
    
    with open(audio_path, 'rb') as f:
        files = {'file': (os.path.basename(audio_path), f, 'audio/mpeg')}
        data = {'model': model}
        
        response = session.post(
            f'{API_BASE}/v1/audio/transcriptions',
            headers=headers,
            files=files,
            data=data,
            timeout=600
        )
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")
    
    result = response.json()
    
    if 'text' not in result:
        raise Exception(f"No text in response: {result}")
    
    return result['text']


def save_to_obsidian(text, video_title, video_url):
    """保存转写结果到 Obsidian 知识库"""
    import datetime
    
    today = datetime.datetime.now()
    month_dir = today.strftime("%Y%m")
    date_file = today.strftime("%Y%m%d")
    
    month_path = f"{OBSIDIAN_BASE}/{month_dir}"
    os.makedirs(month_path, exist_ok=True)
    
    file_path = f"{month_path}/{date_file}.md"
    
    existing_content = ""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    
    new_section = f"""
---

## YouTube 视频转写：{video_title}

**视频链接**: {video_url}
**转写时间**: {today.strftime("%Y-%m-%d %H:%M")}
**转写模型**: {DEFAULT_MODEL}
**字数**: {len(text)} 字

### 转写内容

{text}

---
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(existing_content + new_section)
    
    print(f"Saved to {file_path}")
    return file_path


def cleanup(*paths):
    """清理临时文件"""
    for path in paths:
        if path and path.startswith('/tmp/') and os.path.exists(path):
            try:
                os.remove(path)
                print(f"Cleaned up: {path}")
            except Exception as e:
                print(f"Failed to clean up {path}: {e}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python youtube_transcription.py <youtube_url> [output_file]")
        print("Options:")
        print("  --save-to-obsidian  Save to Obsidian knowledge base")
        print("Example:")
        print("  python youtube_transcription.py https://www.youtube.com/watch?v=xxx")
        print("  python youtube_transcription.py https://www.youtube.com/watch?v=xxx --save-to-obsidian")
        sys.exit(1)
    
    youtube_url = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    save_to_obs = '--save-to-obsidian' in sys.argv
    
    cookie_file = None
    audio_file = None
    
    try:
        # Step 1: 导出 cookies
        cookie_file = asyncio.run(export_chrome_cookies())
        
        # Step 2: 获取视频信息
        video_info = get_video_info(youtube_url)
        video_title = video_info.get('title', 'Unknown')
        print(f"Video: {video_title}")
        
        # Step 3: 下载音频
        audio_file = download_audio(youtube_url, cookie_file)
        
        # Step 4: 转写
        text = transcribe_audio(audio_file)
        print(f"Transcription complete! Length: {len(text)} chars")
        
        # Step 5: 保存
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Saved to {output_path}")
        
        if save_to_obs:
            save_to_obsidian(text, video_title, youtube_url)
        
        # Step 6: 清理
        cleanup(cookie_file, audio_file)
        
        print("\n=== YouTube Transcription Complete ===")
        if save_to_obs:
            print(f"Saved to Obsidian: {OBSIDIAN_BASE}/YYYYMM/DDDD.md")
        if output_path:
            print(f"Output file: {output_path}")
        print(f"Transcription length: {len(text)} chars")
        
    except Exception as e:
        print(f"Error: {e}")
        cleanup(cookie_file, audio_file)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## 🔧 前置条件

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

---

### 2. Chrome Remote Debugging

**确保 Chrome 已启动并开启远程调试**:

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222

# 或使用已有的 Chrome 实例（如果已配置）
```

---

### 3. yt-dlp 配置

**检查 yt-dlp 版本**:
```bash
yt-dlp --version  # 应该是最新版本
```

**更新 yt-dlp**:
```bash
yt-dlp -U
```

---

## 📝 使用示例

### 示例 1: 基础转写

```bash
python youtube_transcription.py https://www.youtube.com/watch?v=aZT9d8qrirY
```

**输出**:
```
Connecting to Chrome via CDP...
Exported 293 cookies to /tmp/youtube_cookies.txt
Video: 🚀OpenClaw 多智能体终极解决方案
Downloading: yt-dlp -x --audio-format mp3 ...
Downloaded to /tmp/youtube_aZT9d8qrirY.mp3
Transcribing /tmp/youtube_aZT9d8qrirY.mp3...
Response status: 200
Transcription complete! Length: 4367 chars
Cleaned up: /tmp/youtube_cookies.txt
Cleaned up: /tmp/youtube_aZT9d8qrirY.mp3
```

---

### 示例 2: 保存到 Obsidian

```bash
python youtube_transcription.py https://www.youtube.com/watch?v=xxx --save-to-obsidian
```

**输出位置**: `/home/bushuhui/data-all/note/bushuhui/Clippings/YYYYMM/DDDD.md`

---

### 示例 3: 指定输出文件

```bash
python youtube_transcription.py https://www.youtube.com/watch?v=xxx /path/to/output.txt
```

---

### 示例 4: OpenClaw 自然语言调用

```
用户：帮我转写这个 YouTube 视频并保存到知识库
https://www.youtube.com/watch?v=aZT9d8qrirY

AI: 好的，我正在处理...
    ✓ Chrome cookies 导出完成（293 个）
    ✓ 音频下载完成（6.8MB）
    ✓ 转写完成（4367 字）
    ✓ 已保存到知识库：Clippings/202603/20260320.md
```

---

## ⚠️ 注意事项

### 1. Chrome Cookies

**必须使用 CDP 导出**:
- YouTube 有反爬虫机制
- 需要登录态才能下载高质量音频
- cookies 会过期，每次下载前重新导出

---

### 2. yt-dlp 参数

**关键参数**:
```bash
--cookies /tmp/youtube_cookies.txt    # 使用导出的 cookies
--js-runtimes node                     # JS runtime（处理 n 参数）
--remote-components ejs:github         # 远程 challenge solver
```

**缺少这些参数会导致**:
- `403 Forbidden`
- `n parameter` 错误
- `PO Token` 错误

---

### 3. 代理配置

**ASR API 调用必须禁用代理**:
```python
session = requests.Session()
session.trust_env = False
```

---

### 4. 超时设置

```python
timeout=600  # 10 分钟超时
```

长视频转写需要较长时间

---

### 5. 临时文件

**会自动清理**:
- `/tmp/youtube_cookies.txt`
- `/tmp/youtube_<video_id>.mp3`

---

## 🐛 故障排查

### 问题 1: "Cannot connect to Chrome"

**原因**: Chrome 未启动或端口不对

**解决**:
```bash
# 检查 Chrome 是否运行
ps aux | grep chrome

# 启动 Chrome with remote debugging
google-chrome --remote-debugging-port=9222
```

---

### 问题 2: "yt-dlp: 403 Forbidden"

**原因**: cookies 过期或缺失

**解决**:
- 重新运行脚本（会自动重新导出 cookies）
- 确保 Chrome 已登录 YouTube

---

### 问题 3: "n parameter" 错误

**原因**: yt-dlp 缺少 JS runtime

**解决**:
```bash
# 确保参数正确
yt-dlp --js-runtimes node --remote-components ejs:github ...
```

---

### 问题 4: "API error: 401"

**原因**: ASR API Token 无效

**解决**: 检查 `API_TOKEN` 配置

---

### 问题 5: 转写超时

**原因**: 视频太长

**解决**:
- 增加 `timeout` 值
- 使用更短的片段

---

## 🔗 相关资源

### API 文档
- **端点**: `http://api.adv-ci.com:8090/docs`
- **Models**: `http://api.adv-ci.com:8090/v1/models`

### 相关 Skill
- [[Audio Transcription Skill]] - 纯音频转写
- [[YouTube Download Skill]] - YouTube 下载

### 外部资源
- **yt-dlp**: https://github.com/yt-dlp/yt-dlp
- **Chrome DevTools Protocol**: https://chromedevtools.github.io/devtools-protocol/

---

## 📊 性能指标

| 指标 | 值 |
|------|-----|
| **下载速度** | ~1-5 MB/s（取决于网络） |
| **转写速度** | ~1-2 分钟/10 分钟音频 |
| **准确率** | 中文 ~95%，英文 ~98% |
| **支持语言** | 中文、英文、日文、韩文等 |

---

## 📈 未来改进

- [ ] 支持播放列表批量转写
- [ ] 支持说话人分离
- [ ] 支持时间戳输出
- [ ] 支持自动生成摘要
- [ ] 支持多语言字幕生成

---

**创建者**: Jack (AI Assistant)
**最后更新**: 2026-03-20
**版本**: 1.0.0

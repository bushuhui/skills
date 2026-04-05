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
        import traceback
        traceback.print_exc()
        cleanup(cookie_file, audio_file)
        sys.exit(1)


if __name__ == "__main__":
    main()

# Bilibili 视频转写平台笔记

## 音频下载

### 无需 Cookies 的场景

yt-dlp 下载 B站音频**不需要 cookies**，直接执行即可：

```bash
yt-dlp -x --audio-format mp3 -o "output.%(ext)s" "https://www.bilibili.com/video/BVxxxxx/"
```

- 默认音质为当前可获取的最高音质
- 4K/1080P高码率需要大会员，但音频轨道通常无限制
- 下载速度约 5-10 MB/s

### 短链接处理

`b23.tv/xxx` 短链接需要先通过浏览器导航获取真实 URL：
- 使用 `browser_navigate` 访问短链接
- 从跳转后的 URL 提取 BV 号（`BV1NvRyBzEhq` 格式）

## 字幕获取（受限）

### yt-dlp 字幕

```bash
yt-dlp --write-sub --all-subs --skip-download "https://www.bilibili.com/video/BVxxxxx/"
```

**问题**：无 cookies 时只会下载弹幕（danmaku.xml），不会下载字幕轨道。

错误信息：`WARNING: [BiliBili] Subtitles are only available when logged in.`

### B站 API 字幕接口

```bash
curl -s "https://api.bilibili.com/x/player/v2?cid=<cid>&bvid=<bvid>"
```

- 需要先从页面提取 `cid`（在视频格式信息中）
- **可能超时**，API 响应不稳定
- 即使返回数据，`subtitles` 字段也可能为空（需要登录态）

### 结论：推荐 ASR 方案

**不要依赖 B站字幕**，最佳路径是：
1. 浏览器打开页面 → 获取视频标题、作者、描述
2. yt-dlp 下载音频（无需 cookies）
3. pi-llm-server ASR 转写

## ⚠️ yt-dlp 失败时的 API 降级方案

**问题**: 部分 B站视频 yt-dlp 报 `ERROR: No video formats found`，即使 yt-dlp 已是最新版本。

**原因**: B站对部分视频（尤其是较新或受限内容）的格式接口做了限制，yt-dlp 无法解析。

**解决方案**: 通过 B站 API 直接获取 DASH 流地址下载：

```python
import requests, subprocess, re

# 1. 从 Chrome CDP 获取 cookies（B站 API 需要登录态 cookies）
result = subprocess.run(
    ['node', '/home/bushuhui/.agents/skills/web-access/scripts/cdp-cli.mjs', 'eval', '<targetId>', 'document.cookie'],
    capture_output=True, text=True
)
cookie_str = result.stdout.strip()

bvid = 'BV1UfGo6GEVR'
cid = '38606145230'  # 从 /x/web-interface/view?bvid=XXX API 获取

headers = {
    'Cookie': cookie_str,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': f'https://www.bilibili.com/video/{bvid}/',
}

# 2. 获取播放地址（DASH 格式）
r = requests.get('https://api.bilibili.com/x/player/playurl', params={
    'bvid': bvid, 'cid': cid, 'qn': 80, 'fnval': 16, 'fourk': 1,
}, headers=headers)
dash = r.json()['data']['dash']
audio_url = max(dash['audio'], key=lambda x: x.get('bandwidth', 0))['baseUrl']
video_url = max(dash['video'], key=lambda x: x.get('bandwidth', 0))['baseUrl']

# 3. 下载音频流
headers2 = {
    'Cookie': cookie_str,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.bilibili.com/',
    'Origin': 'https://www.bilibili.com',
}
host_match = re.search(r'https://([^/]+)', audio_url)
if host_match:
    headers2['Host'] = host_match.group(1)

resp = requests.get(audio_url, headers=headers2, timeout=120)
with open('audio.m4s', 'wb') as f:
    f.write(resp.content)

# 4. 转 MP3
# ffmpeg -y -i audio.m4s -q:a 0 -map a audio.mp3
```

**注意事项**:
- mcdn CDN 节点（`*.mcdn.bilivideo.cn`）需要在请求头中设置 `Host` 字段
- 音频为 `.m4s` 格式，需 ffmpeg 转 mp3
- CID 可通过 `api.bilibili.com/x/web-interface/view?bvid=XXX` 获取
- 视频流和音频流分开下载，如需合并：`ffmpeg -i video.m4s -i audio.m4s -c copy output.mp4`

## ASR 转写

### 使用 pi-llm-server

```bash
# 短时间音频（<10分钟）
python3 scripts/pi_llm_server_skill.py transcribe audio.mp3

# 长视频（>30分钟）→ 后台运行
python3 scripts/pi_llm_server_skill.py transcribe audio.mp3 2>&1 &
# ASR API 超时设置 600s，但大文件仍需等待
```

### 后台运行模式

对于 60 分钟以上的视频，前台执行会超时。使用后台进程：

```bash
# 通过 terminal 工具的 background=true 模式
# 或 nohup + 轮询检查
```

## 知识库保存结构

```
Clippings/YYYYMM/<视频标题目录>/
├── README.md          # 视频元数据 + 转写摘要
└── images/            # 截图（如有）
```

在当日索引文件 `Clippings/YYYYMM/YYYYMMDD.md` 中添加条目。

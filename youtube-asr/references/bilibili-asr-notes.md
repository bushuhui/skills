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

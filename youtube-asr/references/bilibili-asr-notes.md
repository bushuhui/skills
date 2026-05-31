# B站（Bilibili）视频处理补充说明

## yt-dlp 下载

```bash
yt-dlp --format "bestaudio" --extract-audio --audio-format mp3 \
  -o "原始音频.%(ext)s" "https://www.bilibili.com/video/<BV号>"
```

- **不需要 cookies**：yt-dlp 无需登录即可下载音频（免费版音质足够 ASR 使用）
- 提示 "missing formats, need premium" 可忽略
- yt-dlp 版本需保持最新：`yt-dlp -U`（B站经常更新接口）

## 完整工作流

1. 从链接提取 BV 号（区分大小写）或从截图识别
2. 创建目录 `Clippings/YYYYMM/<视频标题>/images`
3. yt-dlp 下载音频 → extract-audio 转 mp3
4. `ffprobe` 检查时长：<20 分钟直接转写，≥20 分钟用 split_transcribe.py
5. ASR 转写（Qwen3-ASR-1.7B 中文效果好）
6. 创建 README.md（标题、UP主、BV号、链接、日期、播放量、概述）
7. 更新当日索引 `Clippings/YYYYMM/YYYYMMDD.md`

## 与 YouTube 的区别

| 项目 | YouTube | B站 |
|------|---------|-----|
| 下载 | 需 CDP 导 cookies | yt-dlp 直连，无需 cookies |
| 音频 | 直接下载 | 下载后 extract-audio 转 mp3 |
| 字幕 | 有字幕轨道时优先 | 无字幕，必须 ASR |
| 权限 | 部分需登录 | 无需登录 |

## 保存结构

```
Clippings/YYYYMM/<视频标题>/
├── README.md          # 结构化笔记
├── 原始音频.mp3        # 必须保留
├── 原始音频.txt        # ASR 转写原文
└── images/            # 截图等（如有）
```

## 索引格式

```markdown
## 📺 <视频标题>

- **来源**: B站 - <UP主名>
- **BV号**: <BV号>
- **链接**: https://www.bilibili.com/video/<BV号>
- **详情**: [[<目录名>/README]]
- **概述**: <一句话概述>
```

## 常见陷阱

- yt-dlp 版本过旧 → `yt-dlp -U`
- BV 号区分大小写，不要改动
- ASR 批量调用 10-15 段后可能 hang（详见 pi-llm-server skill）
- 目录名用 `-` 替代空格

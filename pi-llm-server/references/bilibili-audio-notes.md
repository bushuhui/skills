# B站视频处理注意事项

## 字幕下载

yt-dlp 下载 B站字幕**需要登录认证**（`--cookies-from-browser` 或 `--cookies`），未登录时无法获取字幕轨道：

```
WARNING: Subtitles are only available when logged in.
```

**替代方案**: 下载音频 → ASR 转写 → 获得文字

## ASR 长音频超时

`Qwen/Qwen3-ASR-1.7B` 对 >20 分钟音频极易超时（API 默认 600s timeout）。
必须分段处理（详见 SKILL.md）。

## 典型工作流

1. `yt-dlp -x --audio-format mp3 -o "name.%(ext)s" <B站URL>` — 下载音频
2. 用 `split_transcribe.py` 分割 + 转写
3. 保存字幕到知识库 + 更新当日索引

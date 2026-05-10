---
name: pi-llm-server
description: 统一 LLM 服务网关，提供语音识别 (ASR)、文档解析 (OCR)、Embedding 向量生成、文档重排序 (Rerank) 服务。当用户需要转写音频、解析文档为 Markdown、生成嵌入向量或重排序文档时使用此技能。
triggers:
  - 语音识别
  - 转写
  - 音频转文字
  - 文档解析
  - PDF 转 Markdown
  - OCR
  - embedding
  - rerank
---

## 服务概览

统一 LLM 服务网关，支持 4 种服务：

| 服务 | 端点 | 模型 | 说明 | 详情 |
|------|------|------|------|------|
| **ASR** | `/v1/audio/transcriptions` | `Qwen/Qwen3-ASR-1.7B` | 语音识别 | [`services/asr.md`](services/asr.md) |
| **OCR** | `/v1/ocr/parser` | `mineru/pipeline` | 文档解析 | [`services/ocr.md`](services/ocr.md) |
| **Embedding** | `/v1/embeddings` | `unsloth/Qwen3-Embedding-0.6B` | 文本向量化 | [`services/embedding.md`](services/embedding.md) |
| **Reranker** | `/v1/rerank` | `Qwen/Qwen3-Reranker-0.6B` | 文档重排序 | [`services/rerank.md`](services/rerank.md) |

## 配置

```
API 地址: http://api.adv-ci.com:8090/v1  (环境变量 PI_LLM_URL)
Token:    sk-5f8b839908d14561590b70227c72ca86  (环境变量 PI_LLM_API_KEY)
Swagger:  http://api.adv-ci.com:8090/docs
```

## 调用方式

**自然语言**: "转写这个音频" / "解析这个 PDF" / "生成 embedding" / "重排序这些文档"

**Python 脚本**:
```bash
python scripts/pi_llm_server_skill.py <transcribe|parse|embed|rerank|status> [参数]
```

输出目录固定为**源文件所在目录**，不支持自定义输出路径。

**长音频专用**（>10 分钟）:
```bash
python scripts/split_transcribe.py audio.mp3 [段长度_秒]
```

## 参考文档

- **B站音频处理**: `references/bilibili-audio-notes.md`

## 支持的文件格式

| 类型 | 扩展名 | 处理流程 |
|------|--------|----------|
| PDF | `.pdf` | 直接解析；加密 PDF 自动 Ghostscript 解密后提交 OCR |
| 图片 | `.jpg`, `.jpeg`, `.png` | 转 PDF → 解析 |
| Word | `.docx`, `.doc` | libreoffice 转 PDF → 解析 |
| PPT | `.pptx`, `.ppt` | libreoffice 转 PDF → 解析 |
| Excel | `.xlsx`, `.xls` | libreoffice 转 PDF → 解析 |
| 音频 | `.mp3`, `.wav`, `.m4a`, `.flac` | 语音识别 |

## 文档解析输出结构

所有文档解析后统一输出为 **Markdown + 图片** 格式：

```
源文件:     /path/to/document.pdf
Markdown:   /path/to/document.md          # 与源文件同目录
图片目录:   /path/to/document_images/     # 与源文件同名 + _images
```

Markdown 中的图片路径自动修正为 `document_images/xxx.png`。

**输出 Markdown 内部结构**（按文档类型）:

| 元素 | 输出格式 | 说明 |
|------|----------|------|
| 文档标题 | `# 标题` | 一篇文档仅一个 H1 |
| 章节标题 | `## H2` / `### H3` | 按原始层级 |
| 正文段落 | 普通文本，空行分隔 | 保留段落结构 |
| 列表 | `- ` / `1. ` | 有序/无序列表 |
| 表格 | `| 列1 | 列2 |` | 标准 Markdown 表格 |
| 行内公式 | `$E=mc^2$` | LaTeX 语法 |
| 块级公式 | `$$\n...\n$$` | 独立成块 |
| 代码块 | ```` ```语言名 ```` | 带语言标注 |
| 图片 | `![说明](document_images/xxx.png)` | 提取到独立目录 |
| 图表标题 | 图片下方普通文本 | 如 "图1: 系统架构" |
| 脚注/引用 | `[^1]` + 文末列表 | 标准脚注格式 |
| 页眉页脚 | **删除** | 不保留页码、公司名等 |

**不同类型文档的特殊约定**:

| 类型 | 特殊处理 |
|------|----------|
| **学术论文** | 公式使用 LaTeX，保留参考文献格式，删除双栏布局痕迹 |
| **技术规格书** | 代码块标注语言，参数表格转为标准表格 |
| **合同/法律文书** | 保留编号条款，签名区域标记为 `[签名区]` |
| **Word/PPT** | 保留原始排版层级，幻灯片标题转为 H2 |
| **Excel** | 每个 sheet 转为一个表格，sheet 名作为标题 |
| **扫描件/图片** | 保留 OCR 原文，不确定字符用 `[?]` 标记 |

## ⚠️ ASR 批量转写 Hang 检测

**问题**: `pi_llm_server_skill.py transcribe` 在**批量连续调用**时，部分 chunk 会**无限期 hang** — 无 stdout 输出、无 stderr、文件不生成。健康检查显示 ASR "healthy"（延迟 ~9ms），但实际转录请求卡死。

**实测表现**（78 分钟音频，40 个 2 分钟 chunk）：
- chunk_000~009 正常，每段 ~3-6 秒
- chunk_010 30s timeout 失败，60s 重试成功（721 字符）
- chunk_012 30s timeout 失败，60s 重试成功
- chunk_020 30s timeout 失败
- chunk_013~039 部分 hang 超 120s 仍无输出
- **规律**: 连续调用 10-15 段后开始不稳定，hang 概率递增

**根因**: 服务端的 ASR 模型推理队列可能阻塞，健康检查只探测端口连通性（~9ms），不验证推理能力。

**正确做法**:
1. **每段必须加 timeout 包裹**（最低 60s，推荐 180s）
2. **失败后重试一次**，部分 hang 段在重试时可恢复
3. **逐段执行，不要用 `subprocess.run` 的 pipe 或批量循环**，每个 chunk 独立的 `timeout` 命令最可靠

```bash
# 可靠方案：用 shell timeout 包裹每次调用
for chunk in /tmp/audio_chunks/chunk_*.mp3; do
    name=$(basename "$chunk" .mp3)
    txt="/tmp/audio_chunks/${name}.txt"
    [ -f "$txt" ] && continue
    timeout 180 python3 /home/bushuhui/.agents/skills/pi-llm-server/scripts/pi_llm_server_skill.py transcribe "$chunk" 2>&1
    [ -f "$txt" ] && echo "[$name] OK" || echo "[$name] FAILED, retrying..." && \
    timeout 180 python3 /home/bushuhui/.agents/skills/pi-llm-server/scripts/pi_llm_server_skill.py transcribe "$chunk" 2>&1
done
```

4. **完全卡死时**：SSH 到 tiger 服务器检查 ASR 服务状态，必要时重启 `asr_server.py`

## ⚠️ 长音频处理（ASR 超时陷阱）

**问题**: `Qwen/Qwen3-ASR-1.7B` 模型对 **>20 分钟的音频** 经常超时（API 默认 600s 不够用）。
**实测**: 60 分钟音频（51MB）连续转写必然超时。

**正确做法 — 分段转写**:

1. **用 FFmpeg 切片**（推荐 5 分钟一段，兼顾速度和成功率）:
```bash
ffmpeg -y -i audio.mp3 -f segment -segment_time 300 -c copy out/part_%03d.mp3
```

2. **逐段提交 ASR API**，每段超时设为 1800s:
```python
import requests, glob, os

API_URL = 'http://api.adv-ci.com:8090/v1/audio/transcriptions'
API_KEY = 'sk-5f8b839908d14561590b70227c72ca86'
session = requests.Session()
session.trust_env = False

full_text = []
for part in sorted(glob.glob('out/part_*.mp3')):
    with open(part, 'rb') as f:
        r = session.post(API_URL,
            headers={'Authorization': f'Bearer {API_KEY}'},
            files={'file': (os.path.basename(part), f, 'audio/mpeg')},
            data={'model': 'Qwen/Qwen3-ASR-1.7B'},
            timeout=1800)
    if r.status_code == 200:
        full_text.append(r.json().get('text', ''))

with open('transcript.txt', 'w', encoding='utf-8') as f:
    f.write('\n\n---\n\n'.join(full_text))
```

3. **参考脚本**: `scripts/split_transcribe.py` — 一键分割+转写

## ⚠️ 加密 PDF 自动处理

**机制**: `parse` 命令已内置加密 PDF 自动检测与解密流程，无需手动预处理。

**流程**:
1. **检测**: 使用 `pdfinfo`（回退到 `grep /Encrypt`）检测 PDF 是否加密
2. **备份**: 原始加密文件重命名为 `{原名}_ori.pdf` 保留备份
3. **解密**: Ghostscript 生成解密后的文件到原始文件名 `{原名}.pdf`
4. **OCR**: 用解密后的文件提交 MinerU 解析，输出文件名天然一致
5. **输出**: `{原名}.md` + `{原名}_images/` + `{原名}_ori.pdf`（原始加密备份）

**用户侧零操作**，直接 `python pi_llm_server_skill.py parse encrypted.pdf` 即可。

**⚠️ 图片路径注意**: 如果 Ghostscript 解密生成的临时文件名与原文件名不同，OCR 输出的 Markdown 中图片引用路径可能不匹配。脚本会在输出时自动修正为 `{原文件名}_images/xxx.png` 格式。

## 注意事项

- **`parse` 不支持 `--output` 参数**：输出目录始终为源文件所在目录，不可自定义
- **代理**: 必须 `session.trust_env = False` 禁用系统代理
- **超时**: ASR 600s（短音频）/ 1800s（长音频分段）/ OCR 1800s / Embedding 60s / Rerank 120s
- **文件大小**: 音频 <100MB, 文档 <50MB
- **B站字幕**: yt-dlp 默认无法下载字幕（需要登录），必须先下载音频再 ASR 转写

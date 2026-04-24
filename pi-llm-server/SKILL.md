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

## 支持的文件格式

| 类型 | 扩展名 | 处理流程 |
|------|--------|----------|
| PDF | `.pdf` | 直接解析 |
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

## 注意事项

- **代理**: 必须 `session.trust_env = False` 禁用系统代理
- **超时**: ASR 600s / OCR 1800s / Embedding 60s / Rerank 120s
- **文件大小**: 音频 <100MB, 文档 <50MB

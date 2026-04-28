---
name: markdown-to-docx
description: 将 Markdown 文件转换为 Word DOCX 格式。支持两种模式：直接转换（pandoc，适合含 LaTeX 公式的学术论文）和模板转换（python-docx 匹配参考模板样式，适合公文/技术方案/报告等需要严格格式的场景）。
---

# markdown-to-docx

将 Markdown 文件转换为 Word DOCX 文件，提供两种转换方式。

## 两种转换方式对比

| 维度 | 方式 A：直接转换 | 方式 B：模板转换 |
|------|----------------|----------------|
| **引擎** | pandoc | python-docx |
| **公式支持** | ✅ LaTeX → OMML | ❌ 纯文本（公式保留为 $...$） |
| **样式控制** | pandoc 默认样式 | ✅ 匹配参考模板样式 |
| **中文支持** | 取决于 pandoc 版本 | ✅ 完美（宋体/黑体等） |
| **适用场景** | 学术论文、含公式的技术文档 | 公文、技术方案、报告、需要匹配模板的文档 |
| **图片** | ✅ 支持 | ❌ 不支持 |

### 选择指南

- 用户要求"直接转"、"转一下" → **方式 A**
- 用户提供参考模板（"用这个当模板"） → **方式 B**
- 文档含大量 LaTeX 公式 → **方式 A**
- 需要匹配特定样式/字体/排版 → **方式 B**
- 用户两个都提了 → 两种方式都执行

---

## 方式 A：直接转换（pandoc）

使用 `md2docx.sh` 或 `md2docx_converter.py` 脚本。

### 快速命令

```bash
# Shell 脚本（推荐）
bash /home/bushuhui/.agents/skills/markdown-to-docx/md2docx.sh <input.md> [output.docx]

# Python 脚本（含公式修正）
python3 /home/bushuhui/.agents/skills/markdown-to-docx/md2docx_converter.py <input.md> [output.docx]
```

### 特点
- `--mathml`：LaTeX 公式转为 Word 原生 OMML 格式
- 自动修正公式格式问题（数字间空格、下标等）
- 支持行内 `$...$` 和块级 `$$...$$` 公式

---

## 方式 B：模板转换（python-docx）

使用参考模板的样式（字体、字号、加粗、Heading 级别等）来渲染 Markdown 内容。

### 快速命令

```bash
python3 /home/bushuhui/.agents/skills/markdown-to-docx/md2docx_template.py <input.md> --template <template.docx> -o <output.docx>
```

### Markdown 标题到 Word 样式的映射规则

| Markdown 元素 | 默认映射 | 特殊规则 |
|--------------|---------|---------|
| `# 标题`（第一个） | Normal（加粗黑体，作为文档标题） | 不转 Heading 1 |
| `## 研究内容、功能` / `## 主要性能指标` | Heading 1 | 根据关键词自动识别 |
| `## 1、xxx` / `## 2、xxx` 等 | Heading 2 | 编号型子标题 |
| 正文 | Normal（宋体 12pt） | |
| `1.` `2.` `3.` 开头的行 | Normal（独立段落） | 技术指标等编号列表 |

### 样式配置

```python
# 标题样式
title: 黑体, 16pt, bold
# Heading 1（大章节）
H1: 黑体, 16pt, bold
# Heading 2（子标题）
H2: 黑体, 14pt, bold
# 正文
Normal: 宋体, 12pt
```

### 完整流程

```python
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
import re

# 1. 加载模板
doc = Document(template_path)

# 2. 清空原有内容
for p in doc.paragraphs:
    p.clear()

# 3. 解析 Markdown
lines = md_content.strip().split('\n')
entries = []  # (style_id, text)

for line in lines:
    if line.startswith('## '):
        title = line[3:].strip()
        # 关键词识别大章节
        if title in ('研究内容、功能', '主要性能指标', '研究目标', '技术路线'):
            entries.append(('H1', title))
        else:
            entries.append(('H2', title))
    elif line.startswith('# '):
        entries.append(('Title', line[2:].strip()))
    elif re.match(r'^\d+\.', line):
        entries.append(('Normal', line))  # 编号行独立成段
    else:
        # 合并连续文本行
        ...

# 4. 逐段写入，匹配样式
for idx, (style_id, text) in enumerate(entries):
    p = doc.paragraphs[idx] if idx < len(doc.paragraphs) else doc.add_paragraph()
    p.clear()
    run = p.add_run(text)
    
    if style_id == 'Title':
        p.style = doc.styles['Normal']
        run.font.name = '黑体'; run.font.size = Pt(16); run.font.bold = True
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    elif style_id == 'H1':
        p.style = doc.styles['Heading 1']
        run.font.name = '黑体'; run.font.size = Pt(16); run.font.bold = True
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    elif style_id == 'H2':
        p.style = doc.styles['Heading 2']
        run.font.name = '黑体'; run.font.size = Pt(14); run.font.bold = True
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    else:
        p.style = doc.styles['Normal']
        run.font.name = '宋体'; run.font.size = Pt(12)
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# 5. 删除多余段落
while len(doc.paragraphs) > len(entries):
    p = doc.paragraphs[-1]
    p._element.getparent().remove(p._element)

# 6. 保存
doc.save(output_path)
```

### 关键注意事项

1. **中文字体**：必须用 `run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')` 设置东亚字体，否则 Word 可能用默认字体渲染中文
2. **编号段落独立成段**：技术指标等 `1.` `2.` `3.` 开头的行必须作为独立段落，不能合并
3. **标题识别**：第一个 `#` 行作为文档标题（Normal 样式 + 黑体加粗），不作为 Heading
4. **多余段落清理**：写入完成后必须删除模板中多余的段落，否则文档尾部会有空行
5. **公式处理**：模板转换不支持 LaTeX → OMML，公式保留为 `$...$` 文本

---

## 组合使用示例

### 场景：同时执行两种转换

```bash
# 方式 A：pandoc 直接转（保留公式）
bash md2docx.sh input.md output_pandoc.docx

# 方式 B：模板转换（匹配样式）
python3 md2docx_template.py input.md --template template.docx -o output_template.docx
```

### 场景：先用方式 B 转换，再检查公式显示

如果用户需要公式在 Word 中可编辑，推荐方式 A。如果用户更看重排版/样式匹配，推荐方式 B。

---

## 文件清单

| 文件 | 用途 |
|------|------|
| `md2docx.sh` | Shell 脚本 — pandoc 快速转换 |
| `md2docx_converter.py` | Python 脚本 — 含公式修正的 pandoc 转换 |
| `md2docx_template.py` | Python 脚本 — 模板样式匹配转换 |
| `skill.md` | 本文档 |

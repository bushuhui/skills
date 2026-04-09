---
name: markdown-to-docx
description: Use this skill whenever a Markdown file needs to be converted to Word DOCX format. This includes: converting Markdown documents to .docx files, transforming LaTeX/math equations to Word OMML format, processing academic papers or technical documentation for Word output, working with Markdown templates that need Word delivery. Trigger when the user mentions converting Markdown to Word, .docx output, or any workflow where Markdown content must become a Word document.
---

# markdown-to-docx

将 Markdown 文件（含 LaTeX 公式）转换为 Word DOCX 文件，支持将 LaTeX 公式转换为 Word 原生 OMML 格式。

## 功能

1. **公式错误检测与修正** - 检测并修正 Markdown 中 LaTeX 公式的格式问题
2. **转换为 DOCX** - 使用 pandoc 将 Markdown 转换为 Word 文档，LaTeX 公式自动转为 OMML 格式

## 使用场景

- 学术论文 Markdown 转 Word
- 技术文档含数学公式的转换
- 需要 Word 原生公式格式的文档转换

## 使用方法

```
/markdown-to-docx <markdown 文件路径> [输出文件路径]
```

## 参数说明

- `markdown 文件路径` - 要转换的 Markdown 文件路径（必需）
- `输出文件路径` - 输出的 DOCX 文件路径（可选，默认与 Markdown 同名）

## 示例

```
/markdown-to-docx 2025-IVU-AutoNav_cn.md
/markdown-to-docx paper.md output.docx
```

## 依赖工具

- `pandoc` - 文档转换工具（需已安装）
- python 3.8+
- `latex2mathml` (可选，用于高级公式处理)

## 注意事项

1. 确保 pandoc 已安装：`pandoc --version`
2. LaTeX 公式使用 `$...$`（行内）或 `$$...$$`（块级）格式
3. 转换后的公式为 Word 原生 OMML 格式，可在 Word 中编辑
4. 图片链接需要保持相对路径正确

## 支持的 LaTeX 公式

- 行内公式：`$x^2 + y^2 = z^2$`
- 块级公式：`$$\sum_{i=1}^n x_i$$`
- 矩阵环境：`bmatrix`, `pmatrix`, `array` 等
- 分数、根式、积分、求和等常见数学符号

## 工作流程

1. 读取 Markdown 文件
2. 检测并修正 LaTeX 公式格式问题（数字间空格、下标格式等）
3. 使用 pandoc 将修正后的 Markdown 转换为 DOCX
4. pandoc 自动将 LaTeX 公式转换为 OMML 格式
5. 输出可编辑的 Word 文档

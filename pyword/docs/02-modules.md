---
# 辅助模块索引

## 模块功能与调用关系

| 模块文件 | 主要功能 | 被调用场景 |
|---------|---------|-----------|
| `_01_docx_bookmarks.py` | 书签插入与管理 | 交叉引用、目录生成 |
| `_02_docx_captions.py` | 图题/表题/SEQ题注 | 10.04, 13.01, 16.01 |
| `_03_docx_fields.py` | 目录域/REF/PAGEREF/SEQ | 10.xx, 16.xx |
| `_04_docx_math.py` | OMML公式创建 | 14.xx |
| `_05_docx_numbering.py` | 编号定义与多级编号 | 01.04, 07.xx, 11.xx |
| `_06_docx_styles.py` | 样式创建与管理 | 06.xx, 07.xx |
| `_07_docx_tables.py` | 表格边框/三线表 | 12.xx |
| `_08_docx_textops.py` | 文本遍历与替换 | 15.xx, 04.05 |
| `_09_format_presets.py` | 字号/字体/对齐预设 | 05.xx, 06.xx |
| `_10_style_presets.py` | 论文样式/编号规则 | 06.xx, 07.xx |
| `_11_docx_enhance_presets.py` | 扩展样式/标点规则 | 15.xx |
| `_12_docx_format_helpers.py` | 格式设置辅助函数 | 05.xx, 06.xx |
| `_13_docx_title_helpers.py` | 标题识别辅助 | 02.xx, 07.xx |
| `_14_docx_review_demo.py` | 审阅示例文档生成 | 19.xx |
| `_15_docx_crypto.py` | 密码加密/解密 | 19.01, 19.04 |
| `_16_docx_revisions.py` | 修订生成/接受/拒绝 | 19.05, 19.06 |

---

# 可抽取函数清单

## 通用能力函数（可直接 import 使用）

| 模块 | 函数名 | 功能描述 | 典型调用场景 |
|-----|-------|---------|-------------|
| `_09_format_presets.py` | `resolve_font_size_pt()` | 字号名称转 pt 值 | 05.xx, 06.xx |
| `_09_format_presets.py` | `resolve_font_family()` | 字体名称转规范格式 | 05.xx, 06.xx |
| `_09_format_presets.py` | `resolve_alignment()` | 对齐方式名称转枚举 | 05.xx, 06.xx |
| `_01_docx_bookmarks.py` | `sanitize_bookmark_name()` | 清洗书签名称 | 16.xx, 10.xx |
| `_01_docx_bookmarks.py` | `add_bookmark_to_paragraph()` | 段落级书签插入 | 16.03 |
| `_01_docx_bookmarks.py` | `add_bookmark_around_run()` | 片段级书签插入 | 16.02 |
| `_03_docx_fields.py` | `add_complex_field()` | 通用域插入 | 10.xx, 14.01 |
| `_03_docx_fields.py` | `add_toc_field()` | 插入目录域 | 10.01, 10.02 |
| `_03_docx_fields.py` | `add_seq_field()` | 插入 SEQ 序号域 | 16.01, 13.01 |
| `_03_docx_fields.py` | `add_ref_field()` | 插入 REF 交叉引用域 | 16.02, 16.03 |
| `_08_docx_textops.py` | `iter_all_paragraphs()` | 遍历正文+表格+页眉页脚 | 15.01, 02.xx |
| `_08_docx_textops.py` | `replace_text_in_paragraph()` | 段落内文本替换 | 15.01, 04.05 |
| `_08_docx_textops.py` | `replace_text_everywhere()` | 全文档文本替换 | 15.01 |
| `_12_docx_format_helpers.py` | `set_run_font()` | 设置字体字号 | 05.xx |
| `_12_docx_format_helpers.py` | `apply_direct_format()` | 应用直接格式（加粗/斜体等） | 05.03, 05.04 |
| `_12_docx_format_helpers.py` | `apply_line_spacing()` | 设置行距 | 05.01 |
| `_12_docx_format_helpers.py` | `apply_indentation()` | 设置缩进 | 05.01 |
| `_12_docx_format_helpers.py` | `format_text_fragment()` | 片段级格式化 | 05.04, 15.03 |
| `_06_docx_styles.py` | `get_style()` | 获取样式对象 | 06.xx |
| `_06_docx_styles.py` | `get_or_add_paragraph_style()` | 获取或创建段落样式 | 06.xx |
| `_06_docx_styles.py` | `set_default_style()` | 设置默认正文样式 | 06.xx |
| `_06_docx_styles.py` | `prepare_common_styles()` | 批量创建论文常用样式 | 06.02, 06.06 |

---

# 组合示例

## 示例 1：创建带标题编号的论文文档

**需求**：创建一篇完整的论文文档，包含多级标题、自动编号、目录

**可复用模块**：
```
_06_docx_styles.py    → prepare_common_styles() 创建样式体系
_05_docx_numbering.py → 创建多级编号定义
_03_docx_fields.py    → add_toc_field() 插入目录域
```

**调用顺序**：
```python
from _06_docx_styles import prepare_common_styles
from _03_docx_fields import add_toc_field

# 1. 创建文档并准备样式
doc = Document()
prepare_common_styles(doc)

# 2. 插入带编号的标题（编号由 Word 样式系统自动处理）

# 3. 插入目录
add_toc_field(doc.add_paragraph())
```

## 示例 2：批量替换文档中的占位符

**需求**：根据模板批量替换文档中的占位符（如 `{{title}}`、`{{author}}`）

**可复用模块**：
```
_08_docx_textops.py   → replace_text_everywhere() 全文替换
_12_docx_format_helpers.py → set_default_style() 设置默认样式
```

**调用顺序**：
```python
from _08_docx_textops import replace_text_everywhere
from _12_docx_format_helpers import set_default_style

doc = Document("template.docx")
set_default_style(doc)

replacements = [
    ("{{title}}", "我的论文标题"),
    ("{{author}}", "张三"),
]
replace_text_everywhere(doc, replacements)
doc.save("output.docx")
```

## 示例 3：为图片插入自动编号图题

**需求**：插入图片并添加 "图 1" 这样的自动编号图题

**可复用模块**：
```
_02_docx_captions.py  → create_caption_paragraph() 创建图题
_03_docx_fields.py    → add_seq_field() 插入序号域
_01_docx_bookmarks.py → add_bookmark_around_run() 添加书签
```

**调用顺序**：
```python
from _02_docx_captions import create_caption_paragraph
from _03_docx_fields import add_seq_field
from _01_docx_bookmarks import add_bookmark_around_run

# 插入图片
paragraph = doc.add_paragraph()
run = paragraph.add_run()
run.add_picture("image.png", width=Inches(4))

# 创建图题并插入 SEQ 域
caption = create_caption_paragraph(doc, "图", "图片说明")
add_seq_field(caption, "Figure")

# 为图题添加书签供交叉引用
add_bookmark_around_run(doc, caption.runs[0], "fig_1")
```

## 示例 4：提取文档指定章节内容

**需求**：从文档中提取"摘要"章节的文本内容

**可复用模块**：
```
_13_docx_title_helpers.py → is_title_paragraph() 判断标题
_08_docx_textops.py       → iter_all_paragraphs() 遍历段落
```

**调用顺序**：
```python
from _08_docx_textops import iter_all_paragraphs
from _13_docx_title_helpers import is_title_paragraph

def extract_section(doc, section_name):
    in_section = False
    content = []
    for p in iter_all_paragraphs(doc):
        if is_title_paragraph(p) and section_name in p.text:
            in_section = True
            continue
        if in_section and is_title_paragraph(p):
            break
        if in_section:
            content.append(p.text)
    return "\n".join(content)

text = extract_section(doc, "摘要")
```
# OCR 文档解析服务

解析 PDF、图片、Office 文档为 Markdown 和图片。

## 端点

```
POST /v1/ocr/parser
Content-Type: multipart/form-data
```

## 模型

- `mineru/pipeline`（默认）

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `files` | file | 是 | 待解析文件 |
| `backend` | string | 否 | 解析后端：`pipeline` / `hybrid-auto-engine` / `vlm-auto-engine`，默认 `pipeline` |
| `parse_method` | string | 否 | 解析方法，默认 `auto` |
| `lang_list` | string | 否 | 语言代码，默认 `ch`（中文） |
| `return_md` | string | 否 | 是否返回 Markdown：`true` / `false`，默认 `true` |
| `return_images` | string | 否 | 是否返回图片：`true` / `false`，默认 `true` |
| `response_format_zip` | string | 否 | 是否返回 zip 格式：`true` |

## 返回格式

返回 ZIP 压缩包，解压后包含：
- `.md` 文件：Markdown 格式文档
- `images/` 目录：提取的图片文件

## 输出结构

解析完成后，文件输出为：

```
源文件:     /path/to/document.pdf
Markdown:   /path/to/document.md          # 与源文件同目录
图片目录:   /path/to/document_images/     # 与源文件同名 + _images
```

Markdown 中的图片路径自动修正：`images/xxx.png` → `document_images/xxx.png`。

## 输出 Markdown 内部结构约定

解析后的 Markdown 遵循以下结构规范：

### 通用元素

| 文档元素 | 输出格式 | 示例 |
|----------|----------|------|
| 文档标题 | `# 标题` | `# 产品规格说明书` |
| 章节标题 | `## H2` / `### H3` | `## 1. 引言` |
| 正文段落 | 普通文本，空行分隔 | |
| 无序列表 | `- 条目` | |
| 有序列表 | `1. 条目` | |
| 加粗/斜体 | `**加粗**` / `*斜体*` | |
| 超链接 | `[文字](URL)` | |

### 表格

```markdown
| 参数 | 类型 | 说明 |
|------|------|------|
| name | string | 用户名 |
| age | int | 年龄 |
```

- 表格跨页时合并为一个表格，不重复表头
- 合并单元格展平处理

### 公式

```markdown
行内公式: $E = mc^2$

块级公式:
$$
\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
```

- 使用 LaTeX 语法
- 行内公式用 `$...$`，块级公式用 `$$...$$`

### 代码块

````markdown
```python
def hello():
    print("Hello World")
```
````

- 必须标注语言（如 `python`, `javascript`, `bash`）
- 无法识别语言时用 `text`

### 图片

```markdown
![系统架构图](document_images/001.png)

图1: 系统架构设计
```

- 图片提取到 `{filename}_images/` 目录
- 图表标题作为图片下方普通文本保留

### 脚注与引用

```markdown
正文内容[^1]。

[^1]: 脚注内容。

## 参考文献

[1] Author. Title. Journal, 2024.
```

### 必须删除的元素

| 元素 | 说明 |
|------|------|
| 页眉 | 公司名、文档标题重复等 |
| 页脚 | 页码、版权声明等 |
| 水印 | 背景水印文字 |
| 空白页 | 纯空白页面 |

## 不同类型文档的特殊约定

| 类型 | 处理方式 |
|------|----------|
| **学术论文** | 公式用 LaTeX，保留参考文献格式，删除双栏布局痕迹，摘要用 `> ` 引用块 |
| **技术规格书** | 代码块标注语言，参数表格转标准表格，版本号保留 |
| **合同/法律文书** | 保留编号条款，签名区域标记为 `[签名区]`，日期保留原文格式 |
| **Word 文档** | 保留原始层级，批注转脚注 |
| **PPT 幻灯片** | 每页幻灯片标题转 `## H2`，内容转为列表 |
| **Excel 表格** | 每个 sheet 转为一个表格，sheet 名作为 `### H3` 标题 |
| **扫描件/图片** | 保留 OCR 原文，不确定字符用 `[?]` 标记，手写内容标记为 `[手写: 内容]` |

## Python 调用示例

```python
import requests
import os
import zipfile
import tempfile
import shutil
import re

PI_LLM_URL = os.environ.get('PI_LLM_URL', 'http://api.adv-ci.com:8090/v1')
PI_LLM_API_KEY = os.environ.get('PI_LLM_API_KEY', 'sk-5f8b839908d14561590b70227c72ca86')

def parse_document(file_path, backend="pipeline", output_dir=None):
    session = requests.Session()
    session.trust_env = False

    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]

    if output_dir is None:
        output_dir = os.path.dirname(file_path)

    with open(file_path, 'rb') as f:
        files = {'files': (file_name, f, 'application/octet-stream')}
        data = {
            'backend': backend,
            'parse_method': 'auto',
            'lang_list': 'ch',
            'return_md': 'true',
            'return_images': 'true',
            'response_format_zip': 'true'
        }

        response = session.post(
            f'{PI_LLM_URL}/ocr/parser',
            headers={"Authorization": f"Bearer {PI_LLM_API_KEY}"},
            files=files,
            data=data,
            timeout=1800
        )

    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")

    # 解压到临时目录
    temp_dir = tempfile.mkdtemp(prefix='mineru_')
    zip_path = os.path.join(temp_dir, 'result.zip')
    with open(zip_path, 'wb') as f:
        f.write(response.content)
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(temp_dir)

    # 找到 markdown 和 images
    md_files = []
    temp_images_dir = None
    for root, dirs, files in os.walk(temp_dir):
        for f in files:
            if f.endswith('.md'):
                md_files.append(os.path.join(root, f))
        if 'images' in dirs:
            temp_images_dir = os.path.join(root, 'images')

    final_images_dir = os.path.join(output_dir, f"{base_name}_images")
    os.makedirs(final_images_dir, exist_ok=True)

    for temp_md in md_files:
        dst_md = os.path.join(output_dir, f"{base_name}.md")
        shutil.copy2(temp_md, dst_md)

        # 修正图片路径
        if temp_images_dir:
            with open(dst_md, 'r', encoding='utf-8') as f:
                content = f.read()
            new_content = re.sub(
                r'!\[([^\]]*)\]\(images/',
                f'![\\1]({base_name}_images/',
                content
            )
            with open(dst_md, 'w', encoding='utf-8') as f:
                f.write(new_content)

    # 复制图片
    if temp_images_dir and os.path.exists(temp_images_dir):
        if os.path.exists(final_images_dir):
            shutil.rmtree(final_images_dir)
        shutil.copytree(temp_images_dir, final_images_dir)

    shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        'markdown_files': [os.path.join(output_dir, f"{base_name}.md")],
        'images_dir': final_images_dir
    }
```

## 命令行调用

```bash
# 默认解析（与源文件同目录输出）
python scripts/pi_llm_server_skill.py parse /path/to/document.pdf

# 指定输出目录
python scripts/pi_llm_server_skill.py parse /path/to/document.pdf --output /custom/dir
```

## 超时

1800 秒（30 分钟）

## 文件大小

建议不超过 50MB

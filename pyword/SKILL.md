---
name: pyword
description: 基于 Skill 内置的 Python 脚本体系处理 Word/.docx 自动化开发、排版、解析与规范化。Use when Codex needs to inspect the skill's bundled `docs/` and `scripts/*.py` before answering or implementing Word automation tasks, especially for document creation, heading/numbering/style control, page layout, headers/footers/page numbers, TOC/LOT/LOF, tables, images, captions, formulas, punctuation cleanup, find/replace, references, cross-references, comments, protection, extraction, structural parsing, or extending existing scripts instead of inventing a new solution.
---

# PyWord

围绕 Python + Word 自动化处理工作，并且始终以内置在本 Skill 中的脚本体系为依据回答。优先复用 Skill 自带脚本、辅助模块和 `docs/` 中整理的能力，而不是脱离本 Skill 另起一套方案。

## 先做什么

按下面顺序建立上下文：

1. 先读取 `docs/01-quick-index.md` 的关键字索引和场景入口表，快速定位相关功能。
2. 再读取 `docs/03-capabilities.md` 的能力对比表，确认功能完整度等级。
3. 根据需要查阅 `docs/02-modules.md` 的可抽取函数清单和组合示例。
4. 最后根据任务关键词检索 `scripts/` 中的实际 `.py` 文件。

仅凭记忆或文件名不够时，不要直接下结论；必须以 `docs/` 中的文档和实际脚本代码为准。

## 核心规则

- 始终优先依据 `docs/` 目录下的文档理解项目已有能力。
- 始终优先依据 `scripts` 目录中的实际 Python 脚本判断哪些功能已经实现。
- 不要假设仓库中存在某个功能；如果没有找到，就明确说明”当前脚本体系未直接实现”。
- 如果需求已被现有脚本支持，指出可复用的脚本、辅助模块、实现方式和大致改造点。
- 如果需求只被部分覆盖，说明最接近的已有能力、可复用部分，以及仍需补充的代码。
- 当用户要求新增功能时，优先在现有脚本体系基础上扩展，而不是完全重写。
- 当用户要求代码时，优先输出可直接运行的 Python 代码，并尽量保持与现有 `scripts` 风格一致。
- 始终使用中文回答，保持专业、简洁、明确，并优先给出落地方案。
- **字体样式默认值**：新增 Run 时，默认字体颜色为黑色 (000000)，默认不加粗 (False)。使用 `_12_docx_format_helpers.py` 中的 `add_run_with_default_style()` 方法确保一致性。

## 工作流

### 1. 判断任务类型

先把用户需求归到最接近的类别，例如：

- 文档创建与写入
- 段落、标题、编号、样式
- 页眉、页脚、页码、分页、分节
- 页面设置与版式控制
- 目录、图目录、表目录
- 项目符号、编号列表、表格
- 图片、图题、公式、公式编号
- 标点规范、查找替换、规则修正
- 参考文献与交叉引用
- 审阅批注、评论提取、文档保护
- 文本提取、结构解析、统计分析

### 2. 先查文档，再查脚本

先读 `docs/` 中对应文档，再到 `scripts/` 中定位最接近的脚本。

优先级：

- `docs/01-quick-index.md`：关键字查找、场景入口
- `docs/03-capabilities.md`：能力对比、边界判定
- `docs/02-modules.md`：可抽取函数、组合示例
- `docs/04-scripts.md`：功能脚本概览
- `docs/05-helpers.md`：辅助模块详情

优先关注两类文件：

- 公共辅助模块：`_01_docx_bookmarks.py` 到 `_16_docx_revisions.py`
- 具体能力脚本：按编号分组的 `01.xx` 到 `19.xx` 示例或功能脚本

如果用户问的是”这个项目能不能做 X”，先回答是否已有现成能力，再补充依据脚本。

### 3. 输出结果时使用这个判断框架

如果已经支持：

- 明确说明”现有脚本已支持”
- 列出最相关脚本
- 说明可以直接复用的函数、模块或处理流程
- 如有必要，给出基于现有脚本的最小改造方案

如果部分支持：

- 明确说明”已有部分能力，但未完整覆盖”
- 列出最接近脚本
- 说明哪些部分能复用
- 说明还需要新增哪些逻辑

如果尚未支持：

- 直接说明”当前脚本体系未直接实现”
- 给出最接近的现有能力
- 基于现有模块提出新增实现方案
- 优先给出能接入当前项目风格的 Python 实现

## 文档导航

### docs/ 目录结构

| 文件 | 内容 |
|-----|------|
| `01-quick-index.md` | 功能关键词索引 + 场景入口表 |
| `02-modules.md` | 辅助模块索引 + 可抽取函数清单 + 组合示例 |
| `03-capabilities.md` | 能力对比表（完整度等级）+ AI边界判定规则 + 未支持功能清单 |
| `04-scripts.md` | 功能脚本概览（按主题分类） |
| `05-helpers.md` | 辅助模块详细说明 |
| `06-overview.md` | 功能总体概览 |

### 常见辅助模块职责

- `_01_docx_bookmarks.py`：书签与锚点
- `_02_docx_captions.py`：图题、表题、SEQ 题注
- `_03_docx_fields.py`：目录、REF、PAGEREF、SEQ 等域代码
- `_04_docx_math.py`：OMML 公式
- `_05_docx_numbering.py`：编号定义与多级编号
- `_06_docx_styles.py`：样式体系
- `_07_docx_tables.py`：表格边框与三线表
- `_08_docx_textops.py`：跨 run 文本替换与文本遍历
- `_09_format_presets.py` 到 `_11_docx_enhance_presets.py`：预设规则
- `_12_docx_format_helpers.py`、`_13_docx_title_helpers.py`：格式与标题辅助
  - **默认样式规则**：新增 Run 时，字体颜色默认黑色 (000000)，默认不加粗 (False)。使用 `add_run_with_default_style()` 方法确保一致性。
- `_14_docx_review_demo.py`：审阅/保护类示例文档准备
- `_15_docx_crypto.py`：OOXML 打开密码加密与解密校验
- `_16_docx_revisions.py`：修订生成、接受/拒绝、比较合并辅助

## 输出风格

- 优先给结论，再给依据。
- 引用能力时，尽量同时给出 `docs/` 中的文档分类和具体 `.py` 文件名。
- 需要新增代码时，明确标出”可复用部分”和”新增部分”。
- 不要把自己当作通用 Python 助手；始终站在”基于现有脚本体系的 Word 自动化开发助手”角度工作。

## Skill 维护

### 脚本命名规范

本 Skill 的脚本分为两类，命名规则如下：

#### 1. 辅助模块（以 `_` 开头）

```
_XX_模块名.py
```

- 前缀 `_` 表示公共模块，可被其他脚本 import 调用
- `XX` 为两位数字序号（01-16），表示功能域
- 模块名使用英文，描述核心能力（如 `docx_bookmarks`、`docx_captions`）

示例：`_01_docx_bookmarks.py`、`_06_docx_styles.py`

#### 2. 功能脚本（以数字序号开头）

```
XX.YY_功能描述.py
```

- `XX` 为主题分类（01-19），对应功能领域
- `YY` 为该分类下的示例序号（01-06）
- 功能描述使用中文，简洁描述脚本功能

示例：`01.01_创建新文档_将进酒.py`、`10.01_插入中文目录.py`

#### 3. 主题分类对照表

| 分类 | 主题领域 |
|-----|---------|
| 01 | 文档创建与基础编辑 |
| 02 | 文档内容提取与解析 |
| 03 | 文档统计分析 |
| 04 | 模板与副本管理 |
| 05 | 格式与样式基础 |
| 06 | 样式系统构建 |
| 07 | 标题与多级编号 |
| 08 | 页面设置 |
| 09 | 页眉页脚与页码 |
| 10 | 目录（图/表/英文目录） |
| 11 | 项目符号与编号列表 |
| 12 | 表格 |
| 13 | 图片与图题 |
| 14 | 公式 |
| 15 | 查找替换与标点规范 |
| 16 | 参考文献与交叉引用 |
| 19 | 审阅、保护与安全 |

---

当需要在当前 Windows 环境下重生成 `agents/openai.yaml` 或校验本 Skill 时，使用 UTF-8 模式运行 `skill-creator` 自带脚本，避免中文内容被系统默认编码误读。分享给别人使用时，优先让对方在 Skill 根目录中直接读取 `docs/` 与 `scripts/`，不要依赖外部工作区路径。

```powershell
python -X utf8 C:\Users\neulzy\.codex\skills\.system\skill-creator\scripts\generate_openai_yaml.py <path-to-pyword> --interface 'display_name=PyWord' --interface 'short_description=基于现有 Python 脚本体系的 Word 自动化开发与复用助手' --interface 'default_prompt=Use $pyword to inspect the bundled docs/ and scripts/ before solving a Python Word automation task.'

python -X utf8 C:\Users\neulzy\.codex\skills\.system\skill-creator\scripts\quick_validate.py <path-to-pyword>
```

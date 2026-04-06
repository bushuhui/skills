# Workspace Map

## Canonical Sources

- Skill root: current `pyword` skill directory
- Capability overview: `./docs/06-overview.md`
- Quick lookup: `./docs/01-quick-index.md`
- Scripts directory: `./scripts`

## Documentation Structure

- `docs/01-quick-index.md` - 功能关键词索引 + 场景入口表
- `docs/02-modules.md` - 辅助模块索引 + 可抽取函数 + 组合示例
- `docs/03-capabilities.md` - 能力对比表 + AI边界判定
- `docs/04-scripts.md` - 功能脚本概览
- `docs/05-helpers.md` - 辅助模块详细说明
- `docs/06-overview.md` - 功能总体概览

## Script Grouping

- `scripts/_01_docx_bookmarks.py` to `scripts/_16_docx_revisions.py`
  - Shared helper modules and reusable building blocks
- `scripts/01.xx_*.py` to `scripts/19.xx_*.py`
  - End-to-end examples and task-oriented implementations

## Recommended Lookup Order

1. Read `docs/01-quick-index.md` to find keywords and scenario mapping
2. Check `docs/03-capabilities.md` to confirm capability completeness level
3. Reference `docs/02-modules.md` for reusable functions and examples
4. Search `scripts` for matching keywords or category numbers
5. Open the helper modules first if needed
6. Open the concrete numbered script that demonstrates the task

## High-Value Areas

- `01.xx` to `04.xx`: document creation, templates, extraction, stats
- `05.xx` to `07.xx`: formatting, styles, headings, numbering
- `08.xx` to `10.xx`: page layout, headers/footers, TOC/LOT/LOF
- `11.xx` to `14.xx`: lists, tables, images, captions, formulas
- `15.xx` to `16.xx`: text cleanup, replace, references, cross-references
- `19.xx`: comments, review, protection, open-password encryption, compare/merge
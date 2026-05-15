---
name: write-a-skill
description: |
  创建新的 agent skill（SKILL.md + 目录结构 + 配套脚本/参考文档）。当用户要求创建/编写/设计/封装一个新的 skill、agent 插件、工具包、能力模块时使用。
  触发词包括："写个 skill"、"创建插件"、"做一个 agent 工具"、"封装能力"、"新增 skill"、"add a skill"、"build an agent skill"。
  涵盖：SKILL.md 撰写、目录结构规划、跨平台兼容标准、触发词设计、脚本集成。
  注意：如果是专门创建 MCP server，使用 mcp-builder；如果是从零开始学习 skill 开发流程，也可使用此 skill。
---

# Writing Skills

## Process

1. **Gather requirements** - ask user about:
   - What task/domain does the skill cover?
   - What specific use cases should it handle?
   - Does it need executable scripts or just instructions?
   - Any reference materials to include?

2. **Draft the skill** - create:
   - SKILL.md with concise instructions
   - Additional reference files if content exceeds 500 lines
   - Utility scripts if deterministic operations needed

3. **Review with user** - present draft and ask:
   - Does this cover your use cases?
   - Anything missing or unclear?
   - Should any section be more/less detailed?

## Skill Structure

```
skill-name/
├── SKILL.md           # Main instructions (required)
├── reference.md       # Detailed docs (if needed)
├── example.md        # Usage examples (if needed)
└── scripts/           # Utility scripts (if needed)
    └── helper.js
```

## SKILL.md Template

```md
---
name: skill-name
description: Brief description of capability. Use when [specific triggers].
---

# Skill Name

## Quick start

[Minimal working example]

## Workflows

[Step-by-step processes with checklists for complex tasks]

## Advanced features

[Link to separate files: See [REFERENCE.md](REFERENCE.md)]
```

## Description Requirements

The description is **the only thing your agent sees** when deciding which skill to load. It's surfaced in the system prompt alongside all other installed skills. Your agent reads these descriptions and picks the relevant skill based on the user's request.

**Goal**: Give your agent just enough info to know:

1. What capability this skill provides
2. When/why to trigger it (specific keywords, contexts, file types)

**Format**:

- Max 1024 chars
- Write in third person
- First sentence: what it does
- Second sentence: "Use when [specific triggers]"

**Good example**:

```
Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction.
```

**Bad example**:

```
Helps with documents.
```

The bad example gives your agent no way to distinguish this from other document skills.

## When to Add Scripts

Add utility scripts when:

- Operation is deterministic (validation, formatting)
- Same code would be generated repeatedly
- Errors need explicit handling

Scripts save tokens and improve reliability vs generated code.

## When to Split Files

Split into separate files when:

- SKILL.md exceeds 100 lines
- Content has distinct domains (finance vs sales schemas)
- Advanced features are rarely needed

## Cross-Agent Compatibility

Skills should work across different agent platforms (Claude Code, OpenClaw, custom agents, etc.) regardless of where they are installed. Follow these standards:

### 1. Never hardcode absolute paths

Never write `/home/user/...`, `C:\Users\...`, or any machine-specific path in scripts, SKILL.md, or reference files.

### 2. Use `${SKILL_DIR}` placeholder in SKILL.md

In SKILL.md command examples, always use `${SKILL_DIR}` as a placeholder for the skill's actual directory path. Add a note so any reading agent knows to substitute it:

```md
> `${SKILL_DIR}` refers to this skill's actual directory path. Replace with the real path before executing.

bash "${SKILL_DIR}/scripts/run.sh" --input file.md
python3 "${SKILL_DIR}/converter.py" input.md -o output.docx
```

**Why `${SKILL_DIR}` instead of `${CLAUDE_SKILL_DIR}`:**
`CLAUDE_SKILL_DIR` is an OpenClaw-specific convention that other agents may not recognize. `${SKILL_DIR}` is platform-neutral — each agent can map it however they need.

### 3. Scripts must self-resolve their directory

**Bash scripts:**
```bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Then use "$SCRIPT_DIR" for all relative file access
python3 "$SCRIPT_DIR/helper.py"
```

**Python scripts:**
```python
script_dir = os.path.dirname(os.path.abspath(__file__))
# Then use script_dir for all relative file access
template = os.path.join(script_dir, 'template', 'default.docx')
```

This way, scripts work regardless of the current working directory or how they were invoked.

### 4. Provide fallback logic for optional dependencies

When a script needs external tools (pandoc, ffmpeg, etc.), check availability first and provide a clear error or fallback:

```bash
if ! command -v pandoc &> /dev/null; then
    echo "Error: pandoc is required but not installed"
    exit 1
fi
```

### 5. Avoid platform-specific features

| Avoid | Use instead |
|-------|-------------|
| `#!/usr/bin/env bash` with bashisms | POSIX sh or explicit bash requirement |
| Windows-only paths (`C:\...`) | `os.path.join()` or `${VAR}/path` |
| `sed -i` (macOS incompatible) | `sed -i ''` on macOS or Python |
| `grep -P` (not on macOS) | `grep -E` or Python regex |

### 6. Document the skill's triggers in description

Write the SKILL.md frontmatter `description` with explicit trigger phrases so any agent can match the user's intent:

```yaml
description: |
  Brief capability statement. Use when [trigger phrase 1], [trigger phrase 2].
  Supports: [mode A], [mode B].
  Note: [exclusions — what this does NOT handle].
```

## Review Checklist

After drafting, verify:

- [ ] Description includes triggers ("Use when...")
- [ ] SKILL.md under 100 lines
- [ ] No time-sensitive info
- [ ] Consistent terminology
- [ ] Concrete examples included
- [ ] References one level deep
- [ ] No hardcoded absolute paths
- [ ] Scripts use `SCRIPT_DIR` / `__file__` for path resolution
- [ ] `${SKILL_DIR}` placeholder used in SKILL.md command examples

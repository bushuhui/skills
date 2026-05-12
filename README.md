# PI-Lab skills 合集

本项目是一组 AI Agent 技能（Skills），适用于 Claude Code、Codex、OpenClaw、Hermes Agent 等 AI 编码助手。

## 安装

### Claude Code
将本仓库克隆到 skills 目录即可自动加载：
```bash
git clone git@gitee.com:pi-lab/skills.git ~/.claude/skills
```
或通过 `npx skills add` 安装单个 skill。

也可以统一把 skill 放到 `~/.agents/skills`，然后在 ~/.claude 建立符号链接

```bash
cd ~/.claude
rm -rf skills
ln -s ~/.agents/skills skills
```



### Codex / OpenClaw / Hermes Agent
将 skill 目录复制到对应工具的 skills 路径下即可。每个 skill 以 `SKILL.md` 中的 YAML frontmatter 声明触发条件和使用说明。
```bash
git clone git@gitee.com:pi-lab/skills.git ~/.agents/skills
```

OpenClaw (`~/.openclaw/openclaw.json`)
```json
"skills": {                                              
    "load": {
      "extraDirs": [
        "/home/username/.agents/skills"
      ],
      "watch": true,
      "watchDebounceMs": 250
    },
    "install": {
      "nodeManager": "npm"
    }
  }
```

Hermes Agent (`~/.hermes/config.yaml`)
```yaml
skills:
  external_dirs:
  - /home/username/.agents/skills/
  template_vars: true
  inline_shell: false
  inline_shell_timeout: 10
  guard_agent_created: false
  creation_nudge_interval: 15
```

其中 `username` 是实际你的电脑上的用户名。


## 技能分类

| 分类 | 数量 | 说明 | 详情 |
|------|------|------|------|
| 📄 文档处理 | 9 | PDF/Word/Excel/PPTX 创建、编辑、转换 | [查看详情](docs/README_Detail.md#文档处理) |
| 🔬 研究与知识管理 | 9 | 论文检索、文献综述、知识图谱、RSS 抓取 | [查看详情](docs/README_Detail.md#研究与知识管理) |
| 🤖 AI 辅助工具 | 9 | 搜索、新闻聚合、LLM 网关、数据库、技能发现 | [查看详情](docs/README_Detail.md#ai-辅助工具) |
| 🧠 思维模型 | 7 | Musk/Feynman/Munger/Naval/Jobs/Taleb/张雪峰 | [查看详情](docs/README_Detail.md#思维模型) |
| 🎨 创意与写作 | 4 | 头脑风暴、算法艺术、视觉设计、HTML 构建 | [查看详情](docs/README_Detail.md#创意与写作) |
| 🎬 音视频处理 | 4 | YouTube 字幕/音频转写、视频帧提取 | [查看详情](docs/README_Detail.md#音视频处理) |
| 📝 写作与润色 | 4 | 论文审稿、AI 文本人性化、文献综述、Markdown 转 Word | [查看详情](docs/README_Detail.md#写作与润色) |
| 🎨 图表与演示 | 5 | 流程图、HTML 幻灯片、技术架构图、视觉认知设计 | [查看详情](docs/README_Detail.md#图表与演示) |
| ⚙️ 系统与工具 | 7 | 项目管理、技能开发、自动审稿、tmux、优化 | [查看详情](docs/README_Detail.md#系统与工具) |
| 🛠️ PI-Dev 工程化 | 14 | 从想法到交付的全链路开发流程：设计追问、PRD 拆分、TDD、原型验证、架构审计等 | [查看详情](docs/pd-usage.md) |

共计 **71** 个 skill（其中 3 个为跨分类交叉引用）。

## 详细文档

每个 skill 的目的、用途、用法详见 → [docs/README_Detail.md](docs/README_Detail.md)



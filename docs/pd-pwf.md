# PI-Dev Skills 与 Planning-with-Files 结合使用分析

> 分析日期：2026-05-13
> 目的：评估 pd-* 系列 skills 与 planning-with-files (PWF) 能否结合使用，以及如何结合。

---

## 总体判断：可以结合，而且结合后效果会更强

两者解决的是**不同层面**的问题，不存在根本冲突：

| 维度 | planning-with-files (PWF) | pd-* Skills |
|------|--------------------------|-------------|
| 解决的问题 | **AI agent 的记忆丢失**（上下文工程） | **软件开发流程不规范**（工程纪律） |
| 层面 | 执行层 — 怎么记住做过什么 | 战略层 — 该做什么、什么时候做 |
| 核心产出 | `task_plan.md` / `findings.md` / `progress.md` | `docs/RAD.md` / PRD / `.scratch/issues/` |
| 自动化机制 | IDE Hooks 自动注入 | Slash command 触发结构化流程 |
| 时间尺度 | 单次 session | 从想法到交付的全生命周期 |

---

## 最佳结合方式：串联流水线

```
想法
  │
  ▼
/pd-brainstorming          →  产出 docs/RAD.md（设计方案）
  │
  ▼
/pd-grill-with-docs        →  用领域模型压力测试方案
  │
  ▼
/pd-to-prd                 →  合成 PRD 发布到 issue tracker
  │
  ▼
/pd-to-issues              →  拆分为垂直切片 issue
  │
  ▼
/planning-with-files:plan   ←  在这里切入 PWF！
                               把 issue 的执行过程用 3 文件模式管理
  │
  ▼
/pd-tdd                    →  在 PWF 的 Phase 3（实现）中执行 red-green-refactor
  │
  ▼
/pd-execution              →  批量执行剩余 issue
  │
  ▼
/pd-doc                    →  更新项目文档
```

**关键切入点**：当 PRD 拆分成 issue 之后，不再让 AI "直接上手写代码"，而是先跑 `/plan` 创建 PWF 的三文件，然后用 `task_plan.md` 来跟踪**每个 issue 的执行进度**。

---

## 互补增益点

| PWF 给 pd-* 带来的 | pd-* 给 PWF 带来的 |
|---|---|
| Hooks 自动注入计划，agent 不会做着做着忘了目标 | 结构化的需求分析和设计流程，避免 task_plan.md 变成"拍脑袋写的计划" |
| 会话恢复：`/clear` 后自动找回上下文 | TDD 的 red-green-refactor 纪律，PWF 本身不规定怎么写代码 |
| 并行任务隔离：多终端同时做不同 issue | Issue 拆分和依赖管理，PWF 本身没有 issue 系统 |
| SHA-256 防篡改保护 | 代码质量审计（pd-rules-check）、架构改进（pd-improve-arch） |

---

## 潜在冲突和注意点

### 1. CLAUDE.md/AGENTS.md 的配置权

`pd-setup` 会往 `CLAUDE.md` 或 `AGENTS.md` 里写 `## Agent skills` 块。PWF 的 hooks 也依赖这个文件的配置。

**建议**：先跑 `pd-setup` 完成初始化，再手动把 PWF 的 hooks 配置追加进去，或者让 pd-setup 生成时确认包含 PWF 的 hook 命令。

### 2. 文件产出不会自动关联

pd-* 产出 `docs/RAD.md`，PWF 产出 `.planning/*/task_plan.md`。两者是独立的。

**建议**：在 `findings.md` 中引用 `docs/RAD.md` 的路径，建立交叉引用。

### 3. Hook 数量叠加

PWF 的 Hooks 已经较多（UserPromptSubmit / PreToolUse / PostToolUse / Stop），pd-* 如果也配了 hooks，需要确认不会冲突（比如两个 PreToolUse hook 同时触发）。

---

## 结论

**两者不是替代关系，是正交的**：

- pd-* = **脑子**（想清楚该做什么）
- PWF = **记忆**（确保做着做着不会忘）

结合起来就是：**用 pd-* 规划方向，用 PWF 保证执行不走样**。最自然的切入点在 `pd-to-issues` 之后、开始编码之前，插入 `/plan` 启动 PWF。

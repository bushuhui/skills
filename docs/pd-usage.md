# PD Skills Pipeline 使用指南

## 全链路概览

```
用户想法
  → /pd-brainstorming → docs/RAD.md (原始方案)
      ↓ (可选)
  → /pd-grill-with-docs → 修正 docs/RAD.md + ADR (打磨后的方案)
      ↓ (可选)
  → /pd-prototype → 验证关键设计决策 (降低不确定性)
      ↓
  → /pd-to-prd → issue tracker (结构化 PRD)
      ↓
  → /pd-to-issues → 独立的、可被 AFK agent 执行的 issue
      ↓
  → /pd-tdd 或 /pd-diagnose → 实现
```

## 每个 Skill 做什么

| Skill | 职责 | 产出物 |
|---|---|---|
| `/pd-brainstorming` | 把模糊想法变成完整设计方案 | `docs/RAD.md` |
| `/pd-grill-with-docs` | 用领域模型和 ADR 挑战方案，修正术语和边界 | 修正后的 `docs/RAD.md` + 新 ADR |
| `/pd-prototype` | 构建 throwaway 原型验证关键假设 | 原型代码 + 验证结论 |
| `/pd-to-prd` | 将方案合成为结构化 PRD | Issue Tracker 上的 PRD |
| `/pd-to-issues` | 将 PRD 拆分为垂直切片 | 多个独立的 AFK-ready issue |
| `/pd-tdd` | 测试驱动开发实现 | 可运行的代码 + 测试 |
| `/pd-diagnose` | 诊断和修复 Bug | 修复 + 回归测试 |

## 各阶段详细说明

### 1. /pd-brainstorming — 需求分析 + 方案设计

**何时用：** 只有一个模糊想法，需要把它变成可执行的设计方案。

**做了什么：**
- 深度追问，理解决策树和依赖关系
- 提出 2-3 种实现方案，带权衡分析
- 分段呈现设计并逐一确认
- 最终方案保存到 `docs/RAD.md`

**产出结构（`docs/RAD.md`）：**
```
## YYYY-MM-DD — 方案摘要
### 需求分析
### 需要考虑的细节
### 架构与方案
### 决策记录
### 待办事项
```

**下一步：**
- 需要对方案做压力测试和术语打磨 → `/pd-grill-with-docs`
- 想快速验证关键设计决策 → `/pd-prototype`
- 方案已确定，要转化为需求文档 → `/pd-to-prd`

### 2. /pd-grill-with-docs — 方案打磨

**何时用：** 方案已有，需要检查它是否与项目的领域模型一致、术语是否准确、边界条件是否遗漏。

**做了什么：**
- 逐个挑战方案中的术语是否与 `CONTEXT.md` 一致
- 用具体场景压力测试边界条件
- 检查代码是否与方案描述矛盾
- 重要决策记录为 ADR

**产出：** 修正后的 `docs/RAD.md` + `docs/adr/` 下的新决策文档

**下一步：**
- 方案已打磨完成 → `/pd-to-prd`
- 关键决策仍需验证 → `/pd-prototype`

### 3. /pd-prototype — 原型验证

**何时用：** 有设计决策不确定可行性，需要用实际代码验证（状态机、UI 布局、数据模型）。

**做了什么：**
- **Logic 分支**：构建可交互的终端应用验证状态机/业务逻辑
- **UI 分支**：生成多个截然不同的 UI 变体，通过浮动底栏切换

**规则：** throwaway 代码，不做测试和错误处理，一个命令可启动，验证完即删除。

**产出：** 验证结论 + 被采纳/否决的设计决策

**下一步：**
- 验证通过，回到 `/pd-to-prd` 将验证后的决策写入 PRD
- 原型推翻了原计划 → 回到 `/pd-brainstorming` 重新探索
- UI 原型选定变体 → 删除失败者，将胜出者折叠进生产代码，继续 `/pd-to-prd` 或 `/pd-to-issues`

### 4. /pd-to-prd — 生成 PRD

**何时用：** 方案已确定（或经过打磨），需要转化为结构化的需求文档。

**做了什么：**
- 读取 `docs/RAD.md`（如存在），按字段映射合成 PRD
- 从对话上下文中补充遗漏信息
- 使用项目领域术语（`CONTEXT.md`）
- 发布到 Issue Tracker，标记 `ready-for-agent`

**`docs/RAD.md` → PRD 字段映射：**

| `docs/RAD.md` | → PRD | 转换方式 |
|---|---|---|
| 需求分析 | Problem Statement & Solution | 提炼为用户视角的问题 + 方案 |
| 架构与方案 | Implementation Decisions | 去除文件路径/行号，保留接口和类型 |
| 决策记录 | Implementation Decisions | 保留决策和理由 |
| 待办事项 | User Stories / Out of Scope | 可执行项 → 用户故事；阻塞/延期项 → 超出范围 |
| 需要考虑的细节 | Further Notes | 直接映射 |

**产出：** Issue Tracker 上的 PRD Issue

**下一步：**
- 需要拆分为独立 issue → `/pd-to-issues`
- 关键设计决策仍需验证 → `/pd-prototype`

### 5. /pd-to-issues — Issue 拆分

**何时用：** PRD 已发布，需要拆分为可被 AFK agent 独立执行的垂直切片。

**做了什么：**
- 按 tracer bullet（垂直切片）方式拆分，每个 issue 覆盖端到端的完整路径
- 区分 HITL（需人类介入）和 AFK（可自动完成）切片
- 按依赖顺序发布，支持 `blocked by` 关系

**产出：** 多个独立的 Issue，每个包含：
- What to build（端到端行为描述）
- Acceptance criteria
- Blocked by（依赖关系）

**下一步：**
- 开始实现 → 选一个 `ready-for-agent` 且无阻塞的 issue，用 `/pd-tdd` 实现
- 首个切片的设计决策仍需验证 → `/pd-prototype`

### 6. 实现阶段

**/pd-tdd** — 测试驱动开发
- 红→绿→重构循环
- 垂直切片方式，一个测试一个实现
- 通过公共接口验证行为，不耦合实现细节

**/pd-diagnose** — 调试诊断
- 构建反馈循环 → 复现 → 假设 → 仪器 → 修复 → 回归测试
- 修复后如发现架构问题，建议 `/pd-improve-codebase-architecture`

## 可选路径

不是每次都走完整链路。常见路径：

| 场景 | 路径 |
|---|---|
| 想法还不清楚 → 直接写代码 | brainstorming → tdd |
| 方案已有，但关键决策不确定 | brainstorming → prototype → to-prd → to-issues → tdd |
| 需要打磨术语和边界 | brainstorming → grill-with-docs → to-prd → to-issues → tdd |
| 遇到 bug | diagnose |
| PRD 已存在，只需拆分 | to-issues → tdd |

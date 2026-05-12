# PI-Dev Skills 使用指南

PI-Dev 是一套覆盖**从想法到交付**全链路的工程化 Skill，围绕"先想清楚、再验证、后执行"的理念设计。本文档是 `pd-*` 系列 Skill 的完整使用手册，涵盖全链路开发流程中每个 Skill 的目的、用途、用法和相互关系。

具体的使用示例，可以参考 [uav-planning](https://gitee.com/pi-lab/learn_programming/tree/master/demo_code/2_uav-planning)

本项目部分的 skills 来自 [mattpocock skills](https://github.com/mattpocock/skills)

---

## 一、全链路概览

PI-Dev Skills 是一套覆盖**从想法到交付**全链路的工程化 Skill 集合，围绕"先想清楚、再验证、后执行"的理念设计。当前共有 **14 个 Skill**，按功能域划分：

### 🧭 需求与设计阶段

| Skill | 触发命令 | 一句话 |
|-------|----------|--------|
| `/pd-brainstorming` | brainstorm / 头脑风暴 | 把模糊想法变成经过充分推敲的完整设计方案，保存到 `docs/RAD.md` |
| `/pd-grill-with-docs` | grill / 压力测试 | 用项目的领域模型和已有 ADR 对方案进行压力测试，修正术语、补充边界 |
| `/pd-bdd` | bdd / 行为描述 | 用 Given-When-Then 自然语言精确描述产品行为，与 TDD 双保险 |

### 🏗️ 规划与拆分阶段

| Skill | 触发命令 | 一句话 |
|-------|----------|--------|
| `/pd-to-prd` | to-prd / 生成 PRD | 将 `docs/RAD.md` 合成为结构化 PRD 并发布到 issue tracker |
| `/pd-to-issues` | to-issues / 拆分 issue | 将 PRD 按垂直切片拆分为独立可执行的 issue |
| `/pd-triage` | triage | Issue 状态机管理：分类、分流、准备 Agent Brief |

### 🧪 验证与执行阶段

| Skill | 触发命令 | 一句话 |
|-------|----------|--------|
| `/pd-prototype` | prototype / 原型 | 构建可丢弃的原型来验证关键设计决策（逻辑 or UI） |
| `/pd-tdd` | tdd | 测试驱动开发，red-green-refactor 循环，纵向切片实现 |
| `/pd-diagnose` | diagnose / debug | 系统化排错循环：复现→最小化→假设→调试→修复→回归测试 |
| `/pd-execution` | execution | 批量扫描并执行本地 issue tracker 中未完成的任务 |

### 📐 质量与架构阶段

| Skill | 触发命令 | 一句话 |
|-------|----------|--------|
| `/pd-improve-codebase-architecture` | improve-arch | 发现架构摩擦点，提出"深化"重构机会，提升可测试性和 AI 可导航性 |
| `/pd-rules-check` | rules-check | 基于 14 套经典软件工程书籍对代码进行规范审计 |

### 📋 文档与辅助

| Skill | 触发命令 | 一句话 |
|-------|----------|--------|
| `/pd-doc` | /pd-doc | 项目文档自动管理：新项目创建骨架，已有项目增量更新 |
| `/pd-setup` | setup | 为工程 Skill 配置 issue tracker、Triage 标签、领域文档布局 |
| `/pd-zoom-out` | zoom-out | 拉高视角，生成相关模块地图和调用关系，帮助理解全局 |

### 全链路流程图

```
想法/需求
   │
   ▼
┌─────────────────────┐
│  /pd-brainstorming  │  深度设计追问，产出 docs/RAD.md
└────────┬────────────┘
         │
         ▼
┌────────────────────────────┐
│  /pd-grill-with-docs       │  用领域模型/A DR 压力测试方案
└────────┬───────────────────┘
         │
         ▼
┌─────────────────────┐     ┌──────────────────┐
│    /pd-to-prd       │────▶│  /pd-to-issues   │
│  合成并发布 PRD      │     │  拆分为垂直切片   │
└─────────────────────┘     └────────┬─────────┘
         │                           │
         │                           ▼
         │                  ┌──────────────────┐
         │                  │  /pd-triage      │
         │                  │  Issue 状态管理   │
         │                  └────────┬─────────┘
         │                           │
         │    ┌──────────────────────┘
         │    │
         ▼    ▼
┌─────────────────────┐     ┌──────────────────┐
│  /pd-prototype      │     │  /pd-tdd         │
│  原型验证决策        │────▶│  测试驱动实现     │
└─────────────────────┘     └────────┬─────────┘
                                     │
                                     ▼
                              ┌──────────────────┐
                              │  /pd-doc         │
                              │  更新项目文档     │
                              └──────────────────┘

辅助链（随时可用）：
  /pd-setup              → 初始化项目配置（首次使用）
  /pd-diagnose           → 遇到 bug 时系统化排错
  /pd-improve-arch       → 发现架构问题时深化模块
  /pd-rules-check        → 定期代码质量审计
  /pd-zoom-out           → 需要全局视角时拉高
  /pd-execution          → 批量执行已规划的 issue
  /pd-bdd                → 需求阶段行为描述 + TDD 双保险
```

---

## 二、开发流程与 Skill 映射

本节以一个典型功能开发为例，说明每个 Skill 用在哪一步、用来干什么。

### 阶段 0：项目初始化（首次使用）

**使用的 Skill**: `/pd-setup`

**场景**: 第一次在新项目中使用 PD Skills。

**做了什么**:
1. 探测项目状态（是否有远程仓库、已有文档、issue tracker）
2. 配置三件事：
   - **Issue tracker** — issue 存在哪里（GitHub / GitLab / 本地 Markdown）
   - **Triage 标签** — 五种状态标签的映射（needs-triage / ready-for-agent 等）
   - **领域文档** — 单上下文还是多上下文的 `CONTEXT.md` 布局
3. 在 `CLAUDE.md` 或 `AGENTS.md` 中写入 `## Agent skills` 配置块
4. 在 `docs/agents/` 下生成配置文档

**何时需要重跑**: 切换 issue tracker 或需要重新初始化时。

---

### 阶段 1：想法 → 设计方案

**使用的 Skill**: `/pd-brainstorming` → `/pd-grill-with-docs`

**场景**: "我想给项目加个用户权限系统" / "我要重构支付模块"

**`/pd-brainstorming` 做了什么**:
1. 查看项目当前状态（`docs/architecture.md`、`docs/api.md`、近期变更）
2. **深度追问（Grill 模式）** — 一个一个问，每次只抛出一个问题，给出 2-3 个选项 + 推荐
3. 探索 2-3 种实现方案，列出权衡取舍，给出推荐
4. 渐进式呈现设计（架构 → 组件 → 数据流 → 错误处理 → 测试策略）
5. 确认后保存到 `docs/RAD.md`（按时间倒序追加）

**`/pd-grill-with-docs` 做了什么**:
- 对照项目已有的 `CONTEXT.md`（领域术语表）和 `docs/adr/`（架构决策记录）
- 挑战方案中的术语使用："你的领域词典定义 'cancellation' 是 X，但你说的像是 Y"
- 用具体场景压力测试边界条件
- 对照代码验证方案是否与实际实现矛盾
- 即时更新 `CONTEXT.md`，必要时创建 ADR

**两者的区别**: `brainstorming` 从**零构建**设计，`grill-with-docs` 对**已有方案**进行领域对齐和压力测试。通常先 brainstorming 再 grill-with-docs。

---

### 阶段 2：需求描述精确化

**使用的 Skill**: `/pd-bdd`

**场景**: 设计方案确定了，需要把具体行为描述清楚，确保 AI 不会"做成秃头程序员"。

**做了什么**:
1. 用户提供一句话需求（如"吸血鬼攻击敌人时，恢复造成伤害等量的生命值"）
2. AI 生成 3-5 个 Given-When-Then 用例，覆盖正常路径 + 边界条件
3. 用户确认并补充细节
4. AI 将用例转换为测试代码
5. 根据用例实现业务逻辑
6. 验证功能与 BDD 描述一致

**与 TDD 的配合**: BDD 确保功能描述精确（不做成别的东西），TDD 确保代码实现正确（不出 bug）。双保险机制。

---

### 阶段 3：原型验证

**使用的 Skill**: `/pd-prototype`

**场景**: "状态机这样设计真的能处理 X→Y→Z 的边界情况吗？" / "这个页面应该长什么样？"

**做了什么**（两条分支）：

- **逻辑原型（LOGIC 分支）**: 当问题是关于业务逻辑、状态转换、数据模型时
  - 构建一个交互式终端 TUI 应用，让用户手动驱动状态机
  - 核心逻辑放在纯模块中，TUI 是薄壳
  - 用户通过按键操作观察状态变化，发现 "等等，这个状态不应该出现" 的时刻

- **UI 原型（UI 分支）**: 当问题是关于视觉设计时
  - 在同一路由上生成 3 个截然不同的 UI 变体，通过 `?variant=` 参数切换
  - 底部浮动切换栏，用键盘 `←` `→` 或点击切换
  - 用户的典型反馈是 "我想要 B 的头部 + C 的侧边栏"

**关键原则**: 原型是 throwaway（可丢弃的），回答完问题后删除或吸收有效决策。

---

### 阶段 4：PRD 发布

**使用的 Skill**: `/pd-to-prd`

**场景**: 方案已经打磨完成，需要转化为可执行的需求文档。

**做了什么**:
1. 读取 `docs/RAD.md`（如果存在）作为主要来源
2. 将 RAD 的各节映射到 PRD 模板：
   - 需求分析 → Problem Statement & Solution
   - 架构与方案 → Implementation Decisions
   - 决策记录 → Implementation Decisions（保留决策和理由）
   - 待办事项 → User Stories / Out of Scope
3. 探索仓库确认当前代码状态
4. 规划需要构建/修改的模块
5. 发布到 issue tracker（打上 `ready-for-agent` 标签）

**不需要采访用户** — 直接从已有对话上下文和代码库理解中合成。

---

### 阶段 5：拆分 Issue

**使用的 Skill**: `/pd-to-issues`

**场景**: PRD 已发布，需要拆分为独立可执行的任务。

**做了什么**:
1. 将 PRD 按**垂直切片（tracer bullet）**拆分为 issue
2. 每个 issue 是一个完整的端到端路径（schema → API → UI → tests），而非水平分层
3. 标注每个 slice 是 HITL（需人工）还是 AFK（可自动执行）
4. 展示拆分方案，让用户确认粒度和依赖关系
5. 按依赖顺序发布到 issue tracker

**关键原则**: 一个完成的 slice 应该是可演示/可验证的，宁拆薄不拆厚。

---

### 阶段 6：Issue 管理

**使用的 Skill**: `/pd-triage`

**场景**: 有新的 bug 或 feature request 进来，需要分类和分流。

**做了什么**:
1. 读取 issue 全文 + 评论 + 标签
2. 推荐分类（bug / enhancement）和状态（needs-triage → ready-for-agent / ready-for-human / needs-info / wontfix）
3. 尝试复现 bug
4. 如果 `ready-for-agent`，撰写 Agent Brief（持久化的执行指南）
5. 如果 `wontfix`，写入 `.out-of-scope/` 知识库

---

### 阶段 7：批量执行

**使用的 Skill**: `/pd-execution`

**场景**: 已经规划了一堆 issue，想按依赖顺序批量执行完成。

**做了什么**:
1. 扫描 `.scratch/*/issues/` 下所有 issue
2. 检查每个 issue 的完成状态和验收标准
3. 解析 `Blocked by` 构建依赖图，拓扑排序确定执行顺序
4. 逐个执行：读取 issue → 探索代码库 → 报告发现 → 用户确认 → 实现 → 验证验收标准 → 标记完成

---

### 阶段 8：测试驱动实现

**使用的 Skill**: `/pd-tdd`

**场景**: 开始编码实现某个 issue。

**做了什么**（red-green-refactor 循环）：
1. **Planning** — 确认接口变更、测试优先级、深模块机会，获取用户批准
2. **Tracer Bullet** — 写一个测试（RED）→ 写最少代码通过（GREEN）
3. **Incremental Loop** — 逐个行为重复 RED → GREEN
4. **Refactor** — 所有测试通过后重构，提取重复代码、深化模块

**关键原则**: 纵向切片，不要先写所有测试再写所有实现（水平切片会产生"垃圾测试"）。

---

### 阶段 9：文档更新

**使用的 Skill**: `/pd-doc`

**场景**: 功能开发完成，提交前更新项目文档。

**做了什么**:
- **新项目**: 创建 `docs/architecture.md`、`docs/api.md`、`docs/changelog.md` 骨架
- **已有项目**: 对比上次文档后的变更，增量更新架构和 API 文档，追加 changelog
- **大模块**: 在 `docs/modules/` 下创建独立说明文档

---

### 阶段 10：Bug 排查

**使用的 Skill**: `/pd-diagnose`

**场景**: 线上出 bug 了，或者出现了性能回退。

**做了什么**（六阶段排错循环）：
1. **Phase 1** — 构建反馈循环（失败测试 / curl 脚本 / CLI 调用 / 浏览器脚本 / 回放 trace），这是核心技能
2. **Phase 2** — 复现，确认反馈循环捕获的是用户描述的同一问题
3. **Phase 3** — 生成 3-5 个排序的假设，每个必须是可证伪的
4. **Phase 4** — 仪器化探测，每次探测对应一个假设，变更一个变量
5. **Phase 5** — 先写回归测试再修复
6. **Phase 6** — 清理调试代码、写 post-mortem

**结束后**: 如果排查中发现了架构层面的问题（无可测接缝、调用者纠缠），将发现传递给 `/pd-improve-codebase-architecture`。

---

### 阶段 11：架构改进

**使用的 Skill**: `/pd-improve-codebase-architecture`

**场景**: 代码库中存在紧密耦合、浅模块、不可测的问题，需要系统性改善。

**做了什么**:
1. 读取项目的 `CONTEXT.md` 和 `docs/adr/`
2. 有机探索代码库，寻找摩擦点
3. 展示深化候选项（问题、解决方案、对可测试性和 AI 可导航性的收益）
4. Grill 对话：走设计树，决定深化的模块形状
5. 同步更新 `CONTEXT.md` 和 ADR

**核心概念**: 深模块 = 接口小但封装的行为多。目标是提升 locality（变更集中）和 leverage（接口复用价值高）。

---

### 阶段 12：代码质量审计

**使用的 Skill**: `/pd-rules-check`

**场景**: 定期审查代码质量，或者对某个目录做规范检查。

**做了什么**:
- **模式 A**（扫描推荐）: 快速扫描项目特征 → 生成画像 → 推荐规范集 → 深度审计
- **模式 B**（手动选择）: 展示 14 套规范集 → 用户选择 → 兼容性检查 → 执行审计
- **直接模式**: 指定规范 + 指定路径

14 套规范覆盖：`clean-code`、`clean-architecture`、DDD 系列、DDIA、Release It、The Pragmatic Programmer 等。

---

### 阶段 13：全局视角

**使用的 Skill**: `/pd-zoom-out`

**场景**: 面对一个不熟悉的代码区域，需要理解它在大图中的位置。

**做了什么**:
- 拉高一层抽象，生成相关模块地图和调用关系
- 使用项目的领域术语（CONTEXT.md 词汇）
- 帮助在动手前建立上下文认知

---

## 三、每个 Skill 详细用法

### pd-setup

**目的**: 为工程 Skill 配置项目级基础设施（issue tracker、Triage 标签、领域文档布局）

**触发词**: "setup pd skills"、"初始化工程 skill 配置"

**使用流程**:
1. 自动探测项目状态（git remote、AGENTS.md、CLAUDE.md、CONTEXT.md、docs/adr/ 等）
2. 展示发现，逐个确认三个决策（一次只确认一个）：
   - **Issue tracker**: GitHub / GitLab / 本地 Markdown / 其他
   - **Triage 标签**: 五个状态角色的标签映射，默认与角色名相同
   - **领域文档**: 单上下文 vs 多上下文
3. 生成 `docs/agents/` 下的配置文档
4. 在 CLAUDE.md / AGENTS.md 中写入 `## Agent skills` 配置块

**生成文件**:
```
docs/agents/
├── issue-tracker.md      # issue tracker 配置
├── triage-labels.md      # 标签映射
└── domain.md             # 领域文档消费规则
```

---

### pd-brainstorming

**目的**: 把模糊想法变成经过充分推敲的完整设计方案

**触发词**: brainstorming、头脑风暴、grill me、分析需求、规划任务、讨论设计方案

**工作流程**（5 个阶段）:
1. **理解上下文** — 查看项目状态、读取已有文档、了解目的和约束
2. **深度追问** — 逐个问，优先多选题，能看代码就看代码，每个问题给出推荐答案
3. **探索方案** — 提出 2-3 种方案，列出权衡，给出推荐
4. **渐进式呈现** — 分段呈现设计，每段确认，覆盖架构/组件/数据流/错误处理/测试
5. **保存方案** — 写入 `docs/RAD.md`

**输出**: `docs/RAD.md`（按时间倒序追加）

**关键原则**: 多选型优于开放型、YAGNI 原则、至少 2-3 个方案、增量验证

---

### pd-grill-with-docs

**目的**: 对已有方案进行领域对齐和压力测试，确保术语与项目领域模型一致

**触发词**: "压力测试这个方案"、"grill 一下这个计划"、"检查术语一致性"

**工作流程**:
1. 读取项目的 `CONTEXT.md`（领域术语表）和 `docs/adr/`（架构决策）
2. 逐个挑战方案中的术语使用、模糊语言、边界条件
3. 对照代码验证方案是否与实际实现矛盾
4. 即时更新 `CONTEXT.md`（术语解决后立即写入）
5. 必要时创建 ADR（满足三个条件：难逆转、缺少上下文会令人费解、存在真实权衡）
6. 更新 `docs/RAD.md`

**三不创建 ADR 的原则**:
- 不难逆转 → 跳过
- 不是令人费解的 → 跳过
- 没有真实权衡 → 跳过

---

### pd-bdd

**目的**: 用 Given-When-Then 自然语言精确描述产品行为，与 TDD 形成双保险

**触发词**: "用 BDD 分析这个需求"、"行为驱动开发"

**使用流程**（6 步）:
1. **接收需求** — 一句话描述
2. **生成 BDD 用例** — 3-5 个用例，覆盖正常路径 + 边界条件 + 异常处理
3. **用户确认** — 确认不确定的细节
4. **编写测试代码** — 每个用例对应一个测试函数，保留 BDD 注释
5. **实现代码** — 根据用例实现业务逻辑
6. **验证** — 运行程序确认功能与 BDD 描述一致

**核心公式**:
```
Given（假如） → 处于什么状态
When（当）    → 发生了什么操作
Then（那么）  → 应该得到什么结果
```

**好的用例特征**: 自然语言、状态精确、因果关系明确、一个用例一个场景

**不适合**: 图形界面测试、美术/视觉效果、模糊需求

---

### pd-to-prd

**目的**: 将 `docs/RAD.md` 合成为结构化 PRD 并发布到 issue tracker

**触发词**: "生成 PRD"、"create a PRD"

**工作流程**:
1. 读取 `docs/RAD.md`（如果存在）
2. 映射 RAD 各节到 PRD 模板字段
3. 探索仓库确认代码状态
4. 规划需要构建/修改的模块
5. 按模板编写 PRD
6. 发布到 issue tracker（打上 `ready-for-agent` 标签）

**PRD 模板包含**: Problem Statement、Solution、User Stories（大量）、Implementation Decisions、Testing Decisions、Out of Scope、Further Notes

**不做采访** — 直接从已有上下文合成

---

### pd-to-issues

**目的**: 将 PRD 按垂直切片（tracer bullet）拆分为独立可执行的 issue

**触发词**: "把计划拆成 issue"、"创建实现工单"、"break down work"

**工作流程**:
1. 从 PRD 或已有对话收集上下文
2. 探索代码库（可选）
3. 按**垂直切片**拆分：每个 slice 是完整的端到端路径
4. 标注每个 slice 是 HITL（人工）还是 AFK（自动）
5. 展示拆分方案，确认粒度和依赖
6. 按依赖顺序发布到 issue tracker

**垂直切片规则**:
- 每个 slice 交付一条窄但**完整**的路径（schema → API → UI → tests）
- 完成的 slice 应可独立演示/验证
- 宁拆薄不拆厚

---

### pd-triage

**目的**: Issue 状态机管理 — 分类、分流、准备 Agent Brief

**触发词**: "看看需要我关注的 issue"、"把 #42 标记为 ready-for-agent"

**两种角色**:
- **分类角色**: bug / enhancement
- **状态角色**: needs-triage → needs-info → ready-for-agent / ready-for-human / wontfix

**典型操作**:
- `"Show me anything that needs my attention"` — 展示三类 bucket：未标记、needs-triage、needs-info 有记者活动的
- `"Let's look at #42"` — 阅读完整 issue，推荐分类和状态
- `"Move #42 to ready-for-agent"` — 直接状态覆盖，询问是否需要 Agent Brief

**Agent Brief**: 当标记为 `ready-for-agent` 时，需要撰写持久化的执行指南（参考 `AGENT-BRIEF.md`）

---

### pd-prototype

**目的**: 构建可丢弃的原型来验证关键设计决策

**触发词**: prototype this、let me play with it、try a few designs

**两条分支**:

| 问题类型 | 分支 | 产出 |
|---------|------|------|
| "这个逻辑/状态模型对吗？" | LOGIC.md | 交互式终端 TUI 应用 |
| "这个应该长什么样？" | UI.md | 同一路由上多个 UI 变体，`?variant=` 切换 |

**共同规则**:
1. 从第一天起就标记为 throwaway（可丢弃）
2. 一条命令运行（利用项目已有 task runner）
3. 状态在内存中（无持久化）
4. 跳过抛光（无测试、无错误处理、无抽象）
5. 展示完整状态
6. 完成后删除或吸收

**完成后引导**:
- 验证了设计 → 回到 `/pd-to-prd`
- 验证了 UI → 删除失败变体，吸收获胜方案
- 方案被证伪 → 回到 `/pd-brainstorming`

---

### pd-tdd

**目的**: 测试驱动开发，red-green-refactor 循环

**触发词**: tdd、red-green-refactor、测试驱动、test-first

**工作流程**:
1. **Planning** — 确认接口变更、测试优先级、深模块机会 → 获取用户批准
2. **Tracer Bullet** — 写一个测试（RED）→ 写最少代码通过（GREEN）
3. **Incremental Loop** — 逐个行为 RED → GREEN
4. **Refactor** — 所有测试通过后重构

**关键规则**:
- **纵向切片**：一个测试 → 一个实现 → 重复（不要先写所有测试）
- 测试验证行为而非实现细节
- 使用公共接口
- **RED 时不重构**

**参考子文档**:
- `tests.md` — 测试示例
- `mocking.md` — Mocking 指南
- `deep-modules.md` — 深模块设计
- `interface-design.md` — 接口可测试性设计
- `refactoring.md` — 重构候选

---

### pd-diagnose

**目的**: 系统化排错循环

**触发词**: diagnose this、debug this、出 bug 了、性能回退

**六阶段**:
1. **Phase 1 — Build feedback loop** — 构建可自动运行的 pass/fail 信号（失败测试、curl 脚本、CLI 调用、浏览器脚本、trace 回放等 10 种方式）
2. **Phase 2 — Reproduce** — 确认复现的是用户描述的同一问题
3. **Phase 3 — Hypothesise** — 生成 3-5 个可证伪的假设并排序
4. **Phase 4 — Instrument** — 每次探测对应一个假设，变更一个变量，调试日志带唯一前缀
5. **Phase 5 — Fix + regression test** — 先写回归测试再修复
6. **Phase 6 — Cleanup + post-mortem** — 清理调试代码，写 commit message

**关键理念**: "拥有反馈循环的能力本身就是技能。"

**结束后**: 如果发现架构问题，传递给 `/pd-improve-codebase-architecture`

---

### pd-execution

**目的**: 批量扫描并执行本地 issue tracker 中未完成的任务

**触发词**: "批量执行 issue"、"按依赖顺序实现任务"

**工作流程**:
1. 读取 `.scratch/*/issues/` 下所有 issue
2. 检查每个 issue 的完成状态（查找 `## Completed` 标记和验收标准复选框）
3. 解析 `Blocked by` 构建依赖图，拓扑排序
4. 按顺序逐个执行：读取 → 探索 → 报告 → 确认 → 实现 → 验证 → 标记完成
5. 汇总完成情况

**安全规则**:
- 不执行破坏性操作（无确认）
- 编码前先展示计划
- 一个 issue 完成后再开始下一个
- 遇到模糊标准时询问用户

---

### pd-doc

**目的**: 项目文档自动管理与增量更新

**触发词**: /pd-doc

**三种模式**:
- **模式 A（新项目）**: 创建 `docs/architecture.md` + `docs/api.md` + `docs/changelog.md` 骨架
- **模式 B（增量更新）**: 对比上次文档后的变更，增量更新
- **模式 C（大模块）**: 在 `docs/modules/` 下创建独立文档

**文档目录**:
```
docs/
├── architecture.md          # 项目架构总览
├── api.md                   # 接口定义汇总
├── changelog.md             # 改动日志
└── modules/[module-name].md # 大模块说明
```

**核心原则**: 基于实际代码分析、先验证再记录、大模块才独立文档

---

### pd-improve-codebase-architecture

**目的**: 发现架构摩擦点，提出"深化"重构机会

**触发词**: "改善架构"、"找到重构机会"、"提高可测试性"

**核心概念**（LANGUAGE.md 术语）:
- **Module** — 有接口和实现的任何单元
- **Interface** — 调用者必须知道的一切（类型、不变量、错误模式）
- **Depth** — 接口背后的行为量。深 = 小接口大行为，浅 = 接口和实现差不多复杂
- **Seam** — 接口所在的位置；可修改行为的地方
- **Adapter** — 满足接口的具体实现

**工作流程**:
1. **Explore** — 有机探索，寻找摩擦点
2. **Present candidates** — 展示深化候选项（文件、问题、方案、收益）
3. **Grilling loop** — 用户选择后进入 grill 对话，走设计树

**更新 CONTEXT.md**: 新术语或术语修正即时更新

---

### pd-rules-check

**目的**: 基于 14 套经典软件工程书籍对代码进行规范审计

**触发词**: "审查代码质量"、"检查代码规范"、"评估架构"

**14 套规范集**:

| 层级 | 规范 | 核心问题 |
|-----|------|---------|
| 微观 | clean-code | 能跑的代码 ≠ 干净的代码 |
| 微观 | code-complete | 构造质量不是偶然的 |
| 微观 | refactoring | 重构 ≠ 重写 ≠ 改需求 |
| 微观 | refactoring-guru | 具体重构手法与代码异味 |
| 中观 | a-philosophy-of-software-design | 功能实现 ≠ 设计完成 |
| 中观 | patterns-of-enterprise-application-architecture | 选对模式，不要混合职责 |
| 中观 | working-effectively-with-legacy-code | 没测试的代码就是遗留代码 |
| 宏观 | clean-architecture | 不要让细节成为架构 |
| 宏观 | domain-driven-design | 业务语言 ≠ 代码变量名 |
| 宏观 | domain-driven-design-distilled | DDD 够用就好 |
| 宏观 | implementing-domain-driven-design | DDD 是实现的，不是命名的 |
| 宏观 | designing-data-intensive-applications | 不要假设读写有序新鲜 |
| 宏观 | release-it | happy path ≠ 生产就绪 |
| 全局 | the-pragmatic-programmer | 拥有结果，不要只优化局部 |

**三种模式**:
- **模式 A**（扫描推荐）: 项目扫描 → 画像 → 推荐 → 确认 → 审计
- **模式 B**（手动选择）: 展示全部 → 选择 → 兼容性检查 → 审计
- **直接模式**: 指定规范 + 指定路径

**输出**: `docs/pd-rule-check.md`

---

### pd-zoom-out

**目的**: 拉高视角，理解某个代码区域在大图中的位置

**触发词**: zoom out、"这是干什么的"、"我不熟悉这个区域"

**做了什么**:
- 上拉一层抽象
- 生成相关模块地图和调用关系
- 使用项目的领域术语

**适用场景**: 接手新代码区域、理解模块间依赖、排查不熟悉的问题

---

## 四、Skill列表

| 阶段 | Skill | 一句话 |
|------|-------|--------|
| 需求设计 | `/pd-brainstorming` | 深度设计追问，产出完整方案 |
| 需求设计 | `/pd-grill-with-docs` | 用领域模型和 ADR 压力测试方案 |
| 需求设计 | `/pd-bdd` | Given-When-Then 行为描述，与 TDD 双保险 |
| 规划拆分 | `/pd-to-prd` | 合成结构化 PRD 并发布 |
| 规划拆分 | `/pd-to-issues` | 按垂直切片拆分为独立 issue |
| 规划拆分 | `/pd-triage` | Issue 状态机管理 |
| 验证执行 | `/pd-prototype` | 可丢弃原型验证关键决策 |
| 验证执行 | `/pd-tdd` | 测试驱动开发 |
| 验证执行 | `/pd-diagnose` | 系统化排错循环 |
| 验证执行 | `/pd-execution` | 批量执行已规划的 issue |
| 质量架构 | `/pd-improve-codebase-architecture` | 发现架构摩擦，深化模块 |
| 质量架构 | `/pd-rules-check` | 基于 14 套经典书籍的代码审计 |
| 文档辅助 | `/pd-doc` | 项目文档自动管理 |
| 文档辅助 | `/pd-setup` | 初始化工程 Skill 配置 |
| 文档辅助 | `/pd-zoom-out` | 拉高视角理解全局 |


---



## 附录：Skill 交叉关系

```
从想法到交付的完整路径（推荐顺序）:

pd-setup                                    (首次初始化)
    ↓
pd-brainstorming → pd-grill-with-docs       (设计打磨)
    ↓
pd-bdd                                       (行为精确化)
    ↓
pd-prototype (可选)                          (原型验证)
    ↓
pd-to-prd                                    (发布 PRD)
    ↓
pd-to-issues                                 (拆分 issue)
    ↓
pd-triage                                    (issue 管理)
    ↓
pd-tdd / pd-execution                        (实现)
    ↓
pd-doc                                       (文档更新)

随时可用的辅助 Skill:
pd-diagnose          → 排查 bug
pd-improve-codebase-architecture → 架构改善
pd-rules-check       → 代码质量审计
pd-zoom-out          → 全局视角
```

### 常见路径速查

| 场景 | 路径 |
|---|---|
| 想法还不清楚 → 直接写代码 | brainstorming → tdd |
| 方案已有，但关键决策不确定 | brainstorming → prototype → to-prd → to-issues → tdd |
| 需要打磨术语和边界 | brainstorming → grill-with-docs → to-prd → to-issues → tdd |
| 遇到 bug | diagnose |
| PRD 已存在，只需拆分 | to-issues → tdd |
| 批量执行已规划的 issue | execution |
| 定期代码质量审计 | rules-check |

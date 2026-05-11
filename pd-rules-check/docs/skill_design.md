# Skill 设计：代码规范审计

## 需求描述

基于 `agent-rules-books` 仓库中的 14 套编码规范，构建一个 Skill，能够：
1. 根据用户项目特征，自动判断适用的规范集
2. 读取 reference 目录中的规则文件
3. 扫描用户项目，识别违反规范的地方
4. 输出结构化审计报告，每条引用具体规范来源

## 仓库规范全景

### 14 个规范集一览

| 规范集 | 核心关注点 | 作用层级 | mini 规则数 | 特点 |
|--------|-----------|---------|------------|------|
| **clean-code** | 代码可读性、命名、函数设计 | 微观（函数/变量级） | 29 | 最日常、最低门槛的工程卫生规范 |
| **code-complete** | 软件构造全流程、缺陷预防 | 微观→中观（函数→模块） | 38 | 最全面的编码操作手册，覆盖从需求到调试 |
| **the-pragmatic-programmer** | 工程思维、DRY、正交性、自动化 | 全局（工程哲学） | 47 | 通用工程操作系统，强调 "ownership" 和反馈 |
| **a-philosophy-of-software-design** | 降低复杂度、深模块、信息隐藏 | 中观（模块/API 级） | 28 | 以"降低认知负担"为唯一度量标准 |
| **clean-architecture** | 依赖方向、边界隔离、框架无关 | 宏观（架构级） | 31 | 强硬的"依赖向内"规则，框架/数据库视为细节 |
| **domain-driven-design** | 领域模型、统一语言、限界上下文 | 宏观→中观（领域建模） | 30 | 最重，42K full版，强调业务语言驱动设计 |
| **domain-driven-design-distilled** | DDD 轻量版、子域分类、上下文映射 | 宏观→中观 | 38 | DDD 的快速上手版，"够用就好" |
| **implementing-domain-driven-design** | DDD 落地实现：聚合、事件、仓储 | 中观（实现级） | 39 | 最实操的 DDD，带 Event Sourcing 指导 |
| **patterns-of-enterprise-application-architecture** | 分层、事务脚本 vs 领域模型、ORM 策略 | 中观（企业架构） | 36 | 模式目录型规范，帮你"选对模式" |
| **refactoring** | 行为保留、小步重构、代码异味 | 微观→中观（重构操作） | 31 | 强调"重构 ≠ 重写 ≠ 改需求" |
| **refactoring-guru** | 重构手法目录、代码异味目录 | 微观（具体手法） | 46 | 最大 mini 版（6K+），具体手法最丰富 |
| **working-effectively-with-legacy-code** | 无测试代码的安全修改、接缝技术 | 微观→中观 | 32 | 唯一承认"烂代码是常态"的规范 |
| **release-it** | 生产生存能力：熔断、限流、超时 | 宏观（运维/生产级） | 30 | 唯一关注"代码上线后会发生什么" |
| **designing-data-intensive-applications** | 分布式数据：一致性、复制、分区 | 宏观（数据架构级） | 37 | 唯一关注分布式数据正确性 |

### 规范的应用层级分布

```
宏观架构层
  ├── clean-architecture (依赖边界)
  ├── DDIA (分布式数据)
  ├── release-it (生产生存)
  ├── domain-driven-design (领域建模)
  ├── domain-driven-design-distilled (DDD轻量)
  └── implementing-domain-driven-design (DDD实现)

中观模块层
  ├── patterns-of-enterprise-application-architecture (模式选择)
  ├── a-philosophy-of-software-design (模块复杂度)
  └── working-effectively-with-legacy-code (安全修改)

微观代码层
  ├── clean-code (可读性)
  ├── code-complete (构造纪律)
  ├── refactoring (重构纪律)
  └── refactoring-guru (重构手法)

全局工程思维
  └── the-pragmatic-programmer (工程哲学)
```

### 兼容性矩阵

91 对书之间标注了 ✅互补 / 🔁重叠 / ❌冲突，例如：
- DDD + PoEAA = ❌冲突（领域模型 vs 事务脚本的设计哲学对立）
- Clean Code + APoSD = 🔁重叠（都关注代码层面，选一个即可）
- Release It + 几乎所有书 = ✅互补（运维层面不干扰设计层面）
- Clean Code + Code Complete = 🔁重叠
- Clean Code + Pragmatic Programmer = 🔁重叠

### 每个规范的"纠偏焦点"

- Clean Code："能跑的代码不等于干净的代码"
- APoSD："功能实现 ≠ 设计完成"
- Release It："跑通 happy path ≠ 生产就绪"
- WELC："没测试的代码就是遗留代码"
- DDIA："不要假设读写都是本地、有序、新鲜的"
- Clean Architecture："不要让细节成为架构"

## 可自动化 vs 只能提示的规则

### 可以自动化的（占 60%）

#### 代码异味扫描
| 规范来源 | 检测项 | 检测方法 |
|---------|--------|---------|
| clean-code | 超长函数 | 统计函数行数，超过 30 行标记 |
| clean-code | 超长参数列表 | grep 函数签名，参数超过 3 个标记 |
| clean-code | 深层嵌套 | AST 分析缩进层级，超过 3 层标记 |
| clean-code | 布尔标志参数 | `function(xxx, true/false)` 模式匹配 |
| clean-code | 上帝类/大文件 | 文件行数超过 300 行标记 |
| clean-code | 命名模糊 | 单字母函数名、`tmp/data/info` 等变量名 |
| code-complete | 复杂控制流 | 分支/循环过多，难以验证 |
| refactoring-guru | 代码异味目录 | 重复代码、过长类、过长方法等 |
| refactoring-guru | 重构手法匹配 | 发现异味后推荐具体重构手法 |

#### 架构违规检测
| 规范来源 | 检测项 | 检测方法 |
|---------|--------|---------|
| clean-architecture | 依赖方向错误 | 分析各层 import 语句，domain 层不应 import 框架/数据库 |
| clean-architecture | 框架细节泄漏到业务层 | grep 业务层中的 express/flask/django/sequelize 等引用 |
| clean-architecture | 控制器包含业务决策 | 分析 controller 中是否有 if/else 业务分支 |
| DDD | 跨上下文直接引用 | `import * from '../billing'` 模式 |
| DDD | 数据库结构泄漏到领域层 | 领域层中出现 @Column/@Entity 等 ORM 注解 |
| PoEAA | N+1 查询模式 | 循环内数据库调用 |
| PoEAA | 事务脚本 vs 领域模型 | 检测业务逻辑是否全部在 service/controller 中 |

#### 测试与生产就绪性
| 规范来源 | 检测项 | 检测方法 |
|---------|--------|---------|
| WELC | 无测试的遗留代码 | 检查 test 目录覆盖率 |
| WELC | 缺少接缝 | 难以实例化、依赖硬编码的类 |
| code-complete | 测试只覆盖 happy path | 检查测试用例的边界条件 |
| release-it | 无超时/无重试的外调 | grep 网络调用，检查 timeout 配置 |
| release-it | 循环内远程调用 | 检测循环内调用外部服务 |
| release-it | 无错误处理的 IO 操作 | 检测 try/catch 缺失 |
| release-it | 无限等待 | 检测缺少 timeout 的网络/数据库调用 |

### 只能给提示的（占 40%）

| 规范来源 | 判断项 | 原因 |
|---------|--------|------|
| APoSD | "这个模块是否够深" | 需要人类判断语义 |
| DDD | "统一语言是否一致" | 需要对齐业务专家 |
| APoSD | "这个设计是否降低了认知负担" | 高度主观 |
| PoEAA | "是否选择了正确的业务逻辑模式" | 需要理解业务场景 |
| IDDD | "聚合边界是否合理" | 需要领域知识 |
| clean-architecture | "边界是否足够轻量" | 需要架构权衡判断 |
| PragProg | "这个决策是否可逆" | 需要业务上下文 |
| DDD | "核心领域是否被保护" | 需要商业价值判断 |

## Skill 方案

### 方案一：交互式审计（推荐）

```
用户: 帮我审查一下这个项目的代码质量

Skill 流程:
1. 分析项目特征（语言、框架、架构、文件数）
2. 自动推荐适用的规范集（如后端 API 推荐 clean-architecture + clean-code + release-it）
3. 运行可自动化的扫描规则
4. 对无法自动判断的部分，引导用户回答几个问题
5. 输出结构化审计报告，每条都引用具体规范的哪条规则
```

### 方案二：纯自动化扫描

```
用户: 用 clean-code 审查 src/

Skill 流程:
1. 读取 clean-code 的规则
2. 扫描指定目录
3. 输出违反规则的清单
```

### 方案三：混合式（最佳体验）

```
用户: 我的项目要上线了，帮我做全面审查

Skill 流程:
1. 根据项目类型自动选择规范组合
2. 先运行自动化扫描（发现明显问题）
3. 再针对架构级问题，读取 full 版参考，进行深度对话
4. 生成报告，按规范来源分类，每条都有引用和修复建议
```

## 目录结构

```
.claude/skills/code-audit/
├── SKILL.md                    # skill 定义：何时触发、如何交互
├── reference/                  # 从 agent-rules-books 复制或 symlink
│   ├── clean-code/
│   │   ├── clean-code.mini.md
│   │   └── clean-code.md        # full 参考
│   ├── clean-architecture/
│   ├── domain-driven-design/
│   ├── refactoring/
│   ├── release-it/
│   ├── ...
│   └── COMPATIBILITY.md        # 兼容性矩阵
└── scripts/                    # 可选的扫描脚本
    ├── detect-long-functions.sh
    ├── detect-deep-nesting.sh
    ├── detect-framework-leaks.sh
    └── ...
```

## 扫描能力获取方式

| 方式 | 说明 | 优点 | 缺点 |
|------|------|------|------|
| A: 纯 Claude 扫描 | 让 Claude Code 用 glob/grep 扫描项目 | 灵活，能理解上下文 | 慢，大项目 token 消耗大 |
| B: 预定义脚本 + Claude | shell 脚本快速扫描，Claude 分析结果 | 快，成本低 | 脚本维护成本 |
| C: 混合（推荐） | 简单规则用脚本，复杂规则用 Claude | 平衡速度与质量 | 实现稍复杂 |

## 适用性判断（误报控制）

扫描前必须先判断项目类型，否则会产生大量误报：

| 项目类型 | 适用规范 | 跳过规范 |
|---------|---------|---------|
| CRUD / 内部工具 | clean-code, code-complete | DDD, clean-architecture |
| 后端 API 服务 | clean-architecture, clean-code, release-it | DDD（除非业务复杂） |
| 领域密集型系统 | DDD, clean-architecture, clean-code | - |
| 数据/消息系统 | DDIA, release-it | - |
| 遗留系统改造 | WELC, refactoring, clean-code | clean-architecture（初期） |
| 前端项目 | clean-code, refactoring | release-it, DDIA, DDD |

## 分层扫描策略

| 层级 | 内容 | 速度 | Token 消耗 | 目标 |
|------|------|------|-----------|------|
| L0 | 文件统计（行数、文件数、依赖图） | 快 | 低 | 项目概况 |
| L1 | 热点扫描（最长函数、最大文件、最多参数） | 快 | 低 | 发现最差的 10% |
| L2 | 深度分析（只对热点文件详细分析） | 慢 | 中 | 精准定位 |
| L3 | 架构级审查（依赖方向、分层合规） | 最慢 | 高 | 按需触发 |

## 核心难点

### 1. 规范映射问题

规范文件是原则性的（"深模块"、"依赖向内"），但代码是具体的。需要建立原则到代码的映射关系：

| 规范原则 | 检测模式 |
|---------|---------|
| "深模块"（APoSD） | 分析模块公开 API 数 vs 内部实现行数比 |
| "依赖向内"（Clean Architecture） | grep 各层的 import 语句 |
| "函数单一职责"（Clean Code） | 分析函数中的概念词频 |
| "命令与查询分离"（Clean Code） | 分析函数是否同时有返回值和副作用 |
| "超时必须显式设置"（Release It） | grep 网络调用，检查 timeout 参数 |

### 2. 规范冲突处理

利用已有的 COMPATIBILITY.md 矩阵：
- 如果用户同时选了 DDD + PoEAA，Skill 先预警冲突
- 让用户选择以哪个为准

### 3. 扫描深度 vs 成本

全面扫描一个中大型项目可能需要分析几百个文件、数千个函数，token 消耗巨大。
解决：分层扫描 + 热点优先 + 按需深度分析。

## 报告输出结构

```markdown
# 代码审计报告

## 项目概况
- 语言: TypeScript
- 框架: Express
- 架构: 三层架构（Controller-Service-Repository）
- 文件: 123 files, 4560 lines

## 适用规范
- clean-code.mini (日常代码质量)
- clean-architecture.mini (架构边界)
- release-it.mini (生产就绪性)

## 审计结果

### 🔴 严重 (3 items)
1. **依赖方向违规** (clean-architecture, Decision Rule #4)
   - 文件: src/domain/user.ts L12 导入了 `import { Sequelize } from 'sequelize'`
   - 问题: 领域层直接引用 ORM 框架
   - 修复: 创建仓储接口，将 Sequelize 实现移到基础设施层

### 🟡 警告 (8 items)
...

### 🟢 建议 (12 items)
...

## 规范覆盖率
- clean-code: 29 rules, 18 passed, 7 violated, 4 N/A
- clean-architecture: 31 rules, 12 passed, 5 violated, 14 N/A
- release-it: 30 rules, 5 passed, 12 violated, 13 N/A
```

## 实施阶段

### Phase 1：基础扫描（L0 + L1）
- 自动化扫描明显违规（长函数、大文件、框架泄漏、无超时外调）
- 项目特征分析
- 适用规范推荐
- 基础报告输出

### Phase 2：深度分析（L2）
- Claude 理解上下文后的深度分析
- 架构违规检测（依赖方向、分层合规）
- 测试覆盖分析
- 报告增加规范覆盖率统计

### Phase 3：交互式审查（L3）
- 对话模式引导用户审查无法自动化的部分
- 模块设计质量评估
- 聚合边界合理性讨论
- 统一语言一致性检查

## 关键成功因素

1. **适用性判断必须先于扫描**——不判断项目类型就直接扫描，误报会淹没用户
2. **每条发现必须引用具体规范**——不是"我觉得你的代码不好"，而是"根据 clean-architecture 决策规则 #4..."
3. **报告必须可操作**——不只是指出问题，还要给出最小修复步骤
4. **控制误报率**——宁可漏报，不要误报，误报会迅速消耗用户信任
5. **支持增量审查**——用户可能只想审查某个文件/目录，而不是全项目

## 两种使用模式

### 模式 A：先扫描 → 后推荐（主动式）

用户不需要提前知道规范名称，Skill 先扫描项目，再根据项目特征和问题推荐最匹配的规范。

```
用户: 帮我看看这个项目需要什么规范

Skill 流程:
Step 1 — 项目快速扫描（L0 + L1）
  - 语言/框架识别（package.json, requirements.txt, go.mod, pom.xml 等）
  - 目录结构分析（是否有 domain/, controller/, service/, test/ 等目录）
  - 热点统计（最大文件、最长函数、最深嵌套、最多参数）
  - 快速问题识别（框架泄漏、无超时外调、无测试文件等）

Step 2 — 项目画像生成
  - 语言: TypeScript
  - 框架: Express + Sequelize
  - 架构: 发现 controller/、service/、model/ 目录 → 三层架构
  - 热点: 3 个文件超过 500 行，12 个函数超过 40 行
  - 问题: model/ 目录中有 express 引用（框架泄漏），无 test/ 目录

Step 3 — 规范推荐（基于画像匹配）
  推荐规范:
  1. clean-code (优先级: 高) — 发现大量长函数、长参数列表
  2. clean-architecture (优先级: 高) — 发现框架泄漏到 model 层
  3. working-effectively-with-legacy-code (优先级: 高) — 无测试目录
  4. release-it (优先级: 中) — 后端服务，需检查生产就绪性
  5. patterns-of-enterprise-application-architecture (优先级: 中) — 三层架构适合模式检查

Step 4 — 用户确认
  - 用户可以选择全部、部分、或添加自定义规范
  - Skill 展示每条推荐的原因

Step 5 — 深度审计
  - 根据用户选择的规范，运行对应级别的扫描
  - 输出结构化报告 → docs/pd-rule-check.md
```

#### 匹配规则引擎

项目特征到规范推荐的映射关系：

| 项目特征 | 推荐规范 | 原因 |
|---------|---------|------|
| 有 `controller/` + `service/` + `model/` 目录 | clean-architecture, PoEAA | 典型三层架构，需检查依赖方向 |
| model/ 中有框架引用 | clean-architecture | 框架泄漏检测 |
| 无 test/ 目录 | WELC, clean-code | 遗留代码风险 |
| 有 HTTP client / fetch / axios 调用 | release-it | 需检查超时、重试、熔断 |
| 有数据库连接 + 循环内查询 | PoEAA, release-it | N+1 查询风险 |
| 文件超过 300 行 / 函数超过 30 行 | clean-code, refactoring-guru | 代码异味 |
| 有 `domain/` 或 `aggregate/` 目录 | DDD, IDDD | 领域驱动设计检查 |
| 有消息队列 / Kafka / Redis | DDIA, release-it | 分布式数据 + 生产就绪性 |
| 大量 if/else 分支在 service 中 | PoEAA, clean-code | 可能需要策略/状态模式 |
| 有 `shared/` 或 `common/` 大包 | clean-architecture, APoSD | 浅模块 / 共享包膨胀风险 |
| 前端项目 (React/Vue) | clean-code, refactoring | 组件设计、状态管理检查 |
| CLI 工具 | code-complete, the-pragmatic-programmer | 构造纪律、工程思维 |

### 模式 B：用户选择 → 后审计（选择式）

用户列出所有可用规范，自主选择 1 个或多个进行审计。

```
用户: 列出所有可用的规范

Skill 回复:

┌──── 可用规范目录 ────┐
│                      │
│ 📖 14 套编码规范     │
│                      │
│ ── 微观代码层 ──     │
│ 1. clean-code        │
│    代码可读性、命名  │
│    函数设计           │
│    29 rules · 3.8KB  │
│                      │
│ 2. code-complete     │
│    软件构造全流程     │
│    缺陷预防           │
│    38 rules · 6.7KB  │
│                      │
│ 3. refactoring       │
│    行为保留、小步重构 │
│    31 rules · 5.2KB  │
│                      │
│ 4. refactoring-guru  │
│    重构手法、代码异味 │
│    46 rules · 6.3KB  │
│                      │
│ ── 中观模块层 ──     │
│ 5. a-philosophy-of-  │
│    software-design   │
│    降低复杂度、深模块 │
│    28 rules · 5.8KB  │
│                      │
│ 6. patterns-of-      │
│    enterprise-app-   │
│    arch              │
│    分层、模式选择     │
│    36 rules · 8.1KB  │
│                      │
│ 7. working-          │
│    effectively-with- │
│    legacy-code       │
│    无测试代码的安全   │
│    修改               │
│    32 rules · 5.7KB  │
│                      │
│ ── 宏观架构层 ──     │
│ 8. clean-architecture│
│    依赖方向、边界隔离 │
│    31 rules · 5.5KB  │
│                      │
│ 9. domain-driven-    │
│    design            │
│    领域模型、统一语言 │
│    30 rules · 5.7KB  │
│                      │
│ 10. DDD distilled    │
│     DDD 轻量版       │
│     38 rules · 6.4KB │
│                      │
│ 11. implementing DDD │
│     DDD 落地实现     │
│     39 rules · 7.3KB │
│                      │
│ 12. DDIA             │
│     分布式数据一致性 │
│     37 rules · 6.9KB │
│                      │
│ 13. release-it       │
│     生产生存能力     │
│     30 rules · 6.4KB │
│                      │
│ ── 全局工程思维 ──   │
│ 14. the-pragmatic-   │
│     programmer       │
│     工程思维、DRY    │
│     47 rules · 7.2KB │
│                      │
│ 请输入编号选择       │
│ (如: 1,8,13)        │
│ 或输入 "all" 全选    │
│ 或输入 "auto" 自动   │
└──────────────────────┘

用户: 1,8,13

Skill: 已选择 clean-code + clean-architecture + release-it
⚠️ 兼容性检查: 全部 ✅ 互补，无冲突
开始审计...
```

#### 每条规范的详细说明

当用户想了解某个规范时，Skill 展示：

| 字段 | 说明 |
|------|------|
| **名称** | 规范集名称 |
| **核心问题** | 这套规范要解决的核心问题 |
| **适用场景** | 什么时候应该用 |
| **不适用场景** | 什么时候不该用 |
| **纠偏焦点** | 这套规范特有的"纠正偏见" |
| **典型发现** | 这套规范最常发现的 3-5 个问题 |
| **与其他规范关系** | 互补/重叠/冲突 |

示例输出：

```
📖 clean-code (Robert C. Martin)

核心问题: 能跑的代码不等于干净的代码
适用场景: 日常代码审查、重构前准备、代码合并审查
不适用场景: 架构设计讨论、分布式系统设计
纠偏焦点: 可读性 >  cleverness
典型发现:
  - 函数过长、参数过多、嵌套过深
  - 布尔标志参数、命令查询混合
  - 命名模糊、注释解释代码而非解释意图
与 clean-architecture: ✅ 互补（微观 + 宏观）
与 code-complete: 🔁 重叠（选一个即可）
与 pragmatic-programmer: 🔁 部分重叠
```

## References 目录方案

将所有规范原始文件内嵌到 Skill 的 `references/` 目录，消除外部依赖。

### 目录结构

```
.claude/skills/pd-rule-check/
├── SKILL.md                              # Skill 定义、触发条件、交互流程
├── references/                           # 规范原始文件（自包含，无外部依赖）
│   ├── COMPATIBILITY.md                  # 兼容性矩阵（精简版）
│   ├── clean-code/
│   │   ├── clean-code.md                 # full 版
│   │   ├── clean-code.mini.md            # mini 版
│   │   └── clean-code.nano.md            # nano 版
│   ├── clean-architecture/
│   ├── a-philosophy-of-software-design/
│   ├── code-complete/
│   ├── domain-driven-design/
│   ├── domain-driven-design-distilled/
│   ├── implementing-domain-driven-design/
│   ├── patterns-of-enterprise-application-architecture/
│   ├── refactoring/
│   ├── refactoring-guru/
│   ├── release-it/
│   ├── designing-data-intensive-applications/
│   ├── the-pragmatic-programmer/
│   └── working-effectively-with-legacy-code/
└── rules/                                # 用户项目分析报告输出目录
    └── pd-rule-check.md                  # 审计报告（自动生成）
```

### references 数据来源

从 `agent-rules-books` 仓库复制所有文件到 Skill 的 `references/` 目录：

| 来源路径 | 目标路径 |
|---------|---------|
| `clean-code/clean-code.md` | `references/clean-code/clean-code.md` |
| `clean-code/clean-code.mini.md` | `references/clean-code/clean-code.mini.md` |
| `clean-code/clean-code.nano.md` | `references/clean-code/clean-code.nano.md` |
| ...（每个规范 3 个文件） | ... |
| `COMPATIBILITY.md` | `references/COMPATIBILITY.md` |

总计：14 个规范 × 3 个版本 = 42 个规则文件 + 1 个兼容性矩阵

### COMPATIBILITY.md 精简方案

原始兼容性矩阵有 91 个独立 `.md` 文件，Skill 中保留主矩阵表格即可，
不需要每个 pair 的详细解释文件。精简版只保留：
- 主矩阵表格（✅/❌/🔁）
- 冲突 pair 的简要说明
- 重叠 pair 的选择建议

### references 更新策略

当 `agent-rules-books` 仓库更新规范时：
1. 检查 git diff，识别哪些规范文件有变化
2. 复制变化的文件到 Skill 的 `references/`
3. 更新 SKILL.md 中的版本号

## 完整工作流程

### 流程图

```
用户触发
    │
    ├── 模式 A: "帮我看看项目需要什么" ──→ 先扫描项目 ──→ 推荐规范 ──→ 用户确认 ──→ 审计
    │                                                                              │
    └── 模式 B: "列出所有规范" ────────────→ 展示目录 ──→ 用户选择 ──→ 兼容检查 ──→ 审计
                                                                                         │
                                                                                         ▼
                                                                              生成 docs/pd-rule-check.md
```

### 审计报告输出格式（docs/pd-rule-check.md）

```markdown
# 代码规范审计报告

> 生成时间: 2026-05-11
> 项目: /path/to/project
> 使用规范: clean-code.mini, clean-architecture.mini, release-it.mini

## 一、项目概况

| 指标 | 值 |
|------|-----|
| 语言 | TypeScript |
| 框架 | Express 4.x + Sequelize |
| 架构风格 | 三层架构 (Controller-Service-Model) |
| 文件数 | 123 (.ts) |
| 总行数 | 4,560 |
| 测试文件 | 0 (无测试) |
| 最大文件 | src/services/order.ts (682 行) |
| 最长函数 | processOrder (89 行) |
| 最深嵌套 | 5 层 (src/controllers/user.ts:45) |

## 二、适用性分析

| 规范 | 适用度 | 原因 |
|------|--------|------|
| clean-code | ✅ 高 | 发现长函数、长参数、命名模糊 |
| clean-architecture | ✅ 高 | Model 层泄漏 express 引用 |
| release-it | ⚠️ 中 | 后端服务，需检查生产就绪性 |
| DDD | ❌ 低 | CRUD 项目，无复杂领域逻辑 |

## 三、审计结果

### 🔴 严重问题 (3)

#### 1. 依赖方向违规
- **规范来源**: clean-architecture, Decision Rule #4
- **文件**: `src/models/user.ts` L12
- **代码**: `import { Sequelize, DataTypes } from 'sequelize'`
- **问题**: Model 层直接引用 ORM 框架，违反"框架/数据库视为细节"原则
- **影响**: 更换数据库时需要修改所有 model 文件
- **修复建议**: 创建仓储接口，将 Sequelize 实现移到基础设施层
  ```typescript
  // 建议: src/domain/ports/UserRepository.ts
  interface UserRepository {
    findById(id: string): Promise<User>;
  }
  // 实现: src/infrastructure/SequelizeUserRepository.ts
  ```

#### 2. 无超时设置的外部调用
- **规范来源**: release-it, Decision Rule #16
- **文件**: `src/services/payment.ts` L67
- **代码**: `await axios.post(url, data)`
- **问题**: 外部支付调用无超时设置，可能无限等待
- **修复建议**: 添加 timeout 和重试策略

### 🟡 警告 (8)
...

### 🟢 建议 (12)
...

## 四、规范覆盖率统计

| 规范 | 总规则 | 通过 | 违反 | N/A | 通过率 |
|------|--------|------|------|-----|--------|
| clean-code | 29 | 18 | 7 | 4 | 72% |
| clean-architecture | 31 | 12 | 5 | 14 | 71% |
| release-it | 30 | 5 | 12 | 13 | 29% |

## 五、优先级建议

### 立即修复
1. Model 层框架泄漏（clean-architecture #4）
2. 支付服务无超时调用（release-it #16）

### 短期改进
1. 拆分 processOrder 函数（clean-code #4）
2. 为关键服务添加测试（WELC #1）

### 长期规划
1. 考虑引入仓储模式（PoEAA）
2. 评估是否需要 DDD（业务复杂度增长后）
```

## 实施阶段调整

### Phase 1：基础能力
- 复制 references 到 Skill 目录
- 实现模式 B（用户选择式）
- 支持 1-3 个规范的基础审计
- 输出 docs/pd-rule-check.md

### Phase 2：智能推荐
- 实现模式 A（先扫描 → 后推荐）
- 项目特征识别引擎
- 规范匹配推荐算法
- 兼容性自动检查

### Phase 3：深度审计
- L2/L3 深度分析
- 交互式审查（对话模式）
- 修复建议自动生成
- 规范覆盖率统计

### Phase 4：持续集成
- 支持增量审计（只审计变更文件）
- 与 git diff 集成
- 审计报告历史对比
- 规范版本自动同步

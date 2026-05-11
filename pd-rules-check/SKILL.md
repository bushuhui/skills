---
name: pd-rules-check
description: 基于 14 套经典软件工程书籍的编码规范，对项目进行代码质量审计。支持两种模式：(A) 先扫描项目特征再自动推荐规范，(B) 用户手动选择规范集。输出结构化审计报告。Use when 用户要求审查代码质量、检查代码规范、评估项目架构、推荐编码规则、或提到 pd-rule-check。
---

# PD Rules Check

基于 14 套经典软件工程书籍的编码规范审计工具。扫描项目或按用户选择，对照规范检查代码，输出带具体规则引用的结构化审计报告。

## 可用规范集

### 微观代码层（函数/变量级）

| # | 名称 | 核心问题 | mini 规则数 |
|---|------|---------|------------|
| 1 | `clean-code` | 能跑的代码 ≠ 干净的代码 | 29 |
| 2 | `code-complete` | 构造质量不是偶然的 | 38 |
| 3 | `refactoring` | 重构 ≠ 重写 ≠ 改需求 | 31 |
| 4 | `refactoring-guru` | 具体重构手法与代码异味 | 46 |

### 中观模块层（模块/API级）

| # | 名称 | 核心问题 | mini 规则数 |
|---|------|---------|------------|
| 5 | `a-philosophy-of-software-design` | 功能实现 ≠ 设计完成 | 28 |
| 6 | `patterns-of-enterprise-application-architecture` | 选对模式，不要意外混合职责 | 36 |
| 7 | `working-effectively-with-legacy-code` | 没测试的代码就是遗留代码 | 32 |

### 宏观架构层

| # | 名称 | 核心问题 | mini 规则数 |
|---|------|---------|------------|
| 8 | `clean-architecture` | 不要让细节成为架构 | 31 |
| 9 | `domain-driven-design` | 业务语言 ≠ 代码变量名 | 30 |
| 10 | `domain-driven-design-distilled` | DDD 够用就好，不要过度 | 38 |
| 11 | `implementing-domain-driven-design` | DDD 是实现的，不是命名的 | 39 |
| 12 | `designing-data-intensive-applications` | 不要假设读写都是本地有序新鲜的 | 37 |
| 13 | `release-it` | 跑通 happy path ≠ 生产就绪 | 30 |

### 全局工程思维

| # | 名称 | 核心问题 | mini 规则数 |
|---|------|---------|------------|
| 14 | `the-pragmatic-programmer` | 拥有结果，不要只优化局部 | 47 |

## 工作流

### 模式 A：先扫描 → 后推荐（用户说"帮我看看项目"）

**Step 1 — 项目快速扫描（L0 + L1）**

```
扫描内容:
- 语言/框架识别: package.json, requirements.txt, go.mod, pom.xml, Cargo.toml 等
- 目录结构: 是否有 domain/, controller/, service/, test/, model/, repository/ 等
- 热点统计: 最大文件(行数)、最长函数(行数)、最深嵌套(层级)、最多参数
- 快速问题: 框架泄漏(grep import)、无超时外调(grep fetch/axios/requests)、无测试文件
```

**Step 2 — 项目画像生成**

生成表格:
- 语言、框架、推测架构
- 文件数、总行数、测试覆盖率
- 热点: 超过阈值的具体文件和函数
- 快速发现的问题清单

**Step 3 — 规范推荐**

根据项目特征匹配推荐（参见下方「匹配规则引擎」）。每条推荐标注优先级（高/中/低）和原因。

**Step 4 — 用户确认**

展示推荐清单，询问用户:
- 是否接受全部推荐
- 是否要调整（添加/删除某些规范）
- 是否要查看某个规范的详细说明

**Step 5 — 深度审计**

根据用户确认的规范集，读取 `references/{book}/{book}.mini.md`，逐条对照代码扫描，输出报告到 `docs/pd-rule-check.md`。

### 模式 B：用户选择 → 后审计（用户说"列出所有规范"）

**Step 1 — 展示规范目录**

向用户展示上方「可用规范集」完整列表，包含编号、名称、核心问题、规则数。

提示用户:
```
请输入编号选择 (如: 1,8,13)
或输入 "all" 全选
或输入编号查看规范详情 (如: "?1")
```

**Step 2 — 查看规范详情（可选）**

用户输入 `?N` 时，读取 `references/{book}/{book}.mini.md`，展示:
- 适用场景 / 不适用场景
- 纠偏焦点
- Decision rules 和 Trigger rules 要点
- 与其他规范的兼容性

**Step 3 — 兼容性检查**

读取 `references/COMPATIBILITY.md`，检查用户选择的规范组合:
- ❌ 冲突: 警告用户并说明原因，让用户选择以哪个为准
- 🔁 重叠: 提示可能有重复检查，建议保留一个
- ✅ 互补: 通过

**Step 4 — 执行审计**

读取选中的 `references/{book}/{book}.mini.md`，对照项目代码逐条检查，输出报告到 `docs/pd-rule-check.md`。

### 直接模式：指定规范 + 指定路径

用户说"用 clean-code 审查 src/"时:
1. 直接读取 `references/clean-code/clean-code.mini.md`
2. 只扫描指定目录
3. 输出精简版报告

## 匹配规则引擎

项目特征 → 推荐规范的映射:

| 项目特征 | 推荐规范 | 原因 |
|---------|---------|------|
| `controller/` + `service/` + `model/` 目录 | clean-architecture, PoEAA | 典型三层架构 |
| model/ 中有框架引用 | clean-architecture | 框架泄漏 |
| 无 test/ 目录 | WELC, clean-code | 遗留代码风险 |
| HTTP client / fetch / axios 调用 | release-it | 超时/重试检查 |
| 数据库 + 循环内查询 | PoEAA, release-it | N+1 风险 |
| 文件 >300 行 / 函数 >30 行 | clean-code, refactoring-guru | 代码异味 |
| `domain/` 或 `aggregate/` 目录 | DDD, IDDD | 领域驱动检查 |
| Kafka / Redis / 消息队列 | DDIA, release-it | 分布式数据 + 生产就绪 |
| service 中大量 if/else | PoEAA, clean-code | 策略/状态模式需求 |
| `shared/` 或 `common/` 大包 | clean-architecture, APoSD | 浅模块风险 |
| 前端项目 (React/Vue) | clean-code, refactoring | 组件设计 |
| CRUD / 内部工具 | clean-code, code-complete | 日常质量 |
| CLI 工具 | code-complete, pragmatic-programmer | 构造纪律 |

## 兼容性矩阵（精简）

从 `references/COMPATIBILITY.md` 读取。关键冲突:

| 组合 | 状态 | 说明 |
|------|------|------|
| DDD + PoEAA | ❌ 冲突 | 领域模型 vs 事务脚本哲学对立 |
| DDD + IDDD | 🔁 重叠 | IDDD 是 DDD 的实操版，选一个 |
| DDD + DDD Distilled | 🔁 重叠 | Distilled 是轻量版，选一个 |
| Clean Code + Code Complete | 🔁 重叠 | 部分规则重合 |
| Clean Code + Pragmatic Programmer | 🔁 重叠 | 通用工程指导重叠 |
| Release It + 其他 | ✅ 全部互补 | 运维层面不干扰 |

## 审计扫描规则

### 可自动检测的（60%）

| 检测项 | 方法 | 规范来源 |
|--------|------|---------|
| 超长函数 (>30 行) | 解析函数定义，统计行数 | clean-code |
| 超长参数列表 (>3 个) | 解析函数签名 | clean-code |
| 深层嵌套 (>3 层) | 缩进/AST 分析 | clean-code |
| 布尔标志参数 | 模式匹配 `func(x, true/false)` | clean-code |
| 大文件 (>300 行) | `wc -l` | clean-code, refactoring-guru |
| 模糊命名 | 单字母函数名、tmp/data/info 等 | clean-code |
| 依赖方向错误 | 分析各层 import 语句 | clean-architecture |
| 框架泄漏 | grep 业务层中的框架引用 | clean-architecture |
| 无超时外调 | grep 网络调用，检查 timeout | release-it |
| N+1 查询 | 循环内数据库调用 | PoEAA |
| 无测试覆盖 | 检查 test 目录存在性 | WELC |

### 需人工判断的（40%）

| 判断项 | 规范来源 | 处理方式 |
|--------|---------|---------|
| 模块深度是否足够 | APoSD | 展示模块 API/实现比，引导用户判断 |
| 统一语言一致性 | DDD | 扫描变量名与业务术语匹配度 |
| 聚合边界合理性 | IDDD | 展示候选边界，引导用户判断 |
| 业务模式选择 | PoEAA | 展示代码特征，建议匹配的模式 |

## 审计报告格式

输出到 `docs/pd-rule-check.md`，结构:

```markdown
# 代码规范审计报告

> 生成时间: YYYY-MM-DD
> 项目: /path/to/project
> 使用规范: xxx.mini, yyy.mini

## 一、项目概况
## 二、适用性分析
## 三、审计结果
  ### 🔴 严重问题
  ### 🟡 警告
  ### 🟢 建议
## 四、规范覆盖率统计
## 五、优先级建议
  ### 立即修复
  ### 短期改进
  ### 长期规划
```

每条发现必须包含:
- 规范来源 (具体到规则编号)
- 文件路径 + 行号
- 问题描述
- 影响分析
- 修复建议（含示例代码）

## References

所有规范原始文件位于 `references/` 目录:

```
references/
├── COMPATIBILITY.md                    # 兼容性矩阵
├── clean-code/
│   ├── clean-code.md                   # full 版
│   ├── clean-code.mini.md              # mini 版 (审计用)
│   └── clean-code.nano.md              # nano 版
├── clean-architecture/
├── a-philosophy-of-software-design/
├── code-complete/
├── domain-driven-design/
├── domain-driven-design-distilled/
├── implementing-domain-driven-design/
├── patterns-of-enterprise-application-architecture/
├── refactoring/
├── refactoring-guru/
├── release-it/
├── designing-data-intensive-applications/
├── the-pragmatic-programmer/
└── working-effectively-with-legacy-code/
```

审计时优先使用 `.mini.md` 版本。`.md` (full) 用于深度参考。`.nano.md` 用于快速提醒。

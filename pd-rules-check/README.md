# Agent Rules Books

> 从经典软件工程书籍中提炼的 AI 编码代理规则与技能包

将经典编程书籍的核心原则转化为 AI 编码代理（Codex、Cursor、Claude Code、GitHub Copilot）可以直接理解和执行的 Markdown 规则文件，让 AI 写代码时遵循经过验证的最佳实践。

## 功能概述

本项目提供 **15 套规则集**，分别源自 14 本经典软件工程书籍和 1 个实践网站。每套规则集包含三种粒度版本，适配不同的上下文预算：

| 版本 | 定位 | 适用场景 |
|------|------|----------|
| `mini`（推荐） | 精炼版，核心规则 | 大多数日常编码任务 |
| `nano` | 极简版，最紧凑 | 上下文极度受限时的兜底 |
| `full` | 完整参考版 | 需要全部细节时的权威来源 |

## 规则集清单

| 规则集 | 对应书籍/来源 | 作者 | mini 规则数 | 核心关注点 |
|--------|-------------|------|:---:|----------|
| A Philosophy of Software Design | [同名书籍](https://www.goodreads.com/book/show/39996759) | John Ousterhout | 28 | 降低复杂度、深模块、接口设计 |
| Clean Architecture | [同名书籍](https://www.goodreads.com/book/show/18043011) | Robert C. Martin | 31 | 依赖倒置、边界划分、抗技术变更 |
| Clean Code | [同名书籍](https://www.goodreads.com/book/show/3735293-clean-code) | Robert C. Martin | 29 | 命名、小函数、单一职责、测试 |
| Code Complete | [同名书籍](https://www.goodreads.com/book/show/4845.Code_Complete) | Steve McConnell | 38 | 软件构造全领域实践 |
| Designing Data-Intensive Applications | [同名书籍](https://www.goodreads.com/book/show/23463279) | Martin Kleppmann | 37 | 可靠性、扩展性、一致性、事件流 |
| Domain-Driven Design | [同名书籍](https://www.goodreads.com/en/book/show/179133) | Eric Evans | 30 | 领域模型、限界上下文、通用语言 |
| Domain-Driven Design Distilled | [同名书籍](https://www.goodreads.com/book/show/28602719) | Vaughn Vernon | 38 | DDD 轻量入门、子域、上下文映射 |
| Implementing Domain-Driven Design | [同名书籍](https://www.goodreads.com/book/show/18396266) | Vaughn Vernon | 39 | DDD 落地实践、聚合、领域事件 |
| Patterns of Enterprise Application Architecture | [同名书籍](https://www.goodreads.com/en/book/show/70156) | Martin Fowler | 36 | 分层、Repository、UoW、DTO |
| Refactoring | [同名书籍](https://www.goodreads.com/book/show/44936.Refactoring) | Martin Fowler | 31 | 安全重构、代码味道、测试先行 |
| Refactoring.Guru | [同名网站](https://refactoring.guru/refactoring) | Refactoring.Guru | 46 | 代码味道诊断、重构手法目录 |
| Release It! | [同名书籍](https://www.goodreads.com/en/book/show/1069827) | Michael T. Nygard | 30 | 断路器、限流、超时、可观测性 |
| The Pragmatic Programmer | [同名书籍](https://www.goodreads.com/book/show/50701156) | Andrew Hunt & David Thomas | 47 | DRY、正交性、自动化、反馈 |
| Working Effectively with Legacy Code | [同名书籍](https://www.goodreads.com/book/show/44919) | Michael Feathers | 32 | 遗产代码、特征测试、接缝 |

## 用法

### 方式一：项目级规则（始终启用）

将选定的规则集内容合并到项目根目录的 `CLAUDE.md` / `AGENTS.md` / `.cursorrules` 文件中，使 AI 代理在该项目中始终遵循这些规则。

**Claude Code 示例：**
```bash
# 将 mini 规则追加到 CLAUDE.md
cat agent-rules-books/clean-code/clean-code.mini.md >> CLAUDE.md
```

### 方式二：按需技能（条件触发）

将某个 `mini` 规则集注册为 Claude Code Skill 或 Cursor Custom Command，仅在特定场景下加载。

**Claude Code Skill 示例：**
```
.skills/clean-code/
  SKILL.md          ← 技能描述和触发条件
  clean-code.mini.md ← 规则内容
```

### 方式三：多规则集组合

根据项目阶段组合不同规则集。详见 [docs/COMPATIBILITY.md](https://github.com/ciembor/agent-rules-books/blob/main/docs/COMPATIBILITY.md)。

**推荐组合：**
- 日常开发：`Clean Code` + `The Pragmatic Programmer`
- 新项目架构：`Clean Architecture` + `DDD`
- 微服务/后端：`DDIA` + `Release It!`
- 遗产代码改造：`Working Effectively with Legacy Code` + `Refactoring`

### 各编辑器配置指南

详细的编辑器配置（Codex、Claude Code、Cursor、GitHub Copilot）参见 [docs/USAGE.md](https://github.com/ciembor/agent-rules-books/blob/main/docs/USAGE.md)。

## 资料来源

所有规则均从以下书籍/网站的核心内容中手工提炼：

| 书籍 | 作者 | 出版方 |
|------|------|--------|
| A Philosophy of Software Design | John Ousterhout | Stanford |
| Clean Code | Robert C. Martin | Prentice Hall |
| Clean Architecture | Robert C. Martin | Prentice Hall |
| Code Complete | Steve McConnell | Microsoft Press |
| Designing Data-Intensive Applications | Martin Kleppmann | O'Reilly |
| Domain-Driven Design | Eric Evans | Addison-Wesley |
| Domain-Driven Design Distilled | Vaughn Vernon | Addison-Wesley |
| Implementing Domain-Driven Design | Vaughn Vernon | Addison-Wesley |
| Patterns of Enterprise Application Architecture | Martin Fowler | Addison-Wesley |
| Refactoring | Martin Fowler | Addison-Wesley |
| Refactoring.Guru | Refactoring.Guru | 网站 |
| Release It! | Michael T. Nygard | Pragmatic Bookshelf |
| The Pragmatic Programmer | Andrew Hunt & David Thomas | Pragmatic Bookshelf |
| Working Effectively with Legacy Code | Michael Feathers | Prentice Hall |

> **注意：** 这些规则是受书籍启发的工程实践指令，**不是**原著的替代品，也不是书籍内容的摘要或学习笔记。它们是面向 AI 编码工具的**轻量工作约定**，应视为书籍阅读后的实践补充。

## 许可

MIT License

## 作者

[Maciej Ciemborowicz](https://maciej-ciemborowicz.eu)

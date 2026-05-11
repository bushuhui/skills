---
name: pd_doc
description: 基于文档索引的迭代开发 — 项目文档自动管理与增量更新。Use when starting a new project needing docs/, updating existing project documentation, or after code changes to incrementally update docs/architecture.md, docs/api.md, docs/changelog.md.
trigger: /pd_doc
---

# /pd_doc

基于文档索引的迭代开发工作流：自动管理项目文档，新建项目创建文档骨架，已有项目增量更新。

## 核心原则

- **基于实际代码分析，不猜测** — 无法确定的部分注明"待进一步分析"
- **利用对话上下文** — 已知刚才做了什么改动，不需重新分析代码
- **先验证再记录** — 运行确认没问题后再写文档，不记录半成品
- **大模块才独立文档** — 不为每次小改动新建 MD

## 文档目录约定

```
docs/
├── architecture.md         # 项目架构总览（长期维护）
├── api.md                  # 接口定义汇总（长期维护）
├── changelog.md            # 改动日志（持续追加）
└── modules/[module-name].md   # 大模块说明（按需新增）
```

## 工作流

### 模式 A：新项目初始化（docs/ 不存在）

1. 创建 `docs/` 目录
2. 生成 `docs/architecture.md`，包含：
   - 技术栈与核心依赖
   - 目录结构（树状图，标注核心/配置/资源目录）
   - 模块划分及各模块职责
   - 模块间的依赖关系和数据流向
3. 生成 `docs/api.md`，包含：
   - 所有 API 端点（路径、方法、参数、返回值）
   - 路由定义位置
   - 前后端交互方式
4. 生成 `docs/changelog.md`，包含空模板：
   ```markdown
   # Changelog

   ## 格式说明
   每次改动按以下格式追加到文件顶部：

   ## YYYY-MM-DD — 改动摘要
   - **范围**：涉及的模块
   - **修改**：file_a.ts, file_b.py
   - **接口变更**：如有则列出
   - **备注**：破坏性变更、待办事项等
   ```

### 模式 B：已有项目增量更新（docs/ 已存在）

1. 读取 `docs/changelog.md`，获取最近改动记录
2. 读取现有项目文件，对比上次文档生成后的变更
3. 增量更新 `docs/architecture.md`（如有架构变化）
4. 增量更新 `docs/api.md`（如有接口变化）
5. 追加变更记录到 `docs/changelog.md` 顶部：
   ```markdown
   ## YYYY-MM-DD — 改动摘要
   - **范围**：涉及的模块
   - **修改**：具体文件列表
   - **接口变更**：如有则列出
   - **备注**：破坏性变更、待办事项等
   ```

### 模式 C：大模块新增独立文档

适用于新增功能模块、重构大组件等较大变动。

1. 在 `docs/modules/` 下新建 `[module-name].md`，包含：
   - 模块职责和设计思路
   - 核心文件清单
   - 对外暴露的接口/函数/类
   - 与其他模块的依赖关系
   - 使用示例（如适用）
2. 更新 `docs/architecture.md` 的模块划分章节
3. 在 `docs/changelog.md` 中追加一条大模块变动记录

## 最佳实践

1. **初始分析只做一次** — architecture.md 和 api.md 是基准，后续只增量更新
2. **每次提交前更新 changelog** — 保证改动记录不遗漏
3. **大模块才独立文档** — 不要为每次小改动新建 MD
4. **新任务必带文档路径** — 避免 AI 盲目分析浪费时间
5. **定期清理过时文档** — 重构后删除或更新旧文档

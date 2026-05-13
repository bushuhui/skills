---
name: pd-simplify
description: Simplifies and refines recently modified code for clarity, consistency, and maintainability while preserving exact functionality. Use when code has just been written or modified, when user asks to clean up, refine, or simplify code, or when reviewing for code quality issues.
---

# pd-simplify — 代码精炼

对最近修改的代码进行精炼，提升可读性、一致性和可维护性，**不改变任何功能行为**。

## 使用方式

```
/pd-simplify              # 精炼最近修改的代码
/pd-simplify --file path  # 精炼指定文件
```

如果未指定范围，通过 `git diff` 确定最近修改的代码范围。

## 精炼原则

### 1. 功能不变

**这是硬性约束。** 所有原始功能、输出和行为必须保持完整。只改"怎么做"，不改"做什么"。

### 2. 遵循项目规范

遵循项目 `CLAUDE.md` 中的编码规范，包括：import 排序、函数声明方式（function vs 箭头函数）、显式返回类型、React 组件模式、错误处理模式、命名约定等。若无规范文件，遵循代码既有风格。

### 3. 提升清晰度

- 减少不必要的复杂度和嵌套
- 消除冗余代码和重复逻辑
- 改进变量和函数命名
- 合并相关逻辑
- 删除描述显而易见代码的冗余注释
- **避免嵌套三元运算符** — 优先 switch 或 if/else
- **清晰优先于简短** — 显式代码优于过度紧凑的写法

### 4. 避免过度简化

- 不为"行数更少"牺牲可读性
- 不做过度聪明的"一行式"改写
- 不合并过多关注点到单一函数
- 不删除有助于代码组织的有用抽象
- 不破坏调试和扩展能力

## 精炼流程

1. 识别最近修改的代码范围（通过 git diff 或用户指定）
2. 分析优雅性和一致性改进机会
3. 应用项目最佳实践和编码标准
4. 确保所有功能保持不变
5. 确认精炼后的代码更简洁、更易维护
6. 仅对影响理解的重要变更做简要说明

## 作用域

**默认只作用于当前 session 中修改过的代码**，除非用户明确指定更大范围。

## 输出要求

直接输出精炼后的代码变更，附带简要说明。仅记录显著影响理解的重要变更，不对每个小改动逐一解释。

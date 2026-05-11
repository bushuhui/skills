---
name: clash-verge-control
description: 管理 Clash Verge 代理节点 — 查询节点/延迟、按国家自动切换至可达节点、查看当前状态。Use when 用户提到切换代理、查看节点、Clash 状态、"切到美国/us/jp节点"、"查看当前代理"、"哪些节点可用"、"clash代理切换到us"、"代理状态"、"切换到xx节点"。
---

# Clash Verge Control

通过内置 CLI 脚本管理 Clash Verge 代理，Clash API 默认运行在 `192.168.1.2:9098`。

## 快速使用

所有操作通过 `scripts/clash_ctl.py` 完成：

```bash
# 查看当前状态（Clash 版本 + 各代理组当前选中节点）
python3 scripts/clash_ctl.py status

# 列出所有可用节点及延迟
python3 scripts/clash_ctl.py nodes

# 列出代理组详情（加 -v 显示每个节点的延迟）
python3 scripts/clash_ctl.py list -v
```

## 工作流

### 切换代理

**手动切换（已知节点名称）**：
```bash
python3 scripts/clash_ctl.py switch GLOBAL "🇺🇸 US-NewYork-01"
```

**按国家自动切换（推荐）**：
```bash
# 自动筛选美国节点 → 逐个测试延迟 → 选最快的一个切换到 GLOBAL
python3 scripts/clash_ctl.py switch-country us

# 支持的国家代码: us, cn, jp, kr, hk, tw, sg, uk, de, ru
# 也可传自定义关键词，如 "Europe"
python3 scripts/clash_ctl.py switch-country jp --group SSRDOG
```

### 测试延迟

```bash
# 测试单个节点
python3 scripts/clash_ctl.py test "🇭🇰 Hong Kong丨01"

# 测试整个代理组
python3 scripts/clash_ctl.py test-group GLOBAL
```

## 故障排查

| 错误 | 解决 |
|------|------|
| 连接失败 | 确认 Clash Verge 正在运行，外部控制地址为 `192.168.1.2:9098` |
| 代理组不存在 | 用 `list -v` 查看实际代理组名称 |
| 节点匹配不到 | 节点名可能不含国家关键词，传自定义字符串 |

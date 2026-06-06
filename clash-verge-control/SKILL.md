---
name: clash-verge-control
description: 管理 Clash Verge 代理节点 — 查询节点/延迟、按国家自动切换至可达节点、查看当前状态。Use when 用户提到切换代理、查看节点、Clash 状态、"切到美国/us/jp节点"、"查看当前代理"、"哪些节点可用"、"clash代理切换到us"、"代理状态"、"切换到xx节点"。
---

# Clash Verge Control

通过内置 CLI 脚本管理 Clash Verge 代理，Clash API 默认运行在 `192.168.1.15:9098`。

## 快速使用

所有操作通过 `scripts/clash_ctl.py` 完成：

```bash
# ⚠️ 注意：--api 是全局参数，必须放在子命令之前，不能放在后面！
# 正确：python3 scripts/clash_ctl.py --api http://192.168.1.15:9098 status
# 错误：python3 scripts/clash_ctl.py status --api http://192.168.1.15:9098  （会报 unrecognized arguments）

# 查看当前状态（Clash 版本 + 各代理组当前选中节点）
python3 scripts/clash_ctl.py --api http://192.168.1.15:9098 status

# 列出所有可用节点及延迟
python3 scripts/clash_ctl.py --api http://192.168.1.15:9098 nodes

# 列出代理组详情（加 -v 显示每个节点的延迟）
python3 scripts/clash_ctl.py --api http://192.168.1.15:9098 list -v
```

## 环境信息

- **Clash API 地址**：`http://192.168.1.15:9098`（局域网，Clash Verge 运行在192.168.1.15 上）
- **当前版本**：v1.18.7
- **主要代理组**：SSRDOG（Selector）、GLOBAL（Selector）、Auto（Fallback）
- **流量信息**：83.5 GB / 300 GB（重置倒计时约 3 天，到期 2027-03-25）

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
| 连接失败 | 确认 Clash Verge 正在运行，外部控制地址为 `192.168.1.15:9098` |
| `unrecognized arguments: --api` | `--api` 是全局参数，必须放在子命令**之前**：`python3 clash_ctl.py --api http://... status` |
| 代理组不存在 | 用 `list -v` 查看实际代理组名称 |
| 节点匹配不到 | 节点名可能不含国家关键词，传自定义字符串 |
| GLOBAL 当前是 DIRECT | 默认配置下 GLOBAL 组指向 DIRECT（直连），不走代理。需要通过 SSRDOG/Auto 组或手动切换 GLOBAL 才能走代理 |

## 代理组结构

```
SSRDOG (Selector) ── 手动切换订阅节点组
  ├── Auto (Fallback) ── 按国家聚合的 Fallback 组（当前选 🇭🇰 Hong Kong 319ms）
  │     ├── 🇭🇰 Hong Kong (Selector) ── 15 个 HK 节点
  │     ├── 🇯🇵 Japan (Selector) ── 10 个 JP 节点
  │     └── ...（每国一个 Selector）
  └── 各区域独立节点
GLOBAL (Selector) ── 默认 DIRECT（直连），需手动切换才走代理
```

## 参考文件

- `references/node-baseline.md` — 节点性能基线（含问题节点清单、各区域最佳节点、套餐信息）

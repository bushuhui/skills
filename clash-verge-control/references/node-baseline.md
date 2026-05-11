# Clash Verge 节点性能基线（2026-05-11）

用于后续会话对比节点速度变化、识别劣化节点。

## 各区域最佳节点（按延迟排序）

| 区域 | 最佳节点 | 延迟 | 次优 | 备注 |
|------|----------|------|------|------|
| 🇭🇰 香港 | HK丨11 | 35ms | HK丨05/09 (36/37ms) | 15 个节点，整体稳定在 35-42ms |
| 🇯🇵 日本 | JP丨04 | 81ms | JP丨01/03 (83-84ms) | JP丨02/09/10 延迟破 800ms，疑似问题节点 |
| 🇰🇷 韩国 | KR丨01 | 105ms | - | 仅 1 个节点 |
| 🇸🇬 新加坡 | SG丨07 | 55ms | SG丨06/09 (76ms) | SG丨08 timeout |
| 🇺🇸 美国 | US丨09 | 183ms | US丨08/10 (188ms) | US丨02 (1164ms)、US丨03 (timeout) 问题节点 |
| 🇨🇳 台湾 | TW丨03 | 53ms | TW丨05/06 (50-54ms) | TW丨02 (1061ms) 问题节点 |
| 🇨🇦 加拿大 | CA丨01 | 242ms | - | 仅 1 个节点 |
| 🇹🇷 土耳其 | TR丨01 | 241ms | - | 仅 1 个节点 |

## 已知问题节点（延迟 > 800ms 或 timeout）

| 节点 | 延迟 | 状态 |
|------|------|------|
| 🇸🇬 Singapore丨08 | timeout | 不可达 |
| 🇮🇳 India丨01 | timeout | 不可达 |
| 🇺🇸 United States丨03 | timeout | 不可达 |
| 🇨🇳 Taiwan丨02 | 1061ms | 极慢 |
| 🇯🇵 Japan丨02 | 1044ms | 极慢 |
| 🇯🇵 Japan丨09 | 828ms | 极慢 |
| 🇯🇵 Japan丨10 | 844ms | 极慢 |
| 🇺🇸 United States丨02 | 1164ms | 极慢 |
| 🇬🇧 Great Britain丨01 | 1244ms | 极慢 |
| 🇩🇪 Germany \| 01 | 1238ms | 极慢 |
| 🇳🇱 Netherlands丨01 | 1253ms | 极慢 |

## Auto (Fallback) 组状态

当前选中：`🇭🇰 Hong Kong` (319ms)

但 Fallback 组内各区域代表节点的实际延迟：
- 🇯🇵 Japan: 44ms
- 🇨🇳 Taiwan: 46ms
- 🇬🇧 Great Britain: 46ms
- 🇩🇪 Germany: 47ms
- 🇻🇳 Vietnam: 48ms
- 🇹🇭 Thailand: 48ms
- 🇰🇷 Korea: 49ms
- 🇲🇾 Malaysia: 49ms
- 🇹🇷 Turkey: 44ms
- 🇳🇱 Netherlands: 44ms

**观察**：Auto Fallback 组选了 Hong Kong (319ms) 而非更快的 Japan (44ms) 或 Taiwan (46ms)，说明 Fallback 的排序逻辑可能不基于延迟，或最近一次探测时香港是唯一可用的。

## 套餐信息

- 已用流量：83.5 GB / 300 GB
- 流量重置倒计时：约 3 天
- 到期时间：2027-03-25

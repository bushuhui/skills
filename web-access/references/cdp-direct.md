# CDP 直连模式

> **注意**：现在默认使用 `scripts/cdp-cli.mjs` CLI 工具，无需手写 WebSocket 连接。
> 本文件保留作为底层原理参考。

## 适用场景

默认通过 `scripts/cdp-cli.mjs` 直连 Chrome 的 CDP 端口 9222，使用 Node.js 内置 WebSocket。

## 前置条件

- Chrome 已开启远程调试（端口 9222）
- Node.js 22+（内置原生 WebSocket，无需 `ws` 模块）

## CLI 使用方式

```bash
SCRIPT="${CLAUDE_SKILL_DIR}/scripts/cdp-cli.mjs"

node "$SCRIPT" list                              # 列出所有 tab
node "$SCRIPT" new "https://example.com"          # 创建新 tab
node "$SCRIPT" eval <targetId> "document.title"   # 执行 JS
node "$SCRIPT" scroll <targetId> --direction bottom
node "$SCRIPT" screenshot <targetId> --file /tmp/shot.png
node "$SCRIPT" click <targetId> "button.submit"
node "$SCRIPT" close <targetId>
```

## REST API 底层调用

```bash
# 1. 获取所有已打开的 tab
curl -s http://localhost:9222/json/list

# 2. 创建新 tab（PUT 方法）
curl -X PUT "http://localhost:9222/json/new?https://example.com"

# 3. 关闭 tab（GET 方法）
curl -s "http://localhost:9222/json/close/TARGET_ID"
```

## CDP 原生方法

| 方法 | 用途 |
|------|------|
| `Runtime.evaluate` | 执行 JS，提取 DOM 内容 |
| `Page.navigate` | 页面导航 |
| `Page.captureScreenshot` | 截图 |
| `Input.dispatchMouseEvent` | 真实鼠标事件 |
| `DOM.getDocument` | 获取 DOM 树 |
| `Network.getResponseBody` | 获取网络响应体 |

## ⚠️ 注意事项

1. `json/new` 必须用 **PUT** 方法，GET 会返回 405
2. `json/close` 返回 `"Target is closing"` 字符串（非 JSON）
3. 直连模式没有自动等待机制，需要手动 `setTimeout` 等待页面加载
4. 任务完成后记得关闭 tab，保持环境整洁

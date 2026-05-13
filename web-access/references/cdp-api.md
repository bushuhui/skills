# CDP 操作指南

## 两种模式对比

| 维度 | **CLI 直连** (`cdp-cli.mjs`) | **Proxy** (`cdp-proxy.mjs`) |
|------|---|---|
| **默认推荐** | ✅ 是 | 复杂交互场景 |
| **端口** | 9222 | 3456（可配） |
| **形态** | 一次性 CLI（跑完退出） | 常驻 HTTP 服务 |
| **自动等待** | ❌ 需手动 sleep 2-3s | ✅ `waitForLoad()` |
| **Tab 管理** | 手动 `close` | 自动清理闲置 tab |
| **反风控** | ❌ | ✅ 拦截调试端口探测 |
| **真实鼠标点击** | ❌ 只有 JS click | ✅ `clickAt` (Input.dispatchMouseEvent) |
| **文件上传** | ❌ | ✅ `setFiles` |

**使用建议**：简单操作（查 title、截图、单次 eval）用 CLI 直连；需要导航+等待+点击的串行交互、或需要真实鼠标手势时用 Proxy。

---

## CLI 直连 (cdp-cli.mjs)

```bash
SCRIPT="/home/bushuhui/.agents/skills/web-access/scripts/cdp-cli.mjs"

# 列出所有 tab
node "$SCRIPT" list

# 创建新 tab
node "$SCRIPT" new "https://example.com"
# 返回: {"targetId":"xxx","url":"..."}

# 执行 JS
node "$SCRIPT" eval <targetId> "document.title"

# 滚动
node "$SCRIPT" scroll <targetId> --direction bottom
node "$SCRIPT" scroll <targetId> --y 3000

# 截图
node "$SCRIPT" screenshot <targetId> --file /tmp/shot.png

# 导航
node "$SCRIPT" navigate <targetId> "https://example.com"

# 后退
node "$SCRIPT" back <targetId>

# 点击（JS el.click()）
node "$SCRIPT" click <targetId> "button.submit"

# 关闭 tab
node "$SCRIPT" close <targetId>
```

**注意**：直连模式没有自动等待，页面加载后需要手动 `sleep 2-3` 秒再操作。

### 提取正文推荐模式（TreeWalker）

```js
const article = document.querySelector("article.syl-article-base, .article-content, div.main");
const walker = document.createTreeWalker(article, NodeFilter.SHOW_TEXT);
let node;
const paragraphs = [];
while (node = walker.nextNode()) {
  const t = node.textContent.trim();
  if (t.length > 5 && /* 过滤导航/按钮等噪音 */) {
    paragraphs.push(t);
  }
}
```

TreeWalker 直接拿纯文本节点，避免 `div.innerText` 包含所有子元素文本的污染。

---

## Proxy 模式 (cdp-proxy.mjs)

**启动**：
```bash
node "/home/bushuhui/.agents/skills/web-access/scripts/cdp-proxy.mjs" &
# 或通过 check-deps.mjs 自动启动
node "/home/bushuhui/.agents/skills/web-access/scripts/check-deps.mjs"
```

**停止**：`pkill -f cdp-proxy.mjs`

### HTTP API（端口 3456）

```bash
# 健康检查
curl -s http://localhost:3456/health

# 列出 tab
curl -s http://localhost:3456/targets

# 创建 tab（自动等待加载）
curl -s "http://localhost:3456/new?url=https://example.com"

# 导航（自动等待加载）
curl -s "http://localhost:3456/navigate?target=ID&url=https://example.com"

# 执行 JS
curl -s -X POST "http://localhost:3456/eval?target=ID" -d 'document.title'

# 点击（JS 层面）
curl -s -X POST "http://localhost:3456/click?target=ID" -d 'button.submit'

# 真实鼠标点击（能触发文件对话框、绕过反自动化）
curl -s -X POST "http://localhost:3456/clickAt?target=ID" -d 'button.upload'

# 设置文件上传
curl -s -X POST "http://localhost:3456/setFiles?target=ID" -d '{"selector":"input[type=file]","files":["/path/to/file.png"]}'

# 滚动（自动等待 800ms 懒加载）
curl -s "http://localhost:3456/scroll?target=ID&direction=bottom"

# 截图
curl -s "http://localhost:3456/screenshot?target=ID&file=/tmp/shot.png"

# 关闭 tab
curl -s "http://localhost:3456/close?target=ID"
```

### Proxy 独有功能

- **`waitForLoad()`**：导航/新建 tab 后自动等待 `document.readyState === 'complete'`
- **`clickAt`**：真实鼠标点击，非 JS `el.click()`
- **`setFiles`**：绕过文件对话框直接设置本地文件
- **自动清理**：15 分钟闲置 tab 自动关闭，退出时清理所有自建 tab
- **反风控**：拦截页面对 `127.0.0.1:9222` 的调试端口探测

---

## CDP 加载失败兜底：Jina Reader

当 Chrome 打开页面后 URL 变为 `chrome-error://chromewebdata/`（网络/反爬/文章已删除），CDP 无法提取内容。改用 Jina Reader：

```bash
curl -s "https://r.jina.ai/<URL>"
```

- URL 前加 `r.jina.ai/`，不保留 `http` 前缀
- 限 20 RPM
- 返回 Markdown 格式（标题 + 发布时间 + 正文）
- **已知可用**：今日头条（`m.toutiao.com`）、微信公众号、一般新闻站点
- 不适合：数据面板、商品页等非文章结构页面

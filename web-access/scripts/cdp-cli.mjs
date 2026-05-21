#!/usr/bin/env node
/**
 * CDP 直连 CLI — 通过 WebSocket 直接操作 Chrome DevTools Protocol (端口 9222)
 * 
 * 替代原有的 CDP Proxy 模式，无需额外依赖（Node.js 22+ 内置 WebSocket）。
 * 
 * 用法：
 *   node cdp-cli.mjs list                                          # 列出所有 tab
 *   node cdp-cli.mjs new "https://example.com"                     # 创建新 tab
 *   node cdp-cli.mjs eval <targetId> "document.title"              # 执行 JS
 *   node cdp-cli.mjs scroll <targetId> --direction bottom          # 滚动
 *   node cdp-cli.mjs screenshot <targetId> --file /tmp/shot.png    # 截图
 *   node cdp-cli.mjs navigate <targetId> "https://example.com"     # 导航
 *   node cdp-cli.mjs click <targetId> "button.submit"              # 点击元素
 *   node cdp-cli.mjs close <targetId>                              # 关闭 tab
 *   node cdp-cli.mjs back <targetId>                               # 后退
 */

const CDP_HOST = "localhost";
const CDP_PORT = 9222;
const BASE = `http://${CDP_HOST}:${CDP_PORT}`;

// ─── 参数解析 ───

function parseArgs(argv) {
  const args = { cmd: argv[2], positional: [], opts: {} };
  for (let i = 3; i < argv.length; i++) {
    if (argv[i].startsWith("--")) {
      const key = argv[i].slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith("--")) {
        args.opts[key] = next;
        i++;
      } else {
        args.opts[key] = true;
      }
    } else {
      args.positional.push(argv[i]);
    }
  }
  return args;
}

// ─── HTTP 辅助（创建/关闭 tab 用 REST API） ───

async function httpGet(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  const text = await res.text();
  try { return JSON.parse(text); } catch { return text; }
}

async function httpPut(path) {
  const res = await fetch(`${BASE}${path}`, { method: "PUT" });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  return res.json();
}

// ─── WebSocket CDP 连接 ───

class CDPConnection {
  constructor(targetId) {
    this.targetId = targetId;
    this.ws = new WebSocket(`ws://${CDP_HOST}:${CDP_PORT}/devtools/page/${targetId}`);
    this.pending = new Map();
    this.cmdId = 1;
    this._ready = new Promise((resolve, reject) => {
      this.ws.addEventListener("open", () => resolve());
      this.ws.addEventListener("error", (e) => reject(new Error(`WS connect failed: ${e.message}`)));
    });
    this.ws.addEventListener("message", (event) => {
      const resp = JSON.parse(event.data);
      if (resp.id && this.pending.has(resp.id)) {
        const { resolve, reject } = this.pending.get(resp.id);
        this.pending.delete(resp.id);
        if (resp.error) reject(new Error(JSON.stringify(resp.error)));
        else resolve(resp);
      }
    });
  }

  async ready() { await this._ready; }

  async send(method, params = {}) {
    await this.ready();
    return new Promise((resolve, reject) => {
      const id = this.cmdId++;
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async eval(expression, opts = {}) {
    const result = await this.send("Runtime.evaluate", {
      expression,
      returnByValue: true,
      awaitPromise: true,
      ...opts,
    });
    const r = result.result?.result;
    if (!r) return undefined;
    if (r.type === "string") return r.value;
    if (r.type === "number" || r.type === "boolean") return r.value;
    if (r.type === "undefined") return undefined;
    if (r.type === "object" && r.subtype === "null") return null;
    return r.value;
  }

  close() {
    this.ws.close();
  }
}

// ─── 命令实现 ───

async function cmdList() {
  const tabs = await httpGet("/json/list");
  console.log(JSON.stringify(tabs.map(t => ({
    id: t.id,
    title: t.title,
    url: t.url?.substring(0, 120),
    type: t.type,
  })), null, 2));
}

async function cmdNew(url) {
  if (!url) { console.error("用法: cdp-cli.mjs new <URL>"); process.exit(1); }
  const tab = await httpPut(`/json/new?${encodeURIComponent(url)}`);
  console.log(JSON.stringify({ targetId: tab.id, url: tab.url }));
}

async function cmdClose(targetId) {
  if (!targetId) { console.error("用法: cdp-cli.mjs close <targetId>"); process.exit(1); }
  const result = await httpGet(`/json/close/${targetId}`);
  console.log(JSON.stringify({ success: true, message: typeof result === "string" ? result : result }));
}

async function cmdEval(targetId, expression) {
  if (!targetId || !expression) { console.error("用法: cdp-cli.mjs eval <targetId> <expression>"); process.exit(1); }
  const conn = new CDPConnection(targetId);
  try {
    const result = await conn.eval(expression);
    console.log(typeof result === "string" ? result : JSON.stringify(result));
  } finally {
    conn.close();
  }
}

async function cmdScroll(targetId, opts) {
  if (!targetId) { console.error("用法: cdp-cli.mjs scroll <targetId> [--direction bottom|top] [--y N]"); process.exit(1); }
  const conn = new CDPConnection(targetId);
  try {
    if (opts.direction === "bottom") {
      await conn.eval("window.scrollTo(0, document.body.scrollHeight);");
    } else if (opts.direction === "top") {
      await conn.eval("window.scrollTo(0, 0);");
    } else if (opts.y) {
      await conn.eval(`window.scrollTo(0, ${opts.y});`);
    } else {
      await conn.eval("window.scrollTo(0, document.body.scrollHeight);");
    }
    console.log(JSON.stringify({ success: true, scrolled: opts.direction || `y=${opts.y || "bottom"}` }));
  } finally {
    conn.close();
  }
}

async function cmdNavigate(targetId, url) {
  if (!targetId || !url) { console.error("用法: cdp-cli.mjs navigate <targetId> <URL>"); process.exit(1); }
  const conn = new CDPConnection(targetId);
  try {
    await conn.send("Page.navigate", { url });
    console.log(JSON.stringify({ success: true, url }));
  } finally {
    conn.close();
  }
}

async function cmdBack(targetId) {
  if (!targetId) { console.error("用法: cdp-cli.mjs back <targetId>"); process.exit(1); }
  const conn = new CDPConnection(targetId);
  try {
    await conn.send("Page.navigate", { historyDelta: -1 });
    console.log(JSON.stringify({ success: true }));
  } finally {
    conn.close();
  }
}

async function cmdClick(targetId, selector) {
  if (!targetId || !selector) { console.error("用法: cdp-cli.mjs click <targetId> <css-selector>"); process.exit(1); }
  const conn = new CDPConnection(targetId);
  try {
    const result = await conn.eval(`
      (() => {
        const el = document.querySelector("${selector.replace(/"/g, '\\"')}");
        if (!el) return JSON.stringify({ error: "Element not found: ${selector}" });
        el.click();
        return JSON.stringify({ success: true });
      })()
    `);
    console.log(result);
  } finally {
    conn.close();
  }
}

async function cmdScreenshot(targetId, opts) {
  if (!targetId) { console.error("用法: cdp-cli.mjs screenshot <targetId> [--file /path/to/output.png]"); process.exit(1); }
  const file = opts.file || "/tmp/cdp_screenshot.png";
  const conn = new CDPConnection(targetId);
  try {
    // 等待页面加载完成
    await conn.send("Page.enable");
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const result = await conn.send("Page.captureScreenshot", { format: "png" });
    const data = result.result?.data;
    if (!data) { console.error("Screenshot failed: no data in response"); process.exit(1); }
    const fs = await import("fs");
    fs.writeFileSync(file, Buffer.from(data, "base64"));
    console.log(JSON.stringify({ success: true, file }));
  } finally {
    conn.close();
  }
}

// ─── 主入口 ───

const { cmd, positional, opts } = parseArgs(process.argv);

const commands = {
  list: cmdList,
  new: () => cmdNew(positional[0]),
  close: () => cmdClose(positional[0]),
  eval: () => cmdEval(positional[0], positional.slice(1).join(" ")),
  scroll: () => cmdScroll(positional[0], opts),
  navigate: () => cmdNavigate(positional[0], positional[1]),
  back: () => cmdBack(positional[0]),
  click: () => cmdClick(positional[0], positional[1]),
  screenshot: () => cmdScreenshot(positional[0], opts),
};

if (!cmd || !commands[cmd]) {
  console.log(`CDP 直连 CLI — Chrome DevTools Protocol 操作工具

用法: node cdp-cli.mjs <command> [args] [--options]

命令:
  list                              列出所有已打开的 tab
  new <URL>                         创建新 tab 并导航到 URL
  close <targetId>                  关闭指定 tab
  eval <targetId> <JS>              在页面中执行 JavaScript
  scroll <targetId> [--direction bottom|top] [--y N]  滚动页面
  navigate <targetId> <URL>         导航到指定 URL
  back <targetId>                   后退一页
  click <targetId> <selector>       点击 CSS 选择器对应的元素
  screenshot <targetId> [--file PATH]  截图并保存到文件

示例:
  node cdp-cli.mjs list
  node cdp-cli.mjs new "https://example.com"
  node cdp-cli.mjs eval TAB_ID "document.title"
  node cdp-cli.mjs scroll TAB_ID --direction bottom
  node cdp-cli.mjs screenshot TAB_ID --file /tmp/shot.png
  node cdp-cli.mjs click TAB_ID "button.submit"
  node cdp-cli.mjs close TAB_ID
`);
  process.exit(0);
}

commands[cmd]().catch(err => {
  console.error(`错误: ${err.message || err}`);
  process.exit(1);
});

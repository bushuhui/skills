#!/usr/bin/env node
/**
 * CDP 直连内容抓取脚本 — 一键抓取单页内容
 * 
 * 用法：node cdp-grab.js <URL> [--output /path/to/output.json]
 * 
 * 通过 Chrome DevTools Protocol 直连端口 9222，使用 Node.js 内置 WebSocket。
 * 适用于头条、公众号等动态渲染页面的内容抓取。
 * 
 * 注意：这是单页抓取的快捷脚本。需要页面交互（点击/导航/多步操作）时，
 * 应改用 cdp-cli.mjs（scripts/cdp-cli.mjs）。
 * 
 * 要求：Node.js 22+（内置 WebSocket）
 */

const url = process.argv[2];
if (!url) {
  console.error("用法: node cdp-grab.js <URL> [--output FILE]");
  process.exit(1);
}

const outputArg = process.argv.indexOf("--output");
const outputFile = outputArg > 0 ? process.argv[outputArg + 1] : null;

async function fetchTargets() {
  const res = await fetch("http://localhost:9222/json/list");
  return res.json();
}

async function createTab(targetUrl) {
  const res = await fetch(`http://localhost:9222/json/new?${encodeURIComponent(targetUrl)}`, {
    method: "PUT"
  });
  return res.json();
}

async function closeTab(targetId) {
  await fetch(`http://localhost:9222/json/close/${targetId}`);
}

async function connectAndExtract(targetId) {
  return new Promise((resolve, reject) => {
    const wsUrl = `ws://localhost:9222/devtools/page/${targetId}`;
    const ws = new WebSocket(wsUrl);
    let cmdId = 1;
    const pending = new Map();

    function sendCmd(method, params = {}) {
      return new Promise((res, rej) => {
        const id = cmdId++;
        pending.set(id, { resolve: res, reject: rej });
        ws.send(JSON.stringify({ id, method, params }));
      });
    }

    ws.addEventListener("message", (event) => {
      const resp = JSON.parse(event.data);
      if (resp.id && pending.has(resp.id)) {
        const { resolve } = pending.get(resp.id);
        pending.delete(resp.id);
        resolve(resp);
      }
    });

    ws.addEventListener("error", (err) => reject(err));

    ws.addEventListener("open", async () => {
      try {
        // 等待页面加载
        await new Promise(r => setTimeout(r, 3000));

        // 滚动触发懒加载
        await sendCmd("Runtime.evaluate", {
          expression: "window.scrollTo(0, document.body.scrollHeight);"
        });
        await new Promise(r => setTimeout(r, 1500));
        await sendCmd("Runtime.evaluate", {
          expression: "window.scrollTo(0, document.body.scrollHeight);"
        });
        await new Promise(r => setTimeout(r, 1500));

        // 提取内容 - 通用选择器策略
        const result = await sendCmd("Runtime.evaluate", {
          expression: `
          (() => {
            const title = document.querySelector("h1, h2, .title, .article-title, [class*=title] i")?.innerText?.trim() 
              || document.querySelector("title")?.innerText?.split("-")[0]?.trim() || "";
            const source = document.querySelector(".source, .author, [class*=author], [class*=source]")?.innerText?.trim() || "";
            const meta = document.querySelector("time, .time, .publish-time, [class*=time], [class*=date]")?.innerText?.trim() || "";
            
            const ps = Array.from(document.querySelectorAll("p, div"));
            const contentParts = ps.filter(p => {
              const t = p.innerText.trim();
              return t.length > 30 
                && !t.includes("举报") 
                && !t.includes("评论") 
                && !t.includes("回复") 
                && !t.includes("下载")
                && !t.includes("扫码")
                && !t.includes("打开");
            }).map(p => p.innerText.trim());
            
            const seen = new Set();
            const unique = contentParts.filter(p => {
              if (seen.has(p.substring(0, 50))) return false;
              seen.add(p.substring(0, 50));
              return true;
            });
            
            return JSON.stringify({
              title, source, meta,
              content: unique.join("\\n\\n").substring(0, 10000),
              contentLen: unique.join("\\n\\n").length
            });
          })()
          `,
          returnByValue: true
        });

        const value = result.result?.result?.value;
        const data = value ? JSON.parse(value) : { error: "NO CONTENT" };
        resolve(data);
        ws.close();
      } catch (err) {
        reject(err);
        ws.close();
      }
    });
  });
}

(async () => {
  try {
    console.log(`[1/4] 创建新 tab: ${url.substring(0, 80)}...`);
    const tab = await createTab(url);
    console.log(`[2/4] Tab 已创建: ${tab.id}`);

    console.log(`[3/4] 连接 CDP 并提取内容...`);
    const data = await connectAndExtract(tab.id);

    console.log(`[4/4] 关闭 tab`);
    await closeTab(tab.id);

    // 输出结果
    if (outputFile) {
      const fs = await import("fs");
      fs.writeFileSync(outputFile, JSON.stringify(data, null, 2));
      console.log(`\n结果已保存到: ${outputFile}`);
    } else {
      console.log("\n=== 抓取结果 ===");
      console.log(`标题: ${data.title}`);
      console.log(`来源: ${data.source}`);
      console.log(`时间: ${data.meta}`);
      console.log(`正文长度: ${data.contentLen} 字符`);
      console.log(`正文前 500 字:\n${data.content?.substring(0, 500)}`);
    }
  } catch (err) {
    console.error("抓取失败:", err.message || err);
    process.exit(1);
  }
})();

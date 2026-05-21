#!/usr/bin/env node
// 环境检查 + Chrome CDP 端口 9222 可用性检测
// 默认直连 Chrome 9222 端口；连不上自动运行 chrome-debug.sh 启动 Chrome

import { spawn } from 'node:child_process';
import fs from 'node:fs';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CDP_PORT = 9222;
const CHROME_DEBUG_SCRIPT = path.join(ROOT, 'scripts', 'chrome-debug.sh');

// --- Node.js 版本检查 ---

function checkNode() {
  const major = Number(process.versions.node.split('.')[0]);
  const version = `v${process.versions.node}`;
  if (major >= 22) {
    console.log(`node: ok (${version})`);
  } else {
    console.log(`node: warn (${version}, 建议升级到 22+)`);
  }
}

// --- TCP 端口探测 ---

function checkPort(port, host = '127.0.0.1', timeoutMs = 2000) {
  return new Promise((resolve) => {
    const socket = net.createConnection(port, host);
    const timer = setTimeout(() => { socket.destroy(); resolve(false); }, timeoutMs);
    socket.once('connect', () => { clearTimeout(timer); socket.destroy(); resolve(true); });
    socket.once('error', () => { clearTimeout(timer); resolve(false); });
  });
}

// --- Chrome 调试端口检测（DevToolsActivePort 多路径 + 常见端口回退） ---

function activePortFiles() {
  const home = os.homedir();
  const localAppData = process.env.LOCALAPPDATA || '';
  switch (os.platform()) {
    case 'darwin':
      return [
        path.join(home, 'Library/Application Support/Google/Chrome/DevToolsActivePort'),
        path.join(home, 'Library/Application Support/Chrome/DevToolsActivePort'),
        path.join(home, 'Library/Application Support/Chromium/DevToolsActivePort'),
      ];
    case 'linux':
      return [
        path.join(home, '.config/google-chrome/DevToolsActivePort'),
        path.join(home, '.config/chromium/DevToolsActivePort'),
      ];
    case 'win32':
      return [
        path.join(localAppData, 'Google/Chrome/User Data/DevToolsActivePort'),
        path.join(localAppData, 'Chromium/User Data/DevToolsActivePort'),
      ];
    default:
      return [];
  }
}

async function detectChromePort() {
  // 优先从 DevToolsActivePort 文件读取
  for (const filePath of activePortFiles()) {
    try {
      const lines = fs.readFileSync(filePath, 'utf8').trim().split(/\r?\n/).filter(Boolean);
      const port = parseInt(lines[0], 10);
      if (port > 0 && port < 65536 && await checkPort(port)) {
        return port;
      }
    } catch (_) {}
  }
  // 回退：探测常见端口
  for (const port of [9222, 9229, 9333]) {
    if (await checkPort(port)) {
      return port;
    }
  }
  return null;
}

// --- Chrome 启动（运行 chrome-debug.sh） ---

function launchChromeDebug() {
  return new Promise((resolve) => {
    if (!fs.existsSync(CHROME_DEBUG_SCRIPT)) {
      console.log(`❌ 找不到启动脚本: ${CHROME_DEBUG_SCRIPT}`);
      resolve(false);
      return;
    }

    console.log('chrome: 未检测到调试端口，正在启动 Chrome...');
    const child = spawn('bash', [CHROME_DEBUG_SCRIPT, String(CDP_PORT)], {
      stdio: ['ignore', 'pipe', 'pipe'],
      detached: false,
    });

    let stdout = '';
    child.stdout.on('data', (d) => { stdout += d.toString(); process.stdout.write(d); });
    child.stderr.on('data', (d) => { process.stderr.write(d); });

    child.on('close', (code) => {
      resolve(code === 0);
    });
  });
}

// --- 等待 Chrome 就绪 ---

async function waitForChrome(timeoutMs = 15000, intervalMs = 1000) {
  const start = Date.now();
  let attempts = 0;
  while (Date.now() - start < timeoutMs) {
    attempts++;
    if (await checkPort(CDP_PORT)) {
      // 验证 CDP 是否真正可用
      try {
        const res = await fetch(`http://127.0.0.1:${CDP_PORT}/json/version`, {
          signal: AbortSignal.timeout(3000),
        });
        if (res.ok) {
          return true;
        }
      } catch (_) {}
    }
    if (attempts === 1) {
      console.log('等待 Chrome 启动...');
    }
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  return false;
}

// --- main ---

async function main() {
  checkNode();

  // 第一步：尝试直连已有的 Chrome
  const chromePort = await detectChromePort();
  if (chromePort) {
    console.log(`chrome: ok (port ${chromePort})`);
  } else {
    // 第二步：连不上，自动启动 Chrome
    const launched = await launchChromeDebug();
    if (!launched) {
      console.log('❌ Chrome 启动失败');
      process.exit(1);
    }

    // 第三步：等待 Chrome 就绪
    const ready = await waitForChrome();
    if (!ready) {
      console.log(`❌ Chrome 未在 ${CDP_PORT} 端口就绪，请检查浏览器是否安装`);
      process.exit(1);
    }
    console.log(`chrome: ok (port ${CDP_PORT}, auto-started)`);
  }

  // 列出已有站点经验
  const patternsDir = path.join(ROOT, 'references', 'site-patterns');
  try {
    const sites = fs.readdirSync(patternsDir)
      .filter(f => f.endsWith('.md'))
      .map(f => f.replace(/\.md$/, ''));
    if (sites.length) {
      console.log(`\nsite-patterns: ${sites.join(', ')}`);
    }
  } catch {}
}

await main();

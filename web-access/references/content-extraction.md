# 动态页面正文提取策略

当通过 CDP 抓取网页内容时，很多站点没有固定的正文选择器。以下是一套通用的"盲探"策略。

## 策略优先级

### 1. 先滚动触发懒加载
```bash
# CLI 直连（需手动 sleep）
node cdp-cli.mjs scroll <targetId> --direction bottom
sleep 2

# 或 Proxy（自动等待 800ms）
curl -s "http://localhost:3456/scroll?target=ID&direction=bottom"
```
不滚动就提取，很多内容还没加载到 DOM 中。

### CDP 加载失败兜底

如果 Chrome 打开后变为 `chrome-error://chromewebdata/`（网络/反爬/文章删除），改用 Jina Reader：
```bash
curl -s "https://r.jina.ai/<URL>"
```

### 2. 多选择器试探
```js
const selectors = [
  "article .content", ".article-content", ".content", "[class*=article-content]",
  "[class*=detail-content]", ".rich_media_content", "#js_content",
  ".article-content-detail", ".article__content", ".content_detail",
  ".text", "[class*=content] p", "main p", "article p"
];
let contentEl = null;
for (const sel of selectors) {
  contentEl = document.querySelector(sel);
  if (contentEl && contentEl.innerText.length > 200) break;
}
```
选择器列表可根据平台经验扩展（见 site-patterns/ 目录）。

### 3. 最长文本节点回退
如果标准选择器都失败（或内容长度 < 200）：
```js
const allPs = document.querySelectorAll("p, div, span");
let longest = {el: null, len: 0};
allPs.forEach(p => {
  if (p.innerText.length > longest.len && p.innerText.length > 200)
    longest = {el: p, len: p.innerText.length};
});
if (longest.el) contentEl = longest.el;
```

### 4. 验证 + 过滤
- 检查 `contentEl.innerText.length`，< 200 说明提取失败
- 过滤页面底部干扰区块（导航栏、评论、推荐视频、热榜等）
- 如果内容包含"首页"、"下载 APP"、"热门"等词，说明抓到了页脚而非正文

## 完整 eval 模板
```js
(() => {
  // 1. 多选择器试探
  const selectors = ["article .content", ".article-content", "[class*=content]", "main", "#content"];
  let contentEl = null;
  for (const sel of selectors) {
    contentEl = document.querySelector(sel);
    if (contentEl && contentEl.innerText.length > 200) break;
  }
  // 2. 最长文本节点回退
  if (!contentEl || contentEl.innerText.length < 200) {
    const allPs = document.querySelectorAll("p, div");
    let longest = {el: null, len: 0};
    allPs.forEach(p => { if (p.innerText.length > longest.len) longest = {el: p, len: p.innerText.length}; });
    if (longest.el && longest.len > 200) contentEl = longest.el;
  }
  // 3. 返回结果
  const title = document.querySelector("h1, h2, .title, [class*=title]")?.innerText?.trim() || document.title;
  return JSON.stringify({
    title,
    content: contentEl ? contentEl.innerText.substring(0, 5000) : "[NOT FOUND]",
    contentLen: contentEl ? contentEl.innerText.length : 0
  });
})()
```

## TreeWalker 文本节点提取（推荐，2026-05-13）

当 `innerText` 提取结果混杂（包含标题、来源、导航、按钮等嵌套内容）时，用 TreeWalker 直接遍历纯文本节点，是最干净的回退方案。

```js
const article = document.querySelector("article, .article-content, .content, main, div.main");
const paragraphs = [];
if (article) {
  const walker = document.createTreeWalker(article, NodeFilter.SHOW_TEXT);
  let node;
  while (node = walker.nextNode()) {
    const t = node.textContent.trim();
    if (t.length > 5) paragraphs.push(t);
  }
}
```

**为什么 TreeWalker 比 `innerText` 好**：
- `el.innerText` 返回元素+所有子元素的**合并文本**，无法区分标题和正文
- TreeWalker 直接拿到**每个独立的文本节点**，天然就是段落级别的分割
- 对嵌套结构深的页面（如头条 `div.main` 包含标题+来源+正文+评论），TreeWalker 能逐个提取，配合去重即可分离

**去重**（同一内容可能被多个容器重复引用）：
```js
const seen = new Set();
const unique = paragraphs.filter(p => {
  const key = p.substring(0, 50);
  if (seen.has(key)) return false;
  seen.add(key);
  return true;
});
```

## 常见失败原因

| 现象 | 原因 | 解法 |
|------|------|------|
| 内容 < 200 字 | 没滚动，懒加载未触发 | 先 scroll to bottom，等待后再提取 |
| 内容全是导航/评论 | 抓到了页脚或侧边栏 | 过滤常见干扰词，或缩小选择器范围 |
| 内容为空字符串 | Shadow DOM 或 iframe | 递归穿透 shadowRoot，或切换到 iframe target |
| 页面提示"不存在" | 可能是 URL 缺少必要参数 | 用完整 URL（含所有查询参数）打开 |

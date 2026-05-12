# 动态页面正文提取策略

当通过 CDP 抓取网页内容时，很多站点没有固定的正文选择器。以下是一套通用的"盲探"策略。

## 策略优先级

### 1. 先滚动触发懒加载
```bash
curl -s "http://localhost:3456/scroll?target=ID&direction=bottom"
sleep 2
```
不滚动就提取，很多内容还没加载到 DOM 中。

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

## 常见失败原因

| 现象 | 原因 | 解法 |
|------|------|------|
| 内容 < 200 字 | 没滚动，懒加载未触发 | 先 scroll to bottom，等待后再提取 |
| 内容全是导航/评论 | 抓到了页脚或侧边栏 | 过滤常见干扰词，或缩小选择器范围 |
| 内容为空字符串 | Shadow DOM 或 iframe | 递归穿透 shadowRoot，或切换到 iframe target |
| 页面提示"不存在" | 可能是 URL 缺少必要参数 | 用完整 URL（含所有查询参数）打开 |

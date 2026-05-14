#!/usr/bin/env python3
"""
每日热点资讯抓取脚本 - 使用 CDP (Chrome DevTools Protocol)
来源: NewsNow + 今日热榜 + SoPilot
输出: Clippings/YYYYMM/YYYYMMDD_热点资讯.md
"""

import subprocess
import json
import os
import re
from datetime import datetime

KB_BASE = '/home/a409/knowledge_base/note/pi-lab/Clippings'

JS_SCRIPT = r"""
const puppeteer = require('puppeteer-core');
const fs = require('fs');

async function fetchPage(url, selector, timeout = 30000) {
    const browser = await puppeteer.connect({
        browserURL: 'http://127.0.0.1:9222',
        defaultViewport: null
    });
    const pages = await browser.pages();
    const page = pages[0];
    
    await page.goto(url, { waitUntil: 'networkidle2', timeout });
    await new Promise(r => setTimeout(r, 3000));
    
    // Scroll to load lazy content
    for (let i = 0; i < 20; i++) {
        await page.evaluate('window.scrollBy(0, 300)');
        await new Promise(r => setTimeout(r, 200));
    }
    
    const content = await page.evaluate((sel) => {
        const el = document.querySelector(sel) || document.body;
        return el.innerText;
    }, selector);
    
    await page.close();
    browser.disconnect();
    return content;
}

(async () => {
    const results = {};
    
    // 1. NewsNow
    try {
        console.log('Fetching NewsNow...');
        results['newsnow'] = await fetchPage('https://newsnow.busiyi.world', 'main', 40000);
    } catch(e) {
        results['newsnow'] = 'ERROR: ' + e.message;
    }
    
    // 2. 今日热榜
    try {
        console.log('Fetching 今日热榜...');
        results['tophub'] = await fetchPage('https://tophub.today/c/tech', 'main', 40000);
    } catch(e) {
        results['tophub'] = 'ERROR: ' + e.message;
    }
    
    // 3. SoPilot
    try {
        console.log('Fetching SoPilot...');
        results['sopilot'] = await fetchPage('https://sopilot.net/zh/hot-tweets', 'main', 40000);
    } catch(e) {
        results['sopilot'] = 'ERROR: ' + e.message;
    }
    
    fs.writeFileSync('/tmp/daily_hot_topics.json', JSON.stringify(results, null, 2));
    console.log('Done. Results saved to /tmp/daily_hot_topics.json');
})();
"""

def clean_text(text, max_items=20):
    """从抓取到的文本中提取热点列表"""
    lines = text.strip().split('\n')
    items = []
    for line in lines:
        line = line.strip()
        # 跳过空行、导航、无关内容
        if not line or len(line) < 4:
            continue
        # 跳过常见的非热点内容
        skip = ['登录', '注册', '下载', '首页', '关注', '分享', '收藏', 
                '广告', 'Cookie', '隐私', '关于我们', '联系方式',
                '©', '2026', '©2026', 'Copyright']
        if any(s in line for s in skip):
            continue
        items.append(f'- {line}')
        if len(items) >= max_items:
            break
    return items

def main():
    today = datetime.now().strftime('%Y%m%d')
    month_dir = f'{KB_BASE}/{today[:6]}'
    os.makedirs(month_dir, exist_ok=True)
    
    output_file = f'{month_dir}/{today}_热点资讯.md'
    js_file = '/tmp/daily_hot_fetch.js'
    
    # 写 JS 脚本
    with open(js_file, 'w') as f:
        f.write(JS_SCRIPT)
    
    print(f'📅 开始抓取 {today} 热点资讯...')
    
    # 执行 CDP 抓取
    try:
        result = subprocess.run(
            ['node', js_file],
            cwd='/home/bushuhui',
            capture_output=True,
            text=True,
            timeout=180
        )
        if result.returncode != 0:
            print(f'⚠️  CDP 抓取失败: {result.stderr[:200]}')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f'# {today} 热点资讯\n\n> 抓取时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}\n> ⚠️ CDP 抓取失败，请检查 Chrome 是否运行\n')
            return
    except subprocess.TimeoutExpired:
        print('⚠️  CDP 抓取超时')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f'# {today} 热点资讯\n\n> 抓取时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}\n> ⚠️ CDP 抓取超时\n')
        return
    
    # 读取结果
    try:
        with open('/tmp/daily_hot_topics.json', 'r') as f:
            data = json.load(f)
    except:
        print('⚠️  结果文件读取失败')
        return
    
    # 生成 Markdown
    sections = []
    
    # NewsNow
    if data.get('newsnow', '').startswith('ERROR'):
        sections.append('## NewsNow\n\n抓取失败')
    else:
        items = clean_text(data['newsnow'], 15)
        sections.append('## NewsNow（多平台聚合）\n\n' + '\n'.join(items) if items else '## NewsNow\n\n无数据')
    
    # 今日热榜
    if data.get('tophub', '').startswith('ERROR'):
        sections.append('## 今日热榜\n\n抓取失败')
    else:
        items = clean_text(data['tophub'], 15)
        sections.append('## 今日热榜（技术类目）\n\n' + '\n'.join(items) if items else '## 今日热榜\n\n无数据')
    
    # SoPilot
    if data.get('sopilot', '').startswith('ERROR'):
        sections.append('## SoPilot\n\n抓取失败')
    else:
        items = clean_text(data['sopilot'], 15)
        sections.append('## SoPilot（X 爆款推文）\n\n' + '\n'.join(items) if items else '## SoPilot\n\n无数据')
    
    content = f"""# {today} 热点资讯

> 抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> 来源: NewsNow + 今日热榜 + SoPilot
> 方式: CDP (Chrome DevTools Protocol)

---

{chr(10) + chr(10) + '---' + chr(10) + chr(10).join(sections)}

---

*自动抓取 by daily-hot-topics skill*
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'✅ 已保存到: {output_file}')
    print(f'📊 总计: {len(content)} 字符')

if __name__ == '__main__':
    main()

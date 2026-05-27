#!/usr/bin/env python3
"""GitHub 热点仓库抓取 - 搜索、过滤 SEO 垃圾、分类、保存到知识库"""

import urllib.request
import json
import time
import re
import os
import html
import ssl
from datetime import datetime, timedelta

# 检测代理：检查环境变量或常见本地代理端口
_proxy_url = (
    os.environ.get('https_proxy') or os.environ.get('HTTPS_PROXY')
    or os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY')
    or 'http://127.0.0.1:7890'
)
_proxy_handler = urllib.request.ProxyHandler({'http': _proxy_url, 'https': _proxy_url})
_opener = urllib.request.build_opener(_proxy_handler)
# 跳过 SSL 验证（本地代理常有自签名证书）
_ssl_context = ssl.create_default_context()
_ssl_context.check_hostname = False
_ssl_context.verify_mode = ssl.CERT_NONE
_https_handler = urllib.request.HTTPSHandler(context=_ssl_context)
_opener = urllib.request.build_opener(_proxy_handler, _https_handler)


def _urlopen(url, timeout=30):
    """统一请求函数，走代理"""
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    })
    try:
        return _opener.open(req, timeout=timeout)
    except urllib.error.URLError:
        # 代理失败时尝试直连
        req2 = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })
        return urllib.request.urlopen(req2, timeout=timeout)


def search_trending_repos(days=4, per_page=40):
    """搜索最近 days 天内创建的高 star 仓库"""
    since = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    url = f'https://api.github.com/search/repositories?q=created:>{since}&sort=stars&order=desc&per_page={per_page}'
    with _urlopen(url, timeout=30) as resp:
        raw = resp.read().decode()
    # 用 regex 提取，避免 JSON 截断
    names = re.findall(r'"full_name"\s*:\s*"([^"]+)"', raw)
    return names[:40]


def get_trending_repo_info_with_stars(period='daily'):
    """从 trending 页面抓取仓库名 + 当前 star 数"""
    since_map = {'daily': '', 'weekly': 'weekly', 'monthly': 'monthly'}
    since = since_map.get(period, '')
    url = 'https://github.com/trending'
    if since:
        url += f'?since={since}'

    with _urlopen(url, timeout=30) as resp:
        page_html = resp.read().decode('utf-8')

    articles = re.findall(r'<article\s+class="Box-row".*?</article>', page_html, re.DOTALL)

    results = []
    for article in articles:
        # 提取 owner/repo — 用 h2 块中第一个 /owner/name 格式的链接
        h2_block = re.search(r'<h2 class="h3 lh-condensed">(.*?)</h2>', article, re.DOTALL)
        if not h2_block:
            continue
        # 从 h2 块中提取 href
        link_match = re.search(r'href="(/[^/]+/[^/?"]+)', h2_block.group(1))
        if not link_match:
            continue
        repo_path = link_match.group(1).strip('/')
        if repo_path.count('/') != 1 or repo_path.startswith('sponsors/'):
            continue

        # 提取 star 文本
        star_match = re.search(r'href="[^"]*stargazers"[^>]*>\s*([^<]+)<', article)
        star_text = ''
        star_count = 0
        if star_match:
            star_text = html.unescape(star_match.group(1).strip())
            num_match = re.search(r'([\d,]+)', star_text)
            if num_match:
                star_count = int(num_match.group(1).replace(',', ''))

        results.append({
            'name': repo_path,
            'stars': star_count,
            'star_text': star_text,
        })

    period_label = {'daily': '当天', 'weekly': '本周', 'monthly': '本月'}.get(period, period)
    print(f"  从 GitHub Trending 页面抓取到 {len(results)} 个{period_label}热门仓库")
    return results


def get_repo_info(repo_name):
    """获取单个仓库的详细信息"""
    try:
        url = f'https://api.github.com/repos/{repo_name}'
        with _urlopen(url, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def is_seo_spam(desc, stars=0, forks=0):
    """判断是否为 SEO 垃圾项目

    返回 (is_spam: bool, score: int)
    score >= 2 则确定为垃圾，score == 1 需人工审核
    """
    if not desc or desc.strip() == '':
        return True, 3

    score = 0
    desc_lower = desc.lower()

    # 1. "2026" 出现在描述中（大量 SEO 项目加年份关键词）
    if re.search(r'\b2026\b', desc):
        score += 1

    # 2. 大量 emoji（>=3 个不同 emoji）
    emoji_count = len(re.findall(r'[\U0001F300-\U0001FAD6\U00002702-\U000027B0]', desc))
    if emoji_count >= 3:
        score += 1

    # 3. 下载/破解相关关键词
    crack_terms = ['download', 'free', 'crack', 'full crack', 'unlock', 'bypass',
                   'hack', 'cheat', 'spoof', 'mod menu', 'modded']
    crack_hits = sum(1 for t in crack_terms if t in desc_lower)
    if crack_hits >= 2:
        score += 2
    elif crack_hits >= 1:
        score += 1

    # 4. 平台堆砌
    if re.search(r'(windows|android|ios|mac|pc|linux)', desc_lower):
        platforms = len(re.findall(r'(windows|android|ios|mac|pc|linux)', desc_lower))
        if platforms >= 3:
            score += 1

    # 5. 逗号过多（关键词堆砌）
    if desc.count(',') > 4:
        score += 1

    # 6. 重复文本（同一短语出现 3+ 次）
    words = desc_lower.split()
    if len(words) > 10:
        # 检查是否有连续重复短语
        for phrase_len in range(3, 7):
            for i in range(len(words) - phrase_len * 2):
                phrase = ' '.join(words[i:i + phrase_len])
                if desc_lower.count(phrase) >= 3:
                    score += 2
                    break
            if score >= 2:
                break

    # 7. 特定垃圾模式
    spam_patterns = [
        r'casino', r'bonus', r'gambling', r'betting',
        r'booster', r'optimizer', r'boost.*fps', r'fix.*ping',
        r'token.*manager', r'auto.*boost',
        r'uncensored', r'18\+', r'nsfw',
        r'release.*date', r'multiplayer.*guide', r'mod.*pack',
        r'emulator.*download', r'steam.*download',
    ]
    for pat in spam_patterns:
        if re.search(pat, desc_lower):
            score += 1
            break  # 同类只加一次

    # 8. Star 高但 Fork 为 0 或极低（人工刷 star）
    if stars > 400 and forks < 5:
        score += 1

    is_spam = score >= 2
    return is_spam, score


def fetch_trending(days=4, source='api', period='daily'):
    """主流程：抓取 + 过滤 + 格式化

    Args:
        days: API 模式下搜索最近几天
        source: 'api' | 'trending'，API 搜索或 Trending 页面
        period: 'daily' | 'weekly' | 'monthly'，Trending 页面时间维度
    """
    if source == 'trending':
        return fetch_trending_from_page(period)

    # API 模式（原有逻辑）
    print(f"正在搜索最近 {days} 天的热门仓库...")
    repo_names = search_trending_repos(days=days)
    print(f"找到 {len(repo_names)} 个候选仓库，正在获取详细信息...")

    valid_repos = []
    spam_count = 0
    for i, name in enumerate(repo_names):
        if i % 10 == 0:
            print(f"  处理进度: {i}/{len(repo_names)}")
        info = get_repo_info(name)
        if info and info.get('stargazers_count', 0) >= 50:
            desc = info.get('description') or ''
            stars = info.get('stargazers_count', 0)
            forks = info.get('forks_count', 0)
            is_spam, score = is_seo_spam(desc, stars, forks)
            if not is_spam:
                valid_repos.append(info)
            else:
                spam_count += 1
                print(f"  [SPAM score={score}] {name}: {desc[:80]}")
        time.sleep(0.2)

    print(f"\n过滤结果: 有效 {len(valid_repos)} 个 | 垃圾 {spam_count} 个")

    # 按 stars 排序
    valid_repos.sort(key=lambda x: x['stargazers_count'], reverse=True)

    return _classify_and_return(valid_repos)


def fetch_trending_from_page(period='daily'):
    """从 GitHub Trending 页面抓取热门仓库"""
    period_label = {'daily': '当天', 'weekly': '本周', 'monthly': '本月'}.get(period, period)
    print(f"正在抓取 GitHub Trending 热门仓库（{period_label}）...")

    trending_repos = get_trending_repo_info_with_stars(period)
    print(f"  获取到 {len(trending_repos)} 个热门仓库，正在获取详细信息...")

    valid_repos = []
    spam_count = 0
    for i, item in enumerate(trending_repos):
        name = item['name']
        if i % 10 == 0:
            print(f"  处理进度: {i}/{len(trending_repos)}")
        info = get_repo_info(name)
        if info:
            desc = info.get('description') or ''
            stars = info.get('stargazers_count', 0)
            forks = info.get('forks_count', 0)
            is_spam, score = is_seo_spam(desc, stars, forks)
            if not is_spam:
                # 保留页面 star 文本
                info['_page_star_text'] = item.get('star_text', '')
                valid_repos.append(info)
            else:
                spam_count += 1
                print(f"  [SPAM score={score}] {name}: {desc[:80]}")
        time.sleep(0.2)

    print(f"\n过滤结果: 有效 {len(valid_repos)} 个 | 垃圾 {spam_count} 个")

    # 按 stars 排序
    valid_repos.sort(key=lambda x: x['stargazers_count'], reverse=True)

    return _classify_and_return(valid_repos)


def _classify_and_return(valid_repos):
    """分类仓库"""
    ai_repos = []
    dev_repos = []
    other_repos = []

    ai_keywords = ['ai', 'agent', 'llm', 'model', 'chatbot', 'ml', 'machine learning',
                   'deep learning', 'neural', 'nlp', 'computer vision', 'diffusion',
                   'rag', 'embedding', 'inference', 'training', 'pretraining', 'text generation']
    dev_keywords = ['cli', 'terminal', 'editor', 'ide', 'framework', 'library',
                    'docker', 'kubernetes', 'api', 'devops', 'testing', 'debug',
                    'compiler', 'database', 'web', 'frontend', 'backend']

    for repo in valid_repos:
        desc = ((repo.get('description') or '') + ' ' + ' '.join(repo.get('topics', []) or [])).lower()
        if any(k in desc for k in ai_keywords):
            ai_repos.append(repo)
        elif any(k in desc for k in dev_keywords):
            dev_repos.append(repo)
        else:
            other_repos.append(repo)

    return ai_repos, dev_repos, other_repos


def format_output(ai_repos, dev_repos, other_repos, source='api', period='daily'):
    """格式化为 Markdown（单周期模式）

    Args:
        source: 'api' | 'trending'
        period: 'daily' | 'weekly' | 'monthly'
    """
    today = datetime.now().strftime('%Y-%m-%d')
    period_label = {'daily': '当天', 'weekly': '本周', 'monthly': '本月'}.get(period, period)

    lines = [f'# GitHub 热点仓库速报（{today}）\n']
    if source == 'trending':
        lines.append(f'*从 GitHub Trending 页面抓取（{period_label}热门），已过滤 SEO 垃圾项目*\n')
    else:
        lines.append(f'*自动抓取最近 4 天新建的高 star 仓库，已过滤 SEO 垃圾项目*\n')

    def render_section(title, repos, max_show=10):
        section = [f'## {title} ({len(repos)} 个)\n']
        section.append('| # | 项目 | ⭐ Stars | 简介 | 语言 |')
        section.append('|---|------|---------|------|------|')
        for i, repo in enumerate(repos[:max_show]):
            name = repo['full_name']
            stars = repo['stargazers_count']
            forks = repo['forks_count']
            lang = repo.get('language') or '-'
            desc = (repo.get('description') or '').replace('\n', ' ')[:100]
            url = repo['html_url']
            page_star = repo.get('_page_star_text', '')
            star_display = f'{stars:,} (🍴{forks})'
            if page_star:
                star_display = f'{stars:,} ({page_star}, 🍴{forks})'
            section.append(f'| {i+1} | [{name}]({url}) | {star_display} | {desc} | {lang} |')
        if len(repos) > max_show:
            section.append(f'\n*... 还有 {len(repos) - max_show} 个项目未展示*')
        section.append('')
        return '\n'.join(section)

    lines.append(render_section('🤖 AI / 大模型', ai_repos))
    lines.append(render_section('🛠️ 开发工具 / 基础设施', dev_repos))
    lines.append(render_section('📦 其他', other_repos))

    return '\n'.join(lines)


def fetch_all_periods():
    """抓取当天+本周+本月三个维度的热点，汇总返回"""
    all_results = {}
    for period in ['daily', 'weekly', 'monthly']:
        period_label = {'daily': '当天', 'weekly': '本周', 'monthly': '本月'}.get(period, period)
        print(f"\n{'='*40}")
        print(f"正在抓取 {period_label}热门...")
        print(f"{'='*40}")
        ai, dev, other = fetch_trending_from_page(period)
        all_results[period] = {
            'label': period_label,
            'ai': ai,
            'dev': dev,
            'other': other,
        }
    return all_results


def format_all_periods(all_results):
    """将三个时间维度的结果汇总为一份 Markdown"""
    today = datetime.now().strftime('%Y-%m-%d')

    lines = [f'# GitHub 热点仓库速报（{today}）\n']
    lines.append(f'*从 GitHub Trending 页面抓取（当天+本周+本月），已过滤 SEO 垃圾项目*\n')

    def render_section(title, repos, max_show=10):
        section = [f'### {title} ({len(repos)} 个)\n']
        section.append('| # | 项目 | ⭐ Stars | 简介 | 语言 |')
        section.append('|---|------|---------|------|------|')
        for i, repo in enumerate(repos[:max_show]):
            name = repo['full_name']
            stars = repo['stargazers_count']
            forks = repo['forks_count']
            lang = repo.get('language') or '-'
            desc = (repo.get('description') or '').replace('\n', ' ')[:100]
            url = repo['html_url']
            page_star = repo.get('_page_star_text', '')
            star_display = f'{stars:,} (🍴{forks})'
            if page_star:
                star_display = f'{stars:,} ({page_star}, 🍴{forks})'
            section.append(f'| {i+1} | [{name}]({url}) | {star_display} | {desc} | {lang} |')
        if len(repos) > max_show:
            section.append(f'\n*... 还有 {len(repos) - max_show} 个项目未展示*')
        section.append('')
        return '\n'.join(section)

    for period in ['daily', 'weekly', 'monthly']:
        data = all_results[period]
        label = data['label']
        ai = data['ai']
        dev = data['dev']
        other = data['other']

        lines.append(f'## 📅 {label}热门（共 {len(ai) + len(dev) + len(other)} 个）\n')
        lines.append(render_section('🤖 AI / 大模型', ai))
        lines.append(render_section('🛠️ 开发工具 / 基础设施', dev))
        lines.append(render_section('📦 其他', other))

    return '\n'.join(lines)


def save_to_knowledge_base(content, source='api', period='daily'):
    """保存到知识库

    Args:
        source: 'api' | 'trending' | 'all'
        period: 'daily' | 'weekly' | 'monthly'（source='all' 时忽略）
    """
    today = datetime.now()
    ym = today.strftime('%Y%m')
    ymd = today.strftime('%Y%m%d')

    kb_base = os.environ.get('GITHUB_TRENDING_KB_DIR',
                              os.path.expanduser('~/knowledge_base/note/pi-lab/Clippings'))
    kb_dir = f'{kb_base}/{ym}/GitHub-Trending'
    os.makedirs(kb_dir, exist_ok=True)

    if source == 'all':
        filename = f'{kb_dir}/trending-all-{ymd}.md'
        entry_title = 'GitHub Trending 热点（当天+本周+本月）'
        entry_ref = f'GitHub-Trending/trending-all-{ymd}.md'
    elif source == 'trending':
        period_suffix = {'daily': 'daily', 'weekly': 'weekly', 'monthly': 'monthly'}.get(period, 'daily')
        filename = f'{kb_dir}/trending-page-{period_suffix}-{ymd}.md'
        period_label = {'daily': '当天', 'weekly': '本周', 'monthly': '本月'}.get(period, period)
        entry_title = f'GitHub Trending 热点（{period_label}）'
        entry_ref = f'GitHub-Trending/trending-page-{period_suffix}-{ymd}.md'
    else:
        filename = f'{kb_dir}/trending-{ymd}.md'
        entry_title = 'GitHub 热点仓库速报'
        entry_ref = f'GitHub-Trending/trending-{ymd}.md'

    with open(filename, 'w') as f:
        f.write(content)

    # 更新当日索引
    index_file = f'{kb_base}/{ym}/{ymd}.md'
    entry = f'\n## {entry_title}\n\n- 日期：{ymd}\n- 内容：[[{entry_ref}]]\n'

    if os.path.exists(index_file):
        with open(index_file, 'r') as f:
            existing = f.read()
        if entry_ref not in existing:
            with open(index_file, 'a') as f:
                f.write(entry)
    else:
        with open(index_file, 'w') as f:
            f.write(f'# {ymd} 剪报索引\n{entry}\n')

    return filename


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='GitHub 热点仓库抓取')
    parser.add_argument('--source', choices=['api', 'trending', 'all'], default='all',
                        help='数据来源：all=当天+本周+本月汇总（默认）, trending=单周期, api=GitHub Search API')
    parser.add_argument('--period', choices=['daily', 'weekly', 'monthly'], default='daily',
                        help='trending 模式下时间维度：daily=当天, weekly=本周, monthly=本月（默认 daily）')
    parser.add_argument('--days', type=int, default=4, help='API 模式下搜索最近几天（默认 4）')
    args = parser.parse_args()

    if args.source == 'all':
        # 默认：抓取当天+本周+本月三个维度
        all_results = fetch_all_periods()
        content = format_all_periods(all_results)

        # 统计总数
        total = sum(len(d['ai']) + len(d['dev']) + len(d['other']) for d in all_results.values())
        if total == 0:
            print("未找到符合条件的仓库")
            exit(0)

        saved_path = save_to_knowledge_base(content, source='all')
        print(f'\n已保存到: {saved_path}')
        for period in ['daily', 'weekly', 'monthly']:
            d = all_results[period]
            print(f'  {d["label"]}: AI {len(d["ai"])} 个 | 开发 {len(d["dev"])} 个 | 其他 {len(d["other"])} 个')
        print('\n' + '=' * 60)
        print(content)

    elif args.source == 'trending':
        ai, dev, other = fetch_trending_from_page(args.period)
        content = format_output(ai, dev, other, source='trending', period=args.period)

        if not ai and not dev and not other:
            print("未找到符合条件的仓库")
            exit(0)

        saved_path = save_to_knowledge_base(content, source='trending', period=args.period)
        print(f'\n已保存到: {saved_path}')
        print(f'\n统计: AI {len(ai)} 个 | 开发 {len(dev)} 个 | 其他 {len(other)} 个')
        print('\n' + '=' * 60)
        print(content)

    else:
        # API 模式
        ai, dev, other = fetch_trending(days=args.days, source='api', period='daily')
        content = format_output(ai, dev, other, source='api')

        if not ai and not dev and not other:
            print("未找到符合条件的仓库")
            exit(0)

        saved_path = save_to_knowledge_base(content, source='api')
        print(f'\n已保存到: {saved_path}')
        print(f'\n统计: AI {len(ai)} 个 | 开发 {len(dev)} 个 | 其他 {len(other)} 个')
        print('\n' + '=' * 60)
        print(content)

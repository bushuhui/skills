#!/usr/bin/env python3
"""GitHub 热点仓库抓取 - 搜索、过滤 SEO 垃圾、分类、保存到知识库"""

import urllib.request
import json
import time
import re
import os
from datetime import datetime, timedelta


def search_trending_repos(days=4, per_page=40):
    """搜索最近 days 天内创建的高 star 仓库"""
    since = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    url = f'https://api.github.com/search/repositories?q=created:>{since}&sort=stars&order=desc&per_page={per_page}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode()
    # 用 regex 提取，避免 JSON 截断
    names = re.findall(r'"full_name"\s*:\s*"([^"]+)"', raw)
    return names[:40]


def get_repo_info(repo_name):
    """获取单个仓库的详细信息"""
    try:
        url = f'https://api.github.com/repos/{repo_name}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
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


def fetch_trending(days=4):
    """主流程：抓取 + 过滤 + 格式化"""
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

    # 分类
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


def format_output(ai_repos, dev_repos, other_repos):
    """格式化为 Markdown"""
    today = datetime.now().strftime('%Y-%m-%d')

    lines = [f'# GitHub 热点仓库速报（{today}）\n']
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
            section.append(f'| {i+1} | [{name}]({url}) | {stars:,} (🍴{forks}) | {desc} | {lang} |')
        if len(repos) > max_show:
            section.append(f'\n*... 还有 {len(repos) - max_show} 个项目未展示*')
        section.append('')
        return '\n'.join(section)

    lines.append(render_section('🤖 AI / 大模型', ai_repos))
    lines.append(render_section('🛠️ 开发工具 / 基础设施', dev_repos))
    lines.append(render_section('📦 其他', other_repos))

    return '\n'.join(lines)


def save_to_knowledge_base(content):
    """保存到知识库"""
    today = datetime.now()
    ym = today.strftime('%Y%m')
    ymd = today.strftime('%Y%m%d')

    kb_dir = f'/home/a409/knowledge_base/note/pi-lab/Clippings/{ym}/GitHub-Trending'
    os.makedirs(kb_dir, exist_ok=True)

    filename = f'{kb_dir}/trending-{ymd}.md'
    with open(filename, 'w') as f:
        f.write(content)

    # 更新当日索引
    index_file = f'/home/a409/knowledge_base/note/pi-lab/Clippings/{ym}/{ymd}.md'
    entry = f'\n## GitHub 热点仓库速报\n\n- 日期：{ymd}\n- 内容：[[GitHub-Trending/trending-{ymd}.md]]\n'

    if os.path.exists(index_file):
        # 检查是否已有此条目
        with open(index_file, 'r') as f:
            existing = f.read()
        if 'GitHub-Trending/trending-' not in existing:
            with open(index_file, 'a') as f:
                f.write(entry)
    else:
        with open(index_file, 'w') as f:
            f.write(f'# {ymd} 剪报索引\n{entry}\n')

    return filename


if __name__ == '__main__':
    ai, dev, other = fetch_trending(days=4)
    content = format_output(ai, dev, other)

    if not ai and not dev and not other:
        print("未找到符合条件的仓库")
        exit(0)

    saved_path = save_to_knowledge_base(content)
    print(f'\n已保存到: {saved_path}')
    print(f'\n统计: AI {len(ai)} 个 | 开发 {len(dev)} 个 | 其他 {len(other)} 个')
    print('\n' + '=' * 60)
    print(content)

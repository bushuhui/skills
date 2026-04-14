#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paper Auto Review - 批量自动审稿

流程：
1. 扫描论文目录，找出没有 review*.md 的论文
2. 使用 pi-llm-server 将 PDF/DOCX/DOC 转成 Markdown
3. 将 review_prompt.md + Markdown 论文传给 Bailian LLM 进行审稿
4. 审稿结果保存为 xxx_review_draft.md

依赖：
- requests（用于 pi-llm-server 和 Bailian API）
"""

from __future__ import annotations

import argparse
import os
import random
import time
from pathlib import Path

import requests

# ===== 配置 =====
PI_LLM_URL = os.environ["PI_LLM_URL"]
PI_LLM_API_KEY = os.environ["PI_LLM_API_KEY"]
BAILIAN_URL = os.environ["BAILIAN_URL"]
BAILIAN_API_KEY = os.environ["BAILIAN_API_KEY"]
BAILIAN_MODEL = os.environ["BAILIAN_MODEL"]

SCRIPT_DIR = Path(__file__).resolve().parent
PAPER_ROOT = Path(
    "/home/bushuhui/datacenter/papers/paper-review"
)
REVIEW_PROMPT_PATH = SCRIPT_DIR / "review_prompt.md"
REVIEW_PROMPT_CN_PATH = SCRIPT_DIR / "review_prompt_cn.md"

PI_LLM_HEADERS = {
    "Authorization": f"Bearer {PI_LLM_API_KEY}",
}
BAILIAN_HEADERS = {
    "Authorization": f"Bearer {BAILIAN_API_KEY}",
    "Content-Type": "application/json",
}


# ===== Step 1: 扫描待审稿论文 =====
def scan_pending_papers(root: Path, year: str) -> list[Path]:
    """找出没有 review*.md 的论文目录中的 PDF/DOCX/DOC 文件。"""
    pending = []
    base = root / year
    if not base.exists():
        print(f"[WARN] 目录不存在: {base}")
        return []

    for journal_dir in sorted(base.iterdir()):
        if not journal_dir.is_dir():
            continue
        for paper_dir in sorted(journal_dir.iterdir()):
            if not paper_dir.is_dir():
                continue
            # 检查是否已有审稿意见
            review_files = list(paper_dir.glob("review*.md"))
            if review_files:
                continue
            # 查找 PDF/DOCX/DOC 文件
            for ext in ("*.pdf", "*.docx", "*.doc"):
                found = list(paper_dir.glob(ext))
                if found:
                    pending.append(found[0])
                    break
    return pending


# ===== 语言检测 =====
def detect_language(text: str) -> str:
    """检测文本主要语言，返回 'zh' 或 'en'。"""
    # 统计中文字符比例
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    total_chars = len(text)
    if total_chars == 0:
        return 'en'
    ratio = chinese_chars / total_chars
    return 'zh' if ratio > 0.1 else 'en'


# ===== Step 2: 使用 pi-llm-server 转 Markdown =====
def parse_to_markdown(source_path: Path) -> Path | None:
    """
    调用 pi-llm-server 将 PDF/DOCX/DOC 转成 Markdown，
    输出到源文件同目录，返回 .md 文件路径。
    """
    print(f"  → 正在转换 Markdown: {source_path.name}")
    session = requests.Session()
    session.trust_env = False

    file_name = source_path.name
    base_name = source_path.stem
    output_dir = str(source_path.parent)

    with open(source_path, "rb") as f:
        files = {"files": (file_name, f, "application/octet-stream")}
        data = {
            "backend": "pipeline",
            "parse_method": "auto",
            "lang_list": "ch",
            "return_md": "true",
            "return_images": "true",
            "response_format_zip": "true",
        }
        resp = session.post(
            f"{PI_LLM_URL}/ocr/parser",
            headers=PI_LLM_HEADERS,
            files=files,
            data=data,
            timeout=1800,
        )

    if resp.status_code != 200:
        print(f"  ✗ 转换失败: HTTP {resp.status_code} - {resp.text[:200]}")
        return None

    # 解压并保存 Markdown
    import re
    import shutil
    import tempfile
    import zipfile

    temp_dir = tempfile.mkdtemp(prefix="mineru_")
    zip_path = os.path.join(temp_dir, "result.zip")
    with open(zip_path, "wb") as f:
        f.write(resp.content)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(temp_dir)

    md_files = []
    temp_images_dir = None
    for r, dirs, files_list in os.walk(temp_dir):
        for fn in files_list:
            if fn.endswith(".md"):
                md_files.append(os.path.join(r, fn))
        if "images" in dirs:
            temp_images_dir = os.path.join(r, "images")

    final_images_dir = os.path.join(output_dir, f"{base_name}_images")
    os.makedirs(final_images_dir, exist_ok=True)

    dst_md = None
    for temp_md in md_files:
        dst_md = os.path.join(output_dir, f"{base_name}.md")
        shutil.copy2(temp_md, dst_md)

        # 修正图片路径
        if temp_images_dir:
            with open(dst_md, "r", encoding="utf-8") as f:
                content = f.read()
            new_content = re.sub(
                r"!\[([^\]]*)\]\(images/",
                f"![\\1]({base_name}_images/",
                content,
            )
            with open(dst_md, "w", encoding="utf-8") as f:
                f.write(new_content)

    if temp_images_dir and os.path.exists(temp_images_dir):
        if os.path.exists(final_images_dir):
            shutil.rmtree(final_images_dir)
        shutil.copytree(temp_images_dir, final_images_dir)

    shutil.rmtree(temp_dir, ignore_errors=True)

    if dst_md:
        print(f"  ✓ 转换完成: {dst_md}")
        return Path(dst_md)

    print(f"  ✗ 未找到 Markdown 输出")
    return None


# ===== Step 3: 调用 Bailian LLM 审稿 =====
def generate_review(markdown_path: Path, review_prompt: str, review_prompt_cn: str) -> str | None:
    """
    将 review_prompt + 论文 Markdown 内容发给 Bailian LLM，
    返回审稿意见。
    """
    print(f"  → 正在生成审稿意见...")

    # 读取 Markdown 内容
    content = markdown_path.read_text(encoding="utf-8")

    # 截断过长内容（留足上下文窗口）
    max_chars = 60000
    if len(content) > max_chars:
        content = content[:max_chars]
        print(f"  ⚠ 论文内容过长，已截断至 {max_chars} 字符")

    # 检测论文语言
    lang = detect_language(content)
    if lang == 'zh':
        prompt = review_prompt_cn
        system_msg = "你是一位专业的学术审稿人。请用中文撰写审稿意见。"
        print(f"  ℹ 检测到中文论文，使用中文审稿模板")
    else:
        prompt = review_prompt
        system_msg = "你是一位专业的学术审稿人。请用英文撰写审稿意见。"
        print(f"  ℹ 检测到英文论文，使用英文审稿模板")

    user_message = f"""{prompt}

---

以下是论文的完整内容：

{content}
"""

    session = requests.Session()
    session.trust_env = False

    payload = {
        "model": BAILIAN_MODEL,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.3,
        "max_tokens": 8000,
    }

    try:
        resp = session.post(
            f"{BAILIAN_URL}/chat/completions",
            headers=BAILIAN_HEADERS,
            json=payload,
            timeout=300,
        )
    except Exception as e:
        print(f"  ✗ LLM 请求失败: {e}")
        return None

    if resp.status_code != 200:
        print(f"  ✗ LLM 返回错误: HTTP {resp.status_code} - {resp.text[:200]}")
        return None

    result = resp.json()
    review = result.get("choices", [{}])[0].get("message", {}).get("content", "")

    if not review:
        print(f"  ✗ LLM 返回空内容")
        return None

    print(f"  ✓ 审稿意见生成完成 ({len(review)} 字符)")
    return review


# ===== 主流程 =====
def run(args: argparse.Namespace) -> int:
    year = args.year
    root = args.paper_root or PAPER_ROOT
    review_prompt_path = args.review_prompt or REVIEW_PROMPT_PATH

    # 加载审稿 prompt（英文）
    if not review_prompt_path.exists():
        print(f"[ERROR] 审稿 prompt 文件不存在: {review_prompt_path}")
        return 1
    review_prompt = review_prompt_path.read_text(encoding="utf-8").strip()
    if not review_prompt:
        print(f"[ERROR] 审稿 prompt 文件为空: {review_prompt_path}")
        return 1

    # 加载中文审稿 prompt
    if not REVIEW_PROMPT_CN_PATH.exists():
        print(f"[ERROR] 中文审稿 prompt 文件不存在: {REVIEW_PROMPT_CN_PATH}")
        return 1
    review_prompt_cn = REVIEW_PROMPT_CN_PATH.read_text(encoding="utf-8").strip()
    if not review_prompt_cn:
        print(f"[ERROR] 中文审稿 prompt 文件为空: {REVIEW_PROMPT_CN_PATH}")
        return 1

    # Step 1: 扫描
    print(f"=== 扫描待审稿论文 ({year}) ===")
    pending = scan_pending_papers(root, year)
    if not pending:
        print("没有发现待审稿的论文。")
        return 0
    print(f"发现 {len(pending)} 篇待审稿论文:\n")
    for p in pending:
        print(f"  - {p}")
    print()

    # Step 2 & 3: 逐篇处理
    results = []
    for i, source_path in enumerate(pending, 1):
        print(f"[{i}/{len(pending)}] 处理: {source_path.name}")

        # 检查是否已有 Markdown 文件
        md_path = source_path.parent / f"{source_path.stem}.md"
        if md_path.exists():
            print(f"  ✓ Markdown 已存在: {md_path}")
        else:
            # Step 2: 转换 Markdown
            md_path = parse_to_markdown(source_path)
            if md_path is None:
                print(f"  ✗ Markdown 转换失败，跳过")
                results.append({"paper": source_path, "status": "convert_failed"})
                continue

        # 检查是否已有审稿意见（转换完成后再次检查）
        review_draft = source_path.parent / f"{source_path.stem}_review_draft.md"
        if review_draft.exists():
            print(f"  ✓ 审稿意见已存在: {review_draft}")
            results.append({"paper": source_path, "status": "already_reviewed"})
            continue

        # Step 3: 生成审稿意见
        review_text = generate_review(md_path, review_prompt, review_prompt_cn)
        if review_text:
            review_draft.write_text(review_text.strip() + "\n", encoding="utf-8")
            print(f"  ✓ 已保存: {review_draft}")
            results.append({"paper": source_path, "status": "success"})
        else:
            print(f"  ✗ 审稿意见生成失败")
            results.append({"paper": source_path, "status": "review_failed"})

        # 随机等待，避免 API 限流
        if i < len(pending):
            wait = random.randint(5, 15)
            print(f"  等待 {wait} 秒...\n")
            time.sleep(wait)

    # Step 4: 汇总
    print("\n=== 审稿汇总 ===")
    success = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] in ("convert_failed", "review_failed"))
    skipped = sum(1 for r in results if r["status"] == "already_reviewed")
    print(f"成功: {success} 篇")
    print(f"失败: {failed} 篇")
    print(f"跳过: {skipped} 篇")
    for r in results:
        status_icon = {
            "success": "✓",
            "convert_failed": "✗",
            "review_failed": "✗",
            "already_reviewed": "○",
        }.get(r["status"], "?")
        print(f"  {status_icon} {r['paper'].name} ({r['status']})")

    return 0 if failed == 0 else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="论文自动审稿工具：扫描目录 → 转 Markdown → LLM 审稿"
    )
    parser.add_argument(
        "--year", default="2026", help="论文年份目录（默认 2026）"
    )
    parser.add_argument(
        "--paper-root",
        type=Path,
        default=None,
        help=f"论文根目录（默认 {PAPER_ROOT}）",
    )
    parser.add_argument(
        "--review-prompt",
        type=Path,
        default=None,
        help=f"审稿 prompt 文件（默认 {REVIEW_PROMPT_PATH}）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅扫描并列出待审稿论文，不执行转换和审稿",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.dry_run:
        root = args.paper_root or PAPER_ROOT
        pending = scan_pending_papers(root, args.year)
        if not pending:
            print("没有发现待审稿的论文。")
        else:
            print(f"发现 {len(pending)} 篇待审稿论文:")
            for p in pending:
                print(f"  {p}")
        raise SystemExit(0)

    raise SystemExit(run(args))

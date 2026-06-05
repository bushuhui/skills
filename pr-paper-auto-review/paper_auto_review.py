#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paper Auto Review - 多类型论文自动审稿

流程：
1. 扫描论文目录，找出没有 review*.md 的论文
2. 使用 pi-llm-server 将 PDF/DOCX/DOC 转成 Markdown
3. 根据论文类型选择对应 prompt，传给 LLM 进行审稿
4. 审稿结果保存为 review_draft.md（放在论文同级目录）

依赖：
- requests（用于 pi-llm-server 和 LLM API）

环境变量：
- PI_LLM_URL / PI_LLM_API_KEY: PDF 转 Markdown 服务（pi-llm-server）
- LLM_URL / LLM_API_KEY / LLM_MODEL: 大语言模型审稿服务

支持的审稿类型（--review-type）：
- paper_en: 英文论文
- paper_cn: 中文论文
- midterm: 中期答辩
- proposal: 开题答辩
- master_thesis: 硕士论文
- doctor_thesis: 博士论文
- fine_reading: 论文精读
- critic_mentor: 审稿屠夫-润色匠人
- polishing: 论文润色
- auto: 自动检测类型（默认）
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import time
from pathlib import Path

import requests


# Force stdout to flush after every print
_original_print = print
def _flush_print(*args, **kwargs):
    _original_print(*args, **kwargs)
    sys.stdout.flush()
print = _flush_print

# ===== 配置 =====
# PDF 转 Markdown 服务（pi-llm-server）
PI_LLM_URL = os.environ["PI_LLM_URL"]
PI_LLM_API_KEY = os.environ["PI_LLM_API_KEY"]

# 大语言模型审稿服务
LLM_URL = os.environ["LLM_URL"]
LLM_API_KEY = os.environ["LLM_API_KEY"]
LLM_MODEL = os.environ["LLM_MODEL"]

SCRIPT_DIR = Path(__file__).resolve().parent
PROMPT_DIR = SCRIPT_DIR / "prompt"
PAPER_ROOT = Path(
    "/home/bushuhui/datacenter/papers/paper-review"
)

# 审稿类型 → prompt 文件映射
REVIEW_TYPE_PROMPTS = {
    "paper_en": "paper_review_prompt.md",
    "paper_cn": "paper_review_prompt_cn.md",
    "midterm": "中期答辩.md",
    "proposal": "开题答辩.md",
    "master_thesis": "master_thesis.md",
    "doctor_thesis": "doctor_thesis.md",
    "fine_reading": "paper_fine_reading.md",
    "critic_mentor": "critic_mentor_review.md",
    "polishing": "academic_polishing.md",
    "nsfc": "NSFC.md",
}

# 自动检测：关键词 → 类型
AUTO_DETECT_KEYWORDS = {
    "中期": "midterm",
    "中期报告": "midterm",
    "中期答辩": "midterm",
    "开题": "proposal",
    "开题报告": "proposal",
    "开题答辩": "proposal",
    "硕士学位论文": "master_thesis",
    "硕士论文": "master_thesis",
    "博士学位论文": "doctor_thesis",
    "博士论文": "doctor_thesis",
    "国家自然科学基金": "nsfc",
    "NSFC": "nsfc",
    "基金申请书": "nsfc",
}

PI_LLM_HEADERS = {
    "Authorization": f"Bearer {PI_LLM_API_KEY}",
}
LLM_HEADERS = {
    "Authorization": f"Bearer {LLM_API_KEY}",
    "Content-Type": "application/json",
}


# ===== Step 1: 扫描待审稿论文 =====
def scan_pending_papers(root: Path, year: str, max_depth: int = 5) -> list[Path]:
    """找出没有 review*.md 的论文目录中的 PDF/DOCX/DOC/MD 文件。"""
    pending = []
    base = root / year
    if not base.exists():
        print(f"[WARN] 目录不存在: {base}")
        return []

    for source_path in sorted(base.rglob("*")):
        # 检查目录深度（相对于 year 目录）
        relative = source_path.relative_to(base)
        if len(relative.parts) > max_depth:
            continue
        if not source_path.is_dir():
            continue
        # 检查是否已有审稿意见（review*.md 或 review_draft.md）
        review_files = list(source_path.glob("review*.md")) + list(source_path.glob("review_draft.md"))
        if review_files:
            continue
        # 查找 PDF/DOCX/DOC/MD 文件，优先取非 review_ 开头的 Markdown
        for ext in ("*.pdf", "*.docx", "*.doc", "*.md"):
            found = [f for f in source_path.glob(ext) if not f.name.startswith("review_")]
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


# ===== Step 3: 自动检测论文类型 =====
def detect_review_type(text: str, explicit_type: str | None = None) -> tuple[str, str]:
    """
    检测论文类型，返回 (类型, 对应 prompt 文件名)。

    如果 explicit_type 不为 None，直接使用；
    否则根据内容关键词自动判断；
    默认回退到 paper_en/paper_cn（基于语言检测）。
    """
    if explicit_type and explicit_type != "auto":
        if explicit_type not in REVIEW_TYPE_PROMPTS:
            print(f"  ⚠ 未知审稿类型: {explicit_type}，将自动检测")
        else:
            return explicit_type, REVIEW_TYPE_PROMPTS[explicit_type]

    # 基于关键词自动检测
    first_500 = text[:2000]  # 只看开头部分
    for keyword, review_type in AUTO_DETECT_KEYWORDS.items():
        if keyword in first_500:
            print(f"  ℹ 自动检测到类型: {review_type} (关键词: {keyword})")
            return review_type, REVIEW_TYPE_PROMPTS[review_type]

    # 默认：按语言选择论文审稿模板
    lang = detect_language(text)
    if lang == 'zh':
        return 'paper_cn', REVIEW_TYPE_PROMPTS['paper_cn']
    else:
        return 'paper_en', REVIEW_TYPE_PROMPTS['paper_en']


# ===== Step 4: 调用 LLM 审稿 =====
def generate_review(markdown_path: Path, review_type: str) -> str | None:
    """
    将对应类型的 prompt + 论文 Markdown 内容发给 LLM，
    返回审稿意见。
    """
    print(f"  → 正在生成审稿意见...")

    # 读取 prompt
    prompt_file = REVIEW_TYPE_PROMPTS.get(review_type)
    if not prompt_file:
        print(f"  ✗ 未知的审稿类型: {review_type}")
        return None
    prompt_path = PROMPT_DIR / prompt_file
    if not prompt_path.exists():
        print(f"  ✗ 审稿 prompt 文件不存在: {prompt_path}")
        return None
    prompt = prompt_path.read_text(encoding="utf-8").strip()
    if not prompt:
        print(f"  ✗ 审稿 prompt 文件为空: {prompt_path}")
        return None

    # 读取论文内容
    content = markdown_path.read_text(encoding="utf-8")

    # 截断过长内容（64K tokens ≈ 200K 字符，留足空间给 prompt 和输出）
    max_chars = 200000
    if len(content) > max_chars:
        content = content[:max_chars]
        print(f"  ⚠ 论文内容过长，已截断至 {max_chars} 字符")

    user_message = f"""{prompt}

---

以下是需要审阅的文本内容：

{content}
"""

    # 根据类型设置 system message
    if review_type in ("paper_cn", "midterm", "proposal", "master_thesis", "doctor_thesis", "fine_reading", "critic_mentor", "polishing", "nsfc"):
        system_msg = "你是一位专业的学术审稿人。请用中文撰写审稿意见。"
    else:
        system_msg = "你是一位专业的学术审稿人。请用英文撰写审稿意见。"

    session = requests.Session()
    session.trust_env = False

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.3,
        "max_tokens": 4000,
        "stream": True,
    }

    try:
        resp = session.post(
            f"{LLM_URL}/chat/completions",
            headers=LLM_HEADERS,
            json=payload,
            timeout=900,
            stream=True,
        )
    except Exception as e:
        print(f"  ✗ LLM 请求失败: {e}")
        return None

    if resp.status_code != 200:
        print(f"  ✗ LLM 返回错误: HTTP {resp.status_code} - {resp.text[:200]}")
        return None

    # 流式接收审稿意见
    review = ""
    chunk_count = 0
    for line in resp.iter_lines():
        if not line:
            continue
        line_str = line.decode("utf-8")
        if not line_str.startswith("data: "):
            continue
        data_str = line_str[6:]
        if data_str.strip() == "[DONE]":
            break
        try:
            import json
            data = json.loads(data_str)
            delta = data.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content", "")
            if content:
                review += content
                chunk_count += 1
                if chunk_count % 20 == 0:
                    print(f"  ... 已接收 {len(review)} 字符")
        except Exception:
            continue

    if not review:
        print(f"  ✗ LLM 返回空内容")
        return None

    print(f"  ✓ 审稿意见生成完成 ({len(review)} 字符)")
    return review


# ===== 主流程 =====
def run(args: argparse.Namespace) -> int:
    year = args.year
    root = args.paper_root or PAPER_ROOT
    review_type = args.review_type or "auto"

    # 验证审稿类型
    if review_type != "auto" and review_type not in REVIEW_TYPE_PROMPTS:
        valid_types = ", ".join(REVIEW_TYPE_PROMPTS.keys())
        print(f"[ERROR] 未知审稿类型: {review_type}")
        print(f"支持的类型: {valid_types}")
        return 1

    # Step 1: 扫描
    print(f"=== 扫描待审稿论文 ({year}) ===")
    pending = scan_pending_papers(root, year, args.max_depth)
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
        # 如果输入本身就是 .md 文件，直接使用
        if source_path.suffix.lower() == ".md":
            md_path = source_path
            print(f"  ✓ Markdown 文件: {md_path}")
        else:
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
        review_draft = source_path.parent / "review_draft.md"
        if review_draft.exists():
            print(f"  ✓ 审稿意见已存在: {review_draft}")
            results.append({"paper": source_path, "status": "already_reviewed"})
            continue

        # 读取 Markdown 内容用于类型检测
        content = md_path.read_text(encoding="utf-8")
        if len(content) > 2000:
            detect_content = content[:2000]
        else:
            detect_content = content

        # 检测论文类型
        detected_type, prompt_file = detect_review_type(detect_content, review_type)
        print(f"  ℹ 使用审稿模板: {prompt_file} (类型: {detected_type})")

        # 生成审稿意见
        review_text = generate_review(md_path, detected_type)
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
        "--review-type",
        type=str,
        default=None,
        help="审稿类型（auto/paper_en/paper_cn/midterm/proposal/master_thesis/doctor_thesis/fine_reading/critic_mentor/polishing/nsfc，默认 auto 自动检测）",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="论文目录最大搜索深度（默认 5）",
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
        pending = scan_pending_papers(root, args.year, args.max_depth)
        if not pending:
            print("没有发现待审稿的论文。")
        else:
            print(f"发现 {len(pending)} 篇待审稿论文:")
            for p in pending:
                print(f"  {p}")
        raise SystemExit(0)

    raise SystemExit(run(args))

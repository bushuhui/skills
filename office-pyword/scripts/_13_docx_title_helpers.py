from __future__ import annotations

import re

from _06_docx_styles import apply_style_rule, get_or_add_paragraph_style

FRONT_HEADINGS = {"摘要", "Abstract", "目录", "图目录", "表目录", "参考文献", "致谢", "附录"}
CAPTION_PATTERNS = [
    re.compile(r"^[图表]\s*\d+(\.\d+)*"),
    re.compile(r"^(Fig\.?|Figure)\s*\d+", re.IGNORECASE),
    re.compile(r"^Table\s*\d+", re.IGNORECASE),
]
BODY_STYLE_CANDIDATES = {"Normal", "Normal (Web)", "1正文", "Body Text"}
SKIP_STYLE_NAMES = {"EndNote Bibliography", "table of figures", "图目录", "表目录"}

TITLE4_RULE = {
    "base_style": "Normal",
    "next_style": "ThesisBody",
    "font_name": "song_tnr",
    "font_size": 12.0,
    "bold": False,
    "alignment": "left",
    "line_spacing_mode": "multiple",
    "line_spacing_value": 1.25,
    "space_before_lines": 0.5,
    "space_after_lines": 0.5,
    "first_line_chars": 2.0,
    "ui_priority": 12,
}

LOWER_LEVEL_RULE = {
    "base_style": "Normal",
    "next_style": "ThesisBody",
    "font_name": "song_tnr",
    "font_size": 12.0,
    "bold": False,
    "alignment": "left",
    "line_spacing_mode": "multiple",
    "line_spacing_value": 1.25,
    "space_before_lines": 0.5,
    "space_after_lines": 0.5,
    "first_line_chars": 2.0,
    "ui_priority": 12,
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def ensure_lower_title_styles(document, style_names: tuple[str, ...] = ("ThesisTitle4",)) -> None:
    for style_name in style_names:
        style = get_or_add_paragraph_style(document, style_name)
        apply_style_rule(style, document, LOWER_LEVEL_RULE)


def ensure_title4_style(document) -> None:
    style = get_or_add_paragraph_style(document, "ThesisTitle4")
    apply_style_rule(style, document, TITLE4_RULE)


def detect_heading_level(text: str) -> int | None:
    if not text or any(pattern.match(text) for pattern in CAPTION_PATTERNS):
        return None
    if text in FRONT_HEADINGS:
        return 1
    if re.match(r"^\d+\.\d+\.\d+\s*", text):
        return 3
    if re.match(r"^\d+\.\d+\s*", text):
        return 2
    if re.match(r"^\d+\s+\S+", text):
        return 1
    if re.match(r"^第[一二三四五六七八九十百千0-9]+章", text):
        return 1
    if re.match(r"^第[一二三四五六七八九十百千0-9]+节", text):
        return 2
    if re.match(r"^[（(]?\d+[)）]\s*", text):
        return 4
    if re.match(r"^[（(][一二三四五六七八九十]+[)）]\s*", text):
        return 4
    return None

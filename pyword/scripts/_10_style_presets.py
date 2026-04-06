from __future__ import annotations

import re

from docx.enum.text import WD_ALIGN_PARAGRAPH

FONT_SIZE_PRESETS_PT = {
    "小二": 18.0,
    "三号": 16.0,
    "四号": 14.0,
    "小四": 12.0,
    "五号": 10.5,
}

FONT_PRESETS = {
    "song_tnr": {
        "eastAsia": "宋体",
        "ascii": "Times New Roman",
        "hAnsi": "Times New Roman",
        "cs": "Times New Roman",
    },
    "fangsong_tnr": {
        "eastAsia": "仿宋_GB2312",
        "ascii": "Times New Roman",
        "hAnsi": "Times New Roman",
        "cs": "Times New Roman",
    },
    "heiti_tnr": {
        "eastAsia": "黑体",
        "ascii": "Times New Roman",
        "hAnsi": "Times New Roman",
        "cs": "Times New Roman",
    },
    "all_tnr": {
        "eastAsia": "Times New Roman",
        "ascii": "Times New Roman",
        "hAnsi": "Times New Roman",
        "cs": "Times New Roman",
    },
}

FONT_ALIASES = {
    "宋体": "song_tnr",
    "仿宋": "fangsong_tnr",
    "仿宋-GB2312": "fangsong_tnr",
    "仿宋_GB2312": "fangsong_tnr",
    "黑体": "heiti_tnr",
    "Times New Roman": "all_tnr",
    "times new roman": "all_tnr",
}

ALIGNMENT_PRESETS = {
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
    "distribute": WD_ALIGN_PARAGRAPH.DISTRIBUTE,
    "左对齐": WD_ALIGN_PARAGRAPH.LEFT,
    "居中": WD_ALIGN_PARAGRAPH.CENTER,
    "右对齐": WD_ALIGN_PARAGRAPH.RIGHT,
    "两端对齐": WD_ALIGN_PARAGRAPH.JUSTIFY,
    "分散对齐": WD_ALIGN_PARAGRAPH.DISTRIBUTE,
}

STYLE_NAMES = {
    "custom_lead": "CustomLead",
    "custom_quote": "CustomQuote",
    "custom_note": "CustomNote",
    "title1": "ThesisTitle1",
    "title2": "ThesisTitle2",
    "title3": "ThesisTitle3",
    "body": "ThesisBody",
}

CUSTOM_STYLE_RULES = {
    STYLE_NAMES["custom_lead"]: {
        "base_style": "Normal",
        "next_style": STYLE_NAMES["body"],
        "font_name": "黑体",
        "font_size": "三号",
        "bold": True,
        "alignment": "居中",
        "line_spacing_mode": "multiple",
        "line_spacing_value": 1.25,
        "space_before_lines": 0.5,
        "space_after_lines": 0.5,
        "ui_priority": 1,
    },
    STYLE_NAMES["custom_quote"]: {
        "base_style": "Normal",
        "next_style": STYLE_NAMES["body"],
        "font_name": "仿宋",
        "font_size": "小四",
        "bold": False,
        "italic": True,
        "alignment": "两端对齐",
        "line_spacing_mode": "multiple",
        "line_spacing_value": 1.5,
        "left_indent_pt": 18,
        "right_indent_pt": 18,
        "space_before_pt": 6,
        "space_after_pt": 6,
        "ui_priority": 2,
    },
    STYLE_NAMES["custom_note"]: {
        "base_style": "Normal",
        "next_style": STYLE_NAMES["body"],
        "font_name": "宋体",
        "font_size": "五号",
        "bold": False,
        "alignment": "左对齐",
        "line_spacing_mode": "multiple",
        "line_spacing_value": 1.25,
        "space_before_pt": 4,
        "space_after_pt": 4,
        "ui_priority": 3,
    },
}

THESIS_STYLE_RULES = {
    STYLE_NAMES["title1"]: {
        "base_style": "Heading 1",
        "next_style": STYLE_NAMES["body"],
        "font_name": "黑体",
        "font_size": "三号",
        "bold": False,
        "alignment": "居中",
        "line_spacing_mode": "multiple",
        "line_spacing_value": 1.25,
        "space_before_lines": 1.0,
        "space_after_lines": 1.0,
        "outline_level": 0,
        "ui_priority": 9,
        "keep_next": True,
        "keep_lines": True,
    },
    STYLE_NAMES["title2"]: {
        "base_style": "Heading 2",
        "next_style": STYLE_NAMES["body"],
        "font_name": "宋体",
        "font_size": "四号",
        "bold": True,
        "alignment": "左对齐",
        "line_spacing_mode": "multiple",
        "line_spacing_value": 1.25,
        "space_before_lines": 0.5,
        "space_after_lines": 0.5,
        "outline_level": 1,
        "ui_priority": 10,
        "keep_next": True,
        "keep_lines": True,
    },
    STYLE_NAMES["title3"]: {
        "base_style": "Heading 3",
        "next_style": STYLE_NAMES["body"],
        "font_name": "宋体",
        "font_size": "小四",
        "bold": True,
        "alignment": "左对齐",
        "line_spacing_mode": "multiple",
        "line_spacing_value": 1.25,
        "space_before_lines": 0.5,
        "space_after_lines": 0.5,
        "outline_level": 2,
        "ui_priority": 11,
        "keep_next": True,
        "keep_lines": True,
    },
    STYLE_NAMES["body"]: {
        "base_style": "Normal",
        "next_style": STYLE_NAMES["body"],
        "font_name": "宋体",
        "font_size": "小四",
        "bold": False,
        "alignment": "两端对齐",
        "line_spacing_mode": "multiple",
        "line_spacing_value": 1.5,
        "space_before_pt": 0,
        "space_after_pt": 0,
        "first_line_chars": 2,
        "ui_priority": 20,
    },
}

NUMBERING_LEVELS = [
    {
        "level": 1,
        "style_name": STYLE_NAMES["title1"],
        "ilvl": 0,
        "num_fmt": "decimal",
        "lvl_text": "%1",
        "suff": "space",
    },
    {
        "level": 2,
        "style_name": STYLE_NAMES["title2"],
        "ilvl": 1,
        "num_fmt": "decimal",
        "lvl_text": "%1.%2",
        "suff": "space",
    },
    {
        "level": 3,
        "style_name": STYLE_NAMES["title3"],
        "ilvl": 2,
        "num_fmt": "decimal",
        "lvl_text": "%1.%2.%3",
        "suff": "space",
    },
]

AUTO_FORMAT_SAMPLE_LINES = [
    "第一章 绪论",
    "三维重建技术正在成为数字空间构建的重要基础能力，本段用于演示正文样式的自动归一化。",
    "1.1 研究背景",
    "随着多视角重建、神经渲染和数字孪生的发展，研究报告对标题层次和正文格式的一致性要求越来越高。",
    "1.1.1 行业需求",
    "自动化排版脚本可以让章节、节和正文在批量处理时保持统一的字体、行距和缩进规则。",
    "1.2 研究目标",
    "本节说明如何通过样式系统代替分散的直接格式设置。",
]

AUTO_FORMAT_PATTERNS = [
    (re.compile(r"^\d+\.\d+\.\d+\s+"), STYLE_NAMES["title3"]),
    (re.compile(r"^\d+\.\d+\s+"), STYLE_NAMES["title2"]),
    (re.compile(r"^第[一二三四五六七八九十百千0-9]+章\s+"), STYLE_NAMES["title1"]),
]

LINE_UNIT_SCALE = 100
CHAR_UNIT_SCALE = 100


def resolve_font_size_pt(value: str | float | int) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    key = str(value).strip()
    if key not in FONT_SIZE_PRESETS_PT:
        raise KeyError(f"未定义字号预设: {value}")
    return FONT_SIZE_PRESETS_PT[key]


def resolve_font_family(value: str) -> dict[str, str]:
    key = FONT_ALIASES.get(value, FONT_ALIASES.get(value.strip(), value.strip()))
    if key not in FONT_PRESETS:
        raise KeyError(f"未定义字体预设: {value}")
    return dict(FONT_PRESETS[key])


def resolve_alignment(value):
    if value is None or not isinstance(value, str):
        return value
    key = value.strip()
    if key not in ALIGNMENT_PRESETS:
        raise KeyError(f"未定义对齐预设: {value}")
    return ALIGNMENT_PRESETS[key]


def build_style_id(name: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9]+", name)
    if tokens:
        return "".join(token[:1].upper() + token[1:] for token in tokens)
    compact = re.sub(r"\s+", "", name)
    return compact or "CustomStyle"

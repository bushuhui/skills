from __future__ import annotations

from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"
SAMPLE_IMAGE_1 = TESTS_DIR / "images" / "image1.png"
SAMPLE_IMAGE_2 = TESTS_DIR / "images" / "image2.png"

EXTRA_STYLE_RULES = {
    "ToCTitleCn": {
        "base_style": "Normal",
        "next_style": "Normal",
        "font_name": "黑体",
        "font_size": "三号",
        "bold": False,
        "alignment": "居中",
        "line_spacing_mode": "multiple",
        "line_spacing_value": 1.25,
        "space_before_lines": 1.0,
        "space_after_lines": 1.0,
        "ui_priority": 30,
    },
    "ToCTitleEn": {
        "base_style": "Normal",
        "next_style": "Normal",
        "font_name": "黑体",
        "font_size": "三号",
        "bold": False,
        "alignment": "居中",
        "line_spacing_mode": "multiple",
        "line_spacing_value": 1.25,
        "space_before_lines": 1.0,
        "space_after_lines": 1.0,
        "ui_priority": 31,
    },
    "FigureCaption": {
        "base_style": "Normal",
        "next_style": "ThesisBody",
        "font_name": "宋体",
        "font_size": "五号",
        "bold": False,
        "alignment": "居中",
        "line_spacing_mode": "single",
        "line_spacing_value": 1.0,
        "space_before_pt": 3,
        "space_after_pt": 3,
        "ui_priority": 32,
    },
    "TableCaption": {
        "base_style": "Normal",
        "next_style": "ThesisBody",
        "font_name": "宋体",
        "font_size": "五号",
        "bold": False,
        "alignment": "居中",
        "line_spacing_mode": "single",
        "line_spacing_value": 1.0,
        "space_before_pt": 3,
        "space_after_pt": 3,
        "ui_priority": 33,
    },
    "EquationCaption": {
        "base_style": "Normal",
        "next_style": "ThesisBody",
        "font_name": "宋体",
        "font_size": "五号",
        "bold": False,
        "alignment": "右对齐",
        "line_spacing_mode": "single",
        "line_spacing_value": 1.0,
        "space_before_pt": 0,
        "space_after_pt": 0,
        "ui_priority": 34,
    },
    "BibliographyEntry": {
        "base_style": "Normal",
        "next_style": "BibliographyEntry",
        "font_name": "宋体",
        "font_size": "五号",
        "bold": False,
        "alignment": "两端对齐",
        "line_spacing_mode": "multiple",
        "line_spacing_value": 1.25,
        "space_before_pt": 0,
        "space_after_pt": 4,
        "left_indent_pt": 0,
        "hanging_chars": 2,
        "ui_priority": 35,
    },
    "ListBody": {
        "base_style": "Normal",
        "next_style": "ListBody",
        "font_name": "宋体",
        "font_size": "小四",
        "bold": False,
        "alignment": "左对齐",
        "line_spacing_mode": "multiple",
        "line_spacing_value": 1.25,
        "space_before_pt": 0,
        "space_after_pt": 2,
        "ui_priority": 36,
    },
}

SAMPLE_TABLE_DATA = [
    ["指标", "实验组 A", "实验组 B", "说明"],
    ["点云完整率", "92.3%", "88.6%", "完整率越高越好"],
    ["重投影误差", "0.47 px", "0.62 px", "误差越低越好"],
    ["建模时延", "11 min", "15 min", "时延越低越好"],
]

SAMPLE_BIBLIOGRAPHY = [
    {
        "bookmark": "ref_entry_0001",
        "number": 1,
        "text": "Zhang Y, Li H. Neural surface reconstruction for urban scenes[J]. Computer Vision Journal, 2024, 18(3): 101-118.",
    },
    {
        "bookmark": "ref_entry_0002",
        "number": 2,
        "text": "王磊, 陈晨. 三维重建与数字孪生关键技术研究[J]. 测绘学报, 2023, 52(8): 1120-1134.",
    },
]

PUNCTUATION_REPLACEMENTS_ZH = [
    ("(", "（"),
    (")", "）"),
    (",", "，"),
    (":", "："),
    (";", "；"),
]

REVIEW_FIXES = [
    {"action": "replace_text", "find": "digital twin", "replace": "digital twin system"},
    {"action": "replace_text", "find": "图1 ", "replace": "图 1 "},
    {"action": "apply_style_by_text", "contains": "绪论", "style_name": "ThesisTitle1"},
]

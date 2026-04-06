from __future__ import annotations

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
    "all_tnr": {
        "eastAsia": "Times New Roman",
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
}

FONT_ALIASES = {
    "宋体": "song_tnr",
    "仿宋": "fangsong_tnr",
    "仿宋-GB2312": "fangsong_tnr",
    "仿宋_GB2312": "fangsong_tnr",
    "times new roman": "all_tnr",
    "Times New Roman": "all_tnr",
    "黑体": "heiti_tnr",
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

# 默认字体颜色（黑色）
DEFAULT_TEXT_COLOR = "000000"

# 默认字体粗细（非加粗）
DEFAULT_BOLD = False

LINE_SPACING_MODES = {
    "single": "single",
    "multiple": "multiple",
    "exact": "exact",
    "at_least": "at_least",
}

PARAGRAPH_SPACING_UNITS = {
    "pt": "pt",
    "lines": "lines",
}

INDENT_UNITS = {
    "pt": "pt",
    "chars": "chars",
}

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

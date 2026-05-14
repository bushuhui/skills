from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from docx.enum.text import WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from docx.text.run import Run

import _09_format_presets as PRESETS

XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"

# 默认样式常量
DEFAULT_TEXT_COLOR_HEX = PRESETS.DEFAULT_TEXT_COLOR  # "000000" 黑色
DEFAULT_BOLD = PRESETS.DEFAULT_BOLD  # False 非加粗


def ensure_tests_dir(current_file: str | Path) -> Path:
    tests_dir = Path(current_file).resolve().parent.parent / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    return tests_dir


def set_rfonts(r_pr, font_spec: dict[str, str]) -> None:
    r_fonts = r_pr.rFonts
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)
    for key, value in font_spec.items():
        r_fonts.set(qn(f"w:{key}"), value)


def set_run_font(run, font_name: str, font_size) -> None:
    font_spec = PRESETS.resolve_font_family(font_name)
    run.font.name = font_spec["ascii"]
    run.font.size = Pt(PRESETS.resolve_font_size_pt(font_size))
    set_rfonts(run._element.get_or_add_rPr(), font_spec)


def set_default_style(document) -> None:
    normal_style = document.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(PRESETS.resolve_font_size_pt("小四"))
    set_rfonts(normal_style.element.get_or_add_rPr(), PRESETS.resolve_font_family("宋体"))
    normal_style.paragraph_format.line_spacing = 1.5
    normal_style.paragraph_format.space_before = Pt(0)
    normal_style.paragraph_format.space_after = Pt(0)


def apply_direct_format(
    run,
    font_name: str | None = None,
    font_size=None,
    bold: bool | None = None,
    italic: bool | None = None,
    underline: bool | None = None,
    color_hex: str | None = None,
) -> None:
    if font_name is not None or font_size is not None:
        set_run_font(run, font_name or "宋体", font_size or "小四")
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if underline is not None:
        run.underline = underline
    if color_hex is not None:
        run.font.color.rgb = RGBColor.from_string(color_hex)


def add_run_with_default_style(
    paragraph,
    text: str,
    font_name: str | None = None,
    font_size=None,
    bold: bool | None = None,
    italic: bool | None = None,
    underline: bool | None = None,
    color_hex: str | None = None,
):
    """
    在段落中添加一个带默认样式控制的 Run。

    默认样式（当参数为 None 或未指定时）：
    - 字体颜色：黑色 (000000)
    - 字体粗细：不加粗 (False)

    Args:
        paragraph: 段落对象
        text: 要添加的文本内容
        font_name: 字体名称（如 "宋体"、"Times New Roman"），默认 None
        font_size: 字号（如 "小四"、"五号"、12），默认 None
        bold: 是否加粗，默认 None（应用默认不加粗）
        italic: 是否斜体，默认 None
        underline: 是否下划线，默认 None
        color_hex: 字体颜色十六进制值（如 "FF0000"），默认 None（应用默认黑色）

    Returns:
        新创建的 Run 对象
    """
    run = paragraph.add_run(text)

    # 应用默认样式：黑色字体
    run.font.color.rgb = RGBColor.from_string(DEFAULT_TEXT_COLOR_HEX)
    # 应用默认样式：不加粗
    run.bold = DEFAULT_BOLD

    # 应用用户明确指定的样式覆盖（仅当参数不是 None 时）
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if underline is not None:
        run.underline = underline
    if color_hex is not None:
        run.font.color.rgb = RGBColor.from_string(color_hex)

    # 应用字体设置
    if font_name is not None or font_size is not None:
        set_run_font(run, font_name or "宋体", font_size or "小四")

    return run


def set_run_border(run, value: str = "single", color: str = "C0504D", size: int = 12, space: int = 2) -> None:
    r_pr = run._element.get_or_add_rPr()
    border = r_pr.find(qn("w:bdr"))
    if border is None:
        border = OxmlElement("w:bdr")
        r_pr.append(border)
    border.set(qn("w:val"), value)
    border.set(qn("w:sz"), str(size))
    border.set(qn("w:space"), str(space))
    border.set(qn("w:color"), color)


def set_paragraph_border(paragraph, value: str = "single", color: str = "4F81BD", size: int = 12, space: int = 6) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    p_bdr = p_pr.find(qn("w:pBdr"))
    if p_bdr is None:
        p_bdr = OxmlElement("w:pBdr")
        p_pr.append(p_bdr)
    for child in list(p_bdr):
        p_bdr.remove(child)
    for edge in ("top", "left", "bottom", "right"):
        border = OxmlElement(f"w:{edge}")
        border.set(qn("w:val"), value)
        border.set(qn("w:sz"), str(size))
        border.set(qn("w:space"), str(space))
        border.set(qn("w:color"), color)
        p_bdr.append(border)


def get_or_add_spacing(paragraph):
    p_pr = paragraph._p.get_or_add_pPr()
    spacing = p_pr.spacing
    if spacing is None:
        spacing = p_pr.get_or_add_spacing()
    return spacing


def apply_line_spacing(paragraph, mode: str, value: float | None = None) -> None:
    paragraph_format = paragraph.paragraph_format
    if mode == PRESETS.LINE_SPACING_MODES["single"]:
        paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        paragraph_format.line_spacing = 1.0
    elif mode == PRESETS.LINE_SPACING_MODES["multiple"]:
        paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        paragraph_format.line_spacing = float(value)
    elif mode == PRESETS.LINE_SPACING_MODES["exact"]:
        paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        paragraph_format.line_spacing = Pt(float(value))
    elif mode == PRESETS.LINE_SPACING_MODES["at_least"]:
        paragraph_format.line_spacing_rule = WD_LINE_SPACING.AT_LEAST
        paragraph_format.line_spacing = Pt(float(value))
    else:
        raise ValueError(f"不支持的行距模式: {mode}")


def apply_multiple_spacing(paragraph, factor: float) -> None:
    paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    paragraph.paragraph_format.line_spacing = factor


def apply_spacing_before_after(paragraph, before=0, after=0, unit: str = "pt") -> None:
    paragraph_format = paragraph.paragraph_format
    spacing = get_or_add_spacing(paragraph)
    if unit == PRESETS.PARAGRAPH_SPACING_UNITS["pt"]:
        paragraph_format.space_before = Pt(float(before))
        paragraph_format.space_after = Pt(float(after))
        for attr in ("w:beforeLines", "w:afterLines"):
            if spacing.get(qn(attr)) is not None:
                del spacing.attrib[qn(attr)]
        return
    if unit == PRESETS.PARAGRAPH_SPACING_UNITS["lines"]:
        paragraph_format.space_before = Pt(0)
        paragraph_format.space_after = Pt(0)
        spacing.set(qn("w:beforeLines"), str(int(round(float(before) * PRESETS.LINE_UNIT_SCALE))))
        spacing.set(qn("w:afterLines"), str(int(round(float(after) * PRESETS.LINE_UNIT_SCALE))))
        return
    raise ValueError(f"不支持的段前段后单位: {unit}")


def apply_lines_spacing_before_after(paragraph, before_lines: float = 0, after_lines: float = 0) -> None:
    apply_spacing_before_after(paragraph, before_lines, after_lines, PRESETS.PARAGRAPH_SPACING_UNITS["lines"])


def get_or_add_ind(paragraph):
    p_pr = paragraph._p.get_or_add_pPr()
    ind = p_pr.ind
    if ind is None:
        ind = p_pr.get_or_add_ind()
    return ind


def apply_indentation(
    paragraph,
    left_indent_pt: float | None = None,
    right_indent_pt: float | None = None,
    first_line_indent_pt: float | None = None,
    hanging_indent_pt: float | None = None,
    first_line_chars: float | None = None,
    hanging_chars: float | None = None,
) -> None:
    paragraph_format = paragraph.paragraph_format
    if left_indent_pt is not None:
        paragraph_format.left_indent = Pt(float(left_indent_pt))
    if right_indent_pt is not None:
        paragraph_format.right_indent = Pt(float(right_indent_pt))

    ind = get_or_add_ind(paragraph)
    for attr in ("w:firstLineChars", "w:hangingChars"):
        if ind.get(qn(attr)) is not None:
            del ind.attrib[qn(attr)]

    if first_line_indent_pt is not None:
        paragraph_format.first_line_indent = Pt(float(first_line_indent_pt))
    elif hanging_indent_pt is not None:
        paragraph_format.first_line_indent = Pt(-float(hanging_indent_pt))
    else:
        paragraph_format.first_line_indent = None

    if first_line_chars is not None:
        paragraph_format.first_line_indent = Pt(0)
        ind.set(qn("w:firstLineChars"), str(int(round(float(first_line_chars) * PRESETS.CHAR_UNIT_SCALE))))
    elif hanging_chars is not None:
        paragraph_format.first_line_indent = Pt(0)
        ind.set(qn("w:hangingChars"), str(int(round(float(hanging_chars) * PRESETS.CHAR_UNIT_SCALE))))


def apply_first_line_chars(paragraph, chars: float) -> None:
    apply_indentation(paragraph, first_line_chars=chars)


def clone_run_with_text(run, text: str):
    new_r = deepcopy(run._element)
    for child in list(new_r):
        if child.tag != qn("w:rPr"):
            new_r.remove(child)
    text_element = OxmlElement("w:t")
    if text.startswith(" ") or text.endswith(" "):
        text_element.set(XML_SPACE, "preserve")
    text_element.text = text
    new_r.append(text_element)
    return new_r


def find_match_ranges(text: str, needle: str, occurrence: int | str = "all") -> list[tuple[int, int]]:
    if not needle:
        raise ValueError("needle 不能为空")
    matches: list[tuple[int, int]] = []
    start = 0
    while True:
        index = text.find(needle, start)
        if index == -1:
            break
        matches.append((index, index + len(needle)))
        start = index + len(needle)
    if occurrence == "all":
        return matches
    if isinstance(occurrence, int):
        return [matches[occurrence - 1]] if 0 < occurrence <= len(matches) else []
    raise ValueError(f"不支持的 occurrence 参数: {occurrence}")


def rebuild_runs_with_targets(paragraph, ranges: list[tuple[int, int]], formatter) -> None:
    if not ranges:
        return
    original_runs = list(paragraph.runs)
    rebuilt_runs: list[tuple[object, bool]] = []
    cursor = 0
    for run in original_runs:
        text = run.text
        if not text:
            rebuilt_runs.append((deepcopy(run._element), False))
            continue
        run_start = cursor
        run_end = cursor + len(text)
        breakpoints = {0, len(text)}
        for left, right in ranges:
            overlap_start = max(run_start, left)
            overlap_end = min(run_end, right)
            if overlap_start < overlap_end:
                breakpoints.add(overlap_start - run_start)
                breakpoints.add(overlap_end - run_start)
        ordered_points = sorted(breakpoints)
        for left_index, right_index in zip(ordered_points, ordered_points[1:]):
            segment = text[left_index:right_index]
            if not segment:
                continue
            absolute_left = run_start + left_index
            absolute_right = run_start + right_index
            is_target = any(absolute_left >= start and absolute_right <= end for start, end in ranges)
            rebuilt_runs.append((clone_run_with_text(run, segment), is_target))
        cursor = run_end
    for run in original_runs:
        paragraph._p.remove(run._element)
    for run_element, is_target in rebuilt_runs:
        paragraph._p.append(run_element)
        if is_target:
            formatter(Run(run_element, paragraph))


def format_text_fragment(paragraph, needle: str, occurrence: int | str = "all", formatter=None) -> None:
    formatter = formatter or (lambda run: None)
    ranges = find_match_ranges(paragraph.text, needle, occurrence)
    rebuild_runs_with_targets(paragraph, ranges, formatter)

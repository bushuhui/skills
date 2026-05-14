from __future__ import annotations

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def _set_border(parent, tag: str, value: str, size: int = 8, color: str = "000000", space: int = 0) -> None:
    element = OxmlElement(tag)
    element.set(qn("w:val"), value)
    element.set(qn("w:sz"), str(size))
    element.set(qn("w:space"), str(space))
    element.set(qn("w:color"), color)
    parent.append(element)


def set_table_borders(
    table,
    top: tuple[str, int, str] = ("single", 12, "000000"),
    bottom: tuple[str, int, str] = ("single", 12, "000000"),
    left: tuple[str, int, str] = ("nil", 0, "000000"),
    right: tuple[str, int, str] = ("nil", 0, "000000"),
    inside_h: tuple[str, int, str] = ("nil", 0, "000000"),
    inside_v: tuple[str, int, str] = ("nil", 0, "000000"),
) -> None:
    tbl_pr = table._tbl.tblPr
    tbl_borders = tbl_pr.first_child_found_in("w:tblBorders")
    if tbl_borders is None:
        tbl_borders = OxmlElement("w:tblBorders")
        tbl_pr.append(tbl_borders)

    for child in list(tbl_borders):
        tbl_borders.remove(child)

    _set_border(tbl_borders, "w:top", *top)
    _set_border(tbl_borders, "w:left", *left)
    _set_border(tbl_borders, "w:bottom", *bottom)
    _set_border(tbl_borders, "w:right", *right)
    _set_border(tbl_borders, "w:insideH", *inside_h)
    _set_border(tbl_borders, "w:insideV", *inside_v)


def hide_table_borders(table) -> None:
    set_table_borders(
        table,
        top=("nil", 0, "FFFFFF"),
        bottom=("nil", 0, "FFFFFF"),
        left=("nil", 0, "FFFFFF"),
        right=("nil", 0, "FFFFFF"),
        inside_h=("nil", 0, "FFFFFF"),
        inside_v=("nil", 0, "FFFFFF"),
    )


def apply_three_line_table(table) -> None:
    set_table_borders(
        table,
        top=("single", 16, "000000"),
        bottom=("single", 16, "000000"),
        left=("nil", 0, "000000"),
        right=("nil", 0, "000000"),
        inside_h=("nil", 0, "000000"),
        inside_v=("nil", 0, "000000"),
    )

    first_row = table.rows[0]
    for cell in first_row.cells:
        tc_pr = cell._tc.get_or_add_tcPr()
        tc_borders = tc_pr.first_child_found_in("w:tcBorders")
        if tc_borders is None:
            tc_borders = OxmlElement("w:tcBorders")
            tc_pr.append(tc_borders)
        for child in list(tc_borders):
            tc_borders.remove(child)
        _set_border(tc_borders, "w:bottom", "single", 8, "000000")


def format_cell_text(cell, font_name: str = "宋体", font_size_pt: float = 10.5, bold: bool = False, alignment=WD_ALIGN_PARAGRAPH.CENTER) -> None:
    for paragraph in cell.paragraphs:
        paragraph.alignment = alignment
        for run in paragraph.runs:
            run.font.name = font_name
            run.font.size = run.font.size or None
            run.font.bold = bold
            r_pr = run._element.get_or_add_rPr()
            r_fonts = r_pr.rFonts
            if r_fonts is None:
                r_fonts = OxmlElement("w:rFonts")
                r_pr.append(r_fonts)
            for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
                r_fonts.set(qn(f"w:{attr}"), "Times New Roman" if attr != "eastAsia" else font_name)
            sz = r_pr.find(qn("w:sz"))
            if sz is None:
                sz = OxmlElement("w:sz")
                r_pr.append(sz)
            sz.set(qn("w:val"), str(int(round(font_size_pt * 2))))

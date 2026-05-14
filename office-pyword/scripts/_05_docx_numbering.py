from __future__ import annotations

from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def next_abstract_num_id(numbering_root) -> int:
    values = [int(item) for item in numbering_root.xpath("./w:abstractNum/@w:abstractNumId")]
    return max(values, default=-1) + 1


def append_before_nums(numbering_root, element) -> None:
    nums = numbering_root.xpath("./w:num")
    if nums:
        nums[0].addprevious(element)
    else:
        numbering_root.append(element)


def ensure_numbering(document, levels: list[dict[str, object]]) -> int:
    numbering_root = document.part.numbering_part.numbering_definitions._numbering
    abstract_num_id = next_abstract_num_id(numbering_root)

    abstract_num = OxmlElement("w:abstractNum")
    abstract_num.set(qn("w:abstractNumId"), str(abstract_num_id))

    nsid = OxmlElement("w:nsid")
    nsid.set(qn("w:val"), f"{0xE1000000 + abstract_num_id:08X}")
    abstract_num.append(nsid)

    multi = OxmlElement("w:multiLevelType")
    multi.set(qn("w:val"), "multilevel" if len(levels) > 1 else "singleLevel")
    abstract_num.append(multi)

    tmpl = OxmlElement("w:tmpl")
    tmpl.set(qn("w:val"), f"{0xF2000000 + abstract_num_id:08X}")
    abstract_num.append(tmpl)

    for level in levels:
        lvl = OxmlElement("w:lvl")
        lvl.set(qn("w:ilvl"), str(level["ilvl"]))

        start = OxmlElement("w:start")
        start.set(qn("w:val"), str(level.get("start", 1)))
        lvl.append(start)

        num_fmt = OxmlElement("w:numFmt")
        num_fmt.set(qn("w:val"), str(level["num_fmt"]))
        lvl.append(num_fmt)

        if level.get("p_style_id"):
            p_style = OxmlElement("w:pStyle")
            p_style.set(qn("w:val"), str(level["p_style_id"]))
            lvl.append(p_style)

        lvl_text = OxmlElement("w:lvlText")
        lvl_text.set(qn("w:val"), str(level["lvl_text"]))
        lvl.append(lvl_text)

        suff = OxmlElement("w:suff")
        suff.set(qn("w:val"), str(level.get("suff", "space")))
        lvl.append(suff)

        lvl_jc = OxmlElement("w:lvlJc")
        lvl_jc.set(qn("w:val"), str(level.get("jc", "left")))
        lvl.append(lvl_jc)

        p_pr = OxmlElement("w:pPr")
        ind = OxmlElement("w:ind")
        ind.set(qn("w:left"), str(level.get("left", 360)))
        ind.set(qn("w:hanging"), str(level.get("hanging", 360)))
        p_pr.append(ind)
        lvl.append(p_pr)

        if level.get("bullet_font"):
            r_pr = OxmlElement("w:rPr")
            r_fonts = OxmlElement("w:rFonts")
            r_fonts.set(qn("w:ascii"), str(level["bullet_font"]))
            r_fonts.set(qn("w:hAnsi"), str(level["bullet_font"]))
            r_fonts.set(qn("w:hint"), "default")
            r_pr.append(r_fonts)
            lvl.append(r_pr)

        abstract_num.append(lvl)

    append_before_nums(numbering_root, abstract_num)
    num = numbering_root.add_num(abstract_num_id)
    return int(num.numId)


def apply_numbering(paragraph, num_id: int, ilvl: int = 0) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    num_pr = p_pr.numPr
    if num_pr is None:
        num_pr = p_pr.get_or_add_numPr()
    num_pr.get_or_add_ilvl().val = ilvl
    num_pr.get_or_add_numId().val = num_id

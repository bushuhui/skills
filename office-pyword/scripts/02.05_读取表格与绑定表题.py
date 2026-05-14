import csv
import json
import re
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph
from lxml import etree

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}

TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"
INPUT_DOCX = TESTS_DIR / "测试文档.docx"

FRONT_HEADINGS = {"摘要", "Abstract", "目录", "图目录", "表目录", "参考文献", "致谢", "附录"}
EXCLUDED_STYLES = {"table of figures", "图目录2", "表目录3", "表目录2", "图目录"}
STYLE_HINTS = {"Subtitle", "Title", "1正文", "heading 1", "heading 2", "heading 3"}

NUMERIC_HEADING_PATTERNS = [
    (re.compile(r"^(\d+\.\d+\.\d+)\s*(.+)$"), 3),
    (re.compile(r"^(\d+\.\d+)\s*(.+)$"), 2),
    (re.compile(r"^(\d+)\s+(.+)$"), 1),
    (re.compile(r"^(第[一二三四五六七八九十百千0-9]+章)\s*(.+)$"), 1),
    (re.compile(r"^(第[一二三四五六七八九十百千0-9]+节)\s*(.+)$"), 2),
    (re.compile(r"^([一二三四五六七八九十]+、)\s*(.+)$"), 2),
    (re.compile(r"^(（[一二三四五六七八九十]+）)\s*(.+)$"), 3),
]
CAPTION_PATTERNS = [
    re.compile(r"^[图表]\s*\d+(\.\d+)*"),
    re.compile(r"^(Fig\.?|Figure)\s*\d+", re.IGNORECASE),
    re.compile(r"^Table\s*\d+", re.IGNORECASE),
]
TABLE_TITLE_CN = re.compile(r"^表\s*\d+(\.\d+)*")
TABLE_TITLE_EN = re.compile(r"^Table\s*\d+(\.\d+)*", re.IGNORECASE)


def first_or_none(values):
    return values[0] if values else None


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def load_style_metadata(zip_file: ZipFile) -> dict[str, dict[str, int | str | None]]:
    style_map: dict[str, dict[str, int | str | None]] = {}
    if "word/styles.xml" not in zip_file.namelist():
        return style_map

    styles_root = etree.fromstring(zip_file.read("word/styles.xml"))
    for style in styles_root.xpath(".//w:style", namespaces=NS):
        style_id = style.get(f"{{{NS['w']}}}styleId")
        if not style_id:
            continue
        style_name = first_or_none(style.xpath("./w:name/@w:val", namespaces=NS))
        outline_level = first_or_none(style.xpath("./w:pPr/w:outlineLvl/@w:val", namespaces=NS))
        style_map[style_id] = {
            "name": style_name,
            "outline_level": int(outline_level) if outline_level is not None else None,
        }
    return style_map


def extract_paragraph_metadata(docx_path: Path) -> tuple[Document, list[dict[str, object]]]:
    document = Document(docx_path)
    with ZipFile(docx_path) as zip_file:
        style_map = load_style_metadata(zip_file)
        document_root = etree.fromstring(zip_file.read("word/document.xml"))

    body = document_root.find("w:body", namespaces=NS)
    paragraph_elements = [child for child in body if local_name(child.tag) == "p"]

    metadata: list[dict[str, object]] = []
    for index, (paragraph, element) in enumerate(zip(document.paragraphs, paragraph_elements), start=1):
        style_id = first_or_none(element.xpath("./w:pPr/w:pStyle/@w:val", namespaces=NS))
        direct_outline = first_or_none(element.xpath("./w:pPr/w:outlineLvl/@w:val", namespaces=NS))
        style_outline = style_map.get(style_id, {}).get("outline_level")

        metadata.append(
            {
                "paragraph_index": index,
                "text": normalize_text(paragraph.text),
                "style_id": style_id,
                "style_name": paragraph.style.name if paragraph.style is not None else style_map.get(style_id, {}).get("name", ""),
                "outline_level": int(direct_outline) if direct_outline is not None else style_outline,
                "paragraph": paragraph,
            }
        )
    return document, metadata


def is_bold_paragraph(paragraph) -> bool:
    for run in paragraph.runs:
        if run.text.strip() and run.bold is True:
            return True
    return bool(paragraph.style and paragraph.style.font and paragraph.style.font.bold)


def is_caption_or_catalog(text: str, style_name: str) -> bool:
    if style_name in EXCLUDED_STYLES:
        return True
    return any(pattern.match(text) for pattern in CAPTION_PATTERNS)


def extract_heading_number(text: str) -> tuple[str | None, str | None, int | None]:
    for pattern, level in NUMERIC_HEADING_PATTERNS:
        match = pattern.match(text)
        if match:
            return match.group(1), normalize_text(match.group(2)), level
    return None, None, None


def detect_heading(meta: dict[str, object]) -> dict[str, object]:
    text = str(meta["text"])
    style_name = str(meta["style_name"] or "")
    paragraph = meta["paragraph"]
    outline_level = meta.get("outline_level")

    if not text:
        return {"is_heading": False, "heading_level": None, "heading_number": None}

    if is_caption_or_catalog(text, style_name):
        return {"is_heading": False, "heading_level": None, "heading_number": None}

    if text in FRONT_HEADINGS:
        return {"is_heading": True, "heading_level": 1, "heading_number": None}

    heading_number, _, number_level = extract_heading_number(text)
    style_hint = style_name in STYLE_HINTS
    short_text = len(text) <= 80 and not text.endswith("。")
    bold_hint = is_bold_paragraph(paragraph)

    if heading_number and number_level is not None and (style_hint or outline_level is not None or short_text):
        return {"is_heading": True, "heading_level": min(number_level, 3), "heading_number": heading_number}

    if outline_level is not None and style_hint and short_text:
        return {"is_heading": True, "heading_level": min(int(outline_level) + 1, 3), "heading_number": None}

    if style_name == "Title" and short_text:
        return {"is_heading": True, "heading_level": 3, "heading_number": None}

    if style_name in {"Subtitle", "1正文"} and short_text:
        return {"is_heading": True, "heading_level": 1, "heading_number": None}

    if bold_hint and short_text:
        return {"is_heading": True, "heading_level": 1, "heading_number": None}

    return {"is_heading": False, "heading_level": None, "heading_number": None}


def annotate_heading_paths(metadata: list[dict[str, object]]) -> list[dict[str, object]]:
    stack: dict[int, str] = {}
    annotated: list[dict[str, object]] = []

    for item in metadata:
        detection = detect_heading(item)
        row = dict(item)
        row.update(detection)

        if detection["is_heading"]:
            level = int(detection["heading_level"])
            stack[level] = str(item["text"])
            for deeper in range(level + 1, 10):
                stack.pop(deeper, None)
            row["heading_path"] = " > ".join(stack[key] for key in sorted(stack))
        else:
            row["heading_path"] = " > ".join(stack[key] for key in sorted(stack))

        annotated.append(row)

    return annotated


def iter_block_items(document):
    body = document.element.body
    for child in body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


def collect_table_cells(table: Table) -> tuple[list[list[str]], list[list[list[int]]]]:
    rows: list[list[str]] = []
    merged_positions: dict[int, list[list[int]]] = {}

    for row_index, row in enumerate(table.rows, start=1):
        row_values: list[str] = []
        for col_index, cell in enumerate(row.cells, start=1):
            row_values.append(normalize_text(cell.text))
            merged_positions.setdefault(id(cell._tc), []).append([row_index, col_index])
        rows.append(row_values)

    merged_cells = [positions for positions in merged_positions.values() if len(positions) > 1]
    return rows, merged_cells


def bind_table_titles(recent_paragraphs: list[dict[str, object]]) -> tuple[str | None, str | None]:
    title_cn = None
    title_en = None

    for item in reversed(recent_paragraphs[-4:]):
        text = str(item["text"])
        if not title_en and TABLE_TITLE_EN.match(text):
            title_en = text
        if not title_cn and TABLE_TITLE_CN.match(text):
            title_cn = text
        if title_cn and title_en:
            break

    return title_cn, title_en


def write_csv(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def main() -> None:
    if not INPUT_DOCX.exists():
        raise FileNotFoundError(f"未找到输入文件: {INPUT_DOCX}")

    TESTS_DIR.mkdir(parents=True, exist_ok=True)
    document, metadata = extract_paragraph_metadata(INPUT_DOCX)
    annotated = annotate_heading_paths(metadata)

    tables_output = []
    recent_paragraphs: list[dict[str, object]] = []
    paragraph_pointer = 0
    body_order_index = 0
    table_count = 0

    for block in iter_block_items(document):
        body_order_index += 1
        if isinstance(block, Paragraph):
            if paragraph_pointer < len(annotated):
                row = annotated[paragraph_pointer]
                paragraph_pointer += 1
                if row["text"]:
                    recent_paragraphs.append(row)
            continue

        table_count += 1
        rows, merged_cells = collect_table_cells(block)
        title_cn, title_en = bind_table_titles(recent_paragraphs)
        heading_path = recent_paragraphs[-1]["heading_path"] if recent_paragraphs else ""
        title_paragraph_index = recent_paragraphs[-1]["paragraph_index"] if recent_paragraphs else None

        table_record = {
            "table_index": table_count,
            "body_order_index": body_order_index,
            "title_cn": title_cn,
            "title_en": title_en,
            "title_paragraph_index": title_paragraph_index,
            "heading_path": heading_path,
            "row_count": len(rows),
            "col_count": max((len(item) for item in rows), default=0),
            "continued": bool(title_cn and "续" in title_cn),
            "merged_cells": merged_cells,
            "cells": rows,
        }
        tables_output.append(table_record)

        csv_path = TESTS_DIR / f"2.5_table_{table_count:02d}.csv"
        write_csv(csv_path, rows)

    json_path = TESTS_DIR / "2.5_tables.json"
    json_path.write_text(json.dumps(tables_output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[2.5] 输入文档: {INPUT_DOCX}")
    print(f"[2.5] 已输出表格 JSON: {json_path}")
    print(f"[2.5] 提取表格数量: {len(tables_output)}")
    if tables_output:
        print(f"[2.5] 首个表格 CSV: {TESTS_DIR / '2.5_table_01.csv'}")


if __name__ == "__main__":
    main()

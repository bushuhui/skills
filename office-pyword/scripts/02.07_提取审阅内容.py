import csv
import json
import re
from pathlib import Path
from zipfile import ZipFile

from docx import Document
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
        return {"is_heading": False, "heading_level": None}

    if is_caption_or_catalog(text, style_name):
        return {"is_heading": False, "heading_level": None}

    if text in FRONT_HEADINGS:
        return {"is_heading": True, "heading_level": 1}

    heading_number, _, number_level = extract_heading_number(text)
    style_hint = style_name in STYLE_HINTS
    short_text = len(text) <= 80 and not text.endswith("。")
    bold_hint = is_bold_paragraph(paragraph)

    if heading_number and number_level is not None and (style_hint or outline_level is not None or short_text):
        return {"is_heading": True, "heading_level": min(number_level, 3)}

    if outline_level is not None and style_hint and short_text:
        return {"is_heading": True, "heading_level": min(int(outline_level) + 1, 3)}

    if style_name == "Title" and short_text:
        return {"is_heading": True, "heading_level": 3}

    if style_name in {"Subtitle", "1正文"} and short_text:
        return {"is_heading": True, "heading_level": 1}

    if bold_hint and short_text:
        return {"is_heading": True, "heading_level": 1}

    return {"is_heading": False, "heading_level": None}


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


def parse_document_root(zip_file: ZipFile):
    return etree.fromstring(zip_file.read("word/document.xml"))


def get_top_level_paragraphs(document_root):
    body = document_root.find("w:body", namespaces=NS)
    return [child for child in body if local_name(child.tag) == "p"]


def get_all_body_paragraphs(document_root):
    body = document_root.find("w:body", namespaces=NS)
    return body.xpath(".//w:p", namespaces=NS)


def build_recursive_paragraph_context(document_root, top_level_paragraphs, heading_path_map: dict[int, str]):
    top_level_lookup = {id(element): index for index, element in enumerate(top_level_paragraphs, start=1)}
    recursive_paragraphs = get_all_body_paragraphs(document_root)
    context_rows = []
    current_heading_path = ""

    for xml_index, element in enumerate(recursive_paragraphs, start=1):
        top_level_index = top_level_lookup.get(id(element))
        if top_level_index is not None:
            current_heading_path = heading_path_map.get(top_level_index, current_heading_path)

        context_rows.append(
            {
                "xml_index": xml_index,
                "top_level_paragraph_index": top_level_index,
                "text": normalize_text("".join(element.xpath(".//w:t/text()", namespaces=NS))),
                "heading_path": current_heading_path,
                "element": element,
            }
        )

    return context_rows


def extract_comment_anchor_info(
    paragraph_context_rows,
) -> dict[str, dict[str, object]]:
    starts: dict[str, int] = {}
    ends: dict[str, int] = {}
    refs: dict[str, int] = {}

    paragraph_lookup = {row["xml_index"]: row for row in paragraph_context_rows}

    for row in paragraph_context_rows:
        paragraph_index = row["xml_index"]
        element = row["element"]
        for comment_id in set(element.xpath(".//w:commentRangeStart/@w:id", namespaces=NS)):
            starts.setdefault(comment_id, paragraph_index)
        for comment_id in set(element.xpath(".//w:commentRangeEnd/@w:id", namespaces=NS)):
            ends[comment_id] = paragraph_index
        for comment_id in set(element.xpath(".//w:commentReference/@w:id", namespaces=NS)):
            refs.setdefault(comment_id, paragraph_index)

    anchors: dict[str, dict[str, object]] = {}
    all_ids = set(starts) | set(ends) | set(refs)
    for comment_id in all_ids:
        paragraph_index = refs.get(comment_id) or starts.get(comment_id) or ends.get(comment_id)
        start_index = starts.get(comment_id, paragraph_index)
        end_index = ends.get(comment_id, paragraph_index)
        if paragraph_index is None:
            continue

        range_text = "\n".join(
            paragraph_lookup.get(idx, {}).get("text", "")
            for idx in range(start_index, end_index + 1)
            if paragraph_lookup.get(idx, {}).get("text", "")
        )

        anchors[comment_id] = {
            "paragraph_index": paragraph_index,
            "top_level_paragraph_index": paragraph_lookup.get(paragraph_index, {}).get("top_level_paragraph_index"),
            "paragraph_text": paragraph_lookup.get(paragraph_index, {}).get("text", ""),
            "heading_path": paragraph_lookup.get(paragraph_index, {}).get("heading_path", ""),
            "range_text": range_text,
            "start_paragraph_index": start_index,
            "end_paragraph_index": end_index,
        }

    return anchors


def extract_comments(zip_file: ZipFile, anchors: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    if "word/comments.xml" not in zip_file.namelist():
        return []

    comments_root = etree.fromstring(zip_file.read("word/comments.xml"))
    items: list[dict[str, object]] = []

    for comment in comments_root.xpath(".//w:comment", namespaces=NS):
        comment_id = comment.get(f"{{{NS['w']}}}id", "")
        anchor = anchors.get(comment_id, {})
        text = normalize_text("".join(comment.xpath(".//w:t/text()", namespaces=NS)))

        items.append(
            {
                "type": "comment",
                "comment_id": comment_id,
                "author": comment.get(f"{{{NS['w']}}}author", ""),
                "time": comment.get(f"{{{NS['w']}}}date", ""),
                "text": text,
                "paragraph_index": anchor.get("paragraph_index"),
                "top_level_paragraph_index": anchor.get("top_level_paragraph_index"),
                "paragraph_text": anchor.get("paragraph_text", ""),
                "heading_path": anchor.get("heading_path", ""),
                "range_text": anchor.get("range_text", ""),
                "start_paragraph_index": anchor.get("start_paragraph_index"),
                "end_paragraph_index": anchor.get("end_paragraph_index"),
            }
        )

    return items


def extract_tracked_changes(
    document_root,
    paragraph_context_rows,
) -> list[dict[str, object]]:
    paragraph_index_map = {id(row["element"]): row for row in paragraph_context_rows}
    items: list[dict[str, object]] = []

    for tag_name, item_type in [("ins", "insert"), ("del", "delete"), ("moveFrom", "moveFrom"), ("moveTo", "moveTo")]:
        for change in document_root.xpath(f".//w:{tag_name}", namespaces=NS):
            parent = change
            while parent is not None and local_name(parent.tag) != "p":
                parent = parent.getparent()

            paragraph_info = paragraph_index_map.get(id(parent)) if parent is not None else None
            paragraph_index = paragraph_info["xml_index"] if paragraph_info is not None else None
            text = normalize_text("".join(change.xpath(".//w:t/text() | .//w:delText/text()", namespaces=NS)))

            items.append(
                {
                    "type": item_type,
                    "comment_id": "",
                    "author": change.get(f"{{{NS['w']}}}author", ""),
                    "time": change.get(f"{{{NS['w']}}}date", ""),
                    "text": text,
                    "paragraph_index": paragraph_index,
                    "top_level_paragraph_index": paragraph_info["top_level_paragraph_index"] if paragraph_info is not None else None,
                    "paragraph_text": paragraph_info["text"] if paragraph_info is not None else "",
                    "heading_path": paragraph_info["heading_path"] if paragraph_info is not None else "",
                    "range_text": text,
                    "start_paragraph_index": paragraph_index,
                    "end_paragraph_index": paragraph_index,
                }
            )

    return items


def main() -> None:
    if not INPUT_DOCX.exists():
        raise FileNotFoundError(f"未找到输入文件: {INPUT_DOCX}")

    TESTS_DIR.mkdir(parents=True, exist_ok=True)
    _, metadata = extract_paragraph_metadata(INPUT_DOCX)
    annotated = annotate_heading_paths(metadata)

    heading_path_map = {item["paragraph_index"]: item["heading_path"] for item in annotated}

    with ZipFile(INPUT_DOCX) as zip_file:
        document_root = parse_document_root(zip_file)
        top_level_paragraphs = get_top_level_paragraphs(document_root)
        paragraph_context_rows = build_recursive_paragraph_context(document_root, top_level_paragraphs, heading_path_map)
        anchors = extract_comment_anchor_info(paragraph_context_rows)
        review_items = extract_comments(zip_file, anchors)
        review_items.extend(extract_tracked_changes(document_root, paragraph_context_rows))

    json_path = TESTS_DIR / "2.7_review_items.json"
    csv_path = TESTS_DIR / "2.7_review_items.csv"

    json_path.write_text(json.dumps(review_items, ensure_ascii=False, indent=2), encoding="utf-8")

    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "type",
                "comment_id",
                "author",
                "time",
                "text",
                "paragraph_index",
                "top_level_paragraph_index",
                "paragraph_text",
                "heading_path",
                "range_text",
                "start_paragraph_index",
                "end_paragraph_index",
            ],
        )
        writer.writeheader()
        writer.writerows(review_items)

    comment_count = len([item for item in review_items if item["type"] == "comment"])
    tracked_count = len(review_items) - comment_count

    print(f"[2.7] 输入文档: {INPUT_DOCX}")
    print(f"[2.7] 已输出审阅内容 JSON: {json_path}")
    print(f"[2.7] 已输出审阅内容 CSV: {csv_path}")
    print(f"[2.7] 批注数量: {comment_count}，修订记录数量: {tracked_count}")


if __name__ == "__main__":
    main()

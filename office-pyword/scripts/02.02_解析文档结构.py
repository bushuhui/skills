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
        alignment = first_or_none(element.xpath("./w:pPr/w:jc/@w:val", namespaces=NS))

        metadata.append(
            {
                "paragraph_index": index,
                "text": normalize_text(paragraph.text),
                "style_id": style_id,
                "style_name": paragraph.style.name if paragraph.style is not None else style_map.get(style_id, {}).get("name", ""),
                "outline_level": int(direct_outline) if direct_outline is not None else style_outline,
                "alignment": alignment,
                "paragraph": paragraph,
            }
        )
    return document, metadata


def is_bold_paragraph(paragraph) -> bool:
    for run in paragraph.runs:
        if run.text.strip() and run.bold is True:
            return True
    return bool(paragraph.style and paragraph.style.font and paragraph.style.font.bold)


def resolve_alignment(meta: dict[str, object]) -> str:
    if meta.get("alignment"):
        return str(meta["alignment"])

    paragraph = meta["paragraph"]
    value = paragraph.alignment
    if value is None and paragraph.style is not None:
        value = paragraph.style.paragraph_format.alignment

    mapping = {0: "left", 1: "center", 2: "right", 3: "justify", 4: "distribute"}
    return mapping.get(value, "unknown")


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
        return {"is_heading": False, "heading_level": None, "heading_number": None, "title_text": "", "detect_basis": "empty"}

    if is_caption_or_catalog(text, style_name):
        return {"is_heading": False, "heading_level": None, "heading_number": None, "title_text": "", "detect_basis": "caption_or_catalog"}

    if text in FRONT_HEADINGS:
        return {
            "is_heading": True,
            "heading_level": 1,
            "heading_number": None,
            "title_text": text,
            "detect_basis": "front_matter",
        }

    heading_number, title_text, number_level = extract_heading_number(text)
    style_hint = style_name in STYLE_HINTS
    short_text = len(text) <= 80 and not text.endswith("。")
    bold_hint = is_bold_paragraph(paragraph)
    centered = resolve_alignment(meta) in {"center", "distribute"}

    if heading_number and number_level is not None and (style_hint or outline_level is not None or short_text):
        return {
            "is_heading": True,
            "heading_level": min(number_level, 3),
            "heading_number": heading_number,
            "title_text": title_text or text,
            "detect_basis": "number_regex",
        }

    if outline_level is not None and style_hint and short_text:
        return {
            "is_heading": True,
            "heading_level": min(int(outline_level) + 1, 3),
            "heading_number": None,
            "title_text": text,
            "detect_basis": "outline_level",
        }

    if style_name == "Title" and short_text:
        return {
            "is_heading": True,
            "heading_level": 3,
            "heading_number": None,
            "title_text": text,
            "detect_basis": "style_title",
        }

    if style_name in {"Subtitle", "1正文"} and short_text:
        return {
            "is_heading": True,
            "heading_level": 1,
            "heading_number": None,
            "title_text": text,
            "detect_basis": "style_subtitle",
        }

    if centered and bold_hint and short_text:
        return {
            "is_heading": True,
            "heading_level": 1,
            "heading_number": None,
            "title_text": text,
            "detect_basis": "layout_fallback",
        }

    return {"is_heading": False, "heading_level": None, "heading_number": None, "title_text": "", "detect_basis": "body"}


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


def build_structure_tree(annotated: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    heading_rows = [row for row in annotated if row["is_heading"]]
    roots: list[dict[str, object]] = []
    stack: list[dict[str, object]] = []

    for index, row in enumerate(heading_rows):
        next_same_or_higher = next(
            (
                candidate["paragraph_index"] - 1
                for candidate in heading_rows[index + 1 :]
                if int(candidate["heading_level"]) <= int(row["heading_level"])
            ),
            annotated[-1]["paragraph_index"],
        )

        node = {
            "title": row["title_text"] or row["text"],
            "level": row["heading_level"],
            "number": row["heading_number"],
            "path": row["heading_path"],
            "start_paragraph_index": row["paragraph_index"],
            "end_paragraph_index": next_same_or_higher,
            "style_name": row["style_name"],
            "detect_basis": row["detect_basis"],
            "children": [],
        }

        while stack and int(stack[-1]["level"]) >= int(node["level"]):
            stack.pop()

        if stack:
            stack[-1]["children"].append(node)
        else:
            roots.append(node)

        stack.append(node)

    flattened = []
    for row in heading_rows:
        flattened.append(
            {
                "paragraph_index": row["paragraph_index"],
                "title": row["title_text"] or row["text"],
                "level": row["heading_level"],
                "number": row["heading_number"],
                "path": row["heading_path"],
                "style_name": row["style_name"],
                "detect_basis": row["detect_basis"],
            }
        )

    return roots, flattened


def main() -> None:
    if not INPUT_DOCX.exists():
        raise FileNotFoundError(f"未找到输入文件: {INPUT_DOCX}")

    TESTS_DIR.mkdir(parents=True, exist_ok=True)
    _, metadata = extract_paragraph_metadata(INPUT_DOCX)
    annotated = annotate_heading_paths(metadata)
    structure_tree, flattened = build_structure_tree(annotated)

    tree_path = TESTS_DIR / "2.2_结构树.json"
    flat_path = TESTS_DIR / "2.2_结构扁平清单.json"

    tree_path.write_text(json.dumps(structure_tree, ensure_ascii=False, indent=2), encoding="utf-8")
    flat_path.write_text(json.dumps(flattened, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[2.2] 输入文档: {INPUT_DOCX}")
    print(f"[2.2] 已输出结构树: {tree_path}")
    print(f"[2.2] 已输出结构扁平清单: {flat_path}")
    print(f"[2.2] 识别出的标题数量: {len(flattened)}")


if __name__ == "__main__":
    main()

import csv
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

from docx import Document
from lxml import etree

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"
INPUT_DOCX = TESTS_DIR / "测试文档.docx"
IMAGES_DIR = TESTS_DIR / "images"

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


def normalize_zip_path(path: str) -> str:
    parts: list[str] = []
    for part in PurePosixPath(path).parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/".join(parts)


def rels_path_for_part(part_name: str) -> str:
    part = PurePosixPath(part_name)
    return str(part.parent / "_rels" / f"{part.name}.rels")


def resolve_relationship_target(part_name: str, target: str) -> str:
    base = PurePosixPath(part_name).parent
    return normalize_zip_path(str(base / target))


def load_relationships(zip_file: ZipFile, part_name: str) -> dict[str, str]:
    path = rels_path_for_part(part_name)
    if path not in zip_file.namelist():
        return {}

    root = etree.fromstring(zip_file.read(path))
    relationships: dict[str, str] = {}
    for rel in root.xpath(".//rel:Relationship", namespaces=NS):
        rel_id = rel.get("Id")
        target = rel.get("Target")
        if rel_id and target:
            relationships[rel_id] = resolve_relationship_target(part_name, target)
    return relationships


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


def extract_document_image_references(zip_file: ZipFile, heading_paths: dict[int, str]) -> list[dict[str, object]]:
    document_root = etree.fromstring(zip_file.read("word/document.xml"))
    relationships = load_relationships(zip_file, "word/document.xml")
    body = document_root.find("w:body", namespaces=NS)
    paragraph_elements = [child for child in body if local_name(child.tag) == "p"]

    entries: list[dict[str, object]] = []
    for paragraph_index, element in enumerate(paragraph_elements, start=1):
        for rel_id in element.xpath(".//a:blip/@r:embed", namespaces=NS):
            target = relationships.get(rel_id)
            if not target or not target.startswith("word/media/"):
                continue
            entries.append(
                {
                    "source_part": "word/document.xml",
                    "relationship_id": rel_id,
                    "target": target,
                    "paragraph_index": paragraph_index,
                    "heading_path": heading_paths.get(paragraph_index, ""),
                }
            )
    return entries


def extract_other_part_image_references(zip_file: ZipFile) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    other_parts = [
        name
        for name in zip_file.namelist()
        if name.startswith("word/") and ("/header" in name or "/footer" in name or name.startswith("word/header") or name.startswith("word/footer")) and name.endswith(".xml")
    ]

    for part_name in other_parts:
        relationships = load_relationships(zip_file, part_name)
        root = etree.fromstring(zip_file.read(part_name))
        for rel_id in root.xpath(".//a:blip/@r:embed", namespaces=NS):
            target = relationships.get(rel_id)
            if not target or not target.startswith("word/media/"):
                continue
            entries.append(
                {
                    "source_part": part_name,
                    "relationship_id": rel_id,
                    "target": target,
                    "paragraph_index": None,
                    "heading_path": "<非正文部件>",
                }
            )
    return entries


def main() -> None:
    if not INPUT_DOCX.exists():
        raise FileNotFoundError(f"未找到输入文件: {INPUT_DOCX}")

    TESTS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    _, metadata = extract_paragraph_metadata(INPUT_DOCX)
    annotated = annotate_heading_paths(metadata)
    heading_paths = {item["paragraph_index"]: item["heading_path"] for item in annotated}

    manifest_json = TESTS_DIR / "2.6_images_manifest.json"
    manifest_csv = TESTS_DIR / "2.6_images_manifest.csv"

    with ZipFile(INPUT_DOCX) as zip_file:
        media_files = [name for name in zip_file.namelist() if name.startswith("word/media/")]
        hashes: dict[str, str] = {}
        hash_counts: dict[str, int] = {}

        for media_name in media_files:
            data = zip_file.read(media_name)
            file_path = IMAGES_DIR / Path(media_name).name
            file_path.write_bytes(data)
            sha1 = hashlib.sha1(data).hexdigest()
            hashes[media_name] = sha1
            hash_counts[sha1] = hash_counts.get(sha1, 0) + 1

        references = extract_document_image_references(zip_file, heading_paths)
        references.extend(extract_other_part_image_references(zip_file))

    ref_counts: dict[str, int] = {}
    for item in references:
        ref_counts[item["target"]] = ref_counts.get(item["target"], 0) + 1

    manifest_rows: list[dict[str, object]] = []
    referenced_targets = set()

    for item in references:
        target = item["target"]
        referenced_targets.add(target)
        file_name = Path(target).name
        suffix = Path(file_name).suffix.lstrip(".").lower()
        sha1 = hashes.get(target, "")
        is_duplicate = hash_counts.get(sha1, 0) > 1 or ref_counts.get(target, 0) > 1

        manifest_rows.append(
            {
                "image_filename": file_name,
                "relationship_id": item["relationship_id"],
                "paragraph_index": item["paragraph_index"],
                "heading_path": item["heading_path"],
                "image_format": suffix,
                "is_duplicate": is_duplicate,
                "source_part": item["source_part"],
                "sha1": sha1,
            }
        )

    for media_name in media_files:
        if media_name in referenced_targets:
            continue
        file_name = Path(media_name).name
        suffix = Path(file_name).suffix.lstrip(".").lower()
        sha1 = hashes.get(media_name, "")
        manifest_rows.append(
            {
                "image_filename": file_name,
                "relationship_id": "",
                "paragraph_index": None,
                "heading_path": "<未定位或未被正文引用>",
                "image_format": suffix,
                "is_duplicate": hash_counts.get(sha1, 0) > 1,
                "source_part": "<unknown>",
                "sha1": sha1,
            }
        )

    manifest_json.write_text(json.dumps(manifest_rows, ensure_ascii=False, indent=2), encoding="utf-8")

    with manifest_csv.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["image_filename", "relationship_id", "paragraph_index", "heading_path", "image_format", "is_duplicate", "source_part", "sha1"],
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    print(f"[2.6] 输入文档: {INPUT_DOCX}")
    print(f"[2.6] 已提取图片目录: {IMAGES_DIR}")
    print(f"[2.6] 已输出图片清单 JSON: {manifest_json}")
    print(f"[2.6] 已输出图片清单 CSV: {manifest_csv}")
    print(f"[2.6] 提取图片文件数量: {len(list(IMAGES_DIR.glob('*')))}")
    print(f"[2.6] 图片引用记录数量: {len(manifest_rows)}")


if __name__ == "__main__":
    main()

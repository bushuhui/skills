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


def find_section_range_by_heading(annotated: list[dict[str, object]], predicate) -> tuple[int, int] | None:
    start_index = next((idx for idx, item in enumerate(annotated) if item["is_heading"] and predicate(item)), None)
    if start_index is None:
        return None

    end_index = next(
        (idx for idx in range(start_index + 1, len(annotated)) if annotated[idx]["is_heading"]),
        len(annotated),
    )
    return start_index + 1, end_index


def build_result(
    method: str,
    paragraph_slice: list[dict[str, object]],
    start_idx: int | None,
    end_idx: int | None,
    status: str,
    note: str = "",
) -> dict[str, object]:
    text = "\n".join(item["text"] for item in paragraph_slice if item["text"])
    return {
        "method": method,
        "status": status,
        "note": note,
        "start_paragraph_index": paragraph_slice[0]["paragraph_index"] if paragraph_slice else start_idx,
        "end_paragraph_index": paragraph_slice[-1]["paragraph_index"] if paragraph_slice else end_idx,
        "paragraph_count": len([item for item in paragraph_slice if item["text"]]),
        "text": text,
        "paragraphs": [item["text"] for item in paragraph_slice if item["text"]],
    }


def main() -> None:
    if not INPUT_DOCX.exists():
        raise FileNotFoundError(f"未找到输入文件: {INPUT_DOCX}")

    TESTS_DIR.mkdir(parents=True, exist_ok=True)
    _, metadata = extract_paragraph_metadata(INPUT_DOCX)
    annotated = annotate_heading_paths(metadata)

    results: list[dict[str, object]] = []

    keyword_range = find_section_range_by_heading(annotated, lambda item: item["text"] == "摘要")
    if keyword_range:
        start, end = keyword_range
        results.append(build_result("按关键字", annotated[start:end], start, end, "success"))
    else:
        results.append(build_result("按关键字", [], None, None, "not_found", "未找到标题“摘要”。"))

    regex_range = find_section_range_by_heading(annotated, lambda item: re.fullmatch(r"摘要", str(item["text"])) is not None)
    if regex_range:
        start, end = regex_range
        results.append(build_result("按正则", annotated[start:end], start, end, "success"))
    else:
        results.append(build_result("按正则", [], None, None, "not_found", "未匹配到正则 ^摘要$。"))

    title_path_range = find_section_range_by_heading(annotated, lambda item: item["heading_path"] == "摘要")
    if title_path_range:
        start, end = title_path_range
        results.append(build_result("按标题路径", annotated[start:end], start, end, "success"))
    else:
        results.append(build_result("按标题路径", [], None, None, "not_found", "未找到标题路径“摘要”。"))

    start_marker_index = next((idx for idx, item in enumerate(annotated) if item["text"] == "摘要"), None)
    end_marker_index = next((idx for idx, item in enumerate(annotated) if item["text"] == "Abstract"), None)
    if start_marker_index is not None and end_marker_index is not None and end_marker_index > start_marker_index:
        results.append(
            build_result(
                "按开始标记/结束标记",
                annotated[start_marker_index + 1 : end_marker_index],
                start_marker_index + 1,
                end_marker_index,
                "success",
            )
        )
        results.append(
            build_result(
                "按段落索引范围",
                annotated[start_marker_index + 1 : end_marker_index],
                start_marker_index + 1,
                end_marker_index,
                "success",
                note=(
                    f"索引范围基于标题“摘要”和“Abstract”定位得到："
                    f"{annotated[start_marker_index]['paragraph_index'] + 1}-"
                    f"{annotated[end_marker_index - 1]['paragraph_index']}"
                ),
            )
        )
    else:
        results.append(build_result("按开始标记/结束标记", [], None, None, "not_found", "未同时定位到“摘要”和“Abstract”。"))
        results.append(build_result("按段落索引范围", [], None, None, "not_found", "未能基于标题定位摘要段落范围。"))

    table_title_match = next((item for item in annotated if item["text"].startswith("表") and "摘要" in item["text"]), None)
    if table_title_match:
        results.append(
            build_result(
                "按表格标题提取对应表格内容",
                [table_title_match],
                table_title_match["paragraph_index"],
                table_title_match["paragraph_index"],
                "success",
            )
        )
    else:
        results.append(
            build_result(
                "按表格标题提取对应表格内容",
                [],
                None,
                None,
                "not_found",
                "测试文档中不存在标题包含“摘要”的表格，本方法对摘要正文提取场景不适用。",
            )
        )

    json_path = TESTS_DIR / "2.3_自定义提取结果.json"
    txt_path = TESTS_DIR / "2.3_摘要提取文本.txt"

    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    preferred_result = next((item for item in results if item["method"] == "按开始标记/结束标记" and item["status"] == "success"), None)
    if preferred_result is None:
        preferred_result = next((item for item in results if item["status"] == "success"), {"text": ""})
    txt_path.write_text(str(preferred_result["text"]), encoding="utf-8")

    print(f"[2.3] 输入文档: {INPUT_DOCX}")
    print(f"[2.3] 已输出自定义提取结果 JSON: {json_path}")
    print(f"[2.3] 已输出摘要提取文本: {txt_path}")
    for item in results:
        print(f"[2.3] {item['method']}: {item['status']}，段落数={item['paragraph_count']}")


if __name__ == "__main__":
    main()

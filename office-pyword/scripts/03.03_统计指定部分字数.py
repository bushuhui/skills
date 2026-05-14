import json
import re
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from lxml import etree

TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"
INPUT_DOCX = TESTS_DIR / "测试文档.docx"

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}

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

TARGETS = [
    {"section_name": "摘要", "match_type": "heading_exact", "match_value": "摘要"},
    {"section_name": "Abstract", "match_type": "heading_exact", "match_value": "Abstract"},
    {"section_name": "绪论", "match_type": "heading_contains", "match_value": "绪论"},
    {"section_name": "参考文献", "match_type": "style_block", "match_value": "EndNote Bibliography"},
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


def extract_heading_number(text: str) -> tuple[str | None, int | None]:
    for pattern, level in NUMERIC_HEADING_PATTERNS:
        match = pattern.match(text)
        if match:
            return match.group(1), level
    return None, None


def detect_heading(meta: dict[str, object]) -> dict[str, object]:
    text = str(meta["text"])
    style_name = str(meta["style_name"] or "")
    paragraph = meta["paragraph"]
    outline_level = meta.get("outline_level")

    if not text or is_caption_or_catalog(text, style_name):
        return {"is_heading": False, "heading_level": None}

    if text in FRONT_HEADINGS:
        return {"is_heading": True, "heading_level": 1}

    heading_number, number_level = extract_heading_number(text)
    style_hint = style_name in STYLE_HINTS
    short_text = len(text) <= 80 and not text.endswith("。")

    if heading_number and number_level is not None and (style_hint or outline_level is not None or short_text):
        return {"is_heading": True, "heading_level": min(number_level, 3)}

    if outline_level is not None and style_hint and short_text:
        return {"is_heading": True, "heading_level": min(int(outline_level) + 1, 3)}

    if style_name == "Title" and short_text:
        return {"is_heading": True, "heading_level": 3}

    if style_name in {"Subtitle", "1正文"} and short_text:
        return {"is_heading": True, "heading_level": 1}

    if is_bold_paragraph(paragraph) and short_text:
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


def find_heading_section(annotated: list[dict[str, object]], target: dict[str, str]) -> list[dict[str, object]]:
    if target["match_type"] == "heading_exact":
        start_idx = next((idx for idx, item in enumerate(annotated) if item["is_heading"] and item["text"] == target["match_value"]), None)
    else:
        start_idx = next(
            (idx for idx, item in enumerate(annotated) if item["is_heading"] and target["match_value"] in str(item["text"])),
            None,
        )

    if start_idx is None:
        return []

    current_level = int(annotated[start_idx]["heading_level"])
    end_idx = next(
        (
            idx
            for idx in range(start_idx + 1, len(annotated))
            if annotated[idx]["is_heading"] and int(annotated[idx]["heading_level"]) <= current_level
        ),
        len(annotated),
    )
    return annotated[start_idx + 1 : end_idx]


def find_style_block(annotated: list[dict[str, object]], style_name: str) -> list[dict[str, object]]:
    return [item for item in annotated if item["style_name"] == style_name and item["text"]]


def count_metrics(paragraphs: list[dict[str, object]]) -> dict[str, object]:
    texts = [item["text"] for item in paragraphs if item["text"]]
    full_text = "\n".join(texts)
    no_space_text = re.sub(r"\s+", "", full_text)

    return {
        "paragraph_count": len(paragraphs),
        "non_empty_paragraph_count": len(texts),
        "chinese_character_count": len(re.findall(r"[\u4e00-\u9fff]", full_text)),
        "english_word_count": len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", full_text)),
        "digit_count": len(re.findall(r"\d", full_text)),
        "character_count_with_spaces": len(full_text),
        "character_count_without_spaces": len(no_space_text),
        "text_preview": texts[0][:120] if texts else "",
        "full_text": full_text,
    }


def build_report_text(results: list[dict[str, object]]) -> str:
    lines = [
        "特定部分字数统计报告",
        f"输入文件: {INPUT_DOCX}",
        "",
    ]

    for item in results:
        lines.append(f"部分名称: {item['section_name']}")
        lines.append(f"  定位方式: {item['match_type']}")
        lines.append(f"  状态: {item['status']}")
        lines.append(f"  段落范围: {item['start_paragraph_index']} - {item['end_paragraph_index']}")
        lines.append(f"  段落数: {item['paragraph_count']}")
        lines.append(f"  中文字符数: {item['chinese_character_count']}")
        lines.append(f"  英文单词数: {item['english_word_count']}")
        lines.append(f"  数字数: {item['digit_count']}")
        lines.append(f"  字符数(含空格): {item['character_count_with_spaces']}")
        lines.append(f"  字符数(不含空格): {item['character_count_without_spaces']}")
        if item["note"]:
            lines.append(f"  说明: {item['note']}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    if not INPUT_DOCX.exists():
        raise FileNotFoundError(f"未找到输入文件: {INPUT_DOCX}")

    TESTS_DIR.mkdir(parents=True, exist_ok=True)
    _, metadata = extract_paragraph_metadata(INPUT_DOCX)
    annotated = annotate_heading_paths(metadata)

    results: list[dict[str, object]] = []

    for target in TARGETS:
        if target["match_type"] in {"heading_exact", "heading_contains"}:
            paragraphs = find_heading_section(annotated, target)
            status = "success" if paragraphs else "not_found"
            note = "" if paragraphs else "未找到对应标题。"
        else:
            paragraphs = find_style_block(annotated, target["match_value"])
            status = "success" if paragraphs else "not_found"
            note = "" if paragraphs else "未找到对应样式的段落块。"

        metrics = count_metrics(paragraphs)
        results.append(
            {
                "section_name": target["section_name"],
                "match_type": target["match_type"],
                "match_value": target["match_value"],
                "status": status,
                "note": note,
                "start_paragraph_index": paragraphs[0]["paragraph_index"] if paragraphs else None,
                "end_paragraph_index": paragraphs[-1]["paragraph_index"] if paragraphs else None,
                **metrics,
            }
        )

    json_path = TESTS_DIR / "3.3_特定部分字数统计.json"
    txt_path = TESTS_DIR / "3.3_特定部分字数统计.txt"

    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    txt_path.write_text(build_report_text(results), encoding="utf-8")

    print(f"[3.3] 输入文档: {INPUT_DOCX}")
    print(f"[3.3] 已输出特定部分字数统计 JSON: {json_path}")
    print(f"[3.3] 已输出特定部分字数统计 TXT: {txt_path}")
    for item in results:
        print(f"[3.3] {item['section_name']}: {item['status']}，段落数={item['paragraph_count']}，中文字符数={item['chinese_character_count']}")


if __name__ == "__main__":
    main()

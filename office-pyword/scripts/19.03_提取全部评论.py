from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

from lxml import etree


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}

CURRENT_DIR = Path(__file__).resolve().parent
TESTS_DIR = CURRENT_DIR.parent / "tests"
INPUT_DOCX = TESTS_DIR / "19.2_带审阅意见文档.docx"
OUTPUT_JSON = TESTS_DIR / "19.3_评论提取结果.json"
OUTPUT_CSV = TESTS_DIR / "19.3_评论提取结果.csv"


def load_comment_writer_module():
    module_path = CURRENT_DIR / "19.02_写入审阅评论.py"
    spec = importlib.util.spec_from_file_location("section19_comments_writer", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


WRITER = load_comment_writer_module()


def normalize_text(text: str) -> str:
    return " ".join((text or "").split())


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def get_top_level_paragraphs(document_root):
    body = document_root.find("w:body", namespaces=NS)
    return [child for child in body if local_name(child.tag) == "p"]


def get_all_body_paragraphs(document_root):
    body = document_root.find("w:body", namespaces=NS)
    return body.xpath(".//w:p", namespaces=NS)


def build_paragraph_context(document_root):
    top_level_paragraphs = get_top_level_paragraphs(document_root)
    top_level_lookup = {id(element): index for index, element in enumerate(top_level_paragraphs, start=1)}
    context_rows = []

    for xml_index, element in enumerate(get_all_body_paragraphs(document_root), start=1):
        text = normalize_text("".join(element.xpath(".//w:t/text()", namespaces=NS)))
        context_rows.append(
            {
                "xml_index": xml_index,
                "top_level_paragraph_index": top_level_lookup.get(id(element)),
                "text": text,
                "element": element,
            }
        )

    return context_rows


def extract_comment_anchor_info(context_rows) -> dict[str, dict[str, object]]:
    starts: dict[str, int] = {}
    ends: dict[str, int] = {}
    refs: dict[str, int] = {}
    paragraph_lookup = {row["xml_index"]: row for row in context_rows}

    for row in context_rows:
        paragraph_index = row["xml_index"]
        element = row["element"]
        for comment_id in set(element.xpath(".//w:commentRangeStart/@w:id", namespaces=NS)):
            starts.setdefault(comment_id, paragraph_index)
        for comment_id in set(element.xpath(".//w:commentRangeEnd/@w:id", namespaces=NS)):
            ends[comment_id] = paragraph_index
        for comment_id in set(element.xpath(".//w:commentReference/@w:id", namespaces=NS)):
            refs.setdefault(comment_id, paragraph_index)

    anchors: dict[str, dict[str, object]] = {}
    for comment_id in sorted(set(starts) | set(ends) | set(refs), key=lambda value: int(value)):
        paragraph_index = refs.get(comment_id) or starts.get(comment_id) or ends.get(comment_id)
        if paragraph_index is None:
            continue
        start_index = starts.get(comment_id, paragraph_index)
        end_index = ends.get(comment_id, paragraph_index)
        anchor_text = "\n".join(
            paragraph_lookup[idx]["text"]
            for idx in range(start_index, end_index + 1)
            if idx in paragraph_lookup and paragraph_lookup[idx]["text"]
        )
        anchors[comment_id] = {
            "paragraph_index": paragraph_index,
            "top_level_paragraph_index": paragraph_lookup[paragraph_index].get("top_level_paragraph_index"),
            "anchor_text": anchor_text,
        }
    return anchors


def extract_comments(docx_path: Path) -> list[dict[str, object]]:
    with ZipFile(docx_path) as zip_file:
        if "word/comments.xml" not in zip_file.namelist():
            return []

        document_root = etree.fromstring(zip_file.read("word/document.xml"))
        comments_root = etree.fromstring(zip_file.read("word/comments.xml"))
        context_rows = build_paragraph_context(document_root)
        anchors = extract_comment_anchor_info(context_rows)

        items = []
        for comment in comments_root.xpath("./w:comment", namespaces=NS):
            comment_id = comment.get(f"{{{W_NS}}}id", "")
            anchor = anchors.get(comment_id, {})
            items.append(
                {
                    "comment_id": comment_id,
                    "author": comment.get(f"{{{W_NS}}}author", ""),
                    "initials": comment.get(f"{{{W_NS}}}initials", ""),
                    "time": comment.get(f"{{{W_NS}}}date", ""),
                    "comment_text": normalize_text("".join(comment.xpath(".//w:t/text()", namespaces=NS))),
                    "anchor_text": anchor.get("anchor_text", ""),
                    "paragraph_index": anchor.get("paragraph_index"),
                    "top_level_paragraph_index": anchor.get("top_level_paragraph_index"),
                }
            )
        return items


def main() -> None:
    WRITER.ensure_demo_source_document(WRITER.SOURCE_DOCX)
    if not INPUT_DOCX.exists():
        WRITER.add_comments_to_docx(WRITER.SOURCE_DOCX, INPUT_DOCX, WRITER.COMMENT_SPECS)

    comments = extract_comments(INPUT_DOCX)
    OUTPUT_JSON.write_text(json.dumps(comments, ensure_ascii=False, indent=2), encoding="utf-8")

    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "comment_id",
                "author",
                "initials",
                "time",
                "comment_text",
                "anchor_text",
                "paragraph_index",
                "top_level_paragraph_index",
            ],
        )
        writer.writeheader()
        writer.writerows(comments)

    print(f"[19.3] 输入文档: {INPUT_DOCX}")
    print(f"[19.3] 已提取评论数量: {len(comments)}")
    print(f"[19.3] 已输出 JSON: {OUTPUT_JSON}")
    print(f"[19.3] 已输出 CSV: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()

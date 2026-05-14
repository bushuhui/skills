from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree

from _14_docx_review_demo import SOURCE_DOCX, TESTS_DIR, ensure_demo_source_document

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"w": W_NS, "r": R_NS, "ct": CT_NS, "pr": REL_NS}

OUTPUT_DOCX = TESTS_DIR / "19.2_带审阅意见文档.docx"

COMMENT_SPECS = [
    {
        "match_text": "多视角影像采集能够为三维重建提供稳定的数据基础。",
        "author": "指导教师",
        "initials": "JS",
        "comment_text": "建议补充影像采集设备型号与采样环境说明。",
    },
    {
        "match_text": "点云配准与网格重建是实验流程中的关键环节。",
        "author": "评阅人",
        "initials": "PY",
        "comment_text": "这里可以增加一种替代算法作为对比实验。",
    },
    {
        "match_text": "建议在正式论文中补充误差分析与参考文献对比。",
        "author": "项目负责人",
        "initials": "PM",
        "comment_text": "结论部分建议再明确本文的创新点与局限性。",
    },
]


def w_tag(name: str) -> str:
    return f"{{{W_NS}}}{name}"


def r_tag(name: str) -> str:
    return f"{{{R_NS}}}{name}"


def ct_tag(name: str) -> str:
    return f"{{{CT_NS}}}{name}"


def rel_tag(name: str) -> str:
    return f"{{{REL_NS}}}{name}"


def normalize_text(text: str) -> str:
    return " ".join((text or "").split())


def build_package_map(docx_path: Path) -> dict[str, bytes]:
    with ZipFile(docx_path, "r") as zip_file:
        return {info.filename: zip_file.read(info.filename) for info in zip_file.infolist()}


def write_package_map(package_map: dict[str, bytes], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output_path, "w", compression=ZIP_DEFLATED) as zip_file:
        for name, content in package_map.items():
            zip_file.writestr(name, content)


def to_xml_bytes(root) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone="yes")


def ensure_comments_content_type(package_map: dict[str, bytes]) -> None:
    root = etree.fromstring(package_map["[Content_Types].xml"])
    exists = root.xpath(
        "./ct:Override[@PartName='/word/comments.xml']",
        namespaces=NS,
    )
    if not exists:
        override = etree.Element(ct_tag("Override"))
        override.set("PartName", "/word/comments.xml")
        override.set("ContentType", "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml")
        root.append(override)
        package_map["[Content_Types].xml"] = to_xml_bytes(root)


def next_relationship_id(rels_root) -> str:
    numbers = []
    for rel in rels_root.xpath("./pr:Relationship", namespaces=NS):
        rel_id = rel.get("Id", "")
        if rel_id.startswith("rId") and rel_id[3:].isdigit():
            numbers.append(int(rel_id[3:]))
    return f"rId{max(numbers, default=0) + 1}"


def ensure_comments_relationship(package_map: dict[str, bytes]) -> None:
    rels_name = "word/_rels/document.xml.rels"
    rels_root = etree.fromstring(package_map[rels_name])
    exists = rels_root.xpath(
        "./pr:Relationship[@Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments']",
        namespaces=NS,
    )
    if not exists:
        relationship = etree.Element(rel_tag("Relationship"))
        relationship.set("Id", next_relationship_id(rels_root))
        relationship.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments")
        relationship.set("Target", "comments.xml")
        rels_root.append(relationship)
        package_map[rels_name] = to_xml_bytes(rels_root)


def ensure_comments_part(package_map: dict[str, bytes]):
    if "word/comments.xml" not in package_map:
        comments_root = etree.Element(w_tag("comments"), nsmap={"w": W_NS})
        package_map["word/comments.xml"] = to_xml_bytes(comments_root)
    return etree.fromstring(package_map["word/comments.xml"])


def next_comment_id(comments_root) -> int:
    ids = []
    for comment in comments_root.xpath("./w:comment", namespaces=NS):
        value = comment.get(w_tag("id"))
        if value is not None and str(value).isdigit():
            ids.append(int(value))
    return max(ids, default=-1) + 1


def build_comment_element(comment_id: int, author: str, initials: str, comment_text: str):
    comment = etree.Element(w_tag("comment"))
    comment.set(w_tag("id"), str(comment_id))
    comment.set(w_tag("author"), author)
    comment.set(w_tag("initials"), initials)
    comment.set(w_tag("date"), datetime.now(timezone.utc).replace(microsecond=0).isoformat())

    paragraph = etree.SubElement(comment, w_tag("p"))
    ref_run = etree.SubElement(paragraph, w_tag("r"))
    ref_rpr = etree.SubElement(ref_run, w_tag("rPr"))
    ref_style = etree.SubElement(ref_rpr, w_tag("rStyle"))
    ref_style.set(w_tag("val"), "CommentReference")
    etree.SubElement(ref_run, w_tag("annotationRef"))

    text_run = etree.SubElement(paragraph, w_tag("r"))
    text_node = etree.SubElement(text_run, w_tag("t"))
    text_node.text = comment_text
    return comment


def ensure_paragraph_has_run(paragraph_element) -> None:
    has_run = any(child.tag == w_tag("r") for child in paragraph_element)
    if not has_run:
        run = etree.Element(w_tag("r"))
        text = etree.SubElement(run, w_tag("t"))
        text.text = ""
        paragraph_element.append(run)


def add_comment_markup_to_paragraph(paragraph_element, comment_id: int) -> None:
    ensure_paragraph_has_run(paragraph_element)
    children = list(paragraph_element)
    insert_at = 1 if children and children[0].tag == w_tag("pPr") else 0

    start = etree.Element(w_tag("commentRangeStart"))
    start.set(w_tag("id"), str(comment_id))
    paragraph_element.insert(insert_at, start)

    end = etree.Element(w_tag("commentRangeEnd"))
    end.set(w_tag("id"), str(comment_id))
    paragraph_element.append(end)

    ref_run = etree.Element(w_tag("r"))
    ref_rpr = etree.SubElement(ref_run, w_tag("rPr"))
    ref_style = etree.SubElement(ref_rpr, w_tag("rStyle"))
    ref_style.set(w_tag("val"), "CommentReference")
    ref = etree.SubElement(ref_run, w_tag("commentReference"))
    ref.set(w_tag("id"), str(comment_id))
    paragraph_element.append(ref_run)


def add_comments_to_docx(source_docx: Path, output_docx: Path, comment_specs: list[dict[str, str]]) -> int:
    package_map = build_package_map(source_docx)
    ensure_comments_content_type(package_map)
    ensure_comments_relationship(package_map)

    document_root = etree.fromstring(package_map["word/document.xml"])
    comments_root = ensure_comments_part(package_map)
    body = document_root.find("w:body", namespaces=NS)
    paragraphs = [child for child in body if child.tag == w_tag("p")]

    used_indexes: set[int] = set()
    added_count = 0

    for spec in comment_specs:
        target_index = None
        for index, paragraph in enumerate(paragraphs):
            if index in used_indexes:
                continue
            text = normalize_text("".join(paragraph.xpath(".//w:t/text()", namespaces=NS)))
            if text == spec["match_text"]:
                target_index = index
                break
        if target_index is None:
            continue

        comment_id = next_comment_id(comments_root)
        comments_root.append(
            build_comment_element(
                comment_id=comment_id,
                author=spec["author"],
                initials=spec["initials"],
                comment_text=spec["comment_text"],
            )
        )
        add_comment_markup_to_paragraph(paragraphs[target_index], comment_id)
        used_indexes.add(target_index)
        added_count += 1

    package_map["word/document.xml"] = to_xml_bytes(document_root)
    package_map["word/comments.xml"] = to_xml_bytes(comments_root)
    write_package_map(package_map, output_docx)
    return added_count


def main() -> None:
    ensure_demo_source_document(SOURCE_DOCX)
    count = add_comments_to_docx(SOURCE_DOCX, OUTPUT_DOCX, COMMENT_SPECS)
    print(f"[19.2] 已生成示例源文档: {SOURCE_DOCX}")
    print(f"[19.2] 已生成带审阅意见文档: {OUTPUT_DOCX}")
    print(f"[19.2] 已写入评论数量: {count}")


if __name__ == "__main__":
    main()

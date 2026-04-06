from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
import re
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def w_tag(name: str) -> str:
    return f"{{{W_NS}}}{name}"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


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


def insert_in_schema_order(parent, element, successor_names: list[str]) -> None:
    successor_tags = {w_tag(name) for name in successor_names}
    for index, child in enumerate(list(parent)):
        if child.tag in successor_tags:
            parent.insert(index, element)
            return
    parent.append(element)


def ensure_track_revisions_setting(package_map: dict[str, bytes], enabled: bool) -> None:
    settings_root = etree.fromstring(package_map["word/settings.xml"])
    existing = settings_root.find("w:trackRevisions", namespaces=NS)
    if enabled and existing is None:
        element = etree.Element(w_tag("trackRevisions"), nsmap=settings_root.nsmap)
        successors = [
            "defaultTabStop",
            "evenAndOddHeaders",
            "bookFoldPrinting",
            "bookFoldRevPrinting",
            "mirrorMargins",
            "alignBordersAndEdges",
            "bordersDoNotSurroundHeader",
            "bordersDoNotSurroundFooter",
            "gutterAtTop",
            "hideSpellingErrors",
            "hideGrammaticalErrors",
            "activeWritingStyle",
            "proofState",
            "formsDesign",
            "attachedTemplate",
            "linkStyles",
            "stylePaneFormatFilter",
            "stylePaneSortMethod",
            "documentType",
            "mailMerge",
            "revisionView",
            "updateFields",
            "docVars",
            "rsids",
        ]
        insert_in_schema_order(settings_root, element, successors)
    elif not enabled and existing is not None:
        settings_root.remove(existing)
    package_map["word/settings.xml"] = to_xml_bytes(settings_root)


def parse_document_root(package_map: dict[str, bytes]):
    return etree.fromstring(package_map["word/document.xml"])


def update_document_root(package_map: dict[str, bytes], document_root) -> None:
    package_map["word/document.xml"] = to_xml_bytes(document_root)


def get_body(document_root):
    body = document_root.find("w:body", namespaces=NS)
    if body is None:
        raise ValueError("document.xml 中缺少 body 节点。")
    return body


def get_top_level_paragraphs(document_root):
    body = get_body(document_root)
    return [child for child in body if local_name(child.tag) == "p"]


def find_top_level_paragraph_by_text(document_root, text: str):
    target = normalize_text(text)
    for paragraph in get_top_level_paragraphs(document_root):
        paragraph_text = normalize_text("".join(paragraph.xpath(".//w:t/text() | .//w:delText/text()", namespaces=NS)))
        if paragraph_text == target:
            return paragraph
    raise KeyError(text)


def next_revision_id(document_root) -> int:
    ids: list[int] = []
    for value in document_root.xpath(".//@w:id", namespaces=NS):
        if str(value).isdigit():
            ids.append(int(value))
    return max(ids, default=-1) + 1


def build_plain_run(text: str):
    run = etree.Element(w_tag("r"))
    text_node = etree.SubElement(run, w_tag("t"))
    if text.startswith(" ") or text.endswith(" "):
        text_node.set(XML_SPACE, "preserve")
    text_node.text = text
    return run


def build_revision_wrapper(kind: str, text: str, revision_id: int, author: str, timestamp: str):
    tag_name = {"insert": "ins", "delete": "del", "moveFrom": "moveFrom", "moveTo": "moveTo"}[kind]
    wrapper = etree.Element(w_tag(tag_name))
    wrapper.set(w_tag("id"), str(revision_id))
    wrapper.set(w_tag("author"), author)
    wrapper.set(w_tag("date"), timestamp)
    run = etree.SubElement(wrapper, w_tag("r"))
    text_tag = "delText" if kind == "delete" else "t"
    text_node = etree.SubElement(run, w_tag(text_tag))
    if text.startswith(" ") or text.endswith(" "):
        text_node.set(XML_SPACE, "preserve")
    text_node.text = text
    return wrapper


def collapse_segments(segments: list[tuple[str, str]]) -> list[tuple[str, str]]:
    collapsed: list[tuple[str, str]] = []
    for kind, text in segments:
        if not text:
            continue
        if collapsed and collapsed[-1][0] == kind:
            collapsed[-1] = (kind, collapsed[-1][1] + text)
        else:
            collapsed.append((kind, text))
    return collapsed


def replace_paragraph_segments(
    paragraph_element,
    segments: list[tuple[str, str]],
    author: str,
    revision_id_start: int,
    timestamp: str | None = None,
) -> int:
    active_timestamp = timestamp or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    p_pr = paragraph_element.find(w_tag("pPr"))
    for child in list(paragraph_element):
        if p_pr is not None and child is p_pr:
            continue
        paragraph_element.remove(child)

    insert_at = 1 if p_pr is not None else 0
    next_id_value = revision_id_start
    for kind, text in collapse_segments(segments):
        if kind == "keep":
            paragraph_element.insert(insert_at, build_plain_run(text))
            insert_at += 1
            continue
        wrapper = build_revision_wrapper(kind, text, next_id_value, author, active_timestamp)
        paragraph_element.insert(insert_at, wrapper)
        insert_at += 1
        next_id_value += 1
    return next_id_value


def insert_empty_paragraph_after(reference_paragraph, clone_properties_from=None):
    parent = reference_paragraph.getparent()
    new_paragraph = etree.Element(w_tag("p"))
    template = clone_properties_from if clone_properties_from is not None else reference_paragraph
    p_pr = template.find(w_tag("pPr"))
    if p_pr is not None:
        new_paragraph.append(deepcopy(p_pr))
    parent.insert(parent.index(reference_paragraph) + 1, new_paragraph)
    return new_paragraph


def tokenize_text(text: str) -> list[str]:
    if not text:
        return []
    pattern = r"[\u4e00-\u9fff]|[A-Za-z0-9_]+|\s+|[^\w\s]"
    return re.findall(pattern, text)


def paragraph_diff_segments(old_text: str, new_text: str) -> list[tuple[str, str]]:
    old_tokens = tokenize_text(old_text)
    new_tokens = tokenize_text(new_text)
    matcher = SequenceMatcher(a=old_tokens, b=new_tokens)
    segments: list[tuple[str, str]] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            segments.append(("keep", "".join(old_tokens[i1:i2])))
        elif tag == "delete":
            segments.append(("delete", "".join(old_tokens[i1:i2])))
        elif tag == "insert":
            segments.append(("insert", "".join(new_tokens[j1:j2])))
        else:
            segments.append(("delete", "".join(old_tokens[i1:i2])))
            segments.append(("insert", "".join(new_tokens[j1:j2])))
    return collapse_segments(segments)


def convert_deleted_text_nodes(element) -> None:
    for node in element.xpath(".//w:delText", namespaces=NS):
        node.tag = w_tag("t")


def unwrap_revision_element(change_element, convert_deleted_text: bool = False) -> None:
    if convert_deleted_text:
        convert_deleted_text_nodes(change_element)

    parent = change_element.getparent()
    if parent is None:
        return

    insert_at = parent.index(change_element)
    children = [deepcopy(child) for child in list(change_element)]
    parent.remove(change_element)
    for child in children:
        parent.insert(insert_at, child)
        insert_at += 1


def reject_property_change(change_element) -> None:
    parent = change_element.getparent()
    if parent is None:
        return
    parent_name = local_name(parent.tag)
    snapshot = None
    for child in change_element:
        if local_name(child.tag) == parent_name:
            snapshot = child
            break
    if snapshot is None:
        parent.remove(change_element)
        return
    for child in list(parent):
        parent.remove(child)
    for child in snapshot:
        parent.append(deepcopy(child))


def cleanup_empty_top_level_paragraphs(document_root) -> None:
    for paragraph in reversed(get_top_level_paragraphs(document_root)):
        text = normalize_text("".join(paragraph.xpath(".//w:t/text()", namespaces=NS)))
        has_embedded_object = bool(paragraph.xpath(".//w:drawing | .//w:object", namespaces=NS))
        if text or has_embedded_object:
            continue
        non_property_children = [child for child in paragraph if local_name(child.tag) != "pPr"]
        if non_property_children:
            continue
        parent = paragraph.getparent()
        if parent is not None:
            parent.remove(paragraph)


def accept_or_reject_document_root(document_root, accept: bool) -> dict[str, int]:
    counts = {
        "insertions": len(document_root.xpath(".//w:ins", namespaces=NS)),
        "deletions": len(document_root.xpath(".//w:del", namespaces=NS)),
        "move_from": len(document_root.xpath(".//w:moveFrom", namespaces=NS)),
        "move_to": len(document_root.xpath(".//w:moveTo", namespaces=NS)),
    }

    for change in reversed(
        document_root.xpath(".//w:ins | .//w:del | .//w:moveFrom | .//w:moveTo", namespaces=NS)
    ):
        tag_name = local_name(change.tag)
        if accept:
            if tag_name in {"ins", "moveTo"}:
                unwrap_revision_element(change, convert_deleted_text=False)
            else:
                change.getparent().remove(change)
        else:
            if tag_name in {"del", "moveFrom"}:
                unwrap_revision_element(change, convert_deleted_text=True)
            else:
                change.getparent().remove(change)

    property_changes = reversed(
        document_root.xpath(
            ".//w:pPrChange | .//w:rPrChange | .//w:tblPrChange | .//w:trPrChange | .//w:tcPrChange | .//w:sectPrChange | .//w:numPrChange",
            namespaces=NS,
        )
    )
    for change in property_changes:
        if accept:
            change.getparent().remove(change)
        else:
            reject_property_change(change)

    cleanup_empty_top_level_paragraphs(document_root)
    return counts


def process_revisions_docx(input_path: Path, output_path: Path, accept: bool) -> dict[str, int]:
    package_map = build_package_map(input_path)
    document_root = parse_document_root(package_map)
    counts = accept_or_reject_document_root(document_root, accept=accept)
    update_document_root(package_map, document_root)
    ensure_track_revisions_setting(package_map, enabled=False)
    write_package_map(package_map, output_path)
    return counts

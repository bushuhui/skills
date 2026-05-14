from __future__ import annotations

import re

from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def sanitize_bookmark_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", name.strip())
    if not cleaned:
        cleaned = "bookmark"
    if not cleaned[0].isalpha():
        cleaned = f"b_{cleaned}"
    return cleaned[:40]


def next_bookmark_id(document) -> int:
    ids = []
    for item in document._part._element.xpath(".//w:bookmarkStart/@w:id"):
        try:
            ids.append(int(item))
        except ValueError:
            continue
    return max(ids, default=0) + 1


def add_bookmark_to_paragraph(document, paragraph, name: str) -> str:
    bookmark_name = sanitize_bookmark_name(name)
    bookmark_id = next_bookmark_id(document)

    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bookmark_id))
    start.set(qn("w:name"), bookmark_name)

    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bookmark_id))

    paragraph._p.insert(0, start)
    paragraph._p.append(end)
    return bookmark_name


def add_bookmark_around_run(document, run, name: str) -> str:
    bookmark_name = sanitize_bookmark_name(name)
    bookmark_id = next_bookmark_id(document)

    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bookmark_id))
    start.set(qn("w:name"), bookmark_name)

    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bookmark_id))

    run._r.addprevious(start)
    run._r.addnext(end)
    return bookmark_name

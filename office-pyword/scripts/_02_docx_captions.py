from __future__ import annotations

from _01_docx_bookmarks import add_bookmark_to_paragraph
from _03_docx_fields import add_seq_field


def add_caption_paragraph(document, label: str, seq_id: str, title: str, style_name: str, bookmark_name: str | None = None):
    paragraph = document.add_paragraph(style=style_name)
    paragraph.add_run(f"{label} ")
    add_seq_field(paragraph, seq_id, "1")
    paragraph.add_run(f" {title}")
    if bookmark_name:
        add_bookmark_to_paragraph(document, paragraph, bookmark_name)
    return paragraph

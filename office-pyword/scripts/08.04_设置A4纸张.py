from __future__ import annotations

import shutil
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.shared import Cm


TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"
SOURCE_DOCX = TESTS_DIR / "测试文档.docx"
OUTPUT_DOCX = TESTS_DIR / "8.4_A4纸张设置示例.docx"


def copy_docx(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def main() -> None:
    copy_docx(SOURCE_DOCX, OUTPUT_DOCX)
    document = Document(OUTPUT_DOCX)

    for section in document.sections:
        if section.orientation == WD_ORIENT.LANDSCAPE:
            section.page_width = Cm(29.7)
            section.page_height = Cm(21.0)
        else:
            section.page_width = Cm(21.0)
            section.page_height = Cm(29.7)

    document.save(OUTPUT_DOCX)
    print(f"[8.4] 已将所有节设置为 A4 纸张: {OUTPUT_DOCX}")


if __name__ == "__main__":
    main()

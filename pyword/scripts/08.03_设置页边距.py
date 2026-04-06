from __future__ import annotations

import shutil
from pathlib import Path

from docx import Document
from docx.shared import Cm


TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"
SOURCE_DOCX = TESTS_DIR / "测试文档.docx"
OUTPUT_DOCX = TESTS_DIR / "8.3_页边距设置示例.docx"


def copy_docx(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def main() -> None:
    copy_docx(SOURCE_DOCX, OUTPUT_DOCX)
    document = Document(OUTPUT_DOCX)

    for section in document.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.18)
        section.right_margin = Cm(2.54)

    document.save(OUTPUT_DOCX)
    print(f"[8.3] 已设置所有节的页边距: {OUTPUT_DOCX}")


if __name__ == "__main__":
    main()

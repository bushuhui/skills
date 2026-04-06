from __future__ import annotations

import shutil
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"
SOURCE_DOCX = TESTS_DIR / "测试文档.docx"
OUTPUT_DOCX = TESTS_DIR / "4.1_测试文档副本.docx"


def copy_docx(source: Path, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    return target


def main() -> None:
    copied = copy_docx(SOURCE_DOCX, OUTPUT_DOCX)
    print(f"[4.1] 已创建现有文档副本: {copied}")


if __name__ == "__main__":
    main()

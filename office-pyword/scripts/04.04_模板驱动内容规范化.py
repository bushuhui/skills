from __future__ import annotations

import json
import shutil
from pathlib import Path

from docx import Document

from _06_docx_styles import prepare_common_styles
from _13_docx_title_helpers import BODY_STYLE_CANDIDATES, SKIP_STYLE_NAMES, detect_heading_level, normalize_text

TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"
SOURCE_DOCX = TESTS_DIR / "测试文档.docx"
OUTPUT_DOCX = TESTS_DIR / "4.4_按模板修改结果.docx"
REPORT_JSON = TESTS_DIR / "4.4_模板修改报告.json"
REPORT_TXT = TESTS_DIR / "4.4_模板修改报告.txt"


def copy_docx(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def apply_template_rules(document: Document) -> dict[str, object]:
    prepare_common_styles(document)

    heading_count = {1: 0, 2: 0, 3: 0, 4: 0}
    body_count = 0
    modified: list[dict[str, object]] = []

    for index, paragraph in enumerate(document.paragraphs, start=1):
        text = normalize_text(paragraph.text)
        style_name = paragraph.style.name if paragraph.style is not None else ""
        if not text or style_name in SKIP_STYLE_NAMES:
            continue

        level = detect_heading_level(text)
        if level == 1:
            paragraph.style = document.styles["ThesisTitle1"]
            heading_count[1] += 1
            modified.append({"paragraph_index": index, "text": text, "action": "apply_ThesisTitle1"})
        elif level == 2:
            paragraph.style = document.styles["ThesisTitle2"]
            heading_count[2] += 1
            modified.append({"paragraph_index": index, "text": text, "action": "apply_ThesisTitle2"})
        elif level == 3:
            paragraph.style = document.styles["ThesisTitle3"]
            heading_count[3] += 1
            modified.append({"paragraph_index": index, "text": text, "action": "apply_ThesisTitle3"})
        elif level == 4:
            paragraph.style = document.styles["ThesisTitle4"]
            heading_count[4] += 1
            modified.append({"paragraph_index": index, "text": text, "action": "apply_ThesisTitle4"})
        elif style_name in BODY_STYLE_CANDIDATES:
            paragraph.style = document.styles["ThesisBody"]
            body_count += 1

    return {
        "source_document": str(SOURCE_DOCX),
        "output_document": str(OUTPUT_DOCX),
        "heading_count": heading_count,
        "body_paragraphs_normalized": body_count,
        "modified_samples": modified[:120],
    }


def write_report(report: dict[str, object]) -> None:
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_TXT.write_text(
        "\n".join(
            [
                "4.4 按模板要求修改现有内容报告",
                f"源文档: {report['source_document']}",
                f"输出文档: {report['output_document']}",
                f"一级标题规范化数量: {report['heading_count'][1]}",
                f"二级标题规范化数量: {report['heading_count'][2]}",
                f"三级标题规范化数量: {report['heading_count'][3]}",
                f"四级及以下标题规范化数量: {report['heading_count'][4]}",
                f"正文段落归一化数量: {report['body_paragraphs_normalized']}",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    copy_docx(SOURCE_DOCX, OUTPUT_DOCX)
    document = Document(OUTPUT_DOCX)
    report = apply_template_rules(document)
    document.save(OUTPUT_DOCX)
    write_report(report)

    print(f"[4.4] 已生成按模板修改后的文档: {OUTPUT_DOCX}")
    print(f"[4.4] 已输出模板修改报告: {REPORT_JSON}")


if __name__ == "__main__":
    main()

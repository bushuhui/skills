from __future__ import annotations

import json
import shutil
from pathlib import Path

from docx import Document

from _06_docx_styles import prepare_common_styles
from _13_docx_title_helpers import detect_heading_level, normalize_text

TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"
SOURCE_DOCX = TESTS_DIR / "测试文档.docx"
OUTPUT_DOCX = TESTS_DIR / "7.3_标题格式规范结果.docx"
REPORT_JSON = TESTS_DIR / "7.3_标题格式规范报告.json"
REPORT_TXT = TESTS_DIR / "7.3_标题格式规范报告.txt"


def copy_docx(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def main() -> None:
    copy_docx(SOURCE_DOCX, OUTPUT_DOCX)
    document = Document(OUTPUT_DOCX)
    prepare_common_styles(document)

    stats = {"level1": 0, "level2": 0, "level3": 0, "level4_plus": 0}
    samples: list[dict[str, object]] = []

    for index, paragraph in enumerate(document.paragraphs, start=1):
        text = normalize_text(paragraph.text)
        level = detect_heading_level(text)
        if level == 1:
            paragraph.style = document.styles["ThesisTitle1"]
            stats["level1"] += 1
        elif level == 2:
            paragraph.style = document.styles["ThesisTitle2"]
            stats["level2"] += 1
        elif level == 3:
            paragraph.style = document.styles["ThesisTitle3"]
            stats["level3"] += 1
        elif level == 4:
            paragraph.style = document.styles["ThesisTitle4"]
            stats["level4_plus"] += 1
        else:
            continue
        if len(samples) < 120:
            samples.append({"paragraph_index": index, "level": level, "text": text, "style": paragraph.style.name})

    document.save(OUTPUT_DOCX)

    report = {
        "source_document": str(SOURCE_DOCX),
        "output_document": str(OUTPUT_DOCX),
        "statistics": stats,
        "format_spec": {
            "level1": "三号黑体、居中、1.25 倍行距、段前段后各 1 行",
            "level2": "四号宋体加粗、居左、1.25 倍行距、段前段后各 0.5 行",
            "level3": "小四号宋体加粗、居左、1.25 倍行距、段前段后各 0.5 行",
            "level4_plus": "小四号宋体、居左、缩进 2 字符",
        },
        "samples": samples,
    }
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_TXT.write_text(
        "\n".join(
            [
                "7.3 标题格式规范报告",
                f"一级标题规范化数量: {stats['level1']}",
                f"二级标题规范化数量: {stats['level2']}",
                f"三级标题规范化数量: {stats['level3']}",
                f"三级以下标题规范化数量: {stats['level4_plus']}",
            ]
        ),
        encoding="utf-8",
    )

    print(f"[7.3] 已生成标题格式规范结果: {OUTPUT_DOCX}")
    print(f"[7.3] 已输出标题格式规范报告: {REPORT_JSON}")


if __name__ == "__main__":
    main()

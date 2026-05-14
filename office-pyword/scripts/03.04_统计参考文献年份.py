import csv
import json
import re
from pathlib import Path

from docx import Document

TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"
INPUT_DOCX = TESTS_DIR / "测试文档.docx"

YEAR_STRICT_RE = re.compile(r"(?<!\d)(19\d{2}|20[0-2]\d)(?=\s*[,.;:)\]，。）》])")
YEAR_FALLBACK_RE = re.compile(r"(?<!\d)(19\d{2}|20[0-2]\d)(?!\d)")
REFERENCE_NUMBER_RE = re.compile(r"^\[\d+\]")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def collect_reference_entries(document: Document) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []

    for index, paragraph in enumerate(document.paragraphs, start=1):
        text = normalize_text(paragraph.text)
        style_name = paragraph.style.name if paragraph.style is not None else ""
        if not text:
            continue

        if style_name == "EndNote Bibliography" or REFERENCE_NUMBER_RE.match(text):
            entries.append(
                {
                    "paragraph_index": index,
                    "style_name": style_name,
                    "raw_text": text,
                }
            )

    return entries


def parse_reference_year(text: str) -> tuple[int | None, str]:
    strict_matches = list(YEAR_STRICT_RE.finditer(text))
    if strict_matches:
        return int(strict_matches[0].group(1)), "strict_punctuation"

    for match in YEAR_FALLBACK_RE.finditer(text):
        next_char = text[match.end() : match.end() + 1]
        if next_char not in {"-", "–"}:
            return int(match.group(1)), "fallback_non_range"

    return None, "not_found"


def classify_language(text: str) -> str:
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    english_words = len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", text))

    if chinese_chars >= 2 and chinese_chars >= english_words:
        return "中文"
    if english_words >= 3 and english_words > chinese_chars:
        return "英文"
    return "未确定"


def main() -> None:
    if not INPUT_DOCX.exists():
        raise FileNotFoundError(f"未找到输入文件: {INPUT_DOCX}")

    TESTS_DIR.mkdir(parents=True, exist_ok=True)
    document = Document(INPUT_DOCX)
    reference_entries = collect_reference_entries(document)

    year_counter: dict[int, int] = {}
    details: list[dict[str, object]] = []

    for ref_index, entry in enumerate(reference_entries, start=1):
        year, rule = parse_reference_year(entry["raw_text"])
        language = classify_language(entry["raw_text"])
        if year is not None:
            year_counter[year] = year_counter.get(year, 0) + 1

        details.append(
            {
                "ref_index": ref_index,
                "paragraph_index": entry["paragraph_index"],
                "style_name": entry["style_name"],
                "raw_text": entry["raw_text"],
                "parsed_year": year,
                "language": language,
                "matched_rule": rule,
                "status": "success" if year is not None else "year_not_found",
            }
        )

    summary_rows = [
        {"year": year, "count": count}
        for year, count in sorted(year_counter.items())
    ]

    json_path = TESTS_DIR / "3.4_参考文献年份统计.json"
    csv_path = TESTS_DIR / "3.4_参考文献年份统计.csv"
    details_path = TESTS_DIR / "3.4_参考文献解析明细.json"

    output = {
        "input_file": str(INPUT_DOCX),
        "reference_count": len(reference_entries),
        "parsed_year_count": len([item for item in details if item["parsed_year"] is not None]),
        "unresolved_count": len([item for item in details if item["parsed_year"] is None]),
        "year_counts": summary_rows,
    }
    json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    details_path.write_text(json.dumps(details, ensure_ascii=False, indent=2), encoding="utf-8")

    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["year", "count"])
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"[3.4] 输入文档: {INPUT_DOCX}")
    print(f"[3.4] 已输出参考文献年份统计 JSON: {json_path}")
    print(f"[3.4] 已输出参考文献年份统计 CSV: {csv_path}")
    print(f"[3.4] 已输出参考文献解析明细 JSON: {details_path}")
    print(f"[3.4] 参考文献条目数: {len(reference_entries)}，成功识别年份数: {output['parsed_year_count']}")


if __name__ == "__main__":
    main()

import csv
import json
import re
from datetime import date
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

    current_year = date.today().year
    recent_years = list(range(current_year - 4, current_year + 1))
    per_year_counts = {
        year: {"year": year, "chinese_count": 0, "english_count": 0, "unknown_count": 0, "total_count": 0}
        for year in recent_years
    }
    details: list[dict[str, object]] = []

    for ref_index, entry in enumerate(reference_entries, start=1):
        year, rule = parse_reference_year(entry["raw_text"])
        language = classify_language(entry["raw_text"])

        detail = {
            "ref_index": ref_index,
            "paragraph_index": entry["paragraph_index"],
            "style_name": entry["style_name"],
            "raw_text": entry["raw_text"],
            "parsed_year": year,
            "language": language,
            "matched_rule": rule,
            "in_recent_five_years": year in per_year_counts,
        }
        details.append(detail)

        if year not in per_year_counts:
            continue

        bucket = per_year_counts[year]
        bucket["total_count"] += 1
        if language == "中文":
            bucket["chinese_count"] += 1
        elif language == "英文":
            bucket["english_count"] += 1
        else:
            bucket["unknown_count"] += 1

    summary_rows = [per_year_counts[year] for year in sorted(per_year_counts)]
    output = {
        "input_file": str(INPUT_DOCX),
        "statistics_date": str(date.today()),
        "recent_five_year_range": {
            "start_year": recent_years[0],
            "end_year": recent_years[-1],
            "years": recent_years,
        },
        "recent_five_year_total": sum(row["total_count"] for row in summary_rows),
        "recent_five_year_chinese_total": sum(row["chinese_count"] for row in summary_rows),
        "recent_five_year_english_total": sum(row["english_count"] for row in summary_rows),
        "recent_five_year_unknown_total": sum(row["unknown_count"] for row in summary_rows),
        "per_year_counts": summary_rows,
        "details": details,
    }

    json_path = TESTS_DIR / "3.5_近五年参考文献统计.json"
    csv_path = TESTS_DIR / "3.5_近五年参考文献统计.csv"

    json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["year", "chinese_count", "english_count", "unknown_count", "total_count"])
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"[3.5] 输入文档: {INPUT_DOCX}")
    print(f"[3.5] 已输出近五年参考文献统计 JSON: {json_path}")
    print(f"[3.5] 已输出近五年参考文献统计 CSV: {csv_path}")
    print(
        f"[3.5] 近五年范围: {recent_years[0]}-{recent_years[-1]}，"
        f"中文={output['recent_five_year_chinese_total']}，英文={output['recent_five_year_english_total']}，"
        f"未确定={output['recent_five_year_unknown_total']}"
    )


if __name__ == "__main__":
    main()

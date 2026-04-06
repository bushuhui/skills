import json
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile

from lxml import etree

TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"
INPUT_DOCX = TESTS_DIR / "测试文档.docx"

NS = {
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "ep": "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties",
    "ctp": "http://schemas.openxmlformats.org/officeDocument/2006/custom-properties",
    "vt": "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes",
}

CORE_FIELDS = [
    ("title", "dc:title"),
    ("subject", "dc:subject"),
    ("creator", "dc:creator"),
    ("keywords", "cp:keywords"),
    ("description", "dc:description"),
    ("last_modified_by", "cp:lastModifiedBy"),
    ("revision", "cp:revision"),
    ("created", "dcterms:created"),
    ("modified", "dcterms:modified"),
    ("category", "cp:category"),
    ("content_status", "cp:contentStatus"),
]


def first_text(root, xpath: str) -> str | None:
    values = root.xpath(f"./{xpath}/text()", namespaces=NS)
    if not values:
        return None
    value = str(values[0]).strip()
    return value or None


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_iso_datetime(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
    except ValueError:
        return value


def load_core_properties(zip_file: ZipFile) -> dict[str, object]:
    if "docProps/core.xml" not in zip_file.namelist():
        return {}

    root = etree.fromstring(zip_file.read("docProps/core.xml"))
    result: dict[str, object] = {}
    for field, xpath in CORE_FIELDS:
        value = first_text(root, xpath)
        if field in {"created", "modified"}:
            value = parse_iso_datetime(value)
        result[field] = value
    return result


def parse_extended_value(text: str | None) -> object:
    if text is None:
        return None
    value = text.strip()
    if not value:
        return None
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        return value


def load_extended_properties(zip_file: ZipFile) -> dict[str, object]:
    if "docProps/app.xml" not in zip_file.namelist():
        return {}

    root = etree.fromstring(zip_file.read("docProps/app.xml"))
    result: dict[str, object] = {}
    for child in root:
        key = local_name(child.tag)
        result[key] = parse_extended_value(child.text)
    return result


def parse_custom_value(node) -> tuple[str, object]:
    child = next(iter(node), None)
    if child is None:
        return "unknown", None

    tag_name = local_name(child.tag)
    text = child.text.strip() if child.text else ""

    if tag_name in {"i4", "int"}:
        return tag_name, int(text)
    if tag_name in {"r8", "decimal"}:
        return tag_name, float(text)
    if tag_name == "bool":
        return tag_name, text.lower() == "true"
    if tag_name == "filetime":
        return tag_name, parse_iso_datetime(text)
    return tag_name, text


def load_custom_properties(zip_file: ZipFile) -> dict[str, dict[str, object]]:
    if "docProps/custom.xml" not in zip_file.namelist():
        return {}

    root = etree.fromstring(zip_file.read("docProps/custom.xml"))
    properties: dict[str, dict[str, object]] = {}

    for prop in root.xpath(".//ctp:property", namespaces=NS):
        name = prop.get("name", "")
        value_type, value = parse_custom_value(prop)
        properties[name] = {
            "pid": prop.get("pid"),
            "type": value_type,
            "value": value,
        }
    return properties


def load_file_system_properties(docx_path: Path) -> dict[str, object]:
    stat = docx_path.stat()
    modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).astimezone().isoformat()
    created = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).astimezone().isoformat()
    return {
        "file_name": docx_path.name,
        "absolute_path": str(docx_path.resolve()),
        "file_size_bytes": stat.st_size,
        "file_size_kb": round(stat.st_size / 1024, 2),
        "created_time_local": created,
        "modified_time_local": modified,
        "suffix": docx_path.suffix,
    }


def build_report_text(result: dict[str, object]) -> str:
    lines = [
        "文档属性报告",
        f"输入文件: {result['file_system']['absolute_path']}",
        "",
        "核心属性:",
    ]
    for key, value in result["core_properties"].items():
        lines.append(f"  {key}: {value}")

    lines.append("")
    lines.append("扩展属性:")
    for key, value in result["extended_properties"].items():
        lines.append(f"  {key}: {value}")

    lines.append("")
    lines.append("自定义属性:")
    for key, value in result["custom_properties"].items():
        lines.append(f"  {key}: {value['value']} ({value['type']})")

    lines.append("")
    lines.append("文件系统属性:")
    for key, value in result["file_system"].items():
        lines.append(f"  {key}: {value}")

    return "\n".join(lines)


def main() -> None:
    if not INPUT_DOCX.exists():
        raise FileNotFoundError(f"未找到输入文件: {INPUT_DOCX}")

    TESTS_DIR.mkdir(parents=True, exist_ok=True)

    with ZipFile(INPUT_DOCX) as zip_file:
        result = {
            "input_file": str(INPUT_DOCX),
            "core_properties": load_core_properties(zip_file),
            "extended_properties": load_extended_properties(zip_file),
            "custom_properties": load_custom_properties(zip_file),
            "file_system": load_file_system_properties(INPUT_DOCX),
        }

    json_path = TESTS_DIR / "3.1_文档属性.json"
    txt_path = TESTS_DIR / "3.1_文档属性.txt"

    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    txt_path.write_text(build_report_text(result), encoding="utf-8")

    print(f"[3.1] 输入文档: {INPUT_DOCX}")
    print(f"[3.1] 已输出文档属性 JSON: {json_path}")
    print(f"[3.1] 已输出文档属性 TXT: {txt_path}")
    print(f"[3.1] 核心属性项数: {len(result['core_properties'])}，自定义属性项数: {len(result['custom_properties'])}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree

from _14_docx_review_demo import SOURCE_DOCX, TESTS_DIR, ensure_demo_source_document

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}

OUTPUT_DOCX = TESTS_DIR / "19.1_密码保护文档.docx"
INFO_TXT = TESTS_DIR / "19.1_密码说明.txt"
PASSWORD = "Docx@2026"


def w_tag(name: str) -> str:
    return f"{{{W_NS}}}{name}"


def build_package_map(docx_path: Path) -> dict[str, bytes]:
    with ZipFile(docx_path, "r") as zip_file:
        return {info.filename: zip_file.read(info.filename) for info in zip_file.infolist()}


def write_package_map(package_map: dict[str, bytes], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output_path, "w", compression=ZIP_DEFLATED) as zip_file:
        for name, content in package_map.items():
            zip_file.writestr(name, content)


def to_xml_bytes(root) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone="yes")


def legacy_word_password_hash(password: str) -> str:
    verifier = 0
    for char in reversed(password[:15]):
        verifier = ((verifier >> 14) & 0x0001) | ((verifier << 1) & 0x7FFF)
        verifier ^= ord(char)
    verifier = ((verifier >> 14) & 0x0001) | ((verifier << 1) & 0x7FFF)
    verifier ^= len(password[:15])
    verifier ^= 0xCE4B
    return f"{verifier:04X}"


def insert_in_schema_order(parent, element, successor_names: list[str]) -> None:
    successor_tags = {w_tag(name) for name in successor_names}
    for index, child in enumerate(list(parent)):
        if child.tag in successor_tags:
            parent.insert(index, element)
            return
    parent.append(element)


def apply_password_protection(package_map: dict[str, bytes], password: str) -> None:
    settings_root = etree.fromstring(package_map["word/settings.xml"])
    for existing in settings_root.xpath("./w:documentProtection", namespaces=NS):
        settings_root.remove(existing)

    protection = etree.Element(w_tag("documentProtection"), nsmap=settings_root.nsmap)
    protection.set(w_tag("edit"), "readOnly")
    protection.set(w_tag("enforcement"), "1")
    protection.set(w_tag("formatting"), "0")
    protection.set(w_tag("password"), legacy_word_password_hash(password))

    successors = [
        "autoFormatOverride",
        "styleLockTheme",
        "styleLockQFSet",
        "defaultTabStop",
        "evenAndOddHeaders",
        "updateFields",
        "compat",
        "docVars",
        "rsids",
    ]
    insert_in_schema_order(settings_root, protection, successors)
    package_map["word/settings.xml"] = to_xml_bytes(settings_root)


def main() -> None:
    ensure_demo_source_document(SOURCE_DOCX)
    shutil.copyfile(SOURCE_DOCX, OUTPUT_DOCX)
    package_map = build_package_map(OUTPUT_DOCX)
    apply_password_protection(package_map, PASSWORD)
    write_package_map(package_map, OUTPUT_DOCX)

    INFO_TXT.write_text(
        "\n".join(
            [
                "19.1 密码保护说明",
                f"源文档: {SOURCE_DOCX}",
                f"输出文档: {OUTPUT_DOCX}",
                f"保护方式: Word 限制编辑密码保护",
                f"密码: {PASSWORD}",
                "说明: 该脚本添加的是“停止保护时需要输入密码”的编辑限制，不是打开文档时的文件加密密码。",
            ]
        ),
        encoding="utf-8",
    )

    print(f"[19.1] 已生成示例源文档: {SOURCE_DOCX}")
    print(f"[19.1] 已生成密码保护文档: {OUTPUT_DOCX}")
    print(f"[19.1] 已输出密码说明: {INFO_TXT}")


if __name__ == "__main__":
    main()

from __future__ import annotations

from pathlib import Path

from _14_docx_review_demo import SOURCE_DOCX, TESTS_DIR, ensure_demo_source_document
from _15_docx_crypto import AgileEncryptionConfig, decrypt_docx_file, encrypt_docx_file

OUTPUT_DOCX = TESTS_DIR / "19.4_打开密码保护文档.docx"
INFO_TXT = TESTS_DIR / "19.4_打开密码说明.txt"
PASSWORD = "Open@2026"


def main() -> None:
    source_path = ensure_demo_source_document(SOURCE_DOCX)
    TESTS_DIR.mkdir(parents=True, exist_ok=True)

    encrypt_docx_file(
        input_path=source_path,
        output_path=OUTPUT_DOCX,
        password=PASSWORD,
        config=AgileEncryptionConfig(),
    )

    decrypted_package = decrypt_docx_file(OUTPUT_DOCX, PASSWORD)
    source_bytes = source_path.read_bytes()
    if decrypted_package != source_bytes:
        raise RuntimeError("加密文档回读校验失败，输出文件未能正确还原原始包内容。")

    INFO_TXT.write_text(
        "\n".join(
            [
                "19.4 打开密码保护说明",
                f"源文档: {source_path}",
                f"输出文档: {OUTPUT_DOCX}",
                f"密码: {PASSWORD}",
                "加密方式: OOXML Agile Encryption (AES-256 + SHA-512)",
                "说明: 打开文档时需要输入密码，不同于限制编辑密码。",
                "校验: 脚本已完成加密后回读校验，确认可还原原始 Office 包。",
            ]
        ),
        encoding="utf-8",
    )

    print(f"[19.4] 已生成示例源文档: {source_path}")
    print(f"[19.4] 已生成打开密码保护文档: {OUTPUT_DOCX}")
    print(f"[19.4] 已输出密码说明: {INFO_TXT}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import struct
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from Crypto.Cipher import AES

ENCRYPTION_NS = "http://schemas.microsoft.com/office/2006/encryption"
PASSWORD_NS = "http://schemas.microsoft.com/office/2006/keyEncryptor/password"

FREESECT = 0xFFFFFFFF
ENDOFCHAIN = 0xFFFFFFFE
FATSECT = 0xFFFFFFFD

VERIFIER_INPUT_BLOCK = bytes([0xFE, 0xA7, 0xD2, 0x76, 0x3B, 0x4B, 0x9E, 0x79])
VERIFIER_HASH_BLOCK = bytes([0xD7, 0xAA, 0x0F, 0x6D, 0x30, 0x61, 0x34, 0x4E])
KEY_VALUE_BLOCK = bytes([0x14, 0x6E, 0x0B, 0xE7, 0xAB, 0xAC, 0xD0, 0xD6])
HMAC_KEY_BLOCK = bytes([0x5F, 0xB2, 0xAD, 0x01, 0x0C, 0xB9, 0xE1, 0xF6])
HMAC_VALUE_BLOCK = bytes([0xA0, 0x67, 0x7F, 0x02, 0xB2, 0x2C, 0x84, 0x33])


@dataclass(frozen=True)
class AgileEncryptionConfig:
    spin_count: int = 100000
    key_bits: int = 256
    block_size: int = 16
    segment_size: int = 4096
    hash_algorithm_xml: str = "SHA512"
    hash_algorithm_name: str = "sha512"
    encryption_info_min_size: int = 4608


def zero_pad(data: bytes, block_size: int) -> bytes:
    padding = (-len(data)) % block_size
    if padding == 0:
        return data
    return data + (b"\x00" * padding)


def trim_or_expand(data: bytes, size: int) -> bytes:
    if len(data) >= size:
        return data[:size]
    return data + (b"\x36" * (size - len(data)))


def hash_bytes(data: bytes, hash_name: str) -> bytes:
    return hashlib.new(hash_name, data).digest()


def xml_hash_to_hashlib_name(hash_algorithm: str) -> str:
    return hash_algorithm.replace("-", "").lower()


def derive_agile_key(
    password: str,
    salt: bytes,
    block_key: bytes,
    config: AgileEncryptionConfig,
) -> bytes:
    password_bytes = password.encode("utf-16le")
    result = hash_bytes(salt + password_bytes, config.hash_algorithm_name)
    for index in range(config.spin_count):
        result = hash_bytes(struct.pack("<I", index) + result, config.hash_algorithm_name)
    final = hash_bytes(result + block_key, config.hash_algorithm_name)
    return trim_or_expand(final, config.key_bits // 8)


def derive_iv(
    key_salt: bytes,
    block_size: int,
    hash_name: str,
    block_key: bytes | None = None,
) -> bytes:
    seed = key_salt if block_key is None else hash_bytes(key_salt + block_key, hash_name)
    return trim_or_expand(seed, block_size)


def aes_cbc_encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(data)


def aes_cbc_decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(data)


def encrypt_package_stream(
    package_bytes: bytes,
    package_key: bytes,
    key_data_salt: bytes,
    config: AgileEncryptionConfig,
) -> bytes:
    encrypted = bytearray(struct.pack("<Q", len(package_bytes)))
    for index, offset in enumerate(range(0, len(package_bytes), config.segment_size)):
        chunk = package_bytes[offset : offset + config.segment_size]
        iv = derive_iv(
            key_data_salt,
            config.block_size,
            config.hash_algorithm_name,
            struct.pack("<I", index),
        )
        encrypted.extend(aes_cbc_encrypt(zero_pad(chunk, config.block_size), package_key, iv))
    return bytes(encrypted)


def decrypt_package_stream(
    encrypted_package: bytes,
    package_key: bytes,
    key_data_salt: bytes,
    config: AgileEncryptionConfig,
) -> bytes:
    if len(encrypted_package) < 8:
        raise ValueError("EncryptedPackage 流长度不足，无法读取原始包大小。")

    original_size = struct.unpack("<Q", encrypted_package[:8])[0]
    remaining = original_size
    cursor = 8
    chunks: list[bytes] = []

    for index in range((original_size + config.segment_size - 1) // config.segment_size):
        plain_size = min(config.segment_size, remaining)
        encrypted_size = ((plain_size + config.block_size - 1) // config.block_size) * config.block_size
        block = encrypted_package[cursor : cursor + encrypted_size]
        if len(block) != encrypted_size:
            raise ValueError("EncryptedPackage 流不完整，无法完成分段解密。")
        iv = derive_iv(
            key_data_salt,
            config.block_size,
            config.hash_algorithm_name,
            struct.pack("<I", index),
        )
        chunks.append(aes_cbc_decrypt(block, package_key, iv)[:plain_size])
        cursor += encrypted_size
        remaining -= plain_size

    return b"".join(chunks)[:original_size]


def _ensure_minimum_xml_size(root: ET.Element, config: AgileEncryptionConfig) -> bytes:
    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    while len(xml_bytes) + 8 < config.encryption_info_min_size:
        padding = config.encryption_info_min_size - (len(xml_bytes) + 8)
        root.append(ET.Comment("0" * max(64, padding)))
        xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return xml_bytes


def build_agile_encryption_info(
    password: str,
    encrypted_package: bytes,
    package_key: bytes,
    key_data_salt: bytes,
    password_salt: bytes,
    config: AgileEncryptionConfig,
) -> bytes:
    password_iv = derive_iv(password_salt, config.block_size, config.hash_algorithm_name)

    verifier_input = os.urandom(len(password_salt))
    verifier_hash = hash_bytes(verifier_input, config.hash_algorithm_name)

    verifier_input_key = derive_agile_key(password, password_salt, VERIFIER_INPUT_BLOCK, config)
    verifier_hash_key = derive_agile_key(password, password_salt, VERIFIER_HASH_BLOCK, config)
    key_value_key = derive_agile_key(password, password_salt, KEY_VALUE_BLOCK, config)

    encrypted_verifier_input = aes_cbc_encrypt(
        zero_pad(verifier_input, config.block_size),
        verifier_input_key,
        password_iv,
    )
    encrypted_verifier_hash = aes_cbc_encrypt(
        zero_pad(verifier_hash, config.block_size),
        verifier_hash_key,
        password_iv,
    )
    encrypted_key_value = aes_cbc_encrypt(
        zero_pad(package_key, config.block_size),
        key_value_key,
        password_iv,
    )

    hmac_salt = os.urandom(len(key_data_salt))
    encrypted_hmac_key = aes_cbc_encrypt(
        zero_pad(hmac_salt, config.block_size),
        package_key,
        derive_iv(key_data_salt, config.block_size, config.hash_algorithm_name, HMAC_KEY_BLOCK),
    )
    hmac_value = hmac.new(hmac_salt, encrypted_package, config.hash_algorithm_name).digest()
    encrypted_hmac_value = aes_cbc_encrypt(
        zero_pad(hmac_value, config.block_size),
        package_key,
        derive_iv(key_data_salt, config.block_size, config.hash_algorithm_name, HMAC_VALUE_BLOCK),
    )

    ET.register_namespace("", ENCRYPTION_NS)
    ET.register_namespace("p", PASSWORD_NS)

    root = ET.Element(f"{{{ENCRYPTION_NS}}}encryption")
    ET.SubElement(
        root,
        f"{{{ENCRYPTION_NS}}}keyData",
        {
            "saltSize": str(len(key_data_salt)),
            "blockSize": str(config.block_size),
            "keyBits": str(config.key_bits),
            "hashSize": str(len(hash_bytes(b"", config.hash_algorithm_name))),
            "cipherAlgorithm": "AES",
            "cipherChaining": "ChainingModeCBC",
            "hashAlgorithm": config.hash_algorithm_xml,
            "saltValue": base64.b64encode(key_data_salt).decode("ascii"),
        },
    )
    ET.SubElement(
        root,
        f"{{{ENCRYPTION_NS}}}dataIntegrity",
        {
            "encryptedHmacKey": base64.b64encode(encrypted_hmac_key).decode("ascii"),
            "encryptedHmacValue": base64.b64encode(encrypted_hmac_value).decode("ascii"),
        },
    )
    key_encryptors = ET.SubElement(root, f"{{{ENCRYPTION_NS}}}keyEncryptors")
    key_encryptor = ET.SubElement(
        key_encryptors,
        f"{{{ENCRYPTION_NS}}}keyEncryptor",
        {"uri": "http://schemas.microsoft.com/office/2006/keyEncryptor/password"},
    )
    ET.SubElement(
        key_encryptor,
        f"{{{PASSWORD_NS}}}encryptedKey",
        {
            "spinCount": str(config.spin_count),
            "saltSize": str(len(password_salt)),
            "blockSize": str(config.block_size),
            "keyBits": str(config.key_bits),
            "hashSize": str(len(hash_bytes(b"", config.hash_algorithm_name))),
            "cipherAlgorithm": "AES",
            "cipherChaining": "ChainingModeCBC",
            "hashAlgorithm": config.hash_algorithm_xml,
            "saltValue": base64.b64encode(password_salt).decode("ascii"),
            "encryptedVerifierHashInput": base64.b64encode(encrypted_verifier_input).decode("ascii"),
            "encryptedVerifierHashValue": base64.b64encode(encrypted_verifier_hash).decode("ascii"),
            "encryptedKeyValue": base64.b64encode(encrypted_key_value).decode("ascii"),
        },
    )

    xml_bytes = _ensure_minimum_xml_size(root, config)
    return struct.pack("<HHI", 4, 4, 0x40) + xml_bytes


def _encode_directory_entry(
    name: str,
    object_type: int,
    color_flag: int,
    left_sibling_id: int,
    right_sibling_id: int,
    child_id: int,
    start_sector: int,
    stream_size: int,
) -> bytes:
    encoded_name = (name + "\x00").encode("utf-16le")
    padded_name = encoded_name[:64].ljust(64, b"\x00")
    return struct.pack(
        "<64sHBBIII16sIQQIQ",
        padded_name,
        len(encoded_name),
        object_type,
        color_flag,
        left_sibling_id,
        right_sibling_id,
        child_id,
        b"\x00" * 16,
        0,
        0,
        0,
        start_sector,
        stream_size,
    )


def build_compound_file(streams: list[tuple[str, bytes]]) -> bytes:
    sector_size = 512
    sorted_streams = sorted(streams, key=lambda item: item[0].casefold())
    for name, data in sorted_streams:
        if len(data) < 4096:
            raise ValueError(f"{name} 流长度不足 4096 字节，当前最小 CFB 写入器不支持 mini stream。")

    stream_sector_counts = [(len(data) + sector_size - 1) // sector_size for _, data in sorted_streams]
    directory_sector_count = 1
    non_fat_sectors = sum(stream_sector_counts) + directory_sector_count
    fat_sector_count = 1
    while non_fat_sectors + fat_sector_count > fat_sector_count * (sector_size // 4):
        fat_sector_count += 1
    total_sectors = non_fat_sectors + fat_sector_count

    stream_starts: list[int] = []
    cursor = 0
    for sector_count in stream_sector_counts:
        stream_starts.append(cursor)
        cursor += sector_count
    directory_start = cursor
    cursor += directory_sector_count
    fat_starts = list(range(cursor, cursor + fat_sector_count))

    fat_entries = [FREESECT] * (fat_sector_count * (sector_size // 4))
    for start, sector_count in zip(stream_starts, stream_sector_counts):
        for offset in range(sector_count):
            sector_index = start + offset
            fat_entries[sector_index] = sector_index + 1 if offset + 1 < sector_count else ENDOFCHAIN
    fat_entries[directory_start] = ENDOFCHAIN
    for sector_index in fat_starts:
        fat_entries[sector_index] = FATSECT

    sectors = [bytearray(sector_size) for _ in range(total_sectors)]

    for (name, data), start, sector_count in zip(sorted_streams, stream_starts, stream_sector_counts):
        padded = data.ljust(sector_count * sector_size, b"\x00")
        for offset in range(sector_count):
            begin = offset * sector_size
            end = begin + sector_size
            sectors[start + offset][:] = padded[begin:end]

    directory_entries = [
        _encode_directory_entry(
            name="Root Entry",
            object_type=5,
            color_flag=1,
            left_sibling_id=FREESECT,
            right_sibling_id=FREESECT,
            child_id=1 if sorted_streams else FREESECT,
            start_sector=ENDOFCHAIN,
            stream_size=0,
        )
    ]
    for index, ((name, data), start_sector) in enumerate(zip(sorted_streams, stream_starts), start=1):
        directory_entries.append(
            _encode_directory_entry(
                name=name,
                object_type=2,
                color_flag=1,
                left_sibling_id=FREESECT,
                right_sibling_id=index + 1 if index < len(sorted_streams) else FREESECT,
                child_id=FREESECT,
                start_sector=start_sector,
                stream_size=len(data),
            )
        )
    directory_blob = b"".join(directory_entries).ljust(directory_sector_count * sector_size, b"\x00")
    sectors[directory_start][:] = directory_blob[:sector_size]

    fat_blob = b"".join(struct.pack("<I", entry) for entry in fat_entries)
    fat_blob = fat_blob.ljust(fat_sector_count * sector_size, b"\xFF")
    for offset, sector_index in enumerate(fat_starts):
        begin = offset * sector_size
        end = begin + sector_size
        sectors[sector_index][:] = fat_blob[begin:end]

    difat = fat_starts + ([FREESECT] * (109 - len(fat_starts)))
    header = struct.pack(
        "<8s16sHHHHH6sIIIIIIIII109I",
        bytes.fromhex("D0CF11E0A1B11AE1"),
        b"\x00" * 16,
        0x003E,
        0x0003,
        0xFFFE,
        9,
        6,
        b"\x00" * 6,
        0,
        len(fat_starts),
        directory_start,
        0,
        4096,
        ENDOFCHAIN,
        0,
        ENDOFCHAIN,
        0,
        *difat,
    )

    return header + b"".join(bytes(sector) for sector in sectors)


def _read_chain(start_sector: int, sectors: list[bytes], fat_entries: list[int], sector_size: int) -> bytes:
    if start_sector in {FREESECT, ENDOFCHAIN}:
        return b""
    chunks: list[bytes] = []
    sector_index = start_sector
    visited: set[int] = set()
    while sector_index not in {FREESECT, ENDOFCHAIN}:
        if sector_index in visited or sector_index >= len(sectors):
            raise ValueError("CFB FAT 链异常，无法安全读取流。")
        visited.add(sector_index)
        chunks.append(sectors[sector_index])
        sector_index = fat_entries[sector_index]
    return b"".join(chunks)


def read_compound_streams(container_bytes: bytes) -> dict[str, bytes]:
    if len(container_bytes) < 512:
        raise ValueError("输入数据长度不足，无法识别 CFB 文件头。")

    header = struct.unpack("<8s16sHHHHH6sIIIIIIIII109I", container_bytes[:512])
    signature = header[0]
    if signature != bytes.fromhex("D0CF11E0A1B11AE1"):
        raise ValueError("文件头不是 CFB 容器，无法读取加密流。")

    sector_shift = header[5]
    sector_size = 1 << sector_shift
    fat_sector_count = header[9]
    directory_start = header[10]
    difat = list(header[17 : 17 + 109])

    sectors = [
        container_bytes[offset : offset + sector_size]
        for offset in range(512, len(container_bytes), sector_size)
    ]

    fat_entries: list[int] = []
    for sector_index in difat[:fat_sector_count]:
        if sector_index in {FREESECT, ENDOFCHAIN}:
            continue
        fat_sector = sectors[sector_index]
        fat_entries.extend(struct.unpack("<" + ("I" * (sector_size // 4)), fat_sector))

    directory_stream = _read_chain(directory_start, sectors, fat_entries, sector_size)
    result: dict[str, bytes] = {}
    for offset in range(0, len(directory_stream), 128):
        entry = directory_stream[offset : offset + 128]
        if len(entry) < 128:
            continue
        name_bytes, name_length, object_type, _, _, _, _, _, _, _, _, start_sector, stream_size = struct.unpack(
            "<64sHBBIII16sIQQIQ",
            entry,
        )
        if object_type != 2 or name_length < 2:
            continue
        name = name_bytes[: name_length - 2].decode("utf-16le")
        result[name] = _read_chain(start_sector, sectors, fat_entries, sector_size)[:stream_size]
    return result


def parse_agile_encryption_info(encryption_info: bytes) -> tuple[AgileEncryptionConfig, dict[str, object]]:
    if len(encryption_info) < 8:
        raise ValueError("EncryptionInfo 流长度不足。")
    version_major, version_minor, reserved = struct.unpack("<HHI", encryption_info[:8])
    if (version_major, version_minor, reserved) != (4, 4, 0x40):
        raise ValueError("当前读取器仅支持 Agile Encryption (4.4)。")

    root = ET.fromstring(encryption_info[8:])
    namespaces = {"enc": ENCRYPTION_NS, "p": PASSWORD_NS}
    key_data = root.find("enc:keyData", namespaces)
    data_integrity = root.find("enc:dataIntegrity", namespaces)
    encrypted_key = root.find(".//p:encryptedKey", namespaces)
    if key_data is None or data_integrity is None or encrypted_key is None:
        raise ValueError("EncryptionInfo XML 结构不完整。")

    hash_algorithm_xml = encrypted_key.attrib["hashAlgorithm"]
    config = AgileEncryptionConfig(
        spin_count=int(encrypted_key.attrib["spinCount"]),
        key_bits=int(encrypted_key.attrib["keyBits"]),
        block_size=int(encrypted_key.attrib["blockSize"]),
        hash_algorithm_xml=hash_algorithm_xml,
        hash_algorithm_name=xml_hash_to_hashlib_name(hash_algorithm_xml),
    )

    info = {
        "key_data_salt": base64.b64decode(key_data.attrib["saltValue"]),
        "password_salt": base64.b64decode(encrypted_key.attrib["saltValue"]),
        "encrypted_verifier_hash_input": base64.b64decode(encrypted_key.attrib["encryptedVerifierHashInput"]),
        "encrypted_verifier_hash_value": base64.b64decode(encrypted_key.attrib["encryptedVerifierHashValue"]),
        "encrypted_key_value": base64.b64decode(encrypted_key.attrib["encryptedKeyValue"]),
        "encrypted_hmac_key": base64.b64decode(data_integrity.attrib["encryptedHmacKey"]),
        "encrypted_hmac_value": base64.b64decode(data_integrity.attrib["encryptedHmacValue"]),
        "salt_size": int(key_data.attrib["saltSize"]),
        "hash_size": int(key_data.attrib["hashSize"]),
    }
    return config, info


def decrypt_package_key(
    password: str,
    config: AgileEncryptionConfig,
    info: dict[str, object],
) -> bytes:
    password_salt = info["password_salt"]
    password_iv = derive_iv(password_salt, config.block_size, config.hash_algorithm_name)

    verifier_input_key = derive_agile_key(password, password_salt, VERIFIER_INPUT_BLOCK, config)
    verifier_hash_key = derive_agile_key(password, password_salt, VERIFIER_HASH_BLOCK, config)
    key_value_key = derive_agile_key(password, password_salt, KEY_VALUE_BLOCK, config)

    verifier_input = aes_cbc_decrypt(info["encrypted_verifier_hash_input"], verifier_input_key, password_iv)[
        : len(password_salt)
    ]
    verifier_hash = aes_cbc_decrypt(info["encrypted_verifier_hash_value"], verifier_hash_key, password_iv)[
        : info["hash_size"]
    ]
    if hash_bytes(verifier_input, config.hash_algorithm_name) != verifier_hash:
        raise ValueError("密码校验失败，无法解密包密钥。")

    package_key = aes_cbc_decrypt(info["encrypted_key_value"], key_value_key, password_iv)[: config.key_bits // 8]
    return package_key


def verify_encrypted_package_integrity(
    encrypted_package: bytes,
    package_key: bytes,
    config: AgileEncryptionConfig,
    info: dict[str, object],
) -> None:
    key_data_salt = info["key_data_salt"]
    hmac_salt = aes_cbc_decrypt(
        info["encrypted_hmac_key"],
        package_key,
        derive_iv(key_data_salt, config.block_size, config.hash_algorithm_name, HMAC_KEY_BLOCK),
    )[: info["salt_size"]]
    expected_hmac = hmac.new(hmac_salt, encrypted_package, config.hash_algorithm_name).digest()
    actual_hmac = aes_cbc_decrypt(
        info["encrypted_hmac_value"],
        package_key,
        derive_iv(key_data_salt, config.block_size, config.hash_algorithm_name, HMAC_VALUE_BLOCK),
    )[: info["hash_size"]]
    if not hmac.compare_digest(expected_hmac, actual_hmac):
        raise ValueError("EncryptedPackage HMAC 校验失败，文件可能已损坏。")


def encrypt_docx_file(
    input_path: Path,
    output_path: Path,
    password: str,
    config: AgileEncryptionConfig | None = None,
) -> None:
    active_config = config or AgileEncryptionConfig()
    package_bytes = input_path.read_bytes()
    key_data_salt = os.urandom(16)
    password_salt = os.urandom(16)
    package_key = os.urandom(active_config.key_bits // 8)

    encrypted_package = encrypt_package_stream(package_bytes, package_key, key_data_salt, active_config)
    encryption_info = build_agile_encryption_info(
        password=password,
        encrypted_package=encrypted_package,
        package_key=package_key,
        key_data_salt=key_data_salt,
        password_salt=password_salt,
        config=active_config,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(
        build_compound_file(
            [
                ("EncryptionInfo", encryption_info),
                ("EncryptedPackage", encrypted_package),
            ]
        )
    )


def decrypt_docx_file(
    encrypted_docx_path: Path,
    password: str,
) -> bytes:
    streams = read_compound_streams(encrypted_docx_path.read_bytes())
    encryption_info = streams.get("EncryptionInfo")
    encrypted_package = streams.get("EncryptedPackage")
    if encryption_info is None or encrypted_package is None:
        raise ValueError("加密文档中缺少 EncryptionInfo 或 EncryptedPackage 流。")

    config, info = parse_agile_encryption_info(encryption_info)
    package_key = decrypt_package_key(password, config, info)
    verify_encrypted_package_integrity(encrypted_package, package_key, config, info)
    return decrypt_package_stream(encrypted_package, package_key, info["key_data_salt"], config)

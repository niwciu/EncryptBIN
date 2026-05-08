"""End-to-end integration tests: CLI args -> parsing -> Config -> binary generation -> decryption verification."""

import struct
import zlib

from Crypto.Cipher import AES

from encrypt_bin.cli.parser import get_parsed_args
from encrypt_bin.core.builder import generate_bin
from encrypt_bin.core.config import Config

KEY_HEX = "00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF"
KEY_BYTES = bytes([0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF])

DEVICE_ID = 0x00A0000BC22510E1
BOOTLOADER_ID = 0x00001001
APP_VERSION = 0x20260301
PREV_APP_VERSION = 0x20260201
PAGE_SIZE = 1024


def _create_input_firmware(tmp_path, size=3000):
    """Create a test firmware file with known content."""
    data = bytes(range(256)) * (size // 256) + bytes(range(size % 256))
    firmware = tmp_path / "firmware.bin"
    firmware.write_bytes(data)
    return firmware, data


def _parse_output_header(data):
    """Parse the binary output header and return fields + payload."""
    offset = 0
    bootloader_id = struct.unpack_from("<I", data, offset)[0]
    offset += 4
    product_id_msb = struct.unpack_from("<I", data, offset)[0]
    offset += 4
    product_id_lsb = struct.unpack_from("<I", data, offset)[0]
    offset += 4
    app_version = struct.unpack_from("<I", data, offset)[0]
    offset += 4
    prev_app_version = struct.unpack_from("<I", data, offset)[0]
    offset += 4
    num_pages = struct.unpack_from("<I", data, offset)[0]
    offset += 4
    page_size = struct.unpack_from("<I", data, offset)[0]
    offset += 4
    iv = data[offset : offset + 16]
    offset += 16
    crc32_val = struct.unpack_from("<I", data, offset)[0]
    offset += 4

    product_id = (product_id_msb << 32) | product_id_lsb

    return {
        "bootloader_id": bootloader_id,
        "product_id": product_id,
        "app_version": app_version,
        "prev_app_version": prev_app_version,
        "num_pages": num_pages,
        "page_size": page_size,
        "iv": iv,
        "crc32": crc32_val,
        "encrypted_payload": data[offset:],
    }


def test_e2e_cli_to_binary(tmp_path):
    """Full pipeline: CLI args -> parse -> Config -> generate -> verify header + decrypt."""
    firmware_path, original_data = _create_input_firmware(tmp_path, size=3000)
    output_path = tmp_path / "encrypted.bin"

    # Step 1: Parse CLI arguments
    argv = [
        "-i",
        str(firmware_path),
        "-o",
        str(output_path),
        "-d",
        hex(DEVICE_ID),
        "-b",
        hex(BOOTLOADER_ID),
        "-k",
        KEY_HEX,
        "-v",
        hex(APP_VERSION),
        "-p",
        hex(PREV_APP_VERSION),
        "-l",
        str(PAGE_SIZE),
    ]
    args = get_parsed_args(argv)

    # Step 2: Create Config
    config = Config.from_args(args)
    assert config.device_id == DEVICE_ID
    assert config.bootloader_id == BOOTLOADER_ID
    assert config.key == KEY_BYTES
    assert config.app_version == APP_VERSION
    assert config.prev_app_version == PREV_APP_VERSION
    assert config.page_size == PAGE_SIZE

    # Step 3: Generate encrypted binary
    generate_bin(
        input_path=config.input_path,
        output_path=config.output_path,
        product_id=config.device_id,
        app_version=config.app_version,
        prev_app_version=config.prev_app_version,
        bootloader_id=config.bootloader_id,
        key=config.key,
        page_size=config.page_size,
    )

    assert output_path.exists()
    out_data = output_path.read_bytes()

    # Step 4: Verify header
    header = _parse_output_header(out_data)
    assert header["bootloader_id"] == BOOTLOADER_ID
    assert header["product_id"] == DEVICE_ID
    assert header["app_version"] == APP_VERSION
    assert header["prev_app_version"] == PREV_APP_VERSION
    assert header["page_size"] == PAGE_SIZE

    # Verify num_pages calculation
    padded_len = ((len(original_data) + PAGE_SIZE - 1) // PAGE_SIZE) * PAGE_SIZE
    expected_pages = padded_len // PAGE_SIZE
    assert header["num_pages"] == expected_pages

    # Verify IV is 16 bytes
    assert len(header["iv"]) == 16

    # Verify encrypted payload length matches padded input
    assert len(header["encrypted_payload"]) == padded_len

    # Step 5: Decrypt and verify content
    cipher = AES.new(KEY_BYTES, AES.MODE_CBC, header["iv"])
    decrypted = cipher.decrypt(header["encrypted_payload"])

    # Original data should be at the start, rest is zero-padding
    assert decrypted[: len(original_data)] == original_data
    assert decrypted[len(original_data) :] == b"\x00" * (padded_len - len(original_data))

    # Step 6: Verify CRC32
    expected_crc = zlib.crc32(decrypted) & 0xFFFFFFFF
    assert header["crc32"] == expected_crc


def test_e2e_with_key_file(tmp_path):
    """Full pipeline using key file instead of direct key."""
    firmware_path, original_data = _create_input_firmware(tmp_path, size=512)
    output_path = tmp_path / "encrypted.bin"

    # Create key file
    key_file = tmp_path / "keys.txt"
    key_file.write_text(f"{hex(DEVICE_ID)};{KEY_HEX}\n")
    key_file.chmod(0o600)

    # Parse with -K flag
    argv = [
        "-i",
        str(firmware_path),
        "-o",
        str(output_path),
        "-d",
        hex(DEVICE_ID),
        "-b",
        hex(BOOTLOADER_ID),
        "-K",
        str(key_file),
        "-v",
        hex(APP_VERSION),
        "-p",
        hex(PREV_APP_VERSION),
        "-l",
        str(PAGE_SIZE),
    ]
    args = get_parsed_args(argv)
    config = Config.from_args(args)

    assert config.key == KEY_BYTES

    generate_bin(
        input_path=config.input_path,
        output_path=config.output_path,
        product_id=config.device_id,
        app_version=config.app_version,
        prev_app_version=config.prev_app_version,
        bootloader_id=config.bootloader_id,
        key=config.key,
        page_size=config.page_size,
    )

    assert output_path.exists()
    out_data = output_path.read_bytes()
    header = _parse_output_header(out_data)

    # Decrypt and verify
    cipher = AES.new(KEY_BYTES, AES.MODE_CBC, header["iv"])
    decrypted = cipher.decrypt(header["encrypted_payload"])
    assert decrypted[: len(original_data)] == original_data


def test_e2e_with_config_file(tmp_path):
    """Full pipeline using config file (-c flag)."""
    firmware_path, original_data = _create_input_firmware(tmp_path, size=256)
    output_path = tmp_path / "encrypted.bin"

    # Create config file
    config_file = tmp_path / "params.txt"
    config_file.write_text(
        f'-i "{firmware_path}"\n'
        f'-o "{output_path}"\n'
        f"-d {hex(DEVICE_ID)}\n"
        f"-b {hex(BOOTLOADER_ID)}\n"
        f'-k "{KEY_HEX}"\n'
        f"-v {hex(APP_VERSION)}\n"
        f"-p {hex(PREV_APP_VERSION)}\n"
        f"-l {PAGE_SIZE}\n"
    )

    argv = ["-c", str(config_file)]
    args = get_parsed_args(argv)
    config = Config.from_args(args)

    generate_bin(
        input_path=config.input_path,
        output_path=config.output_path,
        product_id=config.device_id,
        app_version=config.app_version,
        prev_app_version=config.prev_app_version,
        bootloader_id=config.bootloader_id,
        key=config.key,
        page_size=config.page_size,
    )

    assert output_path.exists()
    out_data = output_path.read_bytes()
    header = _parse_output_header(out_data)

    # Decrypt and verify
    cipher = AES.new(KEY_BYTES, AES.MODE_CBC, header["iv"])
    decrypted = cipher.decrypt(header["encrypted_payload"])
    assert decrypted[: len(original_data)] == original_data

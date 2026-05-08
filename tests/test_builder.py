import pytest
from encrypt_bin.core.builder import generate_bin


def test_generate_bin(tmp_path):
    input_file = tmp_path / "firmware.bin"
    output_file = tmp_path / "out.bin"
    input_file.write_bytes(bytes(range(50)))

    product_id = 0x12345678ABCDEF00
    app_version = 0x1201
    prev_app_version = 0x1100
    bootloader_id = 0x10
    page_size = 16
    key = bytes(range(16))

    generate_bin(
        input_path=str(input_file),
        output_path=str(output_file),
        product_id=product_id,
        app_version=app_version,
        prev_app_version=prev_app_version,
        bootloader_id=bootloader_id,
        key=key,
        page_size=page_size,
    )

    assert output_file.exists()
    out_data = output_file.read_bytes()

    # Header is 48 bytes: bootloader_id(4) + product_id_msb(4) + product_id_lsb(4)
    # + app_version(4) + prev_app_version(4) + num_pages(4) + page_size(4) + iv(16) + crc32(4)
    header_len = 48
    assert len(out_data) > header_len

    assert int.from_bytes(out_data[0:4], "little") == bootloader_id
    assert int.from_bytes(out_data[4:8], "little") == (product_id >> 32) & 0xFFFFFFFF
    assert int.from_bytes(out_data[8:12], "little") == product_id & 0xFFFFFFFF
    assert int.from_bytes(out_data[12:16], "little") == app_version
    assert int.from_bytes(out_data[16:20], "little") == prev_app_version

    padded_len = ((50 + page_size - 1) // page_size) * page_size
    expected_pages = padded_len // page_size
    assert int.from_bytes(out_data[20:24], "little") == expected_pages
    assert int.from_bytes(out_data[24:28], "little") == page_size

    iv = out_data[28:44]
    assert len(iv) == 16

    assert len(out_data[header_len:]) == padded_len


def test_generate_bin_returns_output_path(tmp_path):
    input_file = tmp_path / "firmware.bin"
    output_file = tmp_path / "out.bin"
    input_file.write_bytes(bytes(range(16)))

    result = generate_bin(
        input_path=str(input_file),
        output_path=str(output_file),
        product_id=0x1234,
        app_version=0x1,
        prev_app_version=0x0,
        bootloader_id=0x1,
        key=bytes(range(16)),
        page_size=16,
    )

    assert result == str(output_file)


def test_generate_bin_input_file_missing(tmp_path):
    input_file = tmp_path / "missing.bin"
    output_file = tmp_path / "out.bin"
    key = bytes(range(16))

    with pytest.raises(FileNotFoundError) as e:
        generate_bin(
            input_path=str(input_file),
            output_path=str(output_file),
            product_id=0x12345678ABCDEF00,
            app_version=0x1201,
            prev_app_version=0x1100,
            bootloader_id=0x10,
            key=key,
            page_size=16,
        )
    assert "does not exist" in str(e.value)

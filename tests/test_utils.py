import pytest
from unittest.mock import patch
import stat
from encrypt_bin.cli import utils, validators
from encrypt_bin.cli.utils import find_key_in_file


# -----------------------
# parse_int
# -----------------------
@pytest.mark.parametrize(
    "value, expected",
    [
        ("42", 42),
        ("0x10", 16),
    ],
)
def test_parse_int_valid(value, expected):
    assert utils.parse_int(value, name="test_param", max_bits=32) == expected


@pytest.mark.parametrize(
    "value",
    [
        "0x1FFFFFFFF",  # exceeds bit limit
        "notanumber",  # invalid format
    ],
)
def test_parse_int_invalid(value):
    with pytest.raises(ValueError) as e:
        utils.parse_int(value, name="test_param", max_bits=32)
    assert "must be a decimal or hexadecimal number" in str(e.value) or "exceeds uint32" in str(e.value)


# -----------------------
# parse_key
# -----------------------
@pytest.mark.parametrize(
    "key_str",
    [
        "00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF",
        "00112233445566778899AABBCCDDEEFF",
        "0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xAA,0xBB,0xCC,0xDD,0xEE,0xFF",
    ],
)
def test_parse_key_valid(key_str):
    key = utils.parse_key(key_str)
    assert isinstance(key, bytes)
    assert len(key) == 16


@pytest.mark.parametrize(
    "key_str, msg",
    [
        ("00112233", "exactly 16 bytes"),  # too short
        (
            "00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 00",
            "exactly 16 bytes",
        ),  # too long
        (
            "00 11 22 33 44 55 66 77 88 99 GG BB CC DD EE FF",
            "not a valid hex byte",
        ),  # invalid byte
        ("00112233445566778899AABBCCDDEZZ", "invalid hex characters"),  # invalid chars
    ],
)
def test_parse_key_invalid(key_str, msg):
    with pytest.raises(ValueError) as e:
        utils.parse_key(key_str)
    assert msg in str(e.value)


# -----------------------
# validate_file_paths
# -----------------------
def test_validate_file_paths(tmp_path):
    input_file = tmp_path / "in.bin"
    input_file.write_bytes(b"\x00")
    output_file = tmp_path / "out.bin"

    # valid paths
    validators.validate_file_paths(str(input_file), str(output_file))

    # missing input file -> FileNotFoundError
    with pytest.raises(FileNotFoundError) as e:
        validators.validate_file_paths(str(tmp_path / "missing.bin"), str(output_file))
    assert "Input file" in str(e.value)

    # non-existent output directory -> FileNotFoundError
    invalid_output = tmp_path / "nonexistent_dir" / "out.bin"
    with pytest.raises(FileNotFoundError) as e:
        validators.validate_file_paths(str(input_file), str(invalid_output))
    assert "Output directory" in str(e.value)


# -----------------------
# find_key_in_file
# -----------------------
def test_find_key_in_file_various_formats(tmp_path):
    content = (
        "\n"
        "# comment line\n"
        "BADLINE\n"
        "0xZZZZ;00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF\n"
        "0x1234;00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF\n"
        "0x5678 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 00\n"
    )
    key_file = tmp_path / "keys.txt"
    key_file.write_text(content)
    key_file.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

    # valid key using semicolon format — triggers permission warning
    with pytest.warns(UserWarning, match="group/other permissions"):
        key = find_key_in_file(str(key_file), 0x1234)
    assert len(key) == 16

    # lock down permissions so subsequent calls don't re-trigger the warning
    key_file.chmod(0o600)

    # valid key using space-separated format
    key2 = find_key_in_file(str(key_file), 0x5678)
    assert len(key2) == 16

    # device_id not found -> ValueError
    with pytest.raises(ValueError) as e:
        find_key_in_file(str(key_file), 0x9999)
    assert "Could not find key" in str(e.value)

    # missing file -> FileNotFoundError
    with pytest.raises(FileNotFoundError) as e:
        find_key_in_file(str(tmp_path / "missing.txt"), 0x1234)
    assert "Error reading key file" in str(e.value)


def test_find_key_in_file_open_exception(tmp_path):
    key_file = tmp_path / "keys.txt"
    key_file.write_text("0x1234;00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF")
    key_file.chmod(0o600)

    with patch("builtins.open", side_effect=OSError("mocked error")):
        with pytest.raises(OSError) as e:
            find_key_in_file(str(key_file), 0x1234)
        assert "Error reading key file: mocked error" in str(e.value)

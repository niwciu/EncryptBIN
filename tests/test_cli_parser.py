import pytest
import sys
from unittest.mock import patch
from encrypt_bin.cli import parser

# -----------------------
# load_config_file
# -----------------------


def test_load_config_file_success(tmp_path):
    """Correctly loads a config file"""
    path = tmp_path / "params.txt"
    path.write_text("-i input.bin -o output.bin")
    args = parser.load_config_file(str(path))
    assert args == ["-i", "input.bin", "-o", "output.bin"]


def test_load_config_file_missing(tmp_path):
    """Missing file -> OSError"""
    bad_file = tmp_path / "does_not_exist.txt"
    with pytest.raises(OSError) as e:
        parser.load_config_file(str(bad_file))
    assert "Error reading config file" in str(e.value)


def test_load_config_file_open_exception(monkeypatch):
    """Error opening file (e.g., permissions)"""
    with patch("builtins.open", side_effect=OSError("mocked error")):
        with pytest.raises(OSError) as e:
            parser.load_config_file("dummy.txt")
        assert "Error reading config file" in str(e.value)


def test_load_config_file_shlex_exception(tmp_path, monkeypatch):
    """shlex.split parsing error"""
    path = tmp_path / "params.txt"
    path.write_text("-i input.bin -o output.bin")
    monkeypatch.setattr("shlex.split", lambda *_a, **_k: (_ for _ in ()).throw(ValueError("mocked")))
    with pytest.raises(OSError) as e:
        parser.load_config_file(str(path))
    assert "Error reading config file" in str(e.value)


# -----------------------
# merge_args
# -----------------------


def test_merge_args_basic():
    """Correctly merges arguments without conflicts"""
    file_args = ["-i", "file1.bin"]
    cli_args = ["-o", "file2.bin"]
    merged = parser.merge_args(file_args, cli_args)
    assert merged == ["-i", "file1.bin", "-o", "file2.bin"]


def test_merge_args_conflict():
    """Same flag with different values -> ValueError"""
    file_args = ["-i", "file1.bin"]
    cli_args = ["-i", "file2.bin"]
    with pytest.raises(ValueError) as e:
        parser.merge_args(file_args, cli_args)
    assert "appears in both file and CLI" in str(e.value)


def test_merge_args_bad_syntax():
    """Missing flag before value -> ValueError"""
    file_args = ["value_without_flag"]
    cli_args = []
    with pytest.raises(ValueError) as e:
        parser.merge_args(file_args, cli_args)
    assert "Invalid parameter syntax" in str(e.value)


# -----------------------
# get_parsed_args
# -----------------------


def make_bin_file(tmp_path, name="in.bin"):
    f = tmp_path / name
    f.write_bytes(b"\x00" * 16)
    return f


def test_get_parsed_args_with_key(monkeypatch, tmp_path):
    """Provide direct 16-byte key via -k"""
    inp = make_bin_file(tmp_path, "input.bin")
    out = tmp_path / "output.bin"
    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "0x1234",
        "-b",
        "0x10",
        "-k",
        "00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF",
        "-v",
        "0x1201",
        "-p",
        "0x1100",
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    args = parser.get_parsed_args()

    assert args.device_id == 0x1234
    assert isinstance(args.key, bytes)
    assert len(args.key) == 16


def test_get_parsed_args_with_key_file(monkeypatch, tmp_path):
    """Provide key via -K and search in key file"""
    inp = make_bin_file(tmp_path, "input.bin")
    out = tmp_path / "output.bin"
    key_file = tmp_path / "keys.txt"
    key_file.write_text("0x1234;00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF")
    key_file.chmod(0o600)

    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "0x1234",
        "-b",
        "0x10",
        "-K",
        str(key_file),
        "-v",
        "0x1201",
        "-p",
        "0x1100",
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    args = parser.get_parsed_args()
    assert isinstance(args.key, bytes)
    assert len(args.key) == 16


def test_get_parsed_args_with_config_file(monkeypatch, tmp_path):
    """Covers the if pre_args.config path"""
    inp = make_bin_file(tmp_path)
    out = tmp_path / "output.bin"
    config_file = tmp_path / "params.txt"
    config_file.write_text(f"-i {inp} -o {out} -d 0x1234 -b 0x10 -k 00112233445566778899AABBCCDDEEFF -v 0x1201 -p 0x1100")
    monkeypatch.setattr(sys, "argv", ["prog", "-c", str(config_file)])

    args = parser.get_parsed_args()
    assert args.device_id == 0x1234
    assert isinstance(args.key, bytes)
    assert len(args.key) == 16


def test_get_parsed_args_accepts_arg_list(tmp_path):
    """Call parser with explicit argument list instead of relying on sys.argv."""
    inp = make_bin_file(tmp_path)
    out = tmp_path / "output.bin"
    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "0x9876",
        "-b",
        "0x20",
        "-k",
        "00112233445566778899AABBCCDDEEFF",
        "-v",
        "0x1234",
        "-p",
        "0x1111",
    ]
    args = parser.get_parsed_args(argv)
    assert args.device_id == 0x9876
    assert args.bootloader_id == 0x20
    assert args.page_size == 2048  # default
    assert isinstance(args.key, bytes)
    assert len(args.key) == 16


def test_get_parsed_args_invalid_input(monkeypatch, tmp_path):
    """Non-existent input file"""
    inp = tmp_path / "missing.bin"
    out = tmp_path / "output.bin"
    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "0x1",
        "-b",
        "0x2",
        "-k",
        "00" * 16,
        "-v",
        "1",
        "-p",
        "1",
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    with pytest.raises(FileNotFoundError) as e:
        parser.get_parsed_args()
    assert "Input file" in str(e.value)


def test_get_parsed_args_invalid_output(monkeypatch, tmp_path):
    """Non-existent output directory"""
    inp = make_bin_file(tmp_path)
    out = tmp_path / "no_dir" / "out.bin"
    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "1",
        "-b",
        "2",
        "-k",
        "00" * 16,
        "-v",
        "1",
        "-p",
        "1",
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    with pytest.raises(FileNotFoundError) as e:
        parser.get_parsed_args()
    assert "Output directory" in str(e.value)


def test_get_parsed_args_invalid_number(monkeypatch, tmp_path):
    """Invalid Device ID"""
    inp = make_bin_file(tmp_path)
    out = tmp_path / "output.bin"
    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "BAD",
        "-b",
        "0x10",
        "-k",
        "00" * 16,
        "-v",
        "0x1201",
        "-p",
        "0x1100",
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    with pytest.raises(ValueError) as e:
        parser.get_parsed_args()
    assert "Device ID" in str(e.value)


def test_get_parsed_args_invalid_key(monkeypatch, tmp_path):
    """Invalid key (too short)"""
    inp = make_bin_file(tmp_path)
    out = tmp_path / "output.bin"
    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "0x1234",
        "-b",
        "0x10",
        "-k",
        "00",
        "-v",
        "0x1201",
        "-p",
        "0x1100",
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    with pytest.raises(ValueError):
        parser.get_parsed_args()


def test_get_parsed_args_missing_key(monkeypatch, tmp_path):
    """Missing both -k and -K -> argparse SystemExit"""
    inp = make_bin_file(tmp_path)
    out = tmp_path / "output.bin"
    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "0x1234",
        "-b",
        "0x10",
        "-v",
        "0x1201",
        "-p",
        "0x1100",
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    with pytest.raises(SystemExit):
        parser.get_parsed_args()


def test_get_parsed_args_key_file_missing_id(monkeypatch, tmp_path):
    """Key file exists but does not contain the provided device-id"""
    inp = make_bin_file(tmp_path)
    out = tmp_path / "output.bin"
    key_file = tmp_path / "keys.txt"
    key_file.write_text("0x9999;00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF")  # different device-id
    key_file.chmod(0o600)

    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "0x1234",  # ID not in key_file
        "-b",
        "0x10",
        "-K",
        str(key_file),
        "-v",
        "0x1201",
        "-p",
        "0x1100",
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)

    with pytest.raises(ValueError) as e:
        parser.get_parsed_args()

    assert "Could not find key for device_id" in str(e.value)


def test_get_parsed_args_page_size_zero(tmp_path):
    """page_size=0 must be rejected."""
    inp = make_bin_file(tmp_path)
    out = tmp_path / "output.bin"
    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "0x1",
        "-b",
        "0x1",
        "-k",
        "00" * 16,
        "-v",
        "0x1",
        "-p",
        "0x0",
        "-l",
        "0",
    ]
    with pytest.raises(ValueError, match="positive integer"):
        parser.get_parsed_args(argv)


def test_get_parsed_args_page_size_not_multiple_of_16(tmp_path):
    """page_size not divisible by 16 must be rejected."""
    inp = make_bin_file(tmp_path)
    out = tmp_path / "output.bin"
    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "0x1",
        "-b",
        "0x1",
        "-k",
        "00" * 16,
        "-v",
        "0x1",
        "-p",
        "0x0",
        "-l",
        "100",
    ]
    with pytest.raises(ValueError, match="multiple of 16"):
        parser.get_parsed_args(argv)

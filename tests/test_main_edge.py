import sys
import pytest
from encrypt_bin.__main__ import main


def test_main_handles_missing_input_file(tmp_path, monkeypatch):
    """Main exits when input file does not exist"""
    output_file = tmp_path / "out.bin"
    missing_input = tmp_path / "missing.bin"

    argv = [
        "-i",
        str(missing_input),
        "-o",
        str(output_file),
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

    # Expect main to call sys.exit
    with pytest.raises(SystemExit) as e:
        main()

    # Check error message
    assert "Input file" in str(e.value)

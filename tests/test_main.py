# tests/test_main.py
import sys
import pytest
from unittest.mock import patch
from encrypt_bin.__main__ import main


@pytest.mark.parametrize(
    "argv",
    [
        [
            "-i",
            "tests/test_firmware.bin",
            "-o",
            "tests/out.bin",
            "-d",
            "0x12345678",
            "-b",
            "0x10",
            "-k",
            "00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF",
            "-v",
            "0x1201",
            "-p",
            "0x1100",
        ]
    ],
)
def test_main_runs(tmp_path, argv, monkeypatch):
    # Create the input file
    input_file = tmp_path / "test_firmware.bin"
    input_file.write_bytes(bytes(range(50)))
    output_file = tmp_path / "out.bin"

    # Replace paths in argv
    argv[1] = str(input_file)
    argv[3] = str(output_file)
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)

    # Patch print to avoid cluttering the terminal
    with patch("builtins.print"):
        main()

    # Output file should exist
    assert output_file.exists()


def test_main_handles_generate_bin_exception(tmp_path, monkeypatch):
    # Create input file
    input_file = tmp_path / "test_firmware.bin"
    input_file.write_bytes(bytes(range(50)))
    output_file = tmp_path / "out.bin"

    argv = [
        "-i",
        str(input_file),
        "-o",
        str(output_file),
        "-d",
        "0x12345678",
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

    # Patch generate_bin in the __main__ module where main() uses it
    with (
        patch("encrypt_bin.__main__.generate_bin", side_effect=OSError("mocked error")),
        patch("builtins.print"),
    ):
        with pytest.raises(SystemExit) as e:
            main()

    assert "Error while generating the output file: mocked error" in str(e.value)

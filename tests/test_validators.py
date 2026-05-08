import pytest
from encrypt_bin.cli import validators


def test_validate_file_paths(tmp_path):
    input_file = tmp_path / "in.bin"
    input_file.write_bytes(b"\x00")
    output_file = tmp_path / "out.bin"

    # valid case
    validators.validate_file_paths(str(input_file), str(output_file))

    # missing input file -> FileNotFoundError
    with pytest.raises(FileNotFoundError) as e:
        validators.validate_file_paths(str(tmp_path / "missing.bin"), str(output_file))
    assert "Input file" in str(e.value)

    # input file without .bin extension -> ValueError
    input_txt = tmp_path / "in.txt"
    input_txt.write_bytes(b"\x00")
    with pytest.raises(ValueError) as e:
        validators.validate_file_paths(str(input_txt), str(output_file))
    assert "must have the '.bin' extension" in str(e.value)

    # non-existent output directory -> FileNotFoundError
    invalid_output = tmp_path / "nonexistent_dir" / "out.bin"
    with pytest.raises(FileNotFoundError) as e:
        validators.validate_file_paths(str(input_file), str(invalid_output))
    assert "Output directory" in str(e.value)

    # output file without .bin extension -> ValueError
    output_txt = tmp_path / "out.txt"
    with pytest.raises(ValueError) as e:
        validators.validate_file_paths(str(input_file), str(output_txt))
    assert "must have the '.bin' extension" in str(e.value)

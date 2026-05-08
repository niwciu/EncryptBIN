"""GUI tests for the encrypt-bin application."""

import pytest
from pathlib import Path
from unittest.mock import patch

from encrypt_bin.gui.main import EncryptBinGUI

KEY_HEX = "00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF"


@pytest.fixture
def gui(qtbot):
    window = EncryptBinGUI()
    qtbot.addWidget(window)
    return window


def _fill_fields(gui, tmp_path, size=50):
    """Populate all required fields with valid values; return (input_path, output_path)."""
    f = tmp_path / "fw.bin"
    f.write_bytes(bytes(range(size)))
    out = tmp_path / "out.bin"
    gui.input_edit.setText(str(f))
    gui.input_edit.setToolTip(str(f))
    gui.output_edit.setText(str(out))
    gui.output_edit.setToolTip(str(out))
    gui.device_edit.setText("0x00A0000BC22510E1")
    gui.bootloader_edit.setText("0x00000001")
    gui.hex_key_edit.setText(KEY_HEX)
    gui.version_edit.setText("0x20260301")
    gui.prev_version_edit.setText("0x20260201")
    return f, out


# ─────────────────────────── _get_page_size ───────────────────────────────


def test_get_page_size_default(gui):
    assert gui._get_page_size() == 2048


@pytest.mark.parametrize(
    "text, expected",
    [("128 bytes", 128), ("256 bytes", 256), ("512 bytes", 512), ("1024 bytes", 1024), ("2048 bytes", 2048), ("4096 bytes", 4096)],
)
def test_get_page_size_all_options(gui, text, expected):
    gui.page_combo.setCurrentText(text)
    assert gui._get_page_size() == expected


# ─────────────────────────── _generate_random_key ───────────────────────────


def test_generate_random_key_produces_16_hex_bytes(gui):
    gui._generate_random_key()
    parts = gui.hex_key_edit.text().split()
    assert len(parts) == 16
    assert all(len(p) == 2 and int(p, 16) >= 0 for p in parts)


def test_generate_random_key_clears_key_file(gui):
    gui.key_file_edit.setText("/some/key.txt")
    gui._generate_random_key()
    assert gui.key_file_edit.text() == ""


# ─────────────────────────── _validate_and_get_params ───────────────────────


@pytest.mark.parametrize(
    "field_attr, expected_msg",
    [
        ("device_edit", "Device ID"),
        ("bootloader_edit", "Bootloader ID"),
        ("version_edit", "App Version"),
        ("prev_version_edit", "Previous App Version"),
    ],
)
def test_validate_required_text_field_missing(gui, tmp_path, field_attr, expected_msg):
    _fill_fields(gui, tmp_path)
    getattr(gui, field_attr).clear()
    with pytest.raises(ValueError, match=expected_msg):
        gui._validate_and_get_params()


def test_validate_input_file_missing(gui, tmp_path):
    _fill_fields(gui, tmp_path)
    gui.input_edit.clear()
    gui.input_edit.setToolTip("")
    with pytest.raises(ValueError, match="Input file"):
        gui._validate_and_get_params()


def test_validate_output_file_missing(gui, tmp_path):
    _fill_fields(gui, tmp_path)
    gui.output_edit.clear()
    gui.output_edit.setToolTip("")
    with pytest.raises(ValueError, match="Output file"):
        gui._validate_and_get_params()


def test_validate_no_key_raises(gui, tmp_path):
    _fill_fields(gui, tmp_path)
    gui.hex_key_edit.clear()
    with pytest.raises(ValueError, match="required"):
        gui._validate_and_get_params()


def test_validate_both_key_and_keyfile_raises(gui, tmp_path):
    _fill_fields(gui, tmp_path)
    gui.hex_key_edit.blockSignals(True)
    gui.key_file_edit.blockSignals(True)
    gui.hex_key_edit.setText(KEY_HEX)
    gui.key_file_edit.setText("/some/key.txt")
    gui.hex_key_edit.blockSignals(False)
    gui.key_file_edit.blockSignals(False)
    with pytest.raises(ValueError, match="not both"):
        gui._validate_and_get_params()


def test_validate_returns_correct_page_size(gui, tmp_path):
    _fill_fields(gui, tmp_path)
    gui.page_combo.setCurrentText("1024 bytes")
    params = gui._validate_and_get_params()
    assert params["page_size"] == 1024


def test_validate_key_flag_hex(gui, tmp_path):
    _fill_fields(gui, tmp_path)
    params = gui._validate_and_get_params()
    assert params["key_flag"] == "-k"
    assert params["key_value"] == KEY_HEX


def test_validate_key_flag_keyfile(gui, tmp_path):
    _fill_fields(gui, tmp_path)
    gui.hex_key_edit.clear()
    gui.key_file_edit.setText("/some/key.txt")
    params = gui._validate_and_get_params()
    assert params["key_flag"] == "-K"
    assert params["key_value"] == "/some/key.txt"


# ─────────────────────────── generate_binary ────────────────────────────────


def test_generate_binary_success(gui, tmp_path):
    _, out = _fill_fields(gui, tmp_path)
    with patch("encrypt_bin.gui.main.QMessageBox.information"):
        gui.generate_binary()
    assert out.exists()
    assert out.stat().st_size > 48


def test_generate_binary_logs_success(gui, tmp_path):
    _fill_fields(gui, tmp_path)
    with patch("encrypt_bin.gui.main.QMessageBox.information"):
        gui.generate_binary()
    assert "generated successfully" in gui.log_text.toPlainText()


def test_generate_binary_validation_error_logged(gui):
    with patch("encrypt_bin.gui.main.QMessageBox.critical"):
        gui.generate_binary()
    assert "Error" in gui.log_text.toPlainText()


def test_generate_binary_missing_input_file_logged(gui, tmp_path):
    _fill_fields(gui, tmp_path)
    gui.input_edit.setText("nonexistent.bin")
    gui.input_edit.setToolTip("nonexistent.bin")
    with patch("encrypt_bin.gui.main.QMessageBox.critical"):
        gui.generate_binary()
    assert "Error" in gui.log_text.toPlainText()


# ─────────────────────────── save / load configuration ──────────────────────


def test_save_load_configuration_roundtrip(gui, qtbot, tmp_path):
    _fill_fields(gui, tmp_path)
    gui.page_combo.setCurrentText("1024 bytes")
    config_path = str(tmp_path / "config.txt")

    with patch("encrypt_bin.gui.main.QFileDialog.getSaveFileName", return_value=(config_path, "")):
        with patch("encrypt_bin.gui.main.QMessageBox.information"):
            gui.save_configuration()

    assert Path(config_path).exists()

    gui2 = EncryptBinGUI()
    qtbot.addWidget(gui2)
    with patch("encrypt_bin.gui.main.QFileDialog.getOpenFileName", return_value=(config_path, "")):
        gui2.load_configuration()

    assert gui2.device_edit.text() == hex(0x00A0000BC22510E1)
    assert gui2.version_edit.text() == hex(0x20260301)
    assert gui2.prev_version_edit.text() == hex(0x20260201)
    assert gui2.bootloader_edit.text() == hex(0x00000001)
    assert gui2.page_combo.currentText() == "1024 bytes"
    assert "Configuration loaded" in gui2.log_text.toPlainText()


def test_save_configuration_cancelled_does_nothing(gui, tmp_path):
    _fill_fields(gui, tmp_path)
    with patch("encrypt_bin.gui.main.QFileDialog.getSaveFileName", return_value=("", "")):
        gui.save_configuration()


def test_load_configuration_cancelled_does_nothing(gui):
    with patch("encrypt_bin.gui.main.QFileDialog.getOpenFileName", return_value=("", "")):
        gui.load_configuration()
    assert gui.log_text.toPlainText() == ""


def test_save_configuration_validation_error_logged(gui):
    with patch("encrypt_bin.gui.main.QMessageBox.critical"):
        gui.save_configuration()
    assert "Error" in gui.log_text.toPlainText()


def test_save_configuration_adds_txt_extension(gui, tmp_path):
    """A save path without extension gets .txt appended."""
    _fill_fields(gui, tmp_path)
    no_ext_path = str(tmp_path / "myconfig")
    with patch("encrypt_bin.gui.main.QFileDialog.getSaveFileName", return_value=(no_ext_path, "")):
        with patch("encrypt_bin.gui.main.QMessageBox.information"):
            gui.save_configuration()
    assert (tmp_path / "myconfig.txt").exists()


def test_load_configuration_error_logged(gui, tmp_path):
    """A malformed config file is caught and logged."""
    bad_cfg = tmp_path / "bad.txt"
    bad_cfg.write_text("this is not valid cli args --badarg xyz\n")
    with patch("encrypt_bin.gui.main.QFileDialog.getOpenFileName", return_value=(str(bad_cfg), "")):
        with patch("encrypt_bin.gui.main.QMessageBox.critical"):
            gui.load_configuration()
    assert "Error" in gui.log_text.toPlainText()


def test_load_configuration_with_key_file(gui, qtbot, tmp_path):
    """load_configuration populates key_file_edit when config uses -K."""
    f = tmp_path / "fw.bin"
    f.write_bytes(bytes(range(16)))
    out = tmp_path / "out.bin"
    key_file = tmp_path / "keys.txt"
    key_file.write_text(f"0x00A0000BC22510E1;{KEY_HEX}\n")
    key_file.chmod(0o600)
    config_path = tmp_path / "config.txt"
    config_path.write_text(f'-i "{f}"\n-o "{out}"\n-d 0x00A0000BC22510E1\n-b 0x00000001\n' f'-K "{key_file}"\n-v 0x20260301\n-p 0x20260201\n-l 2048\n')
    with patch("encrypt_bin.gui.main.QFileDialog.getOpenFileName", return_value=(str(config_path), "")):
        gui.load_configuration()
    assert gui.key_file_edit.text() == str(key_file)
    assert gui.hex_key_edit.text() == ""


def test_select_input_file_sets_fields(gui, tmp_path):
    f = tmp_path / "fw.bin"
    f.write_bytes(b"\x00")
    with patch("encrypt_bin.gui.main.QFileDialog.getOpenFileName", return_value=(str(f), "")):
        gui.select_input_file()
    assert gui.input_edit.text() == "fw.bin"
    assert gui.input_edit.toolTip() == str(f)


def test_select_output_file_sets_fields(gui, tmp_path):
    out = tmp_path / "out.bin"
    with patch("encrypt_bin.gui.main.QFileDialog.getSaveFileName", return_value=(str(out), "")):
        gui.select_output_file()
    assert gui.output_edit.text() == "out.bin"
    assert gui.output_edit.toolTip() == str(out)


def test_select_key_file_sets_field(gui, tmp_path):
    kf = tmp_path / "keys.txt"
    kf.write_text("dummy")
    with patch("encrypt_bin.gui.main.QFileDialog.getOpenFileName", return_value=(str(kf), "")):
        gui.select_key_file()
    assert gui.key_file_edit.text() == str(kf)

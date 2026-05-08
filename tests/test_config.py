# tests/test_config.py
from encrypt_bin.core.config import Config
from types import SimpleNamespace


def _make_args(tmp_path):
    return SimpleNamespace(
        input=str(tmp_path / "in.bin"),
        output=str(tmp_path / "out.bin"),
        device_id=0x1234,
        bootloader_id=0x10,
        key=b"\x00" * 16,
        app_version=0x1201,
        prev_app_version=0x1100,
        page_size=2048,
    )


def test_config_from_args(tmp_path):
    args = _make_args(tmp_path)
    cfg = Config.from_args(args)
    assert cfg.input_path == args.input
    assert cfg.output_path == args.output
    assert cfg.device_id == args.device_id
    assert cfg.bootloader_id == args.bootloader_id
    assert cfg.key == args.key
    assert cfg.app_version == args.app_version
    assert cfg.prev_app_version == args.prev_app_version
    assert cfg.page_size == args.page_size


def test_config_str(tmp_path):
    cfg = Config.from_args(_make_args(tmp_path))
    summary = str(cfg)

    assert "Input" in summary
    assert "Device" in summary
    assert "0x1234" in summary
    assert "Classified" in summary
    # raw key bytes must not appear
    assert "000000000000000000000000000000" not in summary


def test_config_print_summary(tmp_path, capsys):
    cfg = Config.from_args(_make_args(tmp_path))
    cfg.print_summary()
    captured = capsys.readouterr()
    assert "Input" in captured.out
    assert "Device" in captured.out
    assert "Classified" in captured.out

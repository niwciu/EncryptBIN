"""GUI module for the encrypt-bin application."""

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QMessageBox,
    QTextEdit,
    QMenuBar,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

import os
import shlex
import sys
from pathlib import Path
from Crypto.Random import get_random_bytes  # nosec B413

from encrypt_bin.cli.parser import get_parsed_args
from encrypt_bin.core.config import Config
from encrypt_bin.core.builder import generate_bin

LABEL_WIDTH = 180


def _resource_base() -> Path:
    # PyInstaller extracts to sys._MEIPASS when running as a frozen bundle
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).parent


class EncryptBinGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Encrypted Bin Creator")
        self.setMinimumWidth(620)

        # Menu bar
        menu_bar = QMenuBar(self)
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("Load Configuration", self.load_configuration)
        file_menu.addAction("Save Configuration", self.save_configuration)
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About", self._show_about)
        help_menu.addAction("License", self._show_license)
        self.setMenuBar(menu_bar)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(6)

        # Grid for form fields
        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(1, 1)  # field column stretches

        row = 0

        # --- Product ID (Device ID) ---
        grid.addWidget(self._label("Product ID (hex uint64)"), row, 0)
        self.device_edit = QLineEdit()
        self.device_edit.setPlaceholderText("e.g. 0x00A0000BC22510E1")
        grid.addWidget(self.device_edit, row, 1, 1, 2)
        row += 1

        # --- App Version ---
        grid.addWidget(self._label("App Version (hex uint32)"), row, 0)
        self.version_edit = QLineEdit()
        self.version_edit.setPlaceholderText("e.g. 0x20260301")
        grid.addWidget(self.version_edit, row, 1, 1, 2)
        row += 1

        # --- Previous App Version ---
        grid.addWidget(self._label("Prev. App Ver. (hex uint32)"), row, 0)
        self.prev_version_edit = QLineEdit()
        self.prev_version_edit.setPlaceholderText("e.g. 0x20260201 or 0x00000000 when no prev ver")
        grid.addWidget(self.prev_version_edit, row, 1, 1, 2)
        row += 1

        # --- Key (hex) ---
        grid.addWidget(self._label("Key (16 bytes hex)"), row, 0)
        self.hex_key_edit = QLineEdit()
        self.hex_key_edit.setPlaceholderText("e.g. D9 29 8A C1 0A 2F 68 2C 62 B7 3F 73 08 26 F9 4D")
        self.hex_key_edit.textChanged.connect(self.clear_key_file)
        grid.addWidget(self.hex_key_edit, row, 1)
        generate_key_btn = QPushButton("Generate")
        generate_key_btn.setFixedWidth(80)
        generate_key_btn.clicked.connect(self._generate_random_key)
        grid.addWidget(generate_key_btn, row, 2)
        row += 1

        # --- Key file ---
        grid.addWidget(self._label("Key File"), row, 0)
        self.key_file_edit = QLineEdit()
        self.key_file_edit.setPlaceholderText("Select key file (alternative to hex key)")
        self.key_file_edit.textChanged.connect(self.clear_hex_key)
        grid.addWidget(self.key_file_edit, row, 1)
        key_file_btn = QPushButton("Select")
        key_file_btn.setFixedWidth(80)
        key_file_btn.clicked.connect(self.select_key_file)
        grid.addWidget(key_file_btn, row, 2)
        row += 1

        # --- Bootloader ID ---
        grid.addWidget(self._label("Bootloader ID (hex uint32)"), row, 0)
        self.bootloader_edit = QLineEdit()
        self.bootloader_edit.setPlaceholderText("e.g. 0x00000001")
        grid.addWidget(self.bootloader_edit, row, 1, 1, 2)
        row += 1

        # --- Input file ---
        grid.addWidget(self._label("Input file"), row, 0)
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Select input .bin file")
        grid.addWidget(self.input_edit, row, 1)
        input_btn = QPushButton("Select")
        input_btn.setFixedWidth(80)
        input_btn.clicked.connect(self.select_input_file)
        grid.addWidget(input_btn, row, 2)
        row += 1

        # --- Output file ---
        grid.addWidget(self._label("Output file"), row, 0)
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Select output .bin file")
        grid.addWidget(self.output_edit, row, 1)
        output_btn = QPushButton("Select")
        output_btn.setFixedWidth(80)
        output_btn.clicked.connect(self.select_output_file)
        grid.addWidget(output_btn, row, 2)
        row += 1

        # --- Page Size ---
        grid.addWidget(self._label("Page Size"), row, 0)
        self.page_combo = QComboBox()
        self.page_combo.addItems(["128 bytes", "256 bytes", "512 bytes", "1024 bytes", "2048 bytes", "4096 bytes"])
        self.page_combo.setCurrentText("2048 bytes")
        grid.addWidget(self.page_combo, row, 1, 1, 2)
        row += 1

        # --- Icon + Generate button ---
        icon_label = QLabel()
        icon_path = _resource_base() / "resources" / "icons" / "icon.png"
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path)).scaled(
                48,
                48,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(icon_label, row, 0)

        generate_btn = QPushButton("Generate Encrypted BIN")
        generate_btn.setMinimumHeight(generate_btn.sizeHint().height() * 2)
        generate_btn.clicked.connect(self.generate_binary)
        grid.addWidget(generate_btn, row, 1, 1, 2)
        row += 1

        main_layout.addLayout(grid)

        # --- Log ---
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        self.log_text.setPlaceholderText("Log output...")
        main_layout.addWidget(self.log_text)

        # Fix window size to content
        self.adjustSize()
        self.setFixedHeight(self.sizeHint().height())

        # Center on screen
        frame = self.frameGeometry()
        frame.moveCenter(QApplication.primaryScreen().availableGeometry().center())
        self.move(frame.topLeft())

    @staticmethod
    def _label(text):
        label = QLabel(text)
        label.setFixedWidth(LABEL_WIDTH)
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return label

    def _show_about(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("About Encrypted Bin Creator")
        dlg.setTextFormat(Qt.TextFormat.RichText)
        dlg.setText(
            "<b>Encrypted Bin Creator</b><br><br>"
            "Generates AES-128 CBC encrypted firmware binaries<br>"
            "for the SECURE_BOOTLOADER / SecureLoader ecosystem.<br><br>"
            "<b>Part of the firmware update ecosystem:</b><br>"
            "&#8226; <a href='https://github.com/niwciu/encrypt-bin'>encrypt-bin</a>"
            " &mdash; this tool: creates the encrypted .bin package<br>"
            "&#8226; <a href='https://github.com/niwciu/SecureLoader'>SecureLoader</a>"
            " &mdash; transfers the package to the device over serial<br>"
            "&#8226; <a href='https://github.com/niwciu/SECURE_BOOTLOADER'>SECURE_BOOTLOADER</a>"
            " &mdash; decrypts and flashes the firmware on the device<br><br>"
            "<b>Author:</b>  niwciu<br>"
            "<b>Email:</b>   <a href='mailto:niwciu@gmail.com'>niwciu@gmail.com</a><br>"
            "<b>GitHub:</b>  <a href='https://github.com/niwciu'>github.com/niwciu</a>"
        )
        icon_path = _resource_base() / "resources" / "icons" / "icon.png"
        if icon_path.exists():
            dlg.setIconPixmap(
                QPixmap(str(icon_path)).scaled(
                    128,
                    128,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        dlg.exec()

    def _show_license(self):
        license_path = _resource_base() / "LICENSE"
        try:
            text = license_path.read_text(encoding="utf-8")
        except OSError:
            text = "LICENSE file not found."

        dlg = QDialog(self)
        dlg.setWindowTitle("License")
        dlg.setMinimumSize(520, 340)

        layout = QVBoxLayout(dlg)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(text)
        layout.addWidget(text_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        dlg.exec()

    def _generate_random_key(self):
        key = get_random_bytes(16)
        self.hex_key_edit.setText(" ".join(f"{b:02X}" for b in key))

    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Input File", "", "Binary Files (*.bin);;All Files (*)")
        if file_path:
            self.input_edit.setText(os.path.basename(file_path))
            self.input_edit.setToolTip(file_path)

    def select_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Select Output File", "", "Binary Files (*.bin);;All Files (*)")
        if file_path:
            self.output_edit.setText(os.path.basename(file_path))
            self.output_edit.setToolTip(file_path)

    def select_key_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Key File", "", "All Files (*)")
        if file_path:
            self.key_file_edit.setText(file_path)

    def clear_key_file(self, _):
        if self.hex_key_edit.text():
            self.key_file_edit.clear()

    def clear_hex_key(self, _):
        if self.key_file_edit.text():
            self.hex_key_edit.clear()

    def log_message(self, message):
        self.log_text.append(message)

    def _get_page_size(self) -> int:
        """Extract numeric page length from combo box text."""
        return int(self.page_combo.currentText().split()[0])

    def _validate_and_get_params(self):
        """Validate inputs and return a dictionary of all parameters."""
        fields = {
            "Input file": self.input_edit.toolTip() or self.input_edit.text(),
            "Output file": self.output_edit.toolTip() or self.output_edit.text(),
            "Device ID": self.device_edit.text(),
            "Bootloader ID": self.bootloader_edit.text(),
            "App Version": self.version_edit.text(),
            "Previous App Version": self.prev_version_edit.text(),
        }

        for name, value in fields.items():
            if not value:
                raise ValueError(f"{name} is required")

        hex_key = self.hex_key_edit.text()
        key_file = self.key_file_edit.text()

        if hex_key and key_file:
            raise ValueError("Provide either a hex key or a key file, not both")
        if not hex_key and not key_file:
            raise ValueError("Either hex key or key file is required")

        key_flag = "-k" if hex_key else "-K"
        key_value = hex_key if hex_key else key_file

        return {
            "input": fields["Input file"],
            "output": fields["Output file"],
            "device": fields["Device ID"],
            "bootloader": fields["Bootloader ID"],
            "version": fields["App Version"],
            "prev_version": fields["Previous App Version"],
            "key_flag": key_flag,
            "key_value": key_value,
            "page_size": self._get_page_size(),
        }

    def generate_binary(self):
        try:
            params = self._validate_and_get_params()

            args = [
                "-i",
                params["input"],
                "-o",
                params["output"],
                "-d",
                params["device"],
                "-b",
                params["bootloader"],
                params["key_flag"],
                params["key_value"],
                "-v",
                params["version"],
                "-p",
                params["prev_version"],
                "-l",
                str(params["page_size"]),
            ]
            parsed_args = get_parsed_args(args)
            config = Config.from_args(parsed_args)

            self.log_message("Parameters loaded successfully:")
            self.log_message(str(config))

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

            self.log_message(f"\nOutput file '{config.output_path}' generated successfully.")
            QMessageBox.information(self, "Success", f"Binary file generated successfully:\n{config.output_path}")

        except (ValueError, FileNotFoundError, OSError) as e:
            self.log_message(f"Error: {e}")
            QMessageBox.critical(self, "Error", str(e))

    def save_configuration(self):
        try:
            params = self._validate_and_get_params()

            config_path, _ = QFileDialog.getSaveFileName(self, "Save Configuration", "", "Text Files (*.txt);;All Files (*)")
            if not config_path:
                return
            if not Path(config_path).suffix:
                config_path += ".txt"

            with open(config_path, "w") as f:
                f.write(f'-i {shlex.quote(params["input"])}\n')
                f.write(f'-o {shlex.quote(params["output"])}\n')
                f.write(f'-d {params["device"]}\n')
                f.write(f'-b {params["bootloader"]}\n')
                f.write(f'{params["key_flag"]} {shlex.quote(params["key_value"])}\n')
                f.write(f'-v {params["version"]}\n')
                f.write(f'-p {params["prev_version"]}\n')
                f.write(f'-l {params["page_size"]}\n')

            self.log_message(f"Configuration saved to {config_path}")
            QMessageBox.information(self, "Success", f"Configuration saved to {config_path}")

        except (ValueError, OSError) as e:
            self.log_message(f"Error: {e}")
            QMessageBox.critical(self, "Error", str(e))

    def load_configuration(self):
        try:
            path, _ = QFileDialog.getOpenFileName(self, "Load Configuration", "", "Text Files (*.txt);;All Files (*)")
            if not path:
                return

            parsed_args = get_parsed_args(["-c", path])
            self.input_edit.setText(os.path.basename(parsed_args.input))
            self.input_edit.setToolTip(parsed_args.input)
            self.output_edit.setText(os.path.basename(parsed_args.output))
            self.output_edit.setToolTip(parsed_args.output)
            self.device_edit.setText(hex(parsed_args.device_id))
            self.bootloader_edit.setText(hex(parsed_args.bootloader_id))
            if getattr(parsed_args, 'key_file', None):
                self.key_file_edit.setText(parsed_args.key_file)
                self.hex_key_edit.clear()
            else:
                key_hex = ' '.join(f'{b:02X}' for b in parsed_args.key)
                self.hex_key_edit.setText(key_hex)
                self.key_file_edit.clear()
            self.version_edit.setText(hex(parsed_args.app_version))
            self.prev_version_edit.setText(hex(parsed_args.prev_app_version))
            self.page_combo.setCurrentText(f"{parsed_args.page_size} bytes")
            self.log_message(f"Configuration loaded from {path}")

        except (ValueError, FileNotFoundError, OSError) as e:
            self.log_message(f"Error loading configuration: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load configuration: {e}")


def main():
    app = QApplication(sys.argv)
    window = EncryptBinGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

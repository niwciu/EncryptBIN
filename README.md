<div align="center">
  <img src="src/encrypt_bin/gui/resources/icons/icon_big.png" width="128" alt="EncryptBIN logo">

  # encrypt-bin

  **AES-128-CBC encrypted firmware binary generator for embedded devices**

  [![CI](https://github.com/niwciu/encrypt-bin/actions/workflows/ci.yml/badge.svg)](https://github.com/niwciu/encrypt-bin/actions/workflows/ci.yml)
  [![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/downloads/)
  [![Coverage ≥ 93%](https://img.shields.io/badge/coverage-%E2%89%A593%25-brightgreen)](#)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

**encrypt-bin** is a Python CLI and GUI tool for generating AES-128-CBC encrypted firmware binaries for embedded devices with Tiny-AES-C compatible bootloaders.

This project is part of a firmware update ecosystem for embedded devices:

| Tool | Role |
|---|---|
| 🔐 **[encrypt-bin](https://github.com/niwciu/encrypt-bin)** | *(this tool)* Generates the encrypted `.bin` package on the PC |
| 📡 **[SecureLoader](https://github.com/niwciu/SecureLoader)** | Transfers the encrypted package to the device over serial |
| 🛡️ **[SECURE_BOOTLOADER](https://github.com/niwciu/SECURE_BOOTLOADER)** | Bootloader on the embedded device — decrypts, verifies, and flashes the firmware (Tiny-AES-C, < 4 kB flash) |

The binary format produced by **encrypt-bin** is the format expected by **SECURE_BOOTLOADER**. **SecureLoader** is the transfer layer between them.

---

## ✨ Features

- 🔒 AES-128-CBC encryption (Tiny-AES-C compatible) with random IV per file
- 🔍 CRC32 integrity check of the padded plaintext
- 🖥️ CLI (`encrypt-bin`) and GUI (`encrypt-bin-gui`)
- 🔑 Key supplied inline (`-k`) or looked up from a per-device key file (`-K`)
- 📄 Configuration file support (`-c`) — store and reuse all parameters in a text file
- 📦 Standalone executables for Linux (`.tar.gz`, `.deb`) and Windows (`.zip`, setup installer)
- ✅ Full test suite with ≥ 93% coverage; CI matrix across Python 3.10–3.13

---

## 📁 Project Structure

```
encrypt-bin/
├── src/encrypt_bin/
│   ├── __main__.py           # CLI entry point
│   ├── cli/
│   │   ├── parser.py         # CLI argument handling + config file merging
│   │   ├── utils.py          # parse_int, parse_key, find_key_in_file
│   │   └── validators.py     # Path and file validation
│   ├── core/
│   │   ├── builder.py        # Core logic for BIN generation
│   │   └── config.py         # Config value object
│   └── gui/
│       └── main.py           # PyQt6 GUI
└── tests/
    ├── test_cli_parser.py
    ├── test_utils.py
    ├── test_builder.py
    ├── test_e2e.py
    └── ...
```

---

## 🖥️ GUI (Qt6)

A graphical interface wraps the CLI tool and exposes all parameters in a form. When you click **Generate Encrypted BIN** the same parser and builder code runs under the hood.

Launch after installing from source:

```bash
encrypt-bin-gui
```

---

## 🚀 Installation

### Requirements

- Python **3.10+**
- `pip`

### Install from source

```bash
git clone https://github.com/niwciu/encrypt-bin.git
cd encrypt-bin
pip install -e ".[gui,dev]"
```

### Pre-built binaries

Download from the [Releases](https://github.com/niwciu/encrypt-bin/releases) page — see [Installation docs](docs/installation.md) for details.

---

## 💻 Usage

### Quick start

```bash
encrypt-bin --help
```

### Command-line example

```bash
encrypt-bin \
  -i firmware.bin \
  -o encrypted.bin \
  -d 0x00A0000BC22510E1 \
  -b 0x00000001 \
  -k "D9 29 8A C1 0A 2F 68 2C 62 B7 3F 73 08 26 F9 4D" \
  -v 0x20260301 \
  -p 0x20260201
```

### Using a configuration file

```bash
encrypt-bin -c params.txt
```

---

## 🗂️ CLI Parameters

| Flag | Description | Required | Example |
|------|-------------|----------|---------|
| `-i`, `--input` | Input `.bin` file | yes | `-i firmware.bin` |
| `-o`, `--output` | Output `.bin` file | yes | `-o output.bin` |
| `-d`, `--device-id` | Device ID (uint64) | yes | `-d 0x00A0000BC22510E1` |
| `-b`, `--bootloader-id` | Bootloader ID (uint32) | yes | `-b 0x00000001` |
| `-k`, `--key` | 16-byte hex key | yes* | `-k "D9 29 8A ..."` |
| `-K`, `--key-file` | Per-device key map file | yes* | `-K keys.txt` |
| `-v`, `--app-version` | Application version (uint32) | yes | `-v 0x20260301` |
| `-p`, `--prev-app-version` | Previous app version (uint32) | yes | `-p 0x20260201` |
| `-l`, `--page-size` | Flash page size in bytes (default: 2048) | no | `-l 1024` |
| `-c`, `--config` | Configuration file | no | `-c params.txt` |

\* Exactly one of `-k` or `-K` is required.

---

## 📦 Output Binary Format

| Offset | Size | Field |
|--------|------|-------|
| 0x00 | 4 | Bootloader ID |
| 0x04 | 4 | Product ID (MSB) |
| 0x08 | 4 | Product ID (LSB) |
| 0x0C | 4 | App Version |
| 0x10 | 4 | Previous App Version |
| 0x14 | 4 | Num Pages |
| 0x18 | 4 | Page Size |
| 0x1C | 16 | AES IV |
| 0x2C | 4 | CRC32 |
| 0x30 | N | Encrypted Payload |

See [Output Format docs](docs/output_format.md) for full details.

---

## 🛠️ Development

A `Makefile` provides shortcuts for every check that also runs in CI. Requires Python 3.10+ and `make` (Linux/macOS).

### Quick setup

```bash
make install   # create .venv and install .[gui,dev]
make check     # lint + format-check + type-check + security + tests
```

### Individual targets

| Command | Tool(s) | Purpose |
|---|---|---|
| `make lint` | ruff, flake8 | Style and logic checks |
| `make format` | black | Auto-format source files |
| `make format-check` | black | Verify formatting (read-only) |
| `make type-check` | mypy | Static type analysis |
| `make security` | bandit, pip-audit | Security and CVE scan |
| `make test` | pytest | Run tests with coverage (≥ 90%) |
| `make clean` | — | Remove venv, build artefacts, caches |

The CI pipeline runs the full suite across **Python 3.10, 3.11, 3.12, and 3.13** on every push and pull request.

---

## 🤝 Contributing

See [docs/contributing.md](docs/contributing.md) for dev setup, local checks, and the PR process.

---

## 📄 License

Licensed under the **MIT License** — see [LICENSE](LICENSE).

---

## 👤 Author

**encrypt-bin** was created by niwciu.
Contact: [niwciu@gmail.com](mailto:niwciu@gmail.com) | [GitHub](https://github.com/niwciu)

<br>
<div align="center">

***

![myEmbeddedWayBanerWhiteSmaller](https://github.com/user-attachments/assets/f4825882-e285-4e02-a75c-68fc86ff5716)
***
</div>

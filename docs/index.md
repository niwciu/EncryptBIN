<div align="center">
  <img src="assets/icon_big.png" width="112" alt="EncryptBIN logo">
</div>

# 🔐 encrypt-bin

**AES-128-CBC encrypted firmware binary generator for embedded devices**

---

**encrypt-bin** is a Python CLI and GUI tool that takes a raw firmware `.bin`, pads it to a flash-page boundary, computes a CRC32, encrypts it with AES-128-CBC using a fresh random IV, and writes a structured binary package ready for OTA firmware updates.

It is part of a three-tool firmware update ecosystem:

| Tool | Role |
|---|---|
| 🔐 **[encrypt-bin](https://github.com/niwciu/encrypt-bin)** | *(this tool)* Generates the encrypted `.bin` package on the PC |
| 📡 **[SecureLoader](https://github.com/niwciu/SecureLoader)** | Transfers the encrypted package to the embedded device over serial |
| 🛡️ **[SECURE_BOOTLOADER](https://github.com/niwciu/SECURE_BOOTLOADER)** | Bootloader on the embedded device — decrypts, verifies, and flashes the firmware (Tiny-AES-C, < 4 kB flash) |

The binary format produced by **encrypt-bin** is the format expected by **SECURE_BOOTLOADER**. **SecureLoader** is the transfer layer between them.

```
encrypt-bin  ──►  encrypted .bin  ──►  SecureLoader (serial)  ──►  SECURE_BOOTLOADER (decrypt & flash)
```

---

## ✨ Features

- 🔒 **AES-128-CBC encryption** (Tiny-AES-C compatible) — fresh random IV generated per output file
- 🔍 **CRC32 integrity check** computed over the padded plaintext before encryption
- 🖥️ **CLI** (`encrypt-bin`) and **GUI** (`encrypt-bin-gui`) — same core logic powers both
- 🔑 Key supplied **inline** (`-k`) or looked up from a **per-device key file** (`-K`)
- 📄 **Configuration file** support (`-c`) — store and reuse all parameters in a text file
- 📦 **Standalone executables** for Linux (`.tar.gz`, `.deb`) and Windows (`.zip`, setup installer)
- ✅ Full test suite with ≥ 93% coverage; CI matrix across Python 3.10–3.13

---

## ⚡ Quick start

```bash
# Install from source (includes GUI and dev tools)
git clone https://github.com/niwciu/encrypt-bin.git
cd encrypt-bin
pip install -e ".[gui,dev]"

# Generate an encrypted binary
encrypt-bin \
  -i firmware.bin \
  -o encrypted.bin \
  -d 0x00A0000BC22510E1 \
  -b 0x00000001 \
  -k "D9 29 8A C1 0A 2F 68 2C 62 B7 3F 73 08 26 F9 4D" \
  -v 0x20260301 \
  -p 0x20260201
```

See [Installation](installation.md) for pre-built binaries and [Usage](usage.md) for the full parameter reference.

---

## 📚 Documentation map

| Page | Content |
|---|---|
| [Installation](installation.md) | Pre-built binaries, install from source, local build scripts, uninstall |
| [Usage](usage.md) | CLI flags, key formats, config file, GUI walkthrough |
| [Configuration File](config_file.md) | Store parameters in a file; merge with CLI |
| [Key File](key_file.md) | Per-device key map format and file security notes |
| [Output Format](output_format.md) | Binary header layout and payload preparation steps |
| [Release Signing](release_signing.md) | Windows code-signing certificate setup guide |
| [Contributing](contributing.md) | Run tests, code style, submitting a pull request |
| [Troubleshooting](troubleshooting.md) | Common errors and fixes |

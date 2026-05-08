# 💻 Usage

---

## CLI

### Quick start

```bash
encrypt-bin --help
```

### Full example

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

### Parameters

| Flag | Long form | Type | Required | Description |
|------|-----------|------|----------|-------------|
| `-i` | `--input` | path | yes | Input `.bin` file (source firmware) |
| `-o` | `--output` | path | yes | Output `.bin` file (encrypted package) |
| `-d` | `--device-id` | uint64 hex/dec | yes | Product / device identifier |
| `-b` | `--bootloader-id` | uint32 hex/dec | yes | Bootloader build identifier |
| `-k` | `--key` | 16-byte hex | yes* | AES-128 key (inline hex) |
| `-K` | `--key-file` | path | yes* | Key map file — alternative to `-k` |
| `-v` | `--app-version` | uint32 hex/dec | yes | Current firmware version |
| `-p` | `--prev-app-version` | uint32 hex/dec | yes | Previous firmware version |
| `-l` | `--page-size` | int | no | Flash page size in bytes (default: `2048`) |
| `-c` | `--config` | path | no | Configuration file — see [Configuration File](config_file.md) |

\* Exactly one of `-k` or `-K` is required; they are mutually exclusive.

---

### Version format

Versions are `uint32` values. A recommended convention is a date-based format:

```
0x20260301  →  2026-03-01
```

Use `0x00000000` for `--prev-app-version` when flashing the first firmware release onto a device.

### Page length

`--page-size` must be a **positive multiple of 16** (AES block size). It should match the flash page size of your target microcontroller. Common values:

| Value | Typical target |
|---|---|
| `128` | AVR (e.g. ATmega328P) |
| `256` | AVR (e.g. ATmega2560) |
| `512` | Small MCUs (e.g. STM32F0) |
| `1024` | Mid-range MCUs |
| `2048` | Default — STM32F4 / STM32L4 typical |
| `4096` | Large-page targets |

### Key formats accepted by `-k`

All three formats below are equivalent:

```bash
# Space-separated bytes (most readable)
-k "D9 29 8A C1 0A 2F 68 2C 62 B7 3F 73 08 26 F9 4D"

# Continuous hex string (32 chars)
-k "D9298AC10A2F682C62B73F730826F94D"

# Comma-separated with 0x prefix
-k "0xD9,0x29,0x8A,0xC1,0x0A,0x2F,0x68,0x2C,0x62,0xB7,0x3F,0x73,0x08,0x26,0xF9,0x4D"
```

---

## 📄 Using a configuration file (`-c`)

Store all parameters in a plain text file and pass it with `-c`.

Example `params.txt`:

```
-i firmware.bin
-o encrypted.bin
-d 0x00A0000BC22510E1
-b 0x00000001
-k "D9 29 8A C1 0A 2F 68 2C 62 B7 3F 73 08 26 F9 4D"
-v 0x20260301
-p 0x20260201
-l 2048
```

Run with:

```bash
encrypt-bin -c params.txt
```

You can pass additional flags alongside `-c`. If a flag appears in both the file and the CLI **with the same value**, it is silently accepted. If the values **differ**, the tool exits with an error — there is no silent override.

```bash
# Fine — adds a flag not present in the file
encrypt-bin -c params.txt -l 1024

# Error — -v appears in the file with a different value
encrypt-bin -c params.txt -v 0x20260401
```

!!! tip
    Use separate config files per release (e.g. `v1.0.txt`, `v1.1.txt`) rather than overriding version flags on the command line.

See [Configuration File](config_file.md) for the full format specification.

---

## 🖥️ GUI

Launch the GUI:

```bash
encrypt-bin-gui
```

Or, if running from source:

```bash
python -m encrypt_bin.gui.main
```

### Fields

| Field | Description |
|---|---|
| Product ID | Device identifier — same as CLI `-d` |
| App Version | Current firmware version — same as CLI `-v` |
| Prev. App Ver. | Previous firmware version — same as CLI `-p` |
| Key (16 bytes hex) | Inline AES key — same as CLI `-k` |
| Key File | Key map file — same as CLI `-K` |
| Bootloader ID | Bootloader identifier — same as CLI `-b` |
| Input file | Source `.bin` firmware file |
| Output file | Destination encrypted `.bin` file |
| Page Size | Flash page size selected from a drop-down (128 / 256 / 512 / 1024 / 2048 / 4096 bytes) |

!!! info "Mutually exclusive key fields"
    Typing in the **Key** field clears **Key File**, and vice versa. You cannot provide both at the same time.

### Buttons

| Button | Action |
|---|---|
| **Generate** (next to Key field) | Generates a cryptographically random 16-byte AES key and fills the Key field |
| **Select** (next to Input / Output / Key File) | Opens a file picker dialog |
| **Generate Encrypted BIN** | Validates all fields, runs encryption, and writes the output file |

### File menu

| Menu item | Description |
|---|---|
| **File → Save Configuration** | Saves all current field values to a `.txt` config file (compatible with `-c`) |
| **File → Load Configuration** | Loads a previously saved config file and populates all fields |

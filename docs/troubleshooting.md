# 🔧 Troubleshooting

---

## 🪟 Windows SmartScreen blocks the executable

**Symptom:** "Windows protected your PC" dialog appears on first run.

**Cause:** Unsigned executables downloaded from the internet are blocked until they build sufficient reputation with Microsoft.

**Fix:**

- Click **More info → Run anyway** (one-time, per machine), or
- Right-click the downloaded `.zip` → **Properties** → tick **Unblock** → OK, then extract and run.

For a permanent fix on a controlled machine see [Release Signing](release_signing.md).

---

## 🔑 Key file permission warning

**Symptom:**

```
UserWarning: Key file 'keys.txt' has group/other permissions (check file security).
```

**Cause:** The key file is readable by group or other users on Linux/macOS.

**Fix:**

```bash
chmod 600 keys.txt
```

The tool still runs after the warning — fix the permissions before use in production.

---

## 📁 "Input file … does not exist"

**Cause:** The path passed to `-i` does not resolve to an existing file, or the file does not have a `.bin` extension.

**Fix:** Verify the path and extension:

```bash
ls -l firmware.bin
```

Both conditions must be true: the file must exist **and** end with `.bin`.

---

## 📂 "Output directory … does not exist"

**Cause:** The directory portion of the path passed to `-o` does not exist.

**Fix:** Create the directory first:

```bash
mkdir -p output/
encrypt-bin -i firmware.bin -o output/encrypted.bin ...
```

---

## 🔐 "Key must be exactly 16 bytes"

**Cause:** The key string passed via `-k` parsed to fewer or more than 16 bytes.

**Fix:** Verify the key is exactly 16 hex bytes in one of the supported formats:

```
# Space-separated (16 pairs)
D9 29 8A C1 0A 2F 68 2C 62 B7 3F 73 08 26 F9 4D

# Continuous hex string (32 characters)
D9298AC10A2F682C62B73F730826F94D

# Comma-separated with 0x prefix (16 values)
0xD9,0x29,0x8A,0xC1,0x0A,0x2F,0x68,0x2C,0x62,0xB7,0x3F,0x73,0x08,0x26,0xF9,0x4D
```

---

## 🔍 "Could not find key for device_id"

**Cause:** The `-K` key file was searched for the device ID passed to `-d`, but no matching entry was found.

**Fix:** Open the key file and confirm there is a line for the exact device ID being used. Device IDs are compared numerically, so `0x00A0000BC22510E1` and `45035997338050785` are the same — see [Key File](key_file.md).

---

## ⚠️ "Flag '…' appears in both file and CLI with different values"

**Cause:** A flag was specified in the config file (`-c`) and also passed on the command line, but with different values.

```
Error: Flag '-v' appears in both file and CLI with different values:
 - from file:     0x20260301
 - from terminal: 0x20260401
```

**Cause:** There is no silent override — the tool treats this as an error to prevent accidental key or version mismatches.

**Fix:** Either:

- Remove the conflicting flag from the config file, or
- Remove it from the command line, or
- Make both values identical.

See [Configuration File](config_file.md) for the merging rules.

---

## 📏 "Page size must be a positive integer" / "must be a multiple of 16"

**Cause:** The value passed to `-l` / `--page-size` is either zero/negative, or not divisible by 16 (the AES block size).

**Fix:** Use a positive multiple of 16. Common valid values: `128`, `256`, `512`, `1024`, `2048`, `4096`.

---

## 🔢 "Device ID exceeds uint64 range" / "Bootloader ID exceeds uint32 range"

**Cause:** The numeric value passed to `-d`, `-b`, `-v`, or `-p` is larger than the field's maximum:

| Flag | Type | Maximum |
|---|---|---|
| `-d` | uint64 | `0xFFFFFFFFFFFFFFFF` |
| `-b`, `-v`, `-p` | uint32 | `0xFFFFFFFF` |

**Fix:** Check the value passed to the flag and ensure it fits within the valid range.

---

## 🖥️ GUI does not start on Linux

**Symptom:** No window appears, or an error such as:

```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
```

**Fix:** Install the required Qt platform libraries:

```bash
sudo apt-get install -y libxcb-cursor0 libxkbcommon0 libxcb-xinerama0
```

If running in a headless or CI environment, set:

```bash
export QT_QPA_PLATFORM=offscreen
```

---

## 📄 Config file: "Error reading config file"

**Cause:** The file passed with `-c` is missing, unreadable, or contains a quoting error (e.g. a space-containing path that is not quoted).

**Fix:**

- Verify the file exists and is readable.
- Ensure values containing spaces are wrapped in double quotes — see [Configuration File](config_file.md).

Example of correct quoting:

```
-i "C:/my firmware/release.bin"
-k "D9 29 8A C1 0A 2F 68 2C 62 B7 3F 73 08 26 F9 4D"
```

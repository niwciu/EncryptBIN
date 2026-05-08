# 🔑 Key File Format

A key file maps device IDs to AES-128 keys. Use it with the `-K` / `--key-file` CLI flag or the **Key File** field in the GUI.

When a key file is provided, EncryptBIN looks up the key that matches the `--device-id` value and uses it for encryption. This lets you manage keys for an entire device fleet in one place without embedding them in scripts or config files.

---

## Format

Each non-empty, non-comment line defines one device-to-key mapping.

**Semicolon-separated (recommended):**

```
<device_id> ; <key>
```

**Space or comma separated:**

```
<device_id> <key>
```

- `device_id` — decimal or hex (with `0x` prefix); must match the value passed to `-d`
- `key` — 16 bytes in any hex format accepted by `-k` (see [Usage — Key formats](usage.md))
- Lines starting with `#` are **comments** and are ignored
- Blank lines are ignored

---

## Example

```
# device_id             ; AES-128 key (16 bytes hex)

0x00A0000BC22510E1 ; D9 29 8A C1 0A 2F 68 2C 62 B7 3F 73 08 26 F9 4D
0x00A0000BC22510E2 ; 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 00
0x00A0000BC22510E3 ; 00112233445566778899AABBCCDDEEFF
```

All three key formats are equivalent — space-separated, continuous string, or comma-separated with `0x` prefixes.

---

## 🔒 File security

!!! danger "Keep key files out of version control"
    AES keys are secrets. **Never commit a key file to a Git repository** or store it in any shared location. Add it to `.gitignore`:
    ```
    keys.txt
    *.keys
    ```

### Linux / macOS — file permissions

Restrict access to the owner only:

```bash
chmod 600 keys.txt
```

If the file has group or world read permissions, EncryptBIN will print a warning:

```
UserWarning: Key file 'keys.txt' has group/other permissions (check file security).
```

The tool still runs when the warning is shown — it does not treat loose permissions as a fatal error — but you should fix the permissions before use in production.

### Windows

The permission check is Linux/macOS-only. On Windows, use NTFS permissions or keep the key file in a folder restricted to your user account (e.g. inside `%USERPROFILE%`).

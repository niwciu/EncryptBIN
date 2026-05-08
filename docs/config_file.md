# 📄 Configuration File Format

A configuration file lets you store all CLI parameters in a plain text file and load them with `-c` / `--config`.
The GUI's **Save Configuration** and **Load Configuration** menu items read and write this same format.

---

## Format

One flag–value pair per line:

```
-<flag> <value>
```

- Lines starting with `#` are **comments** and are ignored
- Blank lines are ignored
- Values containing spaces **must** be quoted with `"double quotes"`
- All flags are the same as in the CLI (see [Usage](usage.md))

---

## Example

```
# EncryptBIN configuration — device A, firmware v1.1

-i "C:/firmware/release.bin"
-o "C:/firmware/release_enc.bin"
-d 0x00A0000BC22510E1
-b 0x00000001
-k "D9 29 8A C1 0A 2F 68 2C 62 B7 3F 73 08 26 F9 4D"
-v 0x20260301
-p 0x20260201
-l 2048
```

---

## Merging file and CLI arguments

When `-c` is used together with other flags, the file arguments and CLI arguments are **merged**:

| Situation | Result |
|---|---|
| Flag in file only | Included as-is |
| Flag in CLI only | Included as-is |
| Same flag, **same value** in both | Accepted — treated as one occurrence |
| Same flag, **different values** in file and CLI | ❌ Error — the tool exits |

!!! warning "No silent override"
    Unlike many tools, passing a flag on the command line does **not** silently override the value in the config file. If the values conflict, the tool exits with an error message listing both values. This prevents accidental key or version mismatches.

    ```
    Error: Flag '-v' appears in both file and CLI with different values:
     - from file:     0x20260301
     - from terminal: 0x20260401
    ```

To update a single parameter across builds, keep separate config files per release rather than overriding at the CLI:

```
params_v1.0.txt   →  encrypt-bin -c params_v1.0.txt
params_v1.1.txt   →  encrypt-bin -c params_v1.1.txt
```

---

## Notes

- `-c` itself **cannot** appear inside a config file — this would cause a circular load
- Use `-K` instead of `-k` if you want to reference a key file rather than an inline key
- The config file format is the same file produced by **File → Save Configuration** in the GUI

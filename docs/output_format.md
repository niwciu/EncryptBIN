# 📦 Output Binary Format

The encrypted `.bin` file produced by EncryptBIN has a fixed-size **48-byte header** followed by the encrypted firmware payload.
All multi-byte integers are **little-endian**.

---

## Layout

| Offset | Size (bytes) | Type | Field | Description |
|--------|-------------|------|-------|-------------|
| `0x00` | 4 | uint32 LE | Bootloader ID | Identifies the target bootloader build |
| `0x04` | 4 | uint32 LE | Product ID (MSB) | Upper 32 bits of the 64-bit device/product identifier |
| `0x08` | 4 | uint32 LE | Product ID (LSB) | Lower 32 bits of the 64-bit device/product identifier |
| `0x0C` | 4 | uint32 LE | App Version | Current firmware version |
| `0x10` | 4 | uint32 LE | Previous App Version | Previous firmware version (`0x00000000` if none) |
| `0x14` | 4 | uint32 LE | Num Pages | Number of flash pages in the padded payload |
| `0x18` | 4 | uint32 LE | Page Size | Flash page size in bytes used for padding |
| `0x1C` | 16 | bytes | AES IV | Randomly generated initialization vector (one per output file) |
| `0x2C` | 4 | uint32 LE | CRC32 | CRC32 of the **padded plaintext** (computed before encryption) |
| `0x30` | N | bytes | Encrypted Payload | AES-128-CBC ciphertext of the padded firmware |

**Total header size: 48 bytes** (`0x30`).

---

## Payload preparation

The input firmware goes through three steps before the output file is written:

1. **Padding** — the raw binary is zero-padded (`\x00`) to the next multiple of `page_size`.
2. **CRC32** — computed over the padded plaintext using the standard CRC32 polynomial (`zlib.crc32`).
3. **Encryption** — AES-128-CBC with a fresh random 16-byte IV; compatible with [Tiny-AES-C](https://github.com/kokke/tiny-AES-c).

!!! info "CRC32 covers padded plaintext"
    The CRC32 is computed on the zero-padded plaintext **before** encryption, not on the ciphertext. The bootloader decrypts first, then verifies CRC32 to confirm integrity before flashing.

---

## Product ID split

The 64-bit `device-id` passed via `-d` is split into two 32-bit header fields:

```
Product ID (MSB)  =  (device_id >> 32) & 0xFFFFFFFF
Product ID (LSB)  =   device_id        & 0xFFFFFFFF
```

The bootloader reconstructs the full 64-bit value from both fields before performing device matching.

---

## Worked example

For a **12 KB firmware** with `--page-size 2048`:

| Step | Value |
|---|---|
| Input size | 12 288 bytes (already a multiple of 2048) |
| Padded size | 12 288 bytes (no padding needed) |
| `Num Pages` | `6` |
| `Page Size` | `2048` |
| Encrypted payload | 12 288 bytes |
| **Total file size** | **48 + 12 288 = 12 336 bytes** |

For a **10 KB firmware** with `--page-size 2048`:

| Step | Value |
|---|---|
| Input size | 10 240 bytes |
| Padded size | 12 288 bytes (padded to next multiple of 2048) |
| `Num Pages` | `6` |
| Padding added | 2 048 bytes of `\x00` |
| **Total file size** | **48 + 12 288 = 12 336 bytes** |

---

## 🔗 Ecosystem compatibility

The `.bin` produced by **encrypt-bin** is the exact binary format consumed by **[SECURE_BOOTLOADER](https://github.com/niwciu/SECURE_BOOTLOADER)** — a compact Tiny-AES-C bootloader for embedded devices that occupies less than 4 kB of flash.

Transfer from the host PC to the device is handled by **[SecureLoader](https://github.com/niwciu/SecureLoader)**.

```
encrypt-bin  ──►  encrypted .bin  ──►  SecureLoader (serial)  ──►  SECURE_BOOTLOADER (decrypt & flash)
```

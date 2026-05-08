import os
import struct
import zlib
from Crypto.Cipher import AES  # nosec B413
from Crypto.Random import get_random_bytes  # nosec B413


def pad_bytes(data: bytes, page_size: int) -> bytes:
    """Pads the data with zeros to make its length a multiple of page_size."""
    pad_len = (page_size - len(data) % page_size) % page_size
    return data + b"\x00" * pad_len


def encrypt_aes_cbc(input_bytes: bytes, key: bytes, iv: bytes) -> bytes:
    """Encrypts data using AES-128 CBC, compatible with Tiny-AES-C."""
    if len(key) != 16:
        raise ValueError(f"Key must be exactly 16 bytes, got {len(key)}")
    if len(iv) != 16:
        raise ValueError(f"IV must be exactly 16 bytes, got {len(iv)}")
    if len(input_bytes) % 16 != 0:
        raise ValueError(f"Input data length must be a multiple of 16, got {len(input_bytes)}")

    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(input_bytes)


def generate_bin(
    input_path: str,
    output_path: str,
    product_id: int,
    app_version: int,
    prev_app_version: int,
    bootloader_id: int,
    key: bytes,
    page_size: int = 2048,
) -> str:
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file '{input_path}' does not exist.")

    with open(input_path, "rb") as f:
        input_bytes = f.read()

    input_bytes = pad_bytes(input_bytes, page_size)
    iv = get_random_bytes(16)
    enc_bytes = encrypt_aes_cbc(input_bytes, key, iv)
    crc32_val = zlib.crc32(input_bytes) & 0xFFFFFFFF

    with open(output_path, "wb") as f:
        f.write(struct.pack("<I", bootloader_id))
        f.write(struct.pack("<I", (product_id >> 32) & 0xFFFFFFFF))  # MSB of product_id
        f.write(struct.pack("<I", product_id & 0xFFFFFFFF))  # LSB of product_id
        f.write(struct.pack("<I", app_version))
        f.write(struct.pack("<I", prev_app_version))
        num_pages = len(input_bytes) // page_size
        f.write(struct.pack("<I", num_pages))
        f.write(struct.pack("<I", page_size))
        f.write(iv)
        f.write(struct.pack("<I", crc32_val))
        f.write(enc_bytes)

    return output_path

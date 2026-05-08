"""Configuration module – stores and prints input parameters."""

import argparse


class Config:
    """Represents the set of input parameters for the script."""

    def __init__(
        self,
        input_path: str,
        output_path: str,
        device_id: int,
        bootloader_id: int,
        key: bytes,
        app_version: int,
        prev_app_version: int,
        page_size: int,
    ) -> None:
        self.input_path = input_path
        self.output_path = output_path
        self.device_id = device_id
        self.bootloader_id = bootloader_id
        self.key = key
        self.app_version = app_version
        self.prev_app_version = prev_app_version
        self.page_size = page_size

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Config":
        """Creates a Config object from parsed argparse arguments."""
        return cls(
            args.input,
            args.output,
            args.device_id,
            args.bootloader_id,
            args.key,
            args.app_version,
            args.prev_app_version,
            args.page_size,
        )

    def __str__(self) -> str:
        lines = [
            f" Input file:          {self.input_path}",
            f" Output file:         {self.output_path}",
            f" Device ID:           {self.device_id} (0x{self.device_id:X})",
            f" Bootloader ID:       {self.bootloader_id} (0x{self.bootloader_id:X})",
            f" App version:         {self.app_version} (0x{self.app_version:X})",
            f" Previous app version:{self.prev_app_version} (0x{self.prev_app_version:X})",
            f" Page length:         {self.page_size}",
            " Key (hex):           Classified",
        ]
        return "\n".join(lines)

    def print_summary(self) -> None:
        """Prints the current configuration parameters."""
        print(str(self))

"""Functions for validating file paths and directories."""

import os


def validate_file_paths(input_path: str, output_path: str) -> None:
    """Checks the existence of the input file and validity of the output path."""
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file '{input_path}' does not exist.")
    if not input_path.lower().endswith(".bin"):
        raise ValueError("Input file must have the '.bin' extension.")

    output_dir = os.path.dirname(output_path) or "."
    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Output directory '{output_dir}' does not exist.")
    if not output_path.lower().endswith(".bin"):
        raise ValueError("Output file must have the '.bin' extension.")

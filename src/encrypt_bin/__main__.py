import sys

from encrypt_bin.cli.parser import get_parsed_args
from encrypt_bin.core.config import Config
from encrypt_bin.core.builder import generate_bin


def main() -> None:
    try:
        args = get_parsed_args()
    except (ValueError, FileNotFoundError, OSError) as e:
        sys.exit(f"Error: {e}")

    config = Config.from_args(args)

    print("Parameters loaded successfully:")
    print(config)

    try:
        generate_bin(
            input_path=config.input_path,
            output_path=config.output_path,
            product_id=config.device_id,
            app_version=config.app_version,
            prev_app_version=config.prev_app_version,
            bootloader_id=config.bootloader_id,
            key=config.key,
            page_size=config.page_size,
        )
        print(f"\nOutput file '{config.output_path}' generated successfully.")
    except (ValueError, FileNotFoundError, OSError) as e:
        sys.exit(f"Error while generating the output file: {e}")


if __name__ == "__main__":
    main()

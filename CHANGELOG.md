# Changelog

## v0.2.0 - 2026-10-14

### Added
- Partial configuration-file loading in the GUI.
- GUI version information in **Help → About**.
- Release preparation and tagging instructions for maintainers.

### Changed
- Configuration loading now warns about unavailable paths while restoring the remaining valid parameters.
- Refactored parser and GUI configuration-loading code to satisfy project complexity limits.

## v0.1.0 - 2026-05-09

Initial public release of **encrypt-bin** — a CLI and GUI tool for generating AES-128-CBC encrypted firmware binaries for embedded devices with Tiny-AES-C compatible bootloaders.

### Added
- CLI (`encrypt-bin`) and GUI (`encrypt-bin-gui`) for producing encrypted `.bin` files ready for OTA firmware updates
- AES-128-CBC encryption with random IV and CRC32 integrity check
- Inline key or per-device key file support, configuration file support
- Standalone executables for Linux (`.tar.gz`, `.deb`) and Windows (`.zip`, setup installer)
- Full test suite, CI pipeline, and automated GitHub release workflow

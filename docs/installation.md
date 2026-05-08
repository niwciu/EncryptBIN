# 📦 Installation

---

## 🪟 Windows — first-run note

Executables downloaded from the internet are blocked by Windows SmartScreen until they are signed with a trusted certificate. If you see **"Windows protected your PC"**:

- Click **More info → Run anyway** (one-time, per machine), or
- Right-click the downloaded `.zip` → **Properties** → tick **Unblock** → OK, then extract and run.

Once the certificate builds enough download reputation, SmartScreen stops prompting. For a permanent fix on a controlled machine, see [Release Signing](release_signing.md).

---

## Requirements

- Python **3.10** or newer
- `pip`
- `venv`

---

## 🚀 From a release binary (recommended)

Download the package for your platform from the [Releases](https://github.com/niwciu/encrypt-bin/releases) page.

| Platform | Archive | Contents |
|----------|---------|----------|
| Linux | `EncryptBIN-linux.tar.gz` | `EncryptBIN-linux-binary.tar.gz` (portable) + `EncryptBIN-linux-installer.deb` (Debian package) |
| Windows | `EncryptBIN-windows.zip` | `EncryptBIN-windows-binary.zip` (portable) + `EncryptBIN-windows-setup.exe` (installer) |

=== "Linux — portable binary"

    ```bash
    tar -xzf EncryptBIN-linux.tar.gz
    tar -xzf EncryptBIN-linux-binary.tar.gz
    ./EncryptBIN
    ```

=== "Linux — Debian package"

    ```bash
    tar -xzf EncryptBIN-linux.tar.gz
    sudo dpkg -i EncryptBIN-linux-installer.deb
    EncryptBIN
    ```

=== "Windows — portable"

    Extract `EncryptBIN-windows.zip`, then extract `EncryptBIN-windows-binary.zip` inside it.
    Run `EncryptBIN.exe` directly — no installation required.

=== "Windows — installer"

    Extract `EncryptBIN-windows.zip` and run `EncryptBIN-windows-setup.exe`.
    Follow the wizard; a Start Menu entry and optional desktop shortcut are created.

---

## 🔧 From source

```bash
git clone https://github.com/niwciu/encrypt-bin.git
cd encrypt-bin
pip install -e ".[gui,dev]"
```

Launch the GUI:

```bash
encrypt-bin-gui
```

Launch the CLI:

```bash
encrypt-bin --help
```

---

## 🏗️ Build and install locally

Use the scripts in `install_scripts/` to build a standalone binary from source and install it on your machine. Both scripts ask whether you want a **system-wide** or **local (current user)** install.

=== "Linux"

    ```bash
    cd install_scripts
    bash build.sh
    ```

    | Install type | Binary location | Desktop entry |
    |---|---|---|
    | System-wide (sudo) | `/opt/EncryptBIN/EncryptBIN` | `/usr/share/applications/` |
    | Local (no sudo) | `~/.local/bin/EncryptBIN` | `~/.local/share/applications/` |

    !!! note "PATH for local install"
        If you chose the local install, ensure `~/.local/bin` is on your `$PATH`:
        ```bash
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        source ~/.bashrc
        ```

=== "Windows"

    ```bat
    cd install_scripts
    build.bat
    ```

    | Install type | Binary location | Shortcuts |
    |---|---|---|
    | System-wide (Admin) | `%ProgramFiles%\EncryptBIN\` | All-users Start Menu + Desktop |
    | Local (no Admin) | `%LOCALAPPDATA%\Programs\EncryptBIN\` | User Start Menu + Desktop |

    !!! note "System-wide install"
        The system-wide option requires you to run `build.bat` as Administrator.

---

## 🗑️ Uninstall

Use the matching uninstall script from `install_scripts/`.

=== "Linux"

    ```bash
    cd install_scripts
    bash uninstall.sh
    ```

    Choose the same install type (system-wide or local) that you used during installation. The script removes the binary, icon, and desktop entry.

=== "Windows"

    ```bat
    cd install_scripts
    uninstall.bat
    ```

    Choose the same install type (system-wide or local) that you used during installation. The script removes the binary, Start Menu shortcut, and Desktop shortcut.

!!! note "Debian package uninstall"
    If you installed the `.deb` package, uninstall with:
    ```bash
    sudo dpkg -r encryptbin
    ```

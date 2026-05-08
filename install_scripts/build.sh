#!/bin/bash

APP_NAME="EncryptBIN"
MAIN_PY="../src/encrypt_bin/gui/main.py"
ICON="../src/encrypt_bin/gui/resources/icons/icon.png"
DESKTOP_TEMPLATE="$APP_NAME.desktop"
DIST_DIR="./dist"
VENV_DIR="../.venv"

echo "==== [1/5] Cleaning previous build ===="
rm -rf "$DIST_DIR" __pycache__ *.spec

echo ""
echo "==== [2/5] Creating/activating virtual environment ===="
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

echo ""
echo "==== [3/5] Installing dependencies ===="
pip install --upgrade pip
pip install -e "../.[gui,build]"

echo ""
echo "==== [4/5] Building binary ===="
pyinstaller --onefile --windowed --name "$APP_NAME" --paths "../src" \
    --add-data "../src/encrypt_bin/gui/resources:resources" \
    --add-data "../src/encrypt_bin/gui/LICENSE:." \
    "$MAIN_PY"
chmod +x "$DIST_DIR/$APP_NAME"

deactivate

echo ""
echo "==== [5/5] Installing ===="
echo ""
echo "Install type:"
echo "  1) System-wide  (/opt, requires sudo)"
echo "  2) Local        (~/.local, current user only)"
read -r -p "Choose [1/2]: " CHOICE

if [ "$CHOICE" = "1" ]; then
    INSTALL_DIR="/opt/$APP_NAME"
    BIN_LINK="/usr/local/bin/$APP_NAME"
    ICON_DEST="/usr/share/pixmaps/${APP_NAME}.png"
    DESKTOP_DEST="/usr/share/applications/${APP_NAME}.desktop"

    sudo mkdir -p "$INSTALL_DIR"
    sudo cp "$DIST_DIR/$APP_NAME" "$INSTALL_DIR/$APP_NAME"
    sudo chmod +x "$INSTALL_DIR/$APP_NAME"
    sudo ln -sf "$INSTALL_DIR/$APP_NAME" "$BIN_LINK"
    sudo cp "$ICON" "$ICON_DEST"

    EXEC_PATH="$INSTALL_DIR/$APP_NAME"
    ICON_PATH="$APP_NAME"

    sed \
        -e "s|PLACEHOLDER_NAME|${APP_NAME}|g" \
        -e "s|PLACEHOLDER_EXEC|${EXEC_PATH}|g" \
        -e "s|PLACEHOLDER_ICON|${ICON_PATH}|g" \
        "$DESKTOP_TEMPLATE" | sudo tee "$DESKTOP_DEST" > /dev/null

    echo ""
    echo "Installed to:  $INSTALL_DIR/$APP_NAME"
    echo "Symlink:       $BIN_LINK"
    echo "Desktop entry: $DESKTOP_DEST"

elif [ "$CHOICE" = "2" ]; then
    INSTALL_DIR="$HOME/.local/bin"
    ICON_DEST="$HOME/.local/share/icons/${APP_NAME}.png"
    DESKTOP_DEST="$HOME/.local/share/applications/${APP_NAME}.desktop"

    mkdir -p "$INSTALL_DIR"
    mkdir -p "$HOME/.local/share/icons"
    mkdir -p "$HOME/.local/share/applications"

    cp "$DIST_DIR/$APP_NAME" "$INSTALL_DIR/$APP_NAME"
    chmod +x "$INSTALL_DIR/$APP_NAME"
    cp "$ICON" "$ICON_DEST"

    EXEC_PATH="$INSTALL_DIR/$APP_NAME"
    ICON_PATH="$ICON_DEST"

    sed \
        -e "s|PLACEHOLDER_NAME|${APP_NAME}|g" \
        -e "s|PLACEHOLDER_EXEC|${EXEC_PATH}|g" \
        -e "s|PLACEHOLDER_ICON|${ICON_PATH}|g" \
        "$DESKTOP_TEMPLATE" > "$DESKTOP_DEST"

    echo ""
    echo "Installed to:  $INSTALL_DIR/$APP_NAME"
    echo "Desktop entry: $DESKTOP_DEST"
    echo ""
    echo "Note: make sure ~/.local/bin is on your PATH."
    echo "      Add to ~/.bashrc or ~/.profile if needed:"
    echo "      export PATH=\"\$HOME/.local/bin:\$PATH\""

else
    echo "Invalid choice. Exiting."
    exit 1
fi

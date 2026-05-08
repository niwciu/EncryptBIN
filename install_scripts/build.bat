@echo off
setlocal enabledelayedexpansion

REM === Configuration ===
set APP_NAME=EncryptBIN
set MAIN_PY=..\src\encrypt_bin\gui\main.py
set ICON=..\src\encrypt_bin\gui\resources\icons\icon.ico
set DIST_DIR=dist
set VENV_DIR=..\.venv

echo.
echo ==== [1/5] Cleaning previous build ====
if exist %DIST_DIR% rmdir /s /q %DIST_DIR%
if exist %APP_NAME%.spec del /q %APP_NAME%.spec
if exist __pycache__ rmdir /s /q __pycache__

echo.
echo ==== [2/5] Creating/activating virtual environment ====
if not exist %VENV_DIR% (
    python -m venv %VENV_DIR%
)
call %VENV_DIR%\Scripts\activate.bat

echo.
echo ==== [3/5] Installing dependencies ====
pip install --upgrade pip
pip install -e "..\.[gui,build]"

echo.
echo ==== [4/5] Building EXE ====
pyinstaller --onefile --noconsole --icon=%ICON% --paths="..\src" --name %APP_NAME% %MAIN_PY%

call deactivate

echo.
echo ==== [5/5] Installing ====
echo.
echo Install type:
echo   1) System-wide  (Program Files, requires Administrator)
echo   2) Local        (AppData, current user only)
choice /C 12 /N /M "Choose [1/2]: "

if errorlevel 2 goto local_install
if errorlevel 1 goto system_install

:system_install
    net session >nul 2>&1
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: System-wide install requires Administrator privileges.
        echo Please re-run this script as Administrator.
        pause
        exit /b 1
    )

    set INSTALL_DIR=%ProgramFiles%\%APP_NAME%
    set START_MENU=%ProgramData%\Microsoft\Windows\Start Menu\Programs

    mkdir "%INSTALL_DIR%" 2>nul
    copy /y "%DIST_DIR%\%APP_NAME%.exe" "%INSTALL_DIR%\%APP_NAME%.exe" >nul
    copy /y "..\src\encrypt_bin\gui\resources\icons\icon.ico" "%INSTALL_DIR%\icon.ico" >nul

    powershell -Command ^
        "$s = (New-Object -COM WScript.Shell).CreateShortcut('%START_MENU%\%APP_NAME%.lnk');" ^
        "$s.TargetPath = '%INSTALL_DIR%\%APP_NAME%.exe';" ^
        "$s.IconLocation = '%INSTALL_DIR%\icon.ico';" ^
        "$s.Save()"

    powershell -Command ^
        "$s = (New-Object -COM WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop') + '\%APP_NAME%.lnk');" ^
        "$s.TargetPath = '%INSTALL_DIR%\%APP_NAME%.exe';" ^
        "$s.IconLocation = '%INSTALL_DIR%\icon.ico';" ^
        "$s.Save()"

    echo.
    echo Installed to:     %INSTALL_DIR%\%APP_NAME%.exe
    echo Start Menu entry: %START_MENU%\%APP_NAME%.lnk
    goto done

:local_install
    set INSTALL_DIR=%LOCALAPPDATA%\Programs\%APP_NAME%
    set START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs

    mkdir "%INSTALL_DIR%" 2>nul
    copy /y "%DIST_DIR%\%APP_NAME%.exe" "%INSTALL_DIR%\%APP_NAME%.exe" >nul
    copy /y "..\src\encrypt_bin\gui\resources\icons\icon.ico" "%INSTALL_DIR%\icon.ico" >nul

    powershell -Command ^
        "$s = (New-Object -COM WScript.Shell).CreateShortcut('%START_MENU%\%APP_NAME%.lnk');" ^
        "$s.TargetPath = '%INSTALL_DIR%\%APP_NAME%.exe';" ^
        "$s.IconLocation = '%INSTALL_DIR%\icon.ico';" ^
        "$s.Save()"

    powershell -Command ^
        "$s = (New-Object -COM WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop') + '\%APP_NAME%.lnk');" ^
        "$s.TargetPath = '%INSTALL_DIR%\%APP_NAME%.exe';" ^
        "$s.IconLocation = '%INSTALL_DIR%\icon.ico';" ^
        "$s.Save()"

    echo.
    echo Installed to:     %INSTALL_DIR%\%APP_NAME%.exe
    echo Start Menu entry: %START_MENU%\%APP_NAME%.lnk
    goto done

:done
    echo Desktop shortcut: %USERPROFILE%\Desktop\%APP_NAME%.lnk
    echo.
    pause

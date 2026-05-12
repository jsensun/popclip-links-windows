@echo off
chcp 65001 > nul
title PopClip Links for Windows
cd /d "%~dp0"
echo 正在启动 PopClip Links 工具...
echo.
echo ==========================================
echo   工具已启动！
echo   使用方法：在任何地方选中包含链接的文字
echo ==========================================
echo.
py popclip_links.py
if %errorlevel% neq 0 (
    echo.
    echo 启动失败，请检查是否已安装 Python 3.8 以及 PyQt6, pynput, pyperclip 库。
    pause
)

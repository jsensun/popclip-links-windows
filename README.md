# PopClip Links for Windows

[![Windows](https://img.shields.io/badge/Platform-Windows-blue)]()
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)]()

Select any text containing links, file paths, or search terms — a floating bubble instantly appears for one-click actions.

选中任何包含链接、文件路径或搜索关键词的文字 — 气泡即刻弹出，一键操作。

---

## Features / 功能

| English | 中文 |
|---------|------|
| **Link detection**: select text with URLs → click to open in browser | **链接识别**：选中含链接的文字 → 点击在浏览器中打开 |
| **Path detection**: select absolute/relative/UNC paths → open in Explorer | **路径识别**：选中绝对/相对/UNC 路径 → 在资源管理器中打开 |
| **Text search**: select any text → search via Google/Baidu/Bing/GitHub | **文字搜索**：选中任意文字 → 通过搜索引擎查找 |
| **App exclusion**: prevent triggering in terminals/code editors | **应用排除**：在终端/代码编辑器中不触发，避免干扰 |
| **System tray**: pause, settings, exit from tray menu | **系统托盘**：暂停、设置、退出均从托盘菜单操作 |
| **High DPI support**: works correctly on 4K/retina displays | **高 DPI 支持**：在 4K/视网膜屏上正确定位 |

---

## Downloads / 下载

### Option 1: Standalone EXE (recommended for end users)
[Download latest release](https://github.com/jsensun/popclip-links-windows/releases) — no Python required, just double-click to run.

### Option 2: Run from source (for developers)
```bash
pip install PyQt6 pynput pyperclip
python popclip_links.py
```

---

## Quick Start / 快速上手

1. **Launch** (双击启动)
   - EXE: double-click `PopClipLinks.exe`
   - Source: `python popclip_links.py` or double-click `启动工具.bat`

2. **Select any text** in any application (浏览器、编辑器、聊天工具等)

3. **Bubble appears** with clickable items:
   - 🌐 **Links** → click to open in browser
   - 📁 **Paths** → click to open in Explorer
   - 🔍 **Text** → click to search

4. **Tray icon** (右下角系统托盘):
   - Right-click for menu: Pause / Settings / Exit
   - 右键菜单：暂停监听 / 软件设置 / 退出程序

---

## Settings / 设置

Right-click the tray icon → **Settings** (软件设置...)

| Setting | Description |
|---------|-------------|
| **Enable text search** | Show search bubble for plain text |
| **Enable path detection** | Recognize local file/folder paths |
| **Default search engine** | Google / Baidu / Bing / GitHub |
| **Excluded apps** | Window class names to skip (e.g., terminals) |

### Excluded Apps / 排除应用

By default, the tool skips these window classes to avoid interfering with terminal workflows:

- `ConsoleWindowClass` — cmd / PowerShell
- `CASCADIA_HOSTING_WINDOW_CLASS` — Windows Terminal
- `mintty` — Git Bash / Cygwin
- `VirtualConsoleClass` — ConEmu

You can add more via the Settings dialog. To find a window's class name, use tools like Spy++ or WinSpy.

---

## Project Structure / 项目结构

```
popclip_links.py       — Main application
启动工具.bat           — Quick launcher (Chinese)
popclip.ico            — Application icon
test_links.txt         — Test data
dist/PopClipLinks.exe  — Packaged executable
```

### Architecture / 架构

| Module | Description |
|--------|-------------|
| `SplashScreen` | Startup splash with progress |
| `ConfigManager` | JSON config in `%APPDATA%\PopClipLinks` |
| `SettingsDialog` | GUI for preferences |
| `PopClipBubble` | Floating action bubble widget |
| `PopClipTool` | Main app: clipboard monitor, tray, pynput hooks |

---

## Build from Source / 从源码构建

```bash
# Install dependencies
pip install PyQt6 pynput pyperclip pyinstaller

# Package to single EXE
pyinstaller --onefile --noconsole --icon=popclip.ico --name PopClipLinks popclip_links.py

# Output: dist/PopClipLinks.exe
```

---

## FAQ / 常见问题

**Q: The tool closes my terminal when I select text!**
A: This is now fixed. The tool skips terminal windows by default. If you still have issues, check Settings → Excluded Apps.

**Q: Bubble appears far from my selection on a 4K screen.**
A: Fixed! High-DPI scaling is properly handled now.

**Q: My keyboard doesn't have an Insert key.**
A: The tool auto-falls back to Ctrl+C if Ctrl+Insert doesn't work.

**Q: Antivirus flags the EXE.**
A: This is a false positive common with PyInstaller-packaged apps. The source is fully open for inspection.

---

## License / 许可证

MIT License — free to use, modify, and distribute.

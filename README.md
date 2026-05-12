# PopClip Links for Windows

[![Windows](https://img.shields.io/badge/Platform-Windows-blue)]()
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)]()

## The Problem / 痛点

**EN:** On Windows, working with links or file paths in text is tedious — select, copy, switch to browser/Explorer, paste, press Enter. Repeat dozens of times a day. macOS users have [PopClip](https://popclip.app), which pops up an action bar on text selection, but Windows has no equivalent.

**中文：** 在 Windows 上处理文字中的链接或路径很繁琐——选中、复制、切换到浏览器/资源管理器、粘贴、回车。每天重复几十次。macOS 有 [PopClip](https://popclip.app) 选中即弹窗，但 Windows 一直没有同类工具。

## The Journey / 历程

**EN:** Inspired by PopClip on macOS, I used AI-assisted development to turn the idea into reality. The road was full of pitfalls — DPI issues, shadow artifacts, clipboard races, process detection, and more. But after iterating through all of them, I ended up with a tool I'm genuinely happy with.

**中文：** 受 macOS PopClip 启发，借助 AI 工具把想法直接落地。过程中踩了不少坑——DPI 适配、阴影渲染异常、剪贴板竞态、进程排除检测……一路折腾下来，最终还是搓出来了一个比较满意的作品。

## The Invitation / 邀请

**EN:** This is just a starting point. If you have ideas to make it better, fork it, tweak it, send a PR. Let's build this together.

**中文：** 这只是个起点。如果你有更好的想法，欢迎 fork 改进、提交 PR，咱们一起来让它更完善。

---

## Features / 功能

| English | 中文 |
|---------|------|
| **Link detection** — select text with URLs → click to open in browser | **链接识别** — 选中含链接的文字 → 点击在浏览器中打开 |
| **Path detection** — select absolute/relative/UNC paths → open in Explorer | **路径识别** — 选中绝对/相对/UNC 路径 → 在资源管理器中打开 |
| **Text search** — select any text → search via Google/Baidu/Bing/GitHub | **文字搜索** — 选中任意文字 → 通过搜索引擎查找 |
| **App exclusion** — prevent triggering in terminals/code editors | **应用排除** — 在终端/代码编辑器中不触发，避免干扰 |
| **System tray** — pause, settings, exit from tray menu | **系统托盘** — 暂停、设置、退出均从托盘菜单操作 |
| **High DPI support** — works correctly on 4K/retina displays | **高 DPI 支持** — 在 4K/视网膜屏上正确定位 |

---

## Downloads / 下载

### Standalone EXE（推荐普通用户使用）

[Download latest release](https://github.com/jsensun/popclip-links-windows/releases) — no Python required, just double-click to run.
不需要安装 Python，下载后双击即可运行。

### Run from source（开发者用）

```bash
pip install PyQt6 pynput pyperclip
python popclip_links.py
```

Or double-click `启动工具.bat` / 或双击 `启动工具.bat`

---

## Quick Start / 快速上手

1. **Launch / 启动**
   - EXE: double-click `PopClipLinks.exe` / 双击 `PopClipLinks.exe`
   - Source: `python popclip_links.py` or double-click `启动工具.bat`

2. **Select any text / 选中任意文字** in any application（浏览器、编辑器、聊天工具等）

3. **Bubble appears / 气泡弹出** with clickable items（可点击项目）：
   - 🌐 **Links / 链接** → click to open in browser / 点击在浏览器中打开
   - 📁 **Paths / 路径** → click to open in Explorer / 点击在资源管理器中打开
   - 🔍 **Text / 文字** → click to search / 点击搜索

4. **Tray icon / 系统托盘**（右下角）：
   - Right-click for menu / 右键菜单：**Pause / 暂停监听** | **Settings / 软件设置** | **Exit / 退出程序**

---

## Settings / 设置

Right-click the tray icon → **Settings（软件设置...）**

| Setting / 设置项 | English / Description | 中文说明 |
|------------------|-----------------------|----------|
| **Enable text search** | Show search bubble for plain text | 选中普通文字时弹出搜索按钮 |
| **Enable path detection** | Recognize local file/folder paths | 识别本地文件/文件夹路径 |
| **Default search engine** | Google / Baidu / Bing / GitHub | 默认搜索引擎 |
| **Excluded apps** | Process names to skip (e.g., terminals) | 排除的程序名列表 |

### Excluded Apps / 排除应用

**EN:** By default, the tool skips these processes to avoid interfering with terminal workflows:

**中文：** 默认已排除以下程序，避免干扰终端操作：

| Process / 进程名 | Description / 说明 |
|-------------------|-------------------|
| `opencode.exe` | OpenCode AI terminal |
| `wezterm-gui.exe` | WezTerm terminal |
| `WindowsTerminal.exe` | Windows Terminal |
| `conhost.exe` | Console host (cmd/PowerShell) |
| `mintty.exe` | Git Bash / Cygwin |
| `pwsh.exe` | PowerShell Core |
| `cmd.exe` | Command Prompt |

**EN:** Add more via the Settings dialog — choose from running processes, browse for an `.exe`, or type manually.

**中文：** 在设置对话框可通过三种方式添加：从当前运行的程序中选择、浏览 .exe 文件、或手动输入进程名。

---

## Project Structure / 项目结构

```
popclip_links.py       — Main application / 主程序
启动工具.bat           — Quick launcher / 快速启动脚本
popclip.ico            — Application icon / 程序图标
test_links.txt         — Test data / 测试数据
dist/PopClipLinks.exe  — Packaged executable / 打包好的可执行文件
```

### Architecture / 架构

| Module / 模块 | Description / 说明 |
|----------------|-------------------|
| `SplashScreen` | Startup splash with progress / 启动闪屏 |
| `ConfigManager` | JSON config in `%APPDATA%\PopClipLinks` / 配置文件管理 |
| `SettingsDialog` | GUI for preferences / 设置界面 |
| `PopClipBubble` | Floating action bubble widget / 浮动操作气泡 |
| `PopClipTool` | Main app: clipboard, tray, hooks / 主应用 |

---

## Build from Source / 从源码构建

```bash
# Install dependencies / 安装依赖
pip install PyQt6 pynput pyperclip pyinstaller

# Package to single EXE / 打包为单文件 EXE
pyinstaller --onefile --noconsole --icon=popclip.ico --name PopClipLinks popclip_links.py

# Output / 输出: dist/PopClipLinks.exe
```

---

## FAQ / 常见问题

**Q: The tool closes my terminal / 工具关掉了我的终端！**
A: Fixed. The tool now uses `WM_COPY` instead of `Ctrl+C` keyboard simulation. Terminals won't receive SIGINT anymore. Also, terminals are excluded by default.
A: 已修复。现在使用 `WM_COPY` 消息代替 `Ctrl+C` 键盘模拟，不会再发送中断信号。终端窗口默认也在排除列表中。

**Q: Bubble appears far from my selection / 气泡离选中位置很远**
A: Fixed. High-DPI scaling is properly handled now.
A: 已修复。现在正确处理高 DPI 缩放。

**Q: My keyboard doesn't have Insert key / 没有 Insert 键**
A: Not needed anymore. The tool uses `WM_COPY` message targeting the foreground window, which works in any application.
A: 不再需要。工具通过发送 `WM_COPY` 消息复制选中内容，兼容所有应用。

**Q: Antivirus flags the EXE / 杀毒软件报毒**
A: This is a false positive common with PyInstaller-packaged apps. The source is fully open for inspection.
A: 这是 PyInstaller 打包常见误报，源码完全开放可供审查。

**Q: How do I find a process name / 怎么知道进程名是什么？**
A: Open Task Manager → Details tab, or use the "Select from running processes" button in Settings.
A: 打开任务管理器 → 详细信息选项卡，或者在设置中使用"从运行程序选择"按钮。

---

## License / 许可证

MIT License — free to use, modify, and distribute.
MIT 许可协议 — 可自由使用、修改、分发。

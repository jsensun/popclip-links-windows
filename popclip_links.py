import sys
import re
import time
import threading
import webbrowser
import pyperclip
import os
import json
import subprocess
import ctypes
import traceback
from datetime import datetime
from pynput import mouse, keyboard

LOG_PATH = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'PopClipLinks', 'popclip.log')

def log_msg(msg):
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {msg}\n')
    except: pass

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QHBoxLayout, QFrame, QSystemTrayIcon, QMenu, 
                             QLabel, QCheckBox, QDialog, QComboBox, QProgressBar,
                              QListWidget, QInputDialog, QAbstractItemView, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QColor, QPalette, QFont, QPainter, QPainterPath, QIcon, QAction, QPen, QPixmap

# 增强版识别正则
URL_REGEX = r'((?:https?://|www\.)(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*|(?:\b[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]\.(?:com|net|org|edu|gov|io|me|info|biz|cn|tv|cc|top)\b(?:/[^\s]*)?))'
# 精准本地路径正则：排除 Windows 不允许的字符和换行符，防止提取多个路径时连在一起
PATH_REGEX = r'([a-zA-Z]:\\[^<>:"|?*\r\n]+|[a-zA-Z]:/[^<>:"|?*\r\n]+|\\\\[^\\<>:"|?*\r\n]+\\[^<>:"|?*\r\n]+)'
# 相对路径正则：.\开头、..\开头、~\开头
RELATIVE_PATH_REGEX = r'((?:\.\.?|~)[\\/][^<>:"|?*\r\n]+)'

def clean_url(url):
    while url and not url[-1].isascii():
        url = url[:-1]
    return url.rstrip('.,;:!?)\'"')

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.container = QFrame()
        self.container.setStyleSheet("""
            #container {
                border-radius: 15px;
            }
        """)
        self.container.setObjectName("container")
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(30, 20, 30, 20)
        
        self.label = QLabel("PopClip Links 正在启动...")
        self.label.setStyleSheet("color: white; font-family: 'PingFang SC'; font-size: 14px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #007AFF;
                border-radius: 3px;
            }
        """)
        
        container_layout.addWidget(self.label)
        container_layout.addSpacing(15)
        container_layout.addWidget(self.progress)
        
        layout.addWidget(self.container)
        
        self.setFixedSize(300, 120)
        center = QApplication.primaryScreen().geometry().center()
        self.move(center.x() - self.width() // 2, center.y() - self.height() // 2)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        painter.fillPath(path, QColor(28, 28, 30, 242))

    def set_progress(self, value):
        self.progress.setValue(value)

class ConfigManager:
    SEARCH_ENGINES = {
        "Google": "https://www.google.com/search?q=",
        "Baidu": "https://www.baidu.com/s?wd=",
        "Bing": "https://www.bing.com/search?q=",
        "GitHub": "https://github.com/search?q="
    }
    DEFAULT_CONFIG = {
        "enable_search": True,
        "enable_path": True,
        "search_engine_name": "Google",
        "search_engine": "https://www.google.com/search?q=",
        "opacity": 0.95,
        "auto_hide_ms": 150,
        "font_family": "'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif",
        "font_size": 13,
        "excluded_apps": [
            "opencode.exe",
            "wezterm-gui.exe",
            "WindowsTerminal.exe",
            "conhost.exe",
            "mintty.exe",
            "pwsh.exe",
            "cmd.exe",
        ]
    }
    FILE_PATH = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'PopClipLinks', 'config.json')

    def __init__(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self._ensure_dir()
        self.load()

    def _ensure_dir(self):
        try:
            os.makedirs(os.path.dirname(self.FILE_PATH), exist_ok=True)
        except: pass

    def load(self):
        if os.path.exists(self.FILE_PATH):
            try:
                with open(self.FILE_PATH, 'r', encoding='utf-8') as f:
                    self.config.update(json.load(f))
                excluded = self.config.get("excluded_apps", [])
                if excluded and not any(e.lower().endswith('.exe') for e in excluded):
                    log_msg("Config migration: old class-name exclusion list detected, reset to defaults")
                    self.config["excluded_apps"] = self.DEFAULT_CONFIG["excluded_apps"].copy()
                    self.save()
            except Exception as e:
                log_msg(f"Config load error: {e}")

    def save(self):
        try:
            with open(self.FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            log_msg(f"Config save error: {e}")

class SettingsDialog(QDialog):
    def __init__(self, config_manager):
        super().__init__()
        self.cm = config_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PopClip Links 设置")
        self.setFixedSize(480, 520)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("功能开关："))
        self.cb_search = QCheckBox("开启文字搜索功能")
        self.cb_search.setChecked(self.cm.config["enable_search"])
        self.cb_path = QCheckBox("开启本地路径识别")
        self.cb_path.setChecked(self.cm.config["enable_path"])
        layout.addWidget(self.cb_search)
        layout.addWidget(self.cb_path)
        
        search_layout = QHBoxLayout()
        self.combo_search = QComboBox()
        self.combo_search.addItems(list(ConfigManager.SEARCH_ENGINES.keys()))
        current_name = self.cm.config.get("search_engine_name", "Google")
        self.combo_search.setCurrentText(current_name)
        search_layout.addWidget(QLabel("默认搜索引擎："))
        search_layout.addWidget(self.combo_search)
        layout.addLayout(search_layout)
        
        layout.addSpacing(10)
        layout.addWidget(QLabel("排除以下程序（在这些程序窗口中选中文字时不触发）："))
        
        self.list_excluded = QListWidget()
        self.list_excluded.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        excluded = self.cm.config.get("excluded_apps", [])
        for app in excluded:
            self.list_excluded.addItem(app)
        layout.addWidget(self.list_excluded)
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("+ 手动添加")
        btn_add.clicked.connect(self._add_excluded)
        btn_add.setStyleSheet("QPushButton { background-color: #30D158; color: white; border-radius: 6px; padding: 6px 16px; font-weight: bold; } QPushButton:hover { background-color: #28B84D; }")
        btn_remove = QPushButton("× 移除选中")
        btn_remove.clicked.connect(self._remove_excluded)
        btn_remove.setStyleSheet("QPushButton { background-color: #FF453A; color: white; border-radius: 6px; padding: 6px 16px; font-weight: bold; } QPushButton:hover { background-color: #D6362D; }")
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        layout.addLayout(btn_layout)
        
        btn_layout2 = QHBoxLayout()
        btn_from_processes = QPushButton("从运行程序选择...")
        btn_from_processes.clicked.connect(self._select_from_processes)
        btn_from_processes.setStyleSheet("QPushButton { background-color: #5E5CE6; color: white; border-radius: 6px; padding: 6px 16px; } QPushButton:hover { background-color: #4B49C4; }")
        btn_browse = QPushButton("浏览...")
        btn_browse.clicked.connect(self._browse_exe)
        btn_browse.setStyleSheet("QPushButton { background-color: #5E5CE6; color: white; border-radius: 6px; padding: 6px 16px; } QPushButton:hover { background-color: #4B49C4; }")
        btn_layout2.addWidget(btn_from_processes)
        btn_layout2.addWidget(btn_browse)
        btn_layout2.addStretch()
        layout.addLayout(btn_layout2)
        
        layout.addSpacing(10)
        
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setMinimumHeight(40)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005BB5;
            }
        """)
        layout.addWidget(save_btn)

    def _add_excluded(self):
        text, ok = QInputDialog.getText(self, "添加排除程序", "输入程序名（如 notepad.exe）：")
        if ok and text.strip():
            if self.list_excluded.findItems(text.strip(), Qt.MatchFlag.MatchExactly):
                return
            self.list_excluded.addItem(text.strip().lower())

    def _select_from_processes(self):
        try:
            result = subprocess.run(['tasklist', '/FO', 'CSV', '/NH'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return
            names = set()
            for line in result.stdout.strip().split('\n'):
                if ',' in line:
                    name = line.split(',')[0].strip('"').lower()
                    if name.endswith('.exe'):
                        names.add(name)
            names = sorted(names)
            item, ok = QInputDialog.getItem(self, "选择程序", "从以下列表中选择要排除的程序（可输入筛选）：", names, 0, True)
            if ok and item:
                if self.list_excluded.findItems(item, Qt.MatchFlag.MatchExactly):
                    return
                self.list_excluded.addItem(item.lower())
        except subprocess.TimeoutExpired:
            log_msg("select_from_processes: tasklist timed out")
        except Exception as e:
            log_msg(f"select_from_processes error: {e}")

    def _browse_exe(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择程序", "", "可执行文件 (*.exe)")
        if path:
            name = os.path.basename(path).lower()
            if self.list_excluded.findItems(name, Qt.MatchFlag.MatchExactly):
                return
            self.list_excluded.addItem(name)

    def _remove_excluded(self):
        row = self.list_excluded.currentRow()
        if row >= 0:
            self.list_excluded.takeItem(row)

    def save_settings(self):
        self.cm.config["enable_search"] = self.cb_search.isChecked()
        self.cm.config["enable_path"] = self.cb_path.isChecked()
        
        engine_name = self.combo_search.currentText()
        self.cm.config["search_engine_name"] = engine_name
        self.cm.config["search_engine"] = ConfigManager.SEARCH_ENGINES[engine_name]
        
        excluded = []
        for i in range(self.list_excluded.count()):
            excluded.append(self.list_excluded.item(i).text())
        self.cm.config["excluded_apps"] = excluded
        
        self.cm.save()
        self.accept()

class PopClipBubble(QWidget):
    def __init__(self, content, pos, type='link', config=None):
        super().__init__()
        self.content = content
        self.type = type # 'link', 'path', 'text'
        self.config = config or ConfigManager.DEFAULT_CONFIG
        self.links = []
        self.paths = []
        
        if type == 'link':
            raw_links = re.findall(URL_REGEX, content)
            for l in dict.fromkeys(raw_links):
                l = clean_url(l)
                if l.startswith('www.'): self.links.append('http://' + l)
                elif not l.startswith('http'): self.links.append('http://' + l)
                else: self.links.append(l)
        elif self.type == 'path':
            raw_paths = re.findall(PATH_REGEX, content) + re.findall(RELATIVE_PATH_REGEX, content)
            self.paths = [p.strip() for p in dict.fromkeys(raw_paths) if len(p.strip()) > 3]
        
        self.init_ui(pos)

    def init_ui(self, pos):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool |
                            Qt.WindowType.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        self.setWindowOpacity(0.0)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 10, 20, 10)
        self.main_layout.setSpacing(0)
        
        self.container = QFrame()
        self.container.setObjectName("container")

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(6, 6, 6, 6)
        container_layout.setSpacing(2)

        if self.type == 'link':
            for link in self.links:
                display_text = link.replace('http://', '').replace('https://', '')
                if len(display_text) > 40: display_text = display_text[:37] + "..."
                btn = self.create_button(display_text, lambda checked, l=link: self.open_url(l))
                container_layout.addWidget(btn)
        elif self.type == 'path':
            for path in self.paths:
                # 移除“文件夹：”提示文字，直接显示路径
                display_text = path if len(path) < 45 else "..." + path[-42:]
                btn = self.create_button(display_text, lambda checked, p=path: self.open_local_path(p))
                container_layout.addWidget(btn)
        elif self.type == 'text':
            search_text = self.content if len(self.content) < 25 else self.content[:22] + "..."
            btn = self.create_button(f"搜索: {search_text}", self.open_search)
            container_layout.addWidget(btn)

        self.container.setStyleSheet("""
            #container {
                border-radius: 14px;
            }
        """)
        
        self.main_layout.addWidget(self.container)
        self.adjustSize()
        
        screen_obj = QApplication.screenAt(pos)
        if not screen_obj:
            screen_obj = QApplication.primaryScreen()
        screen = screen_obj.availableGeometry()

        x = pos.x() - self.width() / 2
        y = pos.y() - self.height() - 10

        if y < screen.top() + 10:
            y = pos.y() + 30

        x = max(screen.left() + 10, min(x, screen.right() - self.width() - 10))
        
        self.move(int(x), int(y))
        
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(150)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(self.config['opacity'])
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

    def create_button(self, text, callback):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # 显式设置字体，确保苹方生效
        font = QFont()
        font.setFamily("PingFang SC")
        # 如果系统中没有苹方，回退到微软雅黑
        if not font.exactMatch():
            font.setFamily("Microsoft YaHei")
        font.setPixelSize(self.config['font_size'])
        font.setWeight(QFont.Weight.Medium)
        btn.setFont(font)
        
        btn.clicked.connect(callback)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: #FFFFFF;
                border: none;
                padding: 8px 20px 8px 15px;
                text-align: left;
                border-radius: 8px;
                min-width: 200px;
            }}
            QPushButton:hover {{
                background-color: #007AFF;
                color: white;
            }}
            QPushButton:pressed {{
                background-color: #005BB5;
            }}
        """)
        return btn

    def open_url(self, url):
        webbrowser.open(url)
        self.close()

    def open_local_path(self, path):
        path = path.strip().strip('"').strip("'")
        if path.startswith('~'):
            path = os.path.expanduser(path)
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        path = os.path.normpath(path)
        if os.path.exists(path):
            try:
                subprocess.Popen(f'explorer "{path}"', shell=True)
            except:
                os.startfile(path)
        self.close()

    def open_search(self):
        url = self.config["search_engine"] + self.content
        webbrowser.open(url)
        self.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bg_color = QColor(28, 28, 30, int(self.config['opacity'] * 255))
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 14, 14)
        painter.fillPath(path, bg_color)

class PopClipTool(QApplication):
    show_bubble_signal = pyqtSignal(str, QPoint, str)
    hide_bubble_signal = pyqtSignal()

    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("PopClip Links")
        self.setQuitOnLastWindowClosed(False)
        
        self.splash = SplashScreen()
        self.splash.show()
        
        self.cm = ConfigManager()
        self.bubble = None
        self.is_copying = False
        self.is_paused = False
        self.last_content = ""
        self.last_mouse_pos = QPoint(0, 0)
        self.press_pos = QPoint(0, 0)
        
        self.show_bubble_signal.connect(self.show_bubble)
        self.hide_bubble_signal.connect(self.hide_bubble)
        
        QTimer.singleShot(600, self.finish_startup)

    def finish_startup(self):
        self.setup_tray()
        
        self.mouse_listener = mouse.Listener(on_click=self.on_click, on_scroll=self.on_scroll, on_move=self.on_move)
        self.mouse_listener.daemon = True
        self.mouse_listener.start()
        
        self.kb_listener = keyboard.Listener(on_press=self.on_key_press)
        self.kb_listener.daemon = True
        self.kb_listener.start()
        
        self.fade_splash = QPropertyAnimation(self.splash, b"windowOpacity")
        self.fade_splash.setDuration(400)
        self.fade_splash.setStartValue(1.0)
        self.fade_splash.setEndValue(0.0)
        self.fade_splash.finished.connect(self.splash.close)
        self.fade_splash.start()

    def setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        icon_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'popclip.ico')
        if os.path.exists(icon_path):
            self.tray.setIcon(QIcon(icon_path))
        else:
            self.tray.setIcon(self.style().standardIcon(QApplication.style().StandardPixmap.SP_ComputerIcon))
        
        menu = QMenu()
        
        settings_action = QAction("软件设置...", self)
        settings_action.triggered.connect(self.open_settings)
        
        self.pause_action = QAction("暂停监听", self)
        self.pause_action.setCheckable(True)
        self.pause_action.triggered.connect(self.toggle_pause)
        
        exit_action = QAction("退出程序", self)
        exit_action.triggered.connect(self.quit)
        
        menu.addAction(settings_action)
        menu.addSeparator()
        menu.addAction(self.pause_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        
        self.tray.setContextMenu(menu)
        self.tray.show()
        
        # 启动成功提示
        self.tray.showMessage(
            "PopClip Links 已启动",
            "工具已在后台运行，选中链接或文字即可触发。",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def open_settings(self):
        dialog = SettingsDialog(self.cm)
        dialog.exec()

    def toggle_pause(self):
        self.is_paused = self.pause_action.isChecked()
        if self.is_paused:
            self.hide_bubble()

    def on_move(self, x, y):
        """物理逃逸检测：鼠标远离气泡时自动隐藏"""
        if self.bubble is not None:
            try:
                if self.bubble.isVisible():
                    screen = QApplication.primaryScreen()
                    ratio = screen.devicePixelRatio() if screen else 1.0
                    logical_x = x / ratio
                    logical_y = y / ratio
                    bubble_center = self.bubble.geometry().center()
                    dist = ((logical_x - bubble_center.x())**2 + (logical_y - bubble_center.y())**2)**0.5
                    if dist > 400:
                        self.hide_bubble_signal.emit()
            except Exception as e:
                log_msg(f"on_move error: {e}")

    def on_click(self, x, y, button, pressed):
        if self.is_paused: return
        screen = QApplication.primaryScreen()
        ratio = screen.devicePixelRatio() if screen else 1.0
        pos = QPoint(int(x / ratio), int(y / ratio))
        if button == mouse.Button.left:
            if pressed:
                # 记录鼠标按下的位置
                self.press_pos = pos
            else:
                # 记录鼠标抬起的位置
                self.last_mouse_pos = pos
                
                # 计算拖拽距离 (欧式距离)
                dist = ((pos.x() - self.press_pos.x())**2 + (pos.y() - self.press_pos.y())**2)**0.5
                
                # 关键修复：只有当拖动距离大于 5 像素时，才认为是“选中”操作
                # 这样可以彻底避免点击输入框时干扰 Ctrl+V 粘贴
                if dist > 5:
                    QTimer.singleShot(self.cm.config["auto_hide_ms"], self.check_selection)
                else:
                    # 仅仅是点击，如果当前有气泡，则检查是否需要隐藏
                    if self.bubble is not None:
                        try:
                            if self.bubble.isVisible() and not self.bubble.geometry().contains(pos):
                                self.hide_bubble_signal.emit()
                        except Exception as ex:
                            log_msg(f"on_click bubble check error: {ex}")
                            self.bubble = None

    def on_scroll(self, x, y, dx, dy):
        if self.bubble is not None:
            try:
                if self.bubble.isVisible():
                    self.hide_bubble_signal.emit()
            except: self.bubble = None

    def on_key_press(self, key):
        if self.bubble is not None:
            try:
                if self.bubble.isVisible():
                    self.hide_bubble_signal.emit()
            except: self.bubble = None

    def _is_excluded_app(self):
        try:
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            psapi = ctypes.windll.psapi
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return False
            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if not pid.value:
                return False
            h_process = kernel32.OpenProcess(0x0400 | 0x0010, False, pid.value)
            if not h_process:
                return False
            try:
                buf = ctypes.create_unicode_buffer(260)
                size = ctypes.c_ulong(260)
                if psapi.GetModuleBaseNameW(h_process, None, buf, size):
                    exe_name = buf.value.lower()
                    for entry in self.cm.config.get("excluded_apps", []):
                        if exe_name == entry.lower().strip():
                            return True
                return False
            finally:
                kernel32.CloseHandle(h_process)
        except Exception as e:
            log_msg(f"_is_excluded_app error: {e}")
            return False

    def safe_get_clipboard(self):
        for _ in range(3):
            try:
                return pyperclip.paste()
            except:
                time.sleep(0.05)
        return ""

    def check_selection(self):
        if self.is_copying or self.is_paused: return
        if self._is_excluded_app():
            return
        self.is_copying = True
        
        try:
            self.old_content = self.safe_get_clipboard()
            
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            WM_COPY = 0x0301
            user32.SendMessageW(hwnd, WM_COPY, 0, 0)
            
            QTimer.singleShot(200, self.process_selection)
        except (KeyboardInterrupt, SystemExit):
            self.is_copying = False
            raise
        except Exception as e:
            print(f"Selection trigger error: {e}")
            self.is_copying = False

    def process_selection(self):
        try:
            new_content = self.safe_get_clipboard()
            if not new_content or new_content == self.old_content:
                self.is_copying = False
                return

            if new_content == self.last_content:
                self.is_copying = False
                return

            if self.old_content:
                try: pyperclip.copy(self.old_content)
                except Exception as e:
                    log_msg(f"Clipboard restore error: {e}")

            self.last_content = new_content
            
            if re.findall(URL_REGEX, new_content):
                self.show_bubble_signal.emit(new_content, self.last_mouse_pos, 'link')
            elif self.cm.config["enable_path"] and (re.findall(PATH_REGEX, new_content) or re.findall(RELATIVE_PATH_REGEX, new_content)):
                self.show_bubble_signal.emit(new_content, self.last_mouse_pos, 'path')
            elif self.cm.config["enable_search"] and 0 < len(new_content.strip()) < 500:
                self.show_bubble_signal.emit(new_content.strip(), self.last_mouse_pos, 'text')
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            print(f"Selection processing error: {e}")
        finally:
            self.is_copying = False

    def show_bubble(self, content, pos, type):
        if self.bubble is not None:
            try: self.bubble.close()
            except Exception as e:
                log_msg(f"show_bubble close error: {e}")
            self.bubble = None
            
        self.bubble = PopClipBubble(content, pos, type, self.cm.config)
        self.bubble.show()

    def hide_bubble(self):
        if self.bubble is not None:
            try:
                if self.bubble.isVisible():
                    self.fade_out = QPropertyAnimation(self.bubble, b"windowOpacity")
                    self.fade_out.setDuration(150)
                    self.fade_out.setStartValue(self.cm.config['opacity'])
                    self.fade_out.setEndValue(0.0)
                    self.fade_out.finished.connect(self.bubble.close)
                    self.fade_out.start()
                else:
                    self.bubble.close()
            except Exception as e:
                log_msg(f"hide_bubble error: {e}")
                self.bubble = None

if __name__ == "__main__":
    kernel32 = ctypes.windll.kernel32
    _mutex = kernel32.CreateMutexW(None, False, "PopClipLinks_SingleInstance")
    _err = kernel32.GetLastError()
    if _mutex and _err == 183:
        print("PopClip Links is already running.")
        sys.exit(1)
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    try:
        app = PopClipTool(sys.argv)
        sys.exit(app.exec())
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        log_msg(f"Runtime error: {e}\n{traceback.format_exc()}")
        print(f"Runtime error: {e}")

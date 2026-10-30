import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QStackedWidget, QLabel, QSystemTrayIcon, QMenu
)
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush
from PySide6.QtCore import Qt

from ui.dashboard import Dashboard
from ui.chat_window import ChatWindow
from ui.settings_window import SettingsWindow


class MainWindow(QMainWindow):
    def __init__(self, assistant, config):
        super().__init__()
        self.assistant = assistant
        self.config = config
        self.setWindowTitle("JARVIS — Local AI Desktop Assistant")
        self.resize(1400, 900)
        self.setMinimumSize(1100, 700)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---------------------------------------------------------- sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background: #0a0e1a; color: #8ab4f8;
                border: none; font-size: 14px; padding: 12px;
            }
            QListWidget::item { padding: 14px 10px; border-bottom: 1px solid #1a2333; }
            QListWidget::item:selected { background: #1a2a4a; color: #00e5ff; }
        """)
        for label in [
            "Home", "AI Chat", "Voice Assistant", "System Control",
            "File Assistant", "Internet Search", "Memory",
            "Skills & Plugins", "Settings", "About JARVIS",
        ]:
            self.sidebar.addItem(label)
        self.sidebar.currentRowChanged.connect(self._switch_page)

        # ----------------------------------------------------------- pages
        self.pages = QStackedWidget()
        self.dashboard = Dashboard(assistant, config)
        self.chat = ChatWindow(assistant)
        self.settings = SettingsWindow(assistant, config)

        self.pages.addWidget(self.dashboard)                                    # 0 Home
        self.pages.addWidget(self.chat)                                         # 1 AI Chat
        self.pages.addWidget(QLabel("🎤  Press PUSH TO TALK on the Home page to speak"))  # 2 Voice
        self.pages.addWidget(QLabel("System Control — use chat commands"))      # 3
        self.pages.addWidget(QLabel("File Assistant — use chat commands"))      # 4
        self.pages.addWidget(QLabel("Internet Search — use chat commands"))     # 5
        self.pages.addWidget(QLabel("Memory — managed via chat / settings"))    # 6
        self.pages.addWidget(QLabel("Skills — see settings"))                   # 7
        self.pages.addWidget(self.settings)                                     # 8 Settings
        self.pages.addWidget(QLabel("JARVIS v1.0 — Local-first AI assistant"))  # 9 About

        layout.addWidget(self.sidebar)
        layout.addWidget(self.pages)

        self.sidebar.setCurrentRow(0)

        # ----------------------------------------------------------- tray
        self._setup_tray()

    # --------------------------------------------------------------- helpers
    def _switch_page(self, index: int):
        if 0 <= index < self.pages.count():
            self.pages.setCurrentIndex(index)

    def _build_fallback_icon(self) -> QIcon:
        """Draw a cyan circle so we don't depend on an icon file."""
        pix = QPixmap(64, 64)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QBrush(QColor("#00e5ff")))
        p.setPen(Qt.NoPen)
        p.drawEllipse(8, 8, 48, 48)
        p.end()
        return QIcon(pix)

    def _setup_tray(self):
        icon_path = "assets/icons/jarvis.png"
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            icon = self._build_fallback_icon()

        self.tray = QSystemTrayIcon(icon, self)
        menu = QMenu()
        menu.addAction("Show JARVIS", self.showNormal)
        menu.addAction("Hide", self.hide)
        menu.addSeparator()
        menu.addAction("Quit", self.close)
        self.tray.setContextMenu(menu)
        self.tray.setToolTip("JARVIS — Local AI Assistant")
        self.tray.show()

    def closeEvent(self, event):
        # Cleanly stop the voice stream if it is running
        try:
            if getattr(self.assistant, "voice", None) is not None:
                self.assistant.voice.stop()
        except Exception:
            pass
        super().closeEvent(event)
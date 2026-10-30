import psutil
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont

class Dashboard(QWidget):
    def __init__(self, assistant, config):
        super().__init__()
        self.assistant = assistant
        self.setStyleSheet("background: #060a12;")

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)

        # Header
        title = QLabel("J A R V I S")
        title.setFont(QFont("Segoe UI", 36, QFont.Bold))
        title.setStyleSheet("color: #00e5ff; letter-spacing: 12px;")
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)

        status = QLabel("● SYSTEM ONLINE   |   OFFLINE MODE   |   MIC READY")
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("color: #5f9ea0; font-size: 13px; margin-bottom: 20px;")
        root.addWidget(status)

        # Stats grid
        grid = QGridLayout()
        grid.setSpacing(18)
        self.cpu_label = self._stat_card(grid, 0, 0, "CPU")
        self.ram_label = self._stat_card(grid, 0, 1, "RAM")
        self.battery_label = self._stat_card(grid, 1, 0, "BATTERY")
        self.time_label = self._stat_card(grid, 1, 1, "TIME")
        root.addLayout(grid)

        # Voice button
        self.voice_btn = QPushButton("🎤  PUSH TO TALK")
        self.voice_btn.setFixedHeight(60)
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background: #0a1a33; color: #00e5ff;
                border: 2px solid #00e5ff; border-radius: 30px;
                font-size: 18px; font-weight: bold;
            }
            QPushButton:pressed { background: #00e5ff; color: #060a12; }
        """)
        self.voice_btn.pressed.connect(self.assistant.start_listening)
        self.voice_btn.released.connect(self.assistant.stop_listening)
        root.addWidget(self.voice_btn)
        root.addStretch()

        self.timer = QTimer()
        self.timer.timeout.connect(self._refresh)
        self.timer.start(1000)
        self._refresh()

    def _stat_card(self, layout, row, col, name):
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background: #0b1422; border: 1px solid #1a3050;
                border-radius: 12px; padding: 16px;
            }
        """)
        v = QVBoxLayout(card)
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("color: #5f9ea0; font-size: 11px; letter-spacing: 2px; border: none;")
        value = QLabel("—")
        value.setStyleSheet("color: #e0f7fa; font-size: 26px; font-weight: bold; border: none;")
        v.addWidget(lbl_name)
        v.addWidget(value)
        layout.addWidget(card, row, col)
        return value

    def _refresh(self):
        self.cpu_label.setText(f"{psutil.cpu_percent()}%")
        ram = psutil.virtual_memory()
        self.ram_label.setText(f"{ram.percent}%")
        batt = psutil.sensors_battery()
        self.battery_label.setText(f"{int(batt.percent)}%" if batt else "N/A")
        self.time_label.setText(datetime.now().strftime("%H:%M:%S"))
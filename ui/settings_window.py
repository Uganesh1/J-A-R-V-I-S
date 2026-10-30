from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QCheckBox
)
from PySide6.QtGui import QFont


class SettingsWindow(QWidget):
    def __init__(self, assistant, config):
        super().__init__()
        self.assistant = assistant
        self.config = config
        self.setStyleSheet("background: #060a12; color: #e0f7fa;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)

        title = QLabel("SETTINGS")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #00e5ff; letter-spacing: 4px;")
        layout.addWidget(title)

        layout.addWidget(QLabel("AI Model:"))
        self.model_combo = QComboBox()
        models = self.assistant.ai.models or ["No models detected"]
        self.model_combo.addItems(models)
        current = self.assistant.ai.model
        if current in models:
            self.model_combo.setCurrentText(current)
        self.model_combo.setStyleSheet(
            "background:#0b1422; color:#e0f7fa; padding:6px; border:1px solid #1a3050;"
        )
        layout.addWidget(self.model_combo)

        self.offline_cb = QCheckBox("Offline mode only")
        self.offline_cb.setChecked(self.config.get("privacy.offline_only", True))
        layout.addWidget(self.offline_cb)

        save = QPushButton("SAVE SETTINGS")
        save.setStyleSheet("""
            QPushButton {
                background:#0a1a33; color:#00e5ff;
                border:2px solid #00e5ff; border-radius:8px;
                padding:10px; font-weight:bold; margin-top:20px;
            }
        """)
        save.clicked.connect(self._save)
        layout.addWidget(save)
        layout.addStretch()

        self.status = QLabel("")
        self.status.setStyleSheet("color:#5f9ea0;")
        layout.addWidget(self.status)

    def _save(self):
        model = self.model_combo.currentText()
        if model in self.assistant.ai.models:
            self.assistant.ai.model = model
            self.config.set("ai.model", model)
        self.config.set("privacy.offline_only", self.offline_cb.isChecked())
        self.status.setText("Settings saved.")
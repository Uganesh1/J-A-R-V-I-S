from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton
)


class ChatWindow(QWidget):
    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        self.setStyleSheet("background: #060a12;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.display = QTextEdit()
        self.display.setReadOnly(True)
        self.display.setStyleSheet("""
            QTextEdit {
                background: #0b1422; color: #e0f7fa;
                border: 1px solid #1a3050; border-radius: 12px;
                font-size: 14px; padding: 12px;
            }
        """)
        layout.addWidget(self.display, 1)

        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a command or message…")
        self.input.setStyleSheet("""
            QLineEdit {
                background: #0b1422; color: #e0f7fa;
                border: 1px solid #1a3050; border-radius: 20px;
                padding: 10px 16px; font-size: 14px;
            }
        """)
        self.input.returnPressed.connect(self._send)

        send = QPushButton("SEND")
        send.setFixedWidth(100)
        send.setStyleSheet("""
            QPushButton {
                background: #0a1a33; color: #00e5ff;
                border: 2px solid #00e5ff; border-radius: 20px;
                font-weight: bold; padding: 8px;
            }
            QPushButton:pressed { background: #00e5ff; color: #060a12; }
        """)
        send.clicked.connect(self._send)

        row.addWidget(self.input)
        row.addWidget(send)
        layout.addLayout(row)

        self._append("JARVIS", "Good day. How may I assist you?")

    def _append(self, speaker, text):
        color = "#00e5ff" if speaker == "JARVIS" else "#8ab4f8"
        safe = (text or "").replace("\n", "<br>")
        self.display.append(f'<b style="color:{color};">{speaker}:</b> {safe}<br>')

    def _send(self):
        text = self.input.text().strip()
        if not text:
            return
        self._append("You", text)
        self.input.clear()
        try:
            reply = self.assistant.process_text(text)
        except Exception as e:
            reply = f"[Error] {e}"
        self._append("JARVIS", reply)
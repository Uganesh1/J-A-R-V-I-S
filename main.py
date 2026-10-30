import sys
from PySide6.QtWidgets import QApplication
from utils.logger import setup_logger
from utils.config_manager import ConfigManager
from ui.main_window import MainWindow
from core.assistant import Assistant

def main():
    setup_logger()
    config = ConfigManager()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    assistant = Assistant(config)
    window = MainWindow(assistant, config)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
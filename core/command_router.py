import re
import webbrowser
import psutil
import pyautogui
from automation.app_control import AppController
from automation.file_manager import FileManager
from automation.system_monitor import SystemMonitor

class CommandRouter:
    """Deterministic rule-based engine — always available, no AI required."""

    def __init__(self):
        self.apps = AppController()
        self.files = FileManager()
        self.sys = SystemMonitor()

    def route(self, text: str):
        t = text.lower().strip()

        # System info
        if "ram" in t and ("usage" in t or "using" in t):
            return f"RAM usage is {psutil.virtual_memory().percent} percent."
        if "cpu" in t and ("usage" in t or "using" in t):
            return f"CPU usage is {psutil.cpu_percent()} percent."
        if "battery" in t:
            b = psutil.sensors_battery()
            return f"Battery at {int(b.percent)} percent." if b else "No battery detected."

        # Volume
        m = re.search(r"volume.*?(\d{1,3})", t)
        if m:
            return self.sys.set_volume(int(m.group(1)))

        # Open app
        if t.startswith("open ") and not "http" in t:
            target = text[5:].strip()
            return self.apps.open(target)

        # Open website
        if "open youtube" in t:
            webbrowser.open("https://youtube.com")
            return "Opening YouTube."
        if "open google" in t:
            webbrowser.open("https://google.com")
            return "Opening Google."

        # Folder
        if "open downloads" in t:
            return self.files.open_folder("downloads")

        # Create folder
        m = re.search(r"create (?:a )?folder (?:called )?(.+)", t)
        if m:
            return self.files.create_folder(m.group(1).strip())

        # Screenshot
        if "screenshot" in t:
            path = self.sys.screenshot()
            return f"Screenshot saved to {path}"

        # Lock
        if "lock" in t and "workstation" in t:
            return self.sys.lock()

        # Time
        if "time" in t:
            from datetime import datetime
            return datetime.now().strftime("It is %I:%M %p.")

        return None  # Not a rule-based command → fall through to AI
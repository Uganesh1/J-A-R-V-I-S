import subprocess


class AppController:
    APP_MAP = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "paint": "mspaint.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "edge": "msedge.exe",
        "microsoft edge": "msedge.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",
        "powershell": "powershell.exe",
    }

    def open(self, name):
        key = name.lower().strip()
        exe = self.APP_MAP.get(key, name)
        try:
            subprocess.Popen(exe, shell=True)
            return f"Opening {name}."
        except FileNotFoundError:
            return f"I could not find an application named '{name}'."
        except Exception as e:
            return f"Failed to open {name}: {e}"
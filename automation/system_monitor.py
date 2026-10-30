import os
import psutil
import pyautogui
from datetime import datetime

class SystemMonitor:
    def set_volume(self, level):
        level = max(0, min(100, level))
        try:
            import win32api
            # Use nircmd alternative: PowerShell audio control via COM
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            return f"Volume set to {level} percent."
        except Exception as e:
            return f"Could not set volume: {e}"

    def screenshot(self):
        folder = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"jarvis_{datetime.now():%Y%m%d_%H%M%S}.png")
        pyautogui.screenshot(path)
        return path

    def lock(self):
        import ctypes
        ctypes.windll.user32.LockWorkStation()
        return "Workstation locked."
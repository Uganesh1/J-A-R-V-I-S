import threading
import pyttsx3


class Speaker:
    """Offline text-to-speech using the Windows SAPI5 engine via pyttsx3."""

    def __init__(self, voice_model=None):
        # voice_model kept for signature compatibility with the old Piper code
        self._lock = threading.Lock()
        self.available = False
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", 175)     # words per minute
            self.engine.setProperty("volume", 1.0)   # 0.0 – 1.0
            self.available = True
            self._log_default_voice()
        except Exception as e:
            print(f"[TTS] Engine initialisation failed: {e}")
            self.engine = None
            self.available = False

    # --------------------------------------------------------------- helpers
    def _log_default_voice(self):
        try:
            voices = self.engine.getProperty("voices")
            if voices:
                print(f"[TTS] Default voice: {voices[0].name}")
        except Exception:
            pass

    def list_voices(self):
        """Return a list of (id, name) tuples for available voices."""
        if not self.available:
            return []
        try:
            return [(v.id, v.name) for v in self.engine.getProperty("voices")]
        except Exception:
            return []

    def set_voice(self, voice_id: str):
        if not self.available:
            return
        try:
            self.engine.setProperty("voice", voice_id)
        except Exception as e:
            print(f"[TTS] Could not set voice: {e}")

    def set_rate(self, wpm: int):
        if self.available:
            self.engine.setProperty("rate", max(80, min(300, int(wpm))))

    # ----------------------------------------------------------------- speak
    def speak(self, text: str):
        if not text or not text.strip() or not self.available:
            return
        # pyttsx3 is not thread-safe — serialise calls with a lock.
        with self._lock:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except RuntimeError:
                # The engine occasionally dies after a rapid stop/start.
                # Re-initialise once and retry a single time.
                try:
                    self.engine = pyttsx3.init()
                    self.engine.setProperty("rate", 175)
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"[TTS] Retry failed: {e}")
            except Exception as e:
                print(f"[TTS] Speak failed: {e}")

    def stop(self):
        if not self.available:
            return
        try:
            self.engine.stop()
        except Exception:
            pass
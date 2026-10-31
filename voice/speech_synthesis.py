import threading
import subprocess
import wave
import os
import time

import numpy as np
import sounddevice as sd
import pyttsx3


class Speaker:
    """
    Offline text-to-speech.
      - English  -> pyttsx3 / Windows SAPI5 (original behaviour, unchanged)
      - Tamil    -> Piper standalone exe + ta_IN-rasa_female-medium (female)
                                            ta_IN-ValluvarNeural-medium (male)
    """

    def __init__(self, config=None):
        # config optional for backward compatibility; Assistant passes it in.
        self.config = config
        self._lock = threading.Lock()

        # --- English backend (unchanged) ---
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

        # --- Tamil (Piper) backend ---
        self.piper_exe = self._cfg("voice.piper_exe", os.path.join("piper", "piper.exe"))
        self.piper_model_dir = self._cfg("voice.piper_model_dir", os.path.join("models", "piper"))
        self.language = self._cfg("voice.language", "en")          # "en" or "ta"
        self.tts_gender = self._cfg("voice.tts_gender", "female")  # "male" or "female"
        self.piper_available = os.path.exists(self.piper_exe)

        if self.language == "ta" and not self.piper_available:
            print(f"[TTS] Piper executable not found at {self.piper_exe} — English fallback.")
            self.language = "en"

    # --------------------------------------------------------------- helpers
    def _cfg(self, dotted_key, default):
        if self.config is None:
            return default
        try:
            return self.config.get(dotted_key, default)
        except Exception:
            return default

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

    def set_language(self, lang: str):
        """Switch between 'en' and 'ta' at runtime."""
        if lang in ("en", "ta"):
            self.language = lang

    def set_gender(self, gender: str):
        """Switch Tamil voice between 'male' and 'female'."""
        if gender in ("male", "female"):
            self.tts_gender = gender

    # ----------------------------------------------------------------- speak
    def speak(self, text: str):
        if not text or not text.strip():
            return
        if self.language == "ta" and self.piper_available:
            self._speak_tamil(text)
        elif self.available:
            self._speak_english(text)

    def _speak_english(self, text: str):
        # pyttsx3 is not thread-safe — serialise calls with a lock.
        with self._lock:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except RuntimeError:
                # The engine occasionally dies after a rapid stop/start.
                try:
                    self.engine = pyttsx3.init()
                    self.engine.setProperty("rate", 175)
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"[TTS] Retry failed: {e}")
            except Exception as e:
                print(f"[TTS] Speak failed: {e}")

    def _speak_tamil(self, text: str):
        model_name = (
            "ta_IN-ValluvarNeural-medium"
            if self.tts_gender == "male"
            else "ta_IN-rasa_female-medium"
        )
        model_path = os.path.join(self.piper_model_dir, f"{model_name}.onnx")
        config_path = os.path.join(self.piper_model_dir, f"{model_name}.onnx.json")

        if not os.path.exists(model_path) or not os.path.exists(config_path):
            print(f"[TTS] Tamil model missing: {model_name} — speaking English fallback.")
            if self.available:
                self._speak_english(text)
            return

        os.makedirs("logs", exist_ok=True)
        wav_path = os.path.join("logs", f"tts_ta_{int(time.time() * 1000)}.wav")

        try:
            cmd = [
                self.piper_exe,
                "--model", model_path,
                "--config", config_path,
                "--output_file", wav_path,
            ]
            subprocess.run(
                cmd,
                input=text.encode("utf-8"),
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            with wave.open(wav_path, "rb") as wf:
                frames = wf.readframes(wf.getnframes())
                rate = wf.getframerate()
                audio = np.frombuffer(frames, dtype=np.int16)

            sd.play(audio, rate)
            sd.wait()

        except subprocess.CalledProcessError as e:
            print(f"[TTS] Piper failed (exit {e.returncode}): {e}")
            if self.available:
                self._speak_english(text)
        except Exception as e:
            print(f"[TTS] Tamil speak failed: {e}")
            if self.available:
                self._speak_english(text)
        finally:
            try:
                if os.path.exists(wav_path):
                    os.remove(wav_path)
            except Exception:
                pass

    def stop(self):
        if not self.available:
            return
        try:
            self.engine.stop()
        except Exception:
            pass
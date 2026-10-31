import json
import queue
import threading

import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer

DEFAULT_MODEL_PATH = "models/vosk-model-small-en-us-0.15"


class VoiceInput:
    def __init__(self, assistant, model_path: str = DEFAULT_MODEL_PATH):
        self.assistant = assistant
        self.q: "queue.Queue[bytes]" = queue.Queue()
        self.rec = None
        self.running = False
        self._thread = None
        self.available = False

        # ---- Language routing (from config) ----
        cfg = getattr(assistant, "config", None)
        self.language = "en"
        if cfg is not None:
            try:
                self.language = cfg.get("voice.language", "en")
            except Exception:
                self.language = "en"

        # ---- English: Vosk ----
        self._load_vosk(model_path)

        # ---- Tamil: faster-whisper (lazy) ----
        self._whisper_model = None
        self._whisper_available = False
        self._raw_audio = bytearray()

    # ---------------------------------------------------------------- loading
    def _load_vosk(self, path):
        try:
            model = Model(path)
            self.rec = KaldiRecognizer(model, 16000)
            self.available = True
            print(f"[Voice] Vosk model loaded from {path}")
        except Exception as e:
            self.available = False
            print(f"[Voice] Vosk model NOT loaded: {e}")
            print(f"[Voice] Expected folder: {path}")
            print("[Voice] Download: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")

    def _ensure_whisper(self):
        if self._whisper_model is not None:
            return True
        try:
            from faster_whisper import WhisperModel
            self._whisper_model = WhisperModel(
                "sorika-labs/vaani1-lite-asr-turbo",
                device="cpu",
                compute_type="int8",
            )
            self._whisper_available = True
            print("[Voice] Tamil STT (vaani1-lite-asr-turbo) loaded")
            return True
        except Exception as e:
            print(f"[Voice] Whisper load failed: {e}")
            self._whisper_available = False
            return False

    def _transcribe_tamil(self, pcm_bytes: bytes) -> str:
        if not self._ensure_whisper():
            return ""
        try:
            audio_int16 = np.frombuffer(pcm_bytes, dtype=np.int16)
            audio_float = audio_int16.astype(np.float32) / 32768.0
            segments, info = self._whisper_model.transcribe(
                audio_float, language="ta", vad_filter=True
            )
            text = " ".join(seg.text for seg in segments).strip()
            return text
        except Exception as e:
            print(f"[Voice] Tamil transcription error: {e}")
            return ""

    # --------------------------------------------------------------- helpers
    def _callback(self, indata, frames, time_info, status):
        if status:
            print(f"[Voice] status: {status}")
        self.q.put(bytes(indata))

    def _notify(self, message):
        print(f"[Voice] {message}")
        try:
            self.assistant.speaker.speak(message)
        except Exception:
            pass

    def _handle_text(self, text: str):
        text = text.strip()
        if not text:
            return
        print(f"[Voice] Heard: {text}")
        try:
            # process_text speaks the reply itself (speak=True default)
            self.assistant.process_text(text, speak=True)
        except Exception as e:
            print(f"[Voice] Processing error: {e}")

    # ------------------------------------------------------------------ start
    def start(self):
        if self.language == "ta":
            if not self._ensure_whisper():
                self._notify(
                    "Tamil speech model is not available. "
                    "Please check faster-whisper installation."
                )
                return
        else:
            if not self.available:
                self._notify(
                    "Voice model is not installed. "
                    "Please place the Vosk model folder in the models directory."
                )
                return

        if self.running:
            return
        self.running = True
        self._raw_audio = bytearray()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def _listen_loop(self):
        try:
            with sd.RawInputStream(
                samplerate=16000,
                blocksize=8000,
                dtype="int16",
                channels=1,
                callback=self._callback,
            ):
                while self.running:
                    try:
                        data = self.q.get(timeout=0.1)
                    except queue.Empty:
                        continue

                    if self.language == "ta":
                        # Whisper works on whole utterances → accumulate raw PCM.
                        self._raw_audio.extend(data)
                    else:
                        if self.rec.AcceptWaveform(data):
                            result = json.loads(self.rec.Result())
                            self._handle_text(result.get("text", ""))

                # Flush on stop so short utterances aren't lost
                if self.language == "ta" and len(self._raw_audio) > 0:
                    text = self._transcribe_tamil(bytes(self._raw_audio))
                    self._raw_audio = bytearray()
                    self._handle_text(text)
                elif self.rec is not None:
                    try:
                        final = json.loads(self.rec.FinalResult())
                        self._handle_text(final.get("text", ""))
                    except Exception:
                        pass

        except Exception as e:
            print(f"[Voice] Stream error: {e}")
            self.available = False
        finally:
            # Drain the queue for the next press
            while not self.q.empty():
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    break

    # ------------------------------------------------------------------- stop
    def stop(self):
        self.running = False
        if self._thread is not None:
            self._thread.join(timeout=5)   # Whisper may need a moment
            self._thread = None
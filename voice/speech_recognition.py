import json
import queue
import threading

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
        self._load_model(model_path)

    # ---------------------------------------------------------------- loading
    def _load_model(self, path):
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
        if not self.available:
            self._notify(
                "Voice model is not installed. "
                "Please place the Vosk model folder in the models directory."
            )
            return
        if self.running:
            return
        self.running = True
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
                    if self.rec.AcceptWaveform(data):
                        result = json.loads(self.rec.Result())
                        self._handle_text(result.get("text", ""))

                # Flush any remaining audio so short utterances aren't lost
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
            self._thread.join(timeout=3)
            self._thread = None
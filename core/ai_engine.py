import ollama
import subprocess
import json
import requests

class AIEngine:
    OLLAMA_HOST = "http://localhost:11434"

    def __init__(self, model="llama3.2:1b"):
        self.model = model
        self.available = False
        self.models = []
        self._detect()

    def _detect(self):
        try:
            r = requests.get(f"{self.OLLAMA_HOST}/api/tags", timeout=3)
            if r.status_code == 200:
                self.models = [m["name"] for m in r.json().get("models", [])]
                self.available = len(self.models) > 0
        except Exception:
            self.available = False

    def is_ready(self):
        return self.available and self.model in self.models

    def chat(self, prompt, system=None, history=None):
        if not self.is_ready():
            return None  # Caller falls back to CommandRouter

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        try:
            resp = ollama.chat(model=self.model, messages=messages, stream=False)
            return resp["message"]["content"]
        except Exception as e:
            return f"[AI engine error: {e}]"

    def install_model_instructions(self):
        return (
            "Ollama is not running or the Tamil model is not installed.\n"
            "1. Install Ollama from https://ollama.com\n"
            "2. Open a terminal and run:\n"
            "   ollama pull hf.co/CryptoYogi/vazhi-v7_1-Q4_K_M-GGUF:Q4_K_M\n"
            "3. Restart JARVIS."
        )
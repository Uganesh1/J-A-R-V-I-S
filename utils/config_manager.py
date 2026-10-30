import json
import os

class ConfigManager:
    def __init__(self, path="config/settings.json"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            self._write_defaults()
        with open(path) as f:
            self.data = json.load(f)

    def _write_defaults(self):
        defaults = {
            "ai": {"model": "llama3.2:1b",
                   "system_prompt": "You are JARVIS, a calm, intelligent, concise desktop assistant."},
            "voice": {"wake_word_enabled": False, "push_to_talk": True,
                      "tts_voice": "en_US-lessac-medium"},
            "privacy": {"offline_only": True, "telemetry": False}
        }
        with open(self.path, "w") as f:
            json.dump(defaults, f, indent=2)

    def get(self, dotted_key, default=None):
        keys = dotted_key.split(".")
        val = self.data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def set(self, dotted_key, value):
        keys = dotted_key.split(".")
        target = self.data
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = value
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)
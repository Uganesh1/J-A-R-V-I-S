import logging

from core.command_router import CommandRouter
from core.ai_engine import AIEngine
from core.permission_manager import PermissionManager
from memory.memory_manager import MemoryManager
from voice.speech_synthesis import Speaker

log = logging.getLogger("JARVIS.Assistant")


class Assistant:
    def __init__(self, config):
        self.config = config
        self.router = CommandRouter()
        self.ai = AIEngine(model=config.get("ai.model", "llama3.2:1b"))
        self.permissions = PermissionManager()
        self.memory = MemoryManager()
        self.speaker = Speaker()

        self.voice = None          # lazy-loaded on first push-to-talk press

    # ----------------------------------------------------------- text pipeline
    def process_text(self, text: str, speak: bool = True) -> str:
        # 1. Deterministic command first (fast, always works offline)
        rule_result = self.router.route(text)
        if rule_result:
            self.memory.log_conversation("user", text)
            self.memory.log_conversation("assistant", rule_result)
            if speak:
                self.speaker.speak(rule_result)
            return rule_result

        # 2. Local AI (if Ollama is running and a model is installed)
        if self.ai.is_ready():
            system_prompt = self.config.get(
                "ai.system_prompt",
                "You are JARVIS, a calm, intelligent, concise desktop assistant. "
                "Answer in 1–3 sentences unless asked for detail."
            )
            history = self.memory.get_recent_context(limit=6)
            reply = self.ai.chat(text, system=system_prompt, history=history)
            if reply:
                self.memory.log_conversation("user", text)
                self.memory.log_conversation("assistant", reply)
                if speak:
                    self.speaker.speak(reply)
                return reply

        # 3. Graceful offline fallback
        fallback = (
            "I can handle system commands offline right now. "
            "For open-ended questions, start Ollama and install a model:\n\n"
            + self.ai.install_model_instructions()
        )
        if speak:
            self.speaker.speak(
                "I need a local AI model to answer that. Please check the on-screen message."
            )
        return fallback

    # --------------------------------------------------------- push-to-talk API
    def start_listening(self):
        """Called when the mic button is pressed."""
        try:
            if self.voice is None:
                from voice.speech_recognition import VoiceInput
                self.voice = VoiceInput(self)
            self.voice.start()
        except Exception as e:
            log.exception("Failed to start listening")
            self.speaker.speak(f"Microphone error: {e}")

    def stop_listening(self):
        """Called when the mic button is released."""
        try:
            if self.voice is not None:
                self.voice.stop()
        except Exception as e:
            log.exception("Failed to stop listening")
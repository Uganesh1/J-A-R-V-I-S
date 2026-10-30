# JARVIS — Local-First Desktop AI Assistant

**A fully offline, voice-controlled Windows desktop assistant with local LLM intelligence, offline speech recognition, offline text-to-speech, desktop automation, and persistent memory.**

> Built and tested on: HP 15s, Intel Core i5 11th Gen, 8 GB RAM, Intel Iris Xe, 512 GB SSD, Windows 11, Python 3.11.5  
> No paid APIs. No cloud AI. No subscriptions. No API keys. Everything runs on the machine.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Feature Summary](#2-feature-summary)
3. [Technology Stack (Exact Versions)](#3-technology-stack-exact-versions)
4. [Folder Structure](#4-folder-structure)
5. [File-by-File Reference](#5-file-by-file-reference)
6. [Installation — Step by Step](#6-installation--step-by-step)
7. [Offline Models — Download & Placement](#7-offline-models--download--placement)
8. [Running JARVIS](#8-running-jarvis)
9. [Full Command Reference (What JARVIS Can Do)](#9-full-command-reference-what-jarvis-can-do)
10. [How the Voice Pipeline Works (Technical Deep Dive)](#10-how-the-voice-pipeline-works-technical-deep-dive)
11. [How the AI Pipeline Works](#11-how-the-ai-pipeline-works)
12. [Safety & Permission System](#12-safety--permission-system)
13. [Configuration Reference](#13-configuration-reference)
14. [Testing Checklist](#14-testing-checklist)
15. [Troubleshooting Log (Real Issues & Fixes)](#15-troubleshooting-log-real-issues--fixes)
16. [Female Voice — How to Switch](#16-female-voice--how-to-switch)
17. [Tamil Language — Feasibility Report](#17-tamil-language--feasibility-report)
18. [Performance Notes for 8 GB RAM](#18-performance-notes-for-8-gb-ram)
19. [Future Enhancements](#19-future-enhancements)
20. [Credits & Acknowledgements](#20-credits--acknowledgements)

---

## 1. Project Overview

JARVIS is a **local-first**, **voice-enabled**, **Windows desktop AI assistant** inspired by Iron Man's JARVIS. It is designed from the ground up to:

- **Run 100% offline** for its core features (commands, voice, memory)
- **Use a local large language model** via Ollama, not a cloud API
- **Recognize speech offline** using Vosk
- **Speak offline** using the Windows SAPI5 engine via pyttsx3
- **Automate the desktop** (open apps, create folders, system stats, screenshots)
- **Remember context** across sessions using SQLite
- **Never execute destructive commands** without a permission layer
- **Stay responsive** on an 8 GB RAM laptop with integrated graphics

It is *not* a chatbot wrapper. It is a genuine desktop assistant.

---

## 2. Feature Summary

| Category | Capability | Status |
| --- | --- | --- |
| **UI** | Futuristic dark dashboard with cyan HUD | ✅ Working |
| **UI** | Sidebar navigation (10 pages) | ✅ Working |
| **UI** | Live CPU / RAM / Battery / Clock cards | ✅ Working |
| **UI** | System tray icon + menu | ✅ Working |
| **UI** | Chat interface with styled bubbles | ✅ Working |
| **Voice** | Push-to-talk microphone button | ✅ Working |
| **Voice** | Offline STT (Vosk) | ✅ Working |
| **Voice** | Offline TTS (pyttsx3 / SAPI5) | ✅ Working |
| **AI** | Local LLM via Ollama (`llama3.2:1b`) | ✅ Working |
| **AI** | Conversation context (last 6 turns) | ✅ Working |
| **AI** | Graceful fallback when Ollama offline | ✅ Working |
| **Automation** | Open apps (Notepad, Chrome, Calc, etc.) | ✅ Working |
| **Automation** | Open system folders | ✅ Working |
| **Automation** | Create folders | ✅ Working |
| **Automation** | System stats (CPU, RAM, battery) | ✅ Working |
| **Automation** | Screenshots | ✅ Working |
| **Automation** | Lock workstation | ✅ Working |
| **Automation** | Volume control | ⚠️ Requires `pycaw` (optional) |
| **Memory** | Persistent conversation history (SQLite) | ✅ Working |
| **Memory** | Key-value memories | ✅ Working |
| **Safety** | Permission-gated destructive actions | ✅ Working |
| **Online** | Web search (DuckDuckGo HTML) | ✅ Optional |
| **Online** | Auto-detects offline state | ✅ Working |

---

## 3. Technology Stack (Exact Versions)

| Layer | Library / Tool | Version | Why |
| --- | --- | --- | --- |
| Language | Python | **3.11.5** | All wheels exist; 3.13 fails on NumPy/pyautogui |
| GUI | **PySide6** | 6.8.1 | Qt 6 bindings, native Windows, system tray |
| Local AI Runtime | **Ollama** | latest | Local LLM server, no API key needed |
| Local AI Model | **llama3.2:1b** | Q4_K_M (~1.3 GB) | Smallest usable Llama 3.2, fits 8 GB RAM |
| Speech Recognition | **Vosk** | 0.3.45 | Offline STT, ~50 MB model |
| Vosk Model | **vosk-model-small-en-us-0.15** | ~40 MB | Real-time on i5, ~300 MB RAM |
| Text-to-Speech | **pyttsx3** | 2.90 | Wraps Windows SAPI5, zero setup |
| TTS Voice | **Microsoft David Desktop** | Built-in Windows | Male, clear, offline |
| Wake Word | openwakeword | 0.6.0 | Installed (not enabled by default) |
| Automation | **PyAutoGUI** | 0.9.54 | Screenshots, mouse/keyboard control |
| Automation | **psutil** | 6.1.1 | CPU / RAM / battery / disk stats |
| Automation | **pywin32** | 308 | Windows API access (lock, etc.) |
| Audio | **sounddevice** | 0.5.1 | Microphone stream capture |
| Audio | **numpy** | 2.3.3 | Audio buffer math |
| HTTP | **requests** | 2.32.3 | Ollama API, web search |
| Parsing | **beautifulsoup4** | 4.12.3 | HTML extraction for web search |
| Ollama Client | **ollama** (Python) | 0.4.5 | Thin wrapper on Ollama REST API |
| Database | **sqlite3** | Built-in | Conversation memory |
| Logging | **logging** | Built-in | File + console logs |

### Why Python 3.11 Specifically

- **NumPy 2.3.3** has a `cp311-win_amd64` wheel → no compiler needed
- **PySide6 6.8.1** supports Python 3.11 (but NOT 3.13)
- **pyautogui 0.9.54** has a `py3-none-any` wheel that works on 3.11
- **pywin32 308** ships `cp311-cp311-win_amd64` wheel
- **piper-tts** was dropped in favor of **pyttsx3** because its `piper-phonemize` dep has no Windows wheel at all

---

## 4. Folder Structure

```
D:\Cosmic Author\JARVIS\
│
├── main.py                          # Application entry point
├── requirements.txt                 # Pinned dependency list
├── README.md                        # This file
│
├── config/
│   └── settings.json                # AI model, system prompt, privacy toggles
│
├── models/
│   ├── vosk-model-small-en-us-0.15/ # Folder (STT model)
│   │   ├── am/
│   │   ├── conf/
│   │   ├── graph/
│   │   └── ivector/
│   └── (future: piper .onnx files)
│
├── assets/
│   └── icons/
│       └── jarvis.png               # Optional tray icon (fallback drawn in code)
│
├── core/
│   ├── assistant.py                 # The brain: routes text → command/AI → speaks
│   ├── ai_engine.py                 # Ollama client with health check
│   ├── command_router.py            # Rule-based offline command engine
│   └── permission_manager.py        # Blocks destructive actions by default
│
├── voice/
│   ├── speech_recognition.py        # Vosk + sounddevice push-to-talk loop
│   └── speech_synthesis.py          # pyttsx3 TTS wrapper (thread-safe)
│
├── automation/
│   ├── app_control.py               # App launcher (Notepad, Chrome, etc.)
│   ├── file_manager.py              # Open folders, create folders
│   └── system_monitor.py            # Volume, screenshot, lock
│
├── memory/
│   └── memory_manager.py            # SQLite: conversations + key-value memories
│
├── skills/
│   └── web_search.py                # DuckDuckGo HTML scraper (optional online)
│
├── ui/
│   ├── main_window.py               # Main window + sidebar + tray
│   ├── dashboard.py                 # Home page (HUD + stats + mic button)
│   ├── chat_window.py               # Chat page
│   └── settings_window.py           # Settings page
│
├── utils/
│   ├── logger.py                    # File + console logger
│   ├── config_manager.py            # JSON config reader/writer
│   └── network_checker.py           # is_online() socket check
│
├── logs/
│   └── jarvis_YYYYMMDD.log          # Auto-created daily log
│
├── jarvis_memory.db                 # SQLite database (auto-created)
│
└── jarvis_env_311/                  # Python 3.11 virtual environment
```

---

## 5. File-by-File Reference

| File | Lines | Responsibility |
| --- | --- | --- |
| `main.py` | ~20 | Sets up logger, loads config, creates `Assistant`, launches `MainWindow` |
| `core/assistant.py` | ~80 | Orchestrates: tries router → AI → fallback; manages `start_listening`/`stop_listening` |
| `core/ai_engine.py` | ~60 | Detects Ollama, lists models, sends chat with system prompt + history |
| `core/command_router.py` | ~90 | Regex/string matching for offline commands (RAM, CPU, open X, create folder, etc.) |
| `core/permission_manager.py` | ~30 | Whitelists/blacklists actions; `require()` returns False for restricted ones |
| `voice/speech_recognition.py` | ~120 | Loads Vosk model, opens `sd.RawInputStream`, streams to `KaldiRecognizer`, dispatches text |
| `voice/speech_synthesis.py` | ~50 | Thread-safe pyttsx3 wrapper; retries once on engine failure |
| `automation/app_control.py` | ~30 | Dict of app names → executables; `subprocess.Popen` |
| `automation/file_manager.py` | ~35 | Opens common user folders; creates new folders under Documents |
| `automation/system_monitor.py` | ~35 | Volume (needs `pycaw`), screenshot to `~/Pictures/Screenshots`, lock workstation |
| `memory/memory_manager.py` | ~40 | SQLite tables `conversations` and `memories`; `log_conversation`, `get_recent_context` |
| `skills/web_search.py` | ~30 | DuckDuckGo HTML + BeautifulSoup, returns top 5 titles/snippets |
| `ui/main_window.py` | ~120 | Sidebar + stacked pages + tray; clean close via `closeEvent` |
| `ui/dashboard.py` | ~90 | Cyan title, stat cards, push-to-talk button, `QTimer` refreshing every 1 s |
| `ui/chat_window.py` | ~60 | Read-only `QTextEdit` display + `QLineEdit` input + SEND button |
| `ui/settings_window.py` | ~55 | Model dropdown, offline toggle, save button |
| `utils/logger.py` | ~20 | `setup_logger()` writes to `logs/jarvis_YYYYMMDD.log` |
| `utils/config_manager.py` | ~45 | Nested `get("ai.model")` / `set("ai.model", value)` on JSON |
| `utils/network_checker.py` | ~10 | 2-second TCP connect to `8.8.8.8:53` |

---

## 6. Installation — Step by Step

### Step 6.1 — Verify Python 3.11 Exists

```powershell
py -0
```

Expected output includes `-V:3.11 Python 3.11 (64-bit)`. If not, install from https://www.python.org/downloads/release/python-3119/.

### Step 6.2 — Create the Virtual Environment

```powershell
cd "D:\Cosmic Author\JARVIS"
py -3.11 -m venv jarvis_env_311
.\jarvis_env_311\Scripts\Activate.ps1
```

Your prompt must show `(jarvis_env_311)`.

### Step 6.3 — Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### Step 6.4 — Install Dependencies

`requirements.txt` must contain exactly:

```text
PySide6==6.8.1
ollama==0.4.5
vosk==0.3.45
openwakeword==0.6.0
pyautogui==0.9.54
psutil==6.1.1
pywin32==308
requests==2.32.3
beautifulsoup4==4.12.3
sounddevice==0.5.1
numpy==2.3.3
pyttsx3==2.90
```

Then run:

```powershell
pip install -r requirements.txt
```

### Step 6.5 — Install Ollama (System-Wide)

1. Download `OllamaSetup.exe` from https://ollama.com
2. Run the installer
3. Open a **new** PowerShell window (so PATH updates)
4. Pull the model:

```powershell
ollama pull llama3.2:1b
```

5. Verify:

```powershell
ollama list
```

Expected:

```
NAME           ID              SIZE      MODIFIED
llama3.2:1b    baf6a787fdff    1.3 GB    ...
```

---

## 7. Offline Models — Download & Placement

### 7.1 Vosk STT Model

1. Download: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
2. Extract the ZIP
3. Move the extracted folder into `D:\Cosmic Author\JARVIS\models\`
4. Final path: `models\vosk-model-small-en-us-0.15\`

Verify by listing a file inside:

```powershell
dir "models\vosk-model-small-en-us-0.15"
```

You should see `am`, `conf`, `graph`, `ivector`.

### 7.2 Ollama LLM Model

Already handled in Step 6.5.

### 7.3 (Optional) Piper TTS Model

Not needed for the current build (using pyttsx3). Documented here for the future:

- Model: `en_US-lessac-medium.onnx` + `.onnx.json` from https://huggingface.co/rhasspy/piper-voices
- Place both files in `models\`

---

## 8. Running JARVIS

```powershell
cd "D:\Cosmic Author\JARVIS"
.\jarvis_env_311\Scripts\Activate.ps1
python main.py
```

Expected log lines on startup:

```
[INFO] JARVIS: Logger initialised
[TTS] Default voice: Microsoft David Desktop - English (United States)
[Voice] Vosk model loaded from models/vosk-model-small-en-us-0.15
```

---

## 9. Full Command Reference (What JARVIS Can Do)

### 9.1 System Info (Typed or Spoken)

| Say / Type | Response |
| --- | --- |
| `RAM usage` | "RAM usage is X percent." |
| `how much ram is being used` | Same |
| `CPU usage` | "CPU usage is X percent." |
| `battery` | "Battery at X percent." |
| `time` | "It is 03:45 PM." |

### 9.2 Open Applications

| Say / Type | Action |
| --- | --- |
| `open notepad` | Launches `notepad.exe` |
| `open calculator` or `open calc` | Launches `calc.exe` |
| `open paint` | Launches `mspaint.exe` |
| `open chrome` | Launches `chrome.exe` |
| `open edge` | Launches `msedge.exe` |
| `open word` | Launches `winword.exe` |
| `open excel` | Launches `excel.exe` |
| `open cmd` | Launches `cmd.exe` |
| `open powershell` | Launches `powershell.exe` |
| `open explorer` | Launches Explorer |
| `open <any exe name>` | Tries `shell=True` with the name |

### 9.3 Websites (uses default browser)

| Say / Type | Action |
| --- | --- |
| `open youtube` | Opens `https://youtube.com` |
| `open google` | Opens `https://google.com` |

### 9.4 Folders

| Say / Type | Action |
| --- | --- |
| `open downloads` | Opens `~/Downloads` |
| `open documents` | Opens `~/Documents` |
| `open desktop` | Opens `~/Desktop` |
| `open pictures` | Opens `~/Pictures` |
| `open videos` | Opens `~/Videos` |
| `open music` | Opens `~/Music` |

### 9.5 File Operations

| Say / Type | Action |
| --- | --- |
| `create a folder called <name>` | Creates `~/Documents/<name>` |
| `create folder <name>` | Same |

### 9.6 System Actions

| Say / Type | Action |
| --- | --- |
| `screenshot` | Saves PNG to `~/Pictures/Screenshots/jarvis_<timestamp>.png` |
| `lock workstation` | Locks the PC |
| `set volume to 40 percent` | Sets master volume (needs `pycaw`) |

### 9.7 Open-Ended Questions (Requires Ollama)

Any input that is not a known command goes to the LLM. Examples:

- `hello` → personality greeting
- `what is quantum computing` → 1–3 sentence answer
- `write a haiku about rain` → creative answer
- `explain recursion simply` → educational answer

### 9.8 Fallback Behaviour

If Ollama is **not** running and you ask a non-command question, JARVIS replies:

> "I can handle system commands offline right now. For open-ended questions, start Ollama and install a model:
> 1. Install Ollama from https://ollama.com
> 2. Open a terminal and run: ollama pull llama3.2:1b
> 3. Restart JARVIS."

The app never crashes.

---

## 10. How the Voice Pipeline Works (Technical Deep Dive)

```
[Microphone]
     │  16 kHz, mono, int16
     ▼
sounddevice.RawInputStream(callback=_callback)
     │  each chunk = 8000 bytes (0.25 s)
     ▼
queue.Queue  ────────────────┐
     │                        │
     │  background thread     │
     ▼                        │
KaldiRecognizer.AcceptWaveform(data)
     │
     │  returns True when a full utterance ends
     ▼
json.loads(rec.Result())["text"]
     │
     ▼
Assistant.process_text(text, speak=True)
     │
     ├──► CommandRouter.route()  ──► reply string
     │
     └──► AIEngine.chat()  ──► reply string
     │
     ▼
Speaker.speak(reply)         # pyttsx3 → SAPI5 → speakers
```

**Key properties**

- The `RawInputStream` runs on its own thread, so **the UI never blocks**.
- The `queue.Queue` decouples the audio callback (which must return fast) from the recognition logic.
- Push-to-talk works by calling `VoiceInput.start()` on button press and `VoiceInput.stop()` on release.
- When the button is released, the loop exits and calls `FinalResult()` so short utterances aren't lost.
- If the Vosk folder is missing, `_load_model` sets `available = False` and JARVIS speaks a helpful message instead of crashing.

### Thread Safety for TTS

`pyttsx3`'s engine is **not** thread-safe. It is called from:

1. The UI thread (`process_text` after typed input)
2. The voice thread (after speech recognition)

The fix: `speech_synthesis.py` uses a `threading.Lock` around `engine.say()` + `engine.runAndWait()` and retries once after re-initializing the engine if it dies mid-utterance.

---

## 11. How the AI Pipeline Works

```
Assistant.process_text(text)
     │
     ├── CommandRouter.route(text)
     │       │
     │       └── returns string → done (fast, offline)
     │
     ├── AIEngine.is_ready()
     │       │
     │       ├── GET http://localhost:11434/api/tags
     │       ├── self.models = [names]
     │       └── self.available = len(models) > 0 and model in models
     │
     ├── AIEngine.chat(prompt, system, history)
     │       │
     │       ├── messages = [system] + history[-6:] + [user]
     │       ├── POST /api/chat (stream=False)
     │       └── returns content string
     │
     └── Fallback message with install instructions
```

### Why `stream=False`

- Simpler code path
- Ollama returns after full completion
- For the 1B model, the full reply takes 1–3 seconds on your CPU
- Streaming can be added later by switching to `stream=True` and iterating chunks

### System Prompt

```json
"You are JARVIS, a calm, intelligent, concise desktop assistant. "
"Answer in 1–3 sentences unless asked for detail."
```

Stored in `config/settings.json` under `ai.system_prompt`. Editable without restarting (JARVIS reads it on every request).

---

## 12. Safety & Permission System

The `PermissionManager` class blocks a set of destructive actions unless the user has *explicitly granted* them at runtime:

```python
RESTRICTED = {
    "delete_file", "delete_folder", "install_software",
    "run_script", "modify_system_settings", "send_external"
}
```

**Every automation module must call** `permissions.require(action, details)` **before** touching the filesystem or OS. If it returns `False`, the action is aborted and a message is returned to the user instead.

**Result:** JARVIS will never:

- Delete files autonomously
- Install software autonomously
- Run arbitrary shell commands from the LLM
- Modify system settings autonomously
- Send your data externally without consent

This satisfies the original project rule: *"Never execute arbitrary AI-generated terminal commands directly."*

---

## 13. Configuration Reference

`config/settings.json`:

```json
{
  "ai": {
    "model": "llama3.2:1b",
    "system_prompt": "You are JARVIS, a calm, intelligent, concise desktop assistant. Answer in 1–3 sentences unless asked for detail."
  },
  "voice": {
    "wake_word_enabled": false,
    "push_to_talk": true,
    "tts_voice": "en_US-lessac-medium"
  },
  "privacy": {
    "offline_only": true,
    "telemetry": false
  }
}
```

### Field Reference

| Key | Type | Effect |
| --- | --- | --- |
| `ai.model` | string | Which Ollama model to use |
| `ai.system_prompt` | string | Personality instruction prepended to every LLM call |
| `voice.push_to_talk` | bool | If true, mic button controls recording |
| `voice.wake_word_enabled` | bool | Reserved for openwakeword integration |
| `privacy.offline_only` | bool | If true, disables web search etc. |
| `privacy.telemetry` | bool | Always false; kept for future UI |

### Changing the System Prompt (Live)

Edit `config/settings.json`, save, send another message. No restart needed.

Try: `"You are JARVIS — witty, British, and slightly sarcastic. Keep answers under 2 sentences."`

---

## 14. Testing Checklist

Run through this after installation to verify everything works.

| # | Test | Command / Action | Pass Criteria |
| --- | --- | --- | --- |
| 1 | App launches | `python main.py` | Dashboard appears |
| 2 | Live stats update | Watch for 5 s | CPU/RAM/Battery/Time change |
| 3 | Tray icon exists | Look at system tray | Cyan circle visible |
| 4 | Chat works | Type `open notepad` | Notepad opens, reply in chat |
| 5 | System stat | Type `RAM usage` | Percentage returned |
| 6 | Create folder | Type `create a folder called TestJARVIS` | Folder appears in Documents |
| 7 | LLM works | Type `hello` | AI personality reply |
| 8 | AI fallback | Stop Ollama, type `hello` | Friendly instructions shown, no crash |
| 9 | Voice in | Hold mic, say "open calculator" | Calculator opens |
| 10 | Voice out | Any reply | Reply is spoken aloud |
| 11 | Memory | Type `hello`, restart, type `what did I say` | Context remembered |
| 12 | Offline mode | Disconnect Wi-Fi, repeat tests 4–7 | All still work |
| 13 | Clean shutdown | Close window | No traceback |
| 14 | Log file exists | `dir logs` | `jarvis_YYYYMMDD.log` present |
| 15 | DB exists | `dir jarvis_memory.db` | File present |

---

## 15. Troubleshooting Log (Real Issues & Fixes)

These are the exact issues encountered during the build, with the actual fixes applied.

### 15.1 `NumPy requires GCC >= 8.4` during pip install

**Cause:** Python 3.13 forced pip to compile NumPy from source using MinGW 6.3.0.

**Fix:** Switch to Python 3.11 (`py -3.11 -m venv jarvis_env_311`) and pin `numpy==2.3.3` in `requirements.txt`. Python 3.11 has pre-built wheels.

### 15.2 `ERROR: Could not find a version that satisfies the requirement pyautogui==0.9.54`

**Cause:** Python 3.13 → no wheel available.

**Fix:** Same as 15.1 — use Python 3.11.

### 15.3 `ERROR: No matching distribution found for piper-phonemize~=1.1.0`

**Cause:** Piper's native dependency has no Windows wheel for any Python version.

**Fix:** **Removed `piper-tts` entirely** and switched to `pyttsx3==2.90` (uses native Windows SAPI5). Result: identical functionality, zero compilation.

### 15.4 `ModuleNotFoundError: No module named 'utils.logger'`

**Cause:** `utils/logger.py` was referenced by `main.py` but not provided in the initial code drop.

**Fix:** Provided `utils/logger.py`, `ui/chat_window.py`, `ui/settings_window.py`, `automation/app_control.py`, `automation/file_manager.py`.

### 15.5 `AttributeError: 'Assistant' object has no attribute 'start_listening'`

**Cause:** When replacing `process_text`, the `start_listening` and `stop_listening` methods were accidentally dropped.

**Fix:** Provided a complete replacement `core/assistant.py` that includes all methods.

### 15.6 `IndentationError: expected an indented block after function definition`

**Cause:** Method paste broke indentation.

**Fix:** Provided the **entire file** as a clean drop-in replacement.

### 15.7 `QSystemTrayIcon::setVisible: No Icon set`

**Cause:** `assets/icons/jarvis.png` didn't exist.

**Fix:** `_build_fallback_icon()` draws a cyan circle in memory using `QPainter`. No file required.

### 15.8 `qt.qpa.window: SetProcessDpiAwarenessContext() failed`

**Cause:** Harmless Qt DPI warning on some Windows builds.

**Fix:** Ignored. Does not affect functionality.

---

## 16. Female Voice — How to Switch

Edit `voice/speech_synthesis.py`, in `Speaker.__init__`:

```python
self.engine = pyttsx3.init()
self.engine.setProperty("rate", 175)

for v in self.engine.getProperty("voices"):
    if "zira" in v.name.lower() or "female" in v.name.lower():
        self.engine.setProperty("voice", v.id)
        print(f"[TTS] Using female voice: {v.name}")
        break
```

Restart JARVIS. It will now speak with **Microsoft Zira**.

To list all installed voices:

```powershell
python -c "import pyttsx3; e=pyttsx3.init(); [print(v.id, '|', v.name) for v in e.getProperty('voices')]"
```

---

## 17. Tamil Language — Feasibility Report

| Layer | Supports Tamil? | Notes |
| --- | --- | --- |
| **TTS (Speaking)** | ✅ Yes | Piper has `ta_IN-rasa_female-medium`; requires the standalone Piper executable (Python package failed to install) |
| **STT (Listening)** | ❌ No with Vosk | Vosk has no Tamil model. Alternatives: **Whisper** (offline but heavy) or **Google Speech API** (online) |
| **AI (Understanding)** | ⚠️ Poor with `llama3.2:1b` | Officially supports English, German, French, Italian, Portuguese, Hindi, Spanish, Thai — not Tamil. Alternatives: translate-then-ask layer, or a Tamil-capable model |
| **UI (Display)** | ✅ Yes | PySide6 renders Unicode; label text can be Tamil |

### Recommended Tamil Path

1. **Output:** Use the standalone `piper.exe` with the `ta_IN-rasa_female-medium` model.
2. **Input:** Switch to **Whisper** (`openai-whisper` package, `small` model). Download once, then runs offline. CPU-only on your i5 will be slower but workable.
3. **AI:** Keep the LLM answering in English, then use a small local translation layer (or a bilingual model like Tiny Aya) to bridge.

**Memory impact:** Whisper `small` model ~460 MB on disk, ~1 GB RAM when loaded. Combined with the current stack, you'll approach but not exceed 8 GB — viable.

---

## 18. Performance Notes for 8 GB RAM

| Component | RAM Usage |
| --- | --- |
| PySide6 UI + Python runtime | ~180 MB |
| Vosk small model + recognizer | ~300 MB |
| Ollama server + llama3.2:1b | ~1.5 GB |
| pyttsx3 / SAPI5 | ~30 MB |
| **Total at idle** | **~2 GB** |
| **Peak while listening + LLM replying** | **~3 GB** |

You have ~5 GB free. No swap thrashing, no UI lag.

### Optimizations Used

- **Lazy voice load** — Vosk model is loaded only when the mic button is first pressed.
- **Lazy AI detection** — `AIEngine._detect()` is called once at startup; failure is caught and does not block the app.
- **Single Ollama model loaded** — `stream=False` returns a full response, so Ollama unloads the model after the timeout.
- **Daemon threads** — voice thread is `daemon=True`, so closing the window kills it cleanly.
- **No GPU required** — Ollama auto-detects CPU, no CUDA needed.

### Things to Avoid on 8 GB

- Do **not** switch to `llama3.2:3b` or larger unless you close all other apps
- Do **not** run Whisper `medium` or `large` on this machine
- Do **not** enable `openwakeword` continuously until you've confirmed memory headroom

---

## 19. Future Enhancements

Ordered by ease-of-implementation:

1. **Female voice** — 5-line change (see Section 16)
2. **Custom personality** — edit `config/settings.json`
3. **Persist chat history in UI** — call `mw.chat._append()` from `voice/speech_recognition.py`
4. **Wake word** — use openwakeword pre-trained `hey_jarvis` model (pre-trained download)
5. **Volume control** — `pip install pycaw comtypes` and test
6. **Weather skill** — add `skills/weather.py` using `wttr.in` (free, no API key)
7. **Reminder skill** — add `skills/reminder.py` with SQLite + `threading.Timer`
8. **Notes skill** — add `skills/notes.py` writing to `~/Documents/JARVIS Notes/`
9. **Piper TTS** — use standalone `piper.exe` for higher quality voice
10. **Whisper STT** — for multi-language support including Tamil
11. **Custom wake word** — requires PyTorch + ~2 GB disk for training
12. **Plugin loader** — scan `skills/` for `register()` functions at startup

### Adding a Skill (Template)

```python
# skills/my_skill.py
NAME = "My Skill"
DESCRIPTION = "Does something useful"
PERMISSIONS = []  # any items from PermissionManager.RESTRICTED

def handle(text: str):
    if "trigger phrase" in text.lower():
        return "skill response"
    return None  # not handled
```

Then add `from skills import my_skill` and try `my_skill.handle(text)` in `CommandRouter.route()` before the fallthrough `return None`.

---

## 20. Credits & Acknowledgements

**Built with:**
- **Ganesha & Murugan** — guidance and blessings 🙏
- **Ollama** — Meta's Llama 3.2 team + Ollama community
- **Vosk** — Alpha Cephei
- **PySide6** — Qt Company
- **pyttsx3** — Natesh M. Bhat
- **pyautogui** — Al Sweigart
- **psutil** — Giampaolo Rodola

**Special thanks:**
- The open-source community for making a $0-budget, offline AI assistant genuinely possible in 2026

---

*Document version: 1.0 — Generated after successful local deployment on 2026-10-30*  
*Hardware: HP 15s, Intel Core i5 11th Gen, 8 GB RAM, Windows 11*  
*Python: 3.11.5 | Ollama model: llama3.2:1b | Vosk model: vosk-model-small-en-us-0.15*
import speech_recognition as sr
import threading

# Command mapping: keyword → (status message, text color, state dict)
COMMANDS = [
    (["sunglasses", "sun glasses", "glasses"],     "🕶 Accessory: Sunglasses", "cyan",    {"accessory": "Sunglasses"}),
    (["hat", "cap"],                                "🎩 Accessory: Hat",        "cyan",    {"accessory": "Hat"}),
    (["mask"],                                      "😷 Accessory: Mask",       "cyan",    {"accessory": "Mask"}),
    (["dog", "dog ears"],                           "🐶 Accessory: Dog",        "cyan",    {"accessory": "Dog"}),
    (["cat", "cat ears"],                           "🐱 Accessory: Cat",        "cyan",    {"accessory": "Cat"}),
    (["moustache", "mustache", "stache"],           "🪶 Accessory: Moustache",  "cyan",    {"accessory": "Moustache"}),
    (["snap", "picture", "capture", "photo"],       "📸 Snapping!",             "#00ff88", {"action": "snap"}),
    (["clear", "remove", "none", "reset"],          "✨ Cleared All Filters",   "cyan",    {"accessory": "None", "lipstick": "None", "color_filter": "None", "contouring": False, "smoothing": 0.0}),
    (["lipstick", "lip", "lips", "red lips"],       "💄 Applied Lipstick",      "#f472b6", {"lipstick": "Classic Red"}),
    (["smooth", "beauty", "skin", "beauty mode"],   "✨ Beauty Mode On",        "#f472b6", {"smoothing": 0.6}),
    (["contour", "sculpt", "contouring"],           "🔲 Contouring On",         "#f472b6", {"contouring": True}),
    (["warm", "warm filter", "golden"],             "🌅 Warm Filter On",        "#ff9966", {"color_filter": "Warm"}),
    (["cool", "cold", "cool filter"],               "❄ Cool Filter On",        "#66ccff", {"color_filter": "Cool"}),
    (["vintage", "retro", "sepia"],                 "📷 Vintage Filter On",     "#c9a96e", {"color_filter": "Vintage"}),
    (["no filter", "remove filter", "normal"],      "⬛ Filter Removed",        "white",   {"color_filter": "None"}),
]

class VoiceController:
    def __init__(self, callback):
        self.callback = callback
        # Create recognizer once and keep it alive (not re-instantiated each call)
        self.recognizer = sr.Recognizer()
        # Higher threshold = less noise sensitivity
        self.recognizer.energy_threshold = 300
        # Disable auto-adjustment so threshold stays stable
        self.recognizer.dynamic_energy_threshold = False
        self.is_listening = False

    def _process_command(self, command):
        """Match a recognized command string to an action."""
        for keywords, msg, color, actions in COMMANDS:
            if any(kw in command for kw in keywords):
                return msg, color, actions
        return f'❓ Unknown: "{command}"', "orange", None

    def _listen_once(self):
        """Listen for a single command then stop."""
        self.is_listening = True
        self.callback("🎤 Listening… say a command!", "yellow")

        try:
            with sr.Microphone() as source:
                # Re-calibrate for ambient noise each time for reliability
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                # timeout=8 → wait up to 8s for speech to start
                # phrase_time_limit=5 → max 5s for the command
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=5)

            # Recognize speech
            command = self.recognizer.recognize_google(audio).lower()
            print(f"[Voice] Heard: '{command}'")

            msg, color, actions = self._process_command(command)
            self.callback(msg, color, actions)

        except sr.WaitTimeoutError:
            self.callback("⏱ Timed out — no speech detected", "orange")
        except sr.UnknownValueError:
            self.callback("❌ Couldn't understand — try again", "red")
        except sr.RequestError:
            self.callback("🌐 No internet — speech service unavailable", "red")
        except Exception as e:
            self.callback(f"❌ Voice Error: {e}", "red")
        finally:
            self.is_listening = False

    def listen(self):
        """Public method: called by the Voice Button press. 
        Runs a single-listen session on a background thread."""
        if self.is_listening:
            # Already listening, ignore double press
            self.callback("🎤 Already listening…", "yellow")
            return
        threading.Thread(target=self._listen_once, daemon=True).start()

    def stop(self):
        """Stop flag — used on app close."""
        self.is_listening = False

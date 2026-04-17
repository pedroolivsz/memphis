import pyttsx3
import threading
from .Piper_engine import PiperEngine


class SpeechOutput:
    def __init__(self):
        self._lock = threading.Lock()

        # tenta iniciar Piper
        try:
            self.engine = PiperEngine(
                model_path="models/pt_BR-faber-medium.onnx"
            )
            self.mode = "piper"

        except Exception:
            self.engine = self._init_espeak()
            self.mode = "espeak"

    def _init_espeak(self):
        engine = pyttsx3.init()

        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)

        voices = engine.getProperty("voices")
        pt_voice = next(
            (v for v in voices if "pt" in v.id.lower()),
            None
        )

        if pt_voice:
            engine.setProperty("voice", pt_voice.id)

        return engine

    def speak(self, text: str):
        if not text:
            return

        text = self._preprocess(text)

        with self._lock:
            try:
                if self.mode == "piper":
                    self.engine.speak(text)
                else:
                    self.engine.say(text)
                    self.engine.runAndWait()

            except Exception as e:
                print(f"[ERRO TTS] {e}")

    def _preprocess(self, text: str):
        replacements = {
            "vc": "você",
            "IA": "Inteligência Artificial",
            "API": "A P I"
        }

        for k, v in replacements.items():
            text = text.replace(k, v)

        return text
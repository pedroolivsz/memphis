"""
speech.py — Síntese de voz local com pyttsx3
100% offline, zero custo, funciona no Linux com espeak-ng
"""

import pyttsx3
import threading

class SpeechOutput:
    def __init__(self):
        self.engine = pyttsx3.init()
        self._configure()
        self._lock = threading.Lock()
    
    def _configure(self):
        self.engine.setProperty("rate", 165)
        self.engine.setProperty("volume", 1.0)

        voices = self.engine.getProperty("voices")

        pt_voice = next(
            (v for v in voices if "pt" in v.id.lower() or "brazil" in v.id.lower()),
            None
        )

        if pt_voice:
            self.engine.setProperty("voice", pt_voice.id)
    
    def speak(self, text: str):
        if not text:
            return
        with self._lock:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"[ERRO TTS] {e}")

    def list_voices(self):
        voices = self.engine.getProperty("voices")

        for i, v in enumerate(voices):
            print(f"[{i}] id={v.id} | name={v.name}")
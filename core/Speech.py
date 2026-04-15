"""
speech.py — Síntese de voz local com pyttsx3
100% offline, zero custo, funciona no Linux com espeak-ng
"""

import io
import wave
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
from piper.voice import PiperVoice

class SpeechOutput:
    def __init__(self, model_path: str = "pt_BR-faber-medium.onnx"):
        self._lock = threading.Lock()
        print(f"[TTS] Carregando modelo: {model_path}")
        self.voice = PiperVoice.load(model_path)
        print("[TTS] Modelo pronto.")

    def speak(self, text: str):
        if not text:
            return
        with self._lock:
            try:
                self._synthesize_and_play(text)
            except Exception as e:
                print(f"[ERRO TTS] {e}")

    def speak_async(self, text: str):
        t = threading.Thread(target=self.speak, args=(text,), daemon=True)
        t.start()

    def _synthesize_and_play(self, text: str):
        buf = io.BytesIO()

        with wave.open(buf, "wb") as wav_file:
            self.voice.synthesize(text, wav_file)

        buf.seek(0)

        with wave.open(buf, "rb") as wav_file:
            channels = wav_file.getnchannels()
            samplerate = wav_file.getframerate()
            frames = wav_file.readframes(wav_file.getnframes())
        
        print(f"[DEBUG] channels={channels} rate={samplerate} frames={wav_file.getnframes} bytes={len(frames)}")

        data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

        if channels == 2:
            data = data.reshape(-1, 2)

        print(f"[DEBUG] data.shape={data.shape} data.dtype={data.dtype}")

        sd.play(data, samplerate)
        sd.wait()

"""
voice.py — Captura de áudio e transcrição com Whisper local
Modelo: tiny (leve, ~40MB) ou small (melhor precisão, ~240MB)
Requer: pip install openai-whisper sounddevice soundfile numpy
"""

import tempfile
import numpy as np
import sounddevice as sd
import soundfile as sf
import whisper

SAMPLE_RATE = 16000
DURATION = 6
SILENCE_THREHOLD = 0.01

class VoiceInput:
    def __init__(self, model_size: str = "small"):
        print(f"[M] Carregando whisper ({model_size})...", end=" ", flush=True)
        self.model = whisper.load_model(model_size)
        print("Pronto")
    
    def listen(self) -> str | None:
        # Grava áudio do microfone e retorna a transcrição.
        try:
            print("[M] Gravando... (Fale agora)")
            audio = sd.rec(
                int(DURATION * SAMPLE_RATE),
                samplerate = SAMPLE_RATE,
                channels=1,
                dtype="float32"
            )

            sd.wait()

            # Verifica se há som (evita transcrever silêncio)
            volume = np.abs(audio).mean()

            if(volume < SILENCE_THREHOLD):
                return None
            
            # Salva temporariamente e transcreve
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp:
                sf.write(temp.name, audio, SAMPLE_RATE)
                result = self.model.transcribe(
                    temp.name,
                    language="pt",
                    fp16=False
                )
            text = result.get("text", "").strip()
            return text if text else None
        except Exception as e:
            print(f"[ERRO voz] {e}")
            return None

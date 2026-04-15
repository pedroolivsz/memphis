import subprocess
import threading
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PIPER_PATH = os.path.join(BASE_DIR, "piper")
MODEL_PATH = os.path.join(BASE_DIR, "models", "pt_BR-faber-medium.onnx")

class PiperEngine:
    def __init__(self):
        self._lock = threading.Lock()

    def speak(self, text: str):
        if not text:
            return

        try:
            with self._lock:
                process = subprocess.Popen(
                    [
                        PIPER_PATH,
                        "--model", MODEL_PATH,
                        "--output-raw"
                    ],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE
                )

                audio = process.communicate(input=text.encode())[0]

                # toca áudio usando aplay (Linux)
                play = subprocess.Popen(
                    ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw"],
                    stdin=subprocess.PIPE
                )
                play.communicate(input=audio)

        except Exception as e:
            print(f"[ERRO PIPER] {e}")
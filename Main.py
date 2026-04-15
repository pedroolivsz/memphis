#!/usr/bin/env python3
# Memphis — Assistente de IA pessoal
# Entrada: voz ou texto | Saída: voz + texto
# LM: Groq (gratuito) | STT: Whisper local | TTS: pyttsx3

import sys
import threading
from core.Brain import Brain
from core.Voice import VoiceInput
from core.Speech import SpeechOutput
from core.Memory import Memory

BANNER = """
  ███╗   ███╗███████╗███╗   ███╗██████╗ ██╗  ██╗██╗███████╗
  ████╗ ████║██╔════╝████╗ ████║██╔══██╗██║  ██║██║██╔════╝
  ██╔████╔██║█████╗  ██╔████╔██║██████╔╝███████║██║███████╗
  ██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║██╔═══╝ ██╔══██║██║╚════██║
  ██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║██║     ██║  ██║██║███████║
  ╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝
  Assistente pessoal de IA — modo: voz + texto
  Digite 'sair' ou pressione Ctrl+C para encerrar.
"""

def main():
    print(BANNER)
    
    memory = Memory()
    brain = Brain(memory)
    tts = SpeechOutput("models/pt_BR-faber-medium.onnx")
    voice = VoiceInput()

    tts.speak("Memphis online. Como posso ajudar?")

    while(True):
        try:
            print("\n[M] Pressione enter para falar ou digite sua mensagem: ")
            line = input("> ").strip()

            if line.lower() in ("sair", "exit", "quit"):
                tts.speak("Até logo.")
                break
            
            if not line:
                print("[M] ouvindo...")
                use_input = voice.listen()

                if not use_input:
                    print("[M] Não entendi. Tente novamente.")
                    continue
                print(f"[Você] {use_input}")
            else:
                use_input = line
            
            print("[M] Processando...")
            response = brain.think(use_input)

            print(f"[Memphis] {response}")
            tts.speak(response);
        
        except KeyboardInterrupt:
            print("\n[M] Encerrando...")
            tts.speak("Até logo.")
            break
        except Exception as e:
            print(f"[ERRO] {e}")
 
if __name__ == "__main__":
    main()
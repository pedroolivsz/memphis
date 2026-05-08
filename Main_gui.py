import customtkinter as ctk
import threading

from memphis_core.core.controller.MemphisController import MemphisController

from memphis_core.core.Voice import VoiceInput
from memphis_core.core.Speech import SpeechOutput

class MemphisGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.controller = MemphisController()
        self.voice = VoiceInput()
        self.tts = SpeechOutput()

        self.title("MEMPHIS IA")
        self.geometry("600x400")
        self.attributes("-alpha", 0.9)
        self.configure(fg_color="#0B0B0B")

        self.label_status = ctk.CTkLabel(
            self,
            text="MEMPHIS ONLINE",
            font=("Orbitron", 20),
            text_color="#00D2FF"
        )
        self.label_status.pack(pady=20)

        self.console_input = ctk.CTkTextbox(
            self,
            width=500,
            height=200,
            fg_color="#1A1A1A",
            text_color="#00D2FF"
        )
        self.console_input.pack(pady=10)

        self.entry_input = ctk.CTkEntry(
            self,
            width=400,
            placeholder_text="Digite ou pressione ENTER vazio para usar voz...",
            fg_color="#1A1A1A"
        )
        self.entry_input.pack(pady=10)
        self.entry_input.bind("<Return>", self.process_input_thread)

        self.btn_mic = ctk.CTkButton(
            self,
            text="Falar",
            command=self.start_listening
        )
        self.btn_mic.pack(pady=10)

        self.bind("<Control_L>", lambda e: self.start_listening())

    def update_console(self, text):
        self.after(0, lambda: self._update_console(text))
        
    def _update_console(self, text):
        self.console_input.insert("end", f"\n> {text}")
        self.console_input.see("end")

    def set_status(self, text, color="#00D2FF"):
        self.after(0, lambda: self.label_status.configure(text=text, text_color=color))

    def process_input_thread(self, event=None):
        user_text = self.entry_input.get().strip()
        self.entry_input.delete(0, "end")

        if not user_text:
            self.start_listening()
            return

        threading.Thread(
            target=self.run_logic,
            args=(user_text,),
            daemon=True
        ).start()

    def start_listening(self):
        threading.Thread(
            target=self.listen_microphone,
            daemon=True
        ).start()

    def listen_microphone(self):
        self.set_status("OUVINDO...", "#00FF88")
        self.update_console("[M] Ouvindo...")

        try:
            text = self.voice.listen()

            if not text:
                self.update_console("[M] Não entendi.")
                self.set_status("MEMPHIS ONLINE")
                return
            
            self.update_console(f"Você (voz): {text}")
            self.run_logic(text)
        except Exception as e:
            self.update_console(f"[ERRO] {e}")
        
        self.set_status("MEMPHIS ONLINE")


    def run_logic(self, text):
        self.set_status("Processando...", "yellow")
        self.update_console(f"Você: {text}")

        try:
            response = self.controller.process_text(text)

            self.update_console(f"Memphis: {response}")

            threading.Thread(
                target=self.tts.speak,
                args=(response,),
                daemon=True
            ).start()

        except Exception as e:
            self._update_console(f"[ERRO] {e}")

if __name__ == "__main__":
    app = MemphisGUI()
    app.mainloop()
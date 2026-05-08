from memphis_core.core.Memory import Memory
from memphis_core.core.Brain import Brain
from memphis_core.core.Speech import SpeechOutput
from memphis_core.core.Voice import VoiceInput

class MemphisController:
    def __init__(self):
        self.memory = Memory()
        self.brain = Brain(self.memory)
        self.tts = SpeechOutput()
        self.voice = VoiceInput()

    def process_text(self, text):
        response = self.brain.think(text)
        return response
    
    def process_voice(self):
        text = self.voice.listen()
        if not text:
            return None, "Não entendi."
        
        response = self.brain.think(text)
        self.tts.speak(response)
        return text, response
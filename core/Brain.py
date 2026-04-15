# brain.py — Integração com Groq API (LLM gratuito)
# Modelo padrão: llama-3.3-70b-versatile (rápido e capaz)

import os
from groq import Groq
from core.Memory import Memory
from dotenv import load_dotenv
load_dotenv()

SYSTEM_PROMPT = """Você é Memphis, um assistente pessoal de IA inteligente e direto.
Suas características:
- Respostas concisas mas completas (máximo 3 parágrafos)
- Tom natural, como um assistente pessoal real
- Fala português brasileiro fluente
- Quando não souber algo, admite claramente
- Pode ajudar com código, pesquisa, planejamento, perguntas gerais
Nunca use markdown em respostas faladas — use linguagem natural.
"""

class Brain:
    def __init__(self, memory: Memory):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "Variável GROQ_API_KEY não definida.\n"
                "Crie sua chave gratuita em: https://console.groq.com"
            )
        self.client = Groq(api_key=api_key)
        self.memory = memory
        self.model  = "llama-3.3-70b-versatile"

    def think(self, user_input: str) -> str:
        history = self.memory.get_history()

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=512,
                temperature=0.7,
            )
            reply = response.choices[0].message.content.strip()

            self.memory.add_turn(user_input, reply)

            return reply
        
        except Exception as e:
            return f"Erro ao processar: {e}"
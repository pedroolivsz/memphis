# brain.py — Integração com Groq API (LLM gratuito)
# Modelo padrão: llama-3.3-70b-versatile (rápido e capaz)

import os
import json
from groq import Groq
from core.Memory import Memory
from dotenv import load_dotenv
from modules.Web_search import search, format_for_llm
load_dotenv()

SYSTEM_PROMPT = """Você é Memphis, um assistente pessoal de IA inteligente e direto.
Suas características:
- Respostas concisas mas completas (máximo 3 parágrafos)
- Tom natural, como um assistente pessoal real
- Fala português brasileiro fluente
- Quando não souber algo, admite claramente
- Pode ajudar com código, pesquisa, planejamento, perguntas gerais
- Nunca usa markdown em respostas faladas — use linguagem natural.
- Quando receber resultados de busca na web, sintetiza as informações de forma clara e menciona a fonte qunado relevante

Quando usa a ferramenta de busca:
- Use APENAS o formato de chamada de função fornecido pela API
- NÃO escreva manualmente <function=...>
- NÃO invente formatos
- Apenas retorne a chamada estruturada da ferramenta
- Você pode usar a função buscar_na_web quando precisar de informações atualizadas ou desconhecidas
- Não use a função se conseguir responder com seu próprio conhecimento
- Sempre forneça uma query clara e específica ao usar a função
- Notícias, eventos recentes ou qualquer coisa que mude com o tempo
- Preços, horarios, endereços, informações de produtos
- Perguntas sobre "o que está acontecendo", "qual o resultado de", etc.
- Use apenas quando não tiver certeza se seu conhecimento é atual

Quando não pesquisar:
- Peguntas conceituais ou historicas que você já sabe
- Tarefas de código, matemática, escrita
- Conversa casual
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_na_web",
            "description": (
                "Busca informações atualizadas na internet. "
                "Use apenas quando precisar de dados recentes, notícias, preços, ou "
                "qeventos atuais ou informações que podem ter mudado."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Consulta de busca clara e específica em português. "
                            "Inclua contexto como ano, local ou detalhes relevantes. "
                            "Exemplo: 'jogos de futebol hoje Globo Brasil 2026'"
                        ),
                        "minLength": 3
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            },
        },
    }
]

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

    def _run_tool(self, tool_name: str, tool_args: dict) -> str:
        if tool_name == "buscar_na_web":
            query = tool_args.get("query", "")

            print(f"[Memphis] Buscando na web: '{query}'...")

            results = search(query)
            return format_for_llm(results)
        
        return "Ferramenta desconhecida."

    def think(self, user_input: str) -> str:
        history = self.memory.get_history()

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=512,
                temperature=0.7,
            )

            msg = response.choices[0].message

            if not msg.tool_calls:
                reply = msg.content.strip()
                self.memory.add_turn(user_input, reply)
                return reply
            
            messages.append({
                "role":       "assistant",
                "content":    msg.content or "",
                "tool_calls": [
                    {
                        "id":       tc.id,
                        "type":     "function",
                        "function": {
                            "name":      tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ],
            })

            for tc in msg.tool_calls:
                try:
                    args        = json.loads(tc.function.arguments)
                
                except json.JSONDecodeError:
                    print("[ERRO] Argumentos inválidos: ", tc.function.arguments)
                    continue
                
                tool_result = self._run_tool(tc.function.name, args)
 
                messages.append({
                    "role":         "tool",
                    "tool_call_id": tc.id,
                    "content":      tool_result,
                })

            response2 = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=768,
                temperature=0.7
            )

            reply = response2.choices[0].message.content.strip()
            self.memory.add_turn(user_input, reply)
            return reply
        
        except Exception as e:
            return f"Erro ao processar: {e}"
# brain.py — Integração com Groq API (LLM gratuito)
# Modelo padrão: llama-3.3-70b-versatile (rápido e capaz)

import os
import json
from groq import Groq
from core.Memory import Memory
from dotenv import load_dotenv
from modules.Web_search import search, format_for_llm
from modules.App_control import open_app, open_path, open_terminal_with_command, open_url, close_app, list_running
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

Quando NÃO usar a busca:
- Peguntas conceituais ou historicas que você já sabe
- Tarefas de código, matemática, escrita
- Conversa casual

Quando usar ferramentas de controle de apps:
- "abre o Firefox", "abre o terminal", "abre o VS Code" → abrir_app
- "abre o site X", "vai para youtube.com" → abrir_url
- "abre a pasta Downloads", "abre o arquivo X" → abrir_caminho
- "abre o terminal e roda git status" → abrir_terminal_com_comando
- "fecha o Chrome", "fecha o terminal" → fechar_app
- "quais apps estão abertos", "o que está rodando" → listar_rodando

Se você precisar usar uma ferramenta:
- NÃO escreva texto
- NÃO explique
- NÃO misture resposta com chamada
- Retorne APENAS a chamada da função no formato JSON da API
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
    },
    {
        "type": "function",
        "function": {
            "name": "abrir_app",
            "description": "Abre um aplicativo instalado no sistema. Use para terminal, VS Code, Firefox, Chrome, gerenciador de arquivos, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Nome ou apelido do app. Ex: 'terminal', 'vscode', 'firefox', 'gerenciador de arquivos'.",
                    }
                },
                "required": ["app_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "abrir_url",
            "description": "Abre uma URL no navegador padrão do sistema.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL completa ou domínio. Ex: 'https://github.com' ou 'youtube.com'.",
                    }
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "abrir_caminho",
            "description": "Abre um arquivo ou pasta com o aplicativo padrão do sistema.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Caminho absoluto ou relativo. Ex: '~/Downloads', '/home/user/projeto'.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "abrir_terminal_com_comando",
            "description": "Abre um terminal, opcionalmente já executando um comando shell.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Comando shell a executar. Deixe vazio para só abrir o terminal.",
                        "default": "",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fechar_app",
            "description": "Fecha um aplicativo em execução pelo nome.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Nome do app a fechar. Ex: 'firefox', 'vscode', 'terminal'.",
                    }
                },
                "required": ["app_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_rodando",
            "description": "Lista quais apps monitorados pelo Memphis estão em execução agora.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
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
        
        if tool_name == "abrir_app":
            app = tool_args.get("app_name", "")
            print(f"[Memphis] Abrindo app: '{app}'")
            return open_app(app)
        
        if tool_name == "abrir_url":
            url = tool_args.get("url", "")
            print(f"[Memphis] Abrindo URL: '{url}'")
            return open_url(url)
        
        if tool_name == "abrir_caminho":
            path = tool_args.get("path", "")
            print(f"[Memphis] Abrindo caminho: '{path}'")
            return open_path(path)
        
        if tool_name == "abrir_terminal_com_comando":
            cmd = tool_args.get("command", "")
            print(f"[Memphis] Abrindo terminal" + (f": '{cmd}'" if cmd else "") + "...")
            return open_terminal_with_command(cmd)
 
        if tool_name == "fechar_app":
            app = tool_args.get("app_name", "")
            print(f"[Memphis] Fechando app: '{app}'...")
            return close_app(app)
 
        if tool_name == "listar_rodando":
            return list_running()
        
        return "Ferramenta desconhecida."
    
    def handle_direct_commands(self, user_input: str):
        text = user_input.lower()

        sites = {
            "youtube": "https://www.youtube.com",
            "gmail": "https://mail.google.com",
            "github": "https://github.com",
        }

        for name, url in sites.items():
            if name in text:
                return self._run_tool("abrir_url", {"url": url})
        
        return None

    def think(self, user_input: str) -> str:
        history = self.memory.get_history()

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})

        direct = self.handle_direct_commands(user_input)

        if direct:
            return direct

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=1024,
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
                    args = json.loads(tc.function.arguments)
                
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
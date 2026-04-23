# brain.py — Integração com Groq API (LLM gratuito)
# Modelo padrão: llama-3.3-70b-versatile (rápido e capaz)

import os
import json
from groq import Groq
from memphis_core.core.Memory import Memory
from dotenv import load_dotenv
from memphis_core.modules.Web_search import search, format_for_llm
from memphis_core.modules.App_control import open_app, open_path, open_terminal_with_command, open_url, close_app, list_running
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
- Retorne APENAS JSON válido no formato da API
- Nunca use <function=...>

IMPORTANTE:
- Os nomes dos campos das funções (JSON) devem permanecer EXATAMENTE como definidos
- Nunca traduza nomes de parâmetros (ex: use "command", não "comando")

Se a pergunta exigir dados atualizados:
- Você DEVE usar a ferramenta buscar_na_web
- Nunca responda diretamente nesses casos
"""

def make_tool(name: str, description: str, properties: dict, required: list[str] | None = None) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required or [],
                "additionalProperties": False
            },
        },
    }

def prop(description: str, type: str = "string", required: bool = True) -> dict:
    base = {
        "type": type,
        "description": description,
    }

    if required:
        base["minLength"] = 3

    return base

TOOLS = [
    make_tool(
        name="buscar_na_web",
        description=(
            "Busca informações atualizadas na internet. "
            "Use para notícias, preços, eventos recentes ou qualquer dado que possa ter mudado. "
            "Não use se você já souber a resposta com certeza."
            ),
        properties={
            "query": {
                **prop("Consulta objetiva em português, com contexto relevante."),
                "examples": ["jogos de hoje do Brasileirão 2026"]
            }
        },
        required=["query"],
    ),
    make_tool(
        name="abrir_app",
        description="Abre um aplicativo instalado no sistema. Use para terminal, VS Code, Firefox, Chrome, Brave, gerenciador de arquivos, etc.",
        properties={
            "app_name": prop("Nome ou apelido do app. Ex: 'terminal', 'vscode', 'firefox', 'gerenciador de arquivos'.")
        },
        required=["app_name"],
    ),
    make_tool(
        name="abrir_url",
        description="Abre uma URL no navegador padrão do sistema.",
        properties={
            "url": prop("URL completa ou domínio. Ex: 'https://github.com' ou 'youtube.com'.")
        },
        required=["url"],
    ),
    make_tool(
        name="abrir_caminho",
        description="Abre um arquivo ou pasta com o aplicativo padrão do sistema.",
        properties={
            "path": prop("Caminho absoluto ou relativo. Ex: '~/Downloads', '/home/user/projeto'.")
        },
        required=["path"],
    ),
    make_tool(
        name="abrir_terminal_com_comando",
        description="Abre um terminal, opcionalmente já executando um comando shell.",
        properties={
            "command": prop("Comando shell a executar. Deixe vazio para só abrir o terminal.", required=False)
        },
        required=[],
    ),
    make_tool(
        name="fechar_app",
        description="Fecha um aplicativo em execução pelo nome.",
        properties={
            "app_name": prop("Nome do app a fechar. Ex: 'firefox', 'vscode', 'terminal'.")
        },
        required=["app_name"],
    ),
    make_tool(
        name="listar_rodando",
        description="Lista quais apps monitorados pelo Memphis estão em execução agora.",
        properties={},
        required=[],
    ),
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
    
    def _handle_web_search(self, args):
        query = args.get("query")

        if not query:
            return "Erro: Query não fornecida"
        
        print(f"[Memphis Buscando na web: '{query}'...")
        results = search(query)
        return format_for_llm(results)
    
    def _handle_open_app(self, args):
        app = args.get("app_name", "")

        if not app:
            return "Erro: app_name não fornecido"
        
        print(f"[Memphins] Abrindo app: {app}")
        return open_app(app)
    
    def _handle_open_url(self, args):
        url = args.get("url", "")

        if not url:
            return "Erro: URL não fornecida"
        
        print(f"[Memphis] Abrindo url: {url}")
        return open_url(url)
    
    def _handle_open_path(self, args):
        path = args.get("path", "")

        if not path:
            return "Erro: caminho não fornecido"
        
        print(f"[Memphis] Abrindo caminho: '{path}'")
        return open_path(path)
    
    def _handle_terminal(self, args):
        cmd = args.get("command", "")
        
        print(f"[Memphis] Abrindo terminal" + (f": '{cmd}'" if cmd else "") + "...")
        return open_terminal_with_command(cmd)
    
    def _handle_close_app(self, args):
        app = args.get("app_name", "")
        if not app:
            return "Erro: app_name não fornecido"
        
        print(f"[Memphis] Fechando app: '{app}'...")
        return close_app(app)
    
    def _handle_list_running(self, args):
        return list_running()

    def _run_tool(self, tool_name: str, tool_args: dict) -> str:

        tool_map = {
            "buscar_na_web": self._handle_web_search,
            "abrir_app": self._handle_open_app,
            "abrir_url": self._handle_open_url,
            "abrir_caminho": self._handle_open_path,
            "abrir_terminal_com_comando": self._handle_terminal,
            "fechar_app": self._handle_close_app,
            "listar_rodando": self._handle_list_running
        }
        
        handler = tool_map.get(tool_name)

        if not handler:
            return f"Ferramenta desconhecida: {tool_name}"
        
        try:
            return handler(tool_args)
        except Exception as e:
            return f"Erro ao executar '{tool_name}': {str(e)}"
    
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
        direct = self.handle_direct_commands(user_input)

        if direct:
            self.memory.add_turn(user_input, direct)
            return direct

        history = self.memory.get_history()

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})
        
        base_params = {
            "model": self.model,
            "temperature": 0.7
        }

        try:
            response = self.client.chat.completions.create(
                **base_params,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=1024,
            )

            msg = response.choices[0].message

            if not msg.tool_calls:
                reply = msg.content.strip()
                self.memory.add_turn(user_input, reply)
                return reply
            
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ],
            })

            for tc in msg.tool_calls:
                try:
                    if not tc.function.arguments.strip().startswith("{"):
                        raise ValueError("Formato inválido de argumentos")
                    
                    args = json.loads(tc.function.arguments)
                    tool_result = self._run_tool(tc.function.name, args)
                except json.JSONDecodeError:
                    tool_result = f"[Erro] Argumentos inválidos para '{tc.function.name}': {tc.function.arguments}"
                    print(f"[Memphis] {tool_result}")
                except Exception as e:
                    tool_result = f"[Erro] Falha ao executar '{tc.function.name}': {e}"
                    print(f"[Memphis] {tool_result}")
 
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": tool_result,
                })

            response2 = self.client.chat.completions.create(
                **base_params,
                messages=messages,
                max_tokens=768,
            )

            reply = response2.choices[0].message.content.strip()
            self.memory.add_turn(user_input, reply)
            return reply
        
        except Exception as e:
            msg_error = f"Erro ao processar: {e}"
            err_str = str(e)
            if "tool_use_failed" in err_str or "failed_generation" in err_str:
                print("[Memphis][WARN] Modelo falhou ao chamar tool — convertendo para resposta normal...")

                response = self.client.chat.completions.create(
                    **base_params,
                    messages=messages,
                    max_tokens=1024,
                )
                reply = response.choices[0].message.content.strip()
                return reply
            
            print(f"[Memphis][Erro crítico] {msg_error}")
            return msg_error
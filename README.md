#  Memphis IA

> Assistente pessoal inteligente com voz, memória persistente e controle do sistema — rodando 100% local.

---

![License](https://img.shields.io/badge/License-MIT-green)

---

## Funcionalidades

- **Entrada por voz** — Transcrição local com Whisper (OpenAI)
- **Saída por voz** — Síntese de fala em português via eSpeak / Piper TTS
- **LLM inteligente** — Integrado ao [Groq API](https://console.groq.com) com o modelo `llama-3.3-70b-versatile` (gratuito)
- **Memória persistente** — Histórico de conversas armazenado em SQLite
- **Busca na web** — Pesquisa via DuckDuckGo com scraping leve de conteúdo
- **Controle de apps** — Abre, fecha e gerencia aplicativos Linux via subprocess
- **Interface gráfica** — GUI moderna com CustomTkinter

---

## 🏗️ Arquitetura

```
memphis_core/
├── core/
│   ├── Brain.py          # LLM + tool calling (Groq API)
│   ├── Memory.py         # Memória persistente (SQLite)
│   ├── Speech.py         # Saída de voz (eSpeak / pyttsx3)
│   ├── Voice.py          # Entrada de voz (Whisper)
│   └── controller/
│       └── MemphisController.py  # Orquestra todos os módulos
├── modules/
│   ├── App_control.py    # Controle de aplicativos Linux
│   └── Web_search.py     # Busca via DuckDuckGo
├── data/
│   └── memphis.db        # Banco de dados SQLite (gerado em runtime)
models/
└── pt_BR-faber-medium.onnx  # Modelo de voz Piper (opcional)
gui.py                    # Interface gráfica (CustomTkinter)
```

---

## Instalação

### Pré-requisitos

- Python 3.11+
- Linux (testado em Ubuntu/Debian e derivados)
- `aplay` (pacote `alsa-utils`) para reprodução de áudio com Piper

### 1. Clone o repositório

```bash
git clone https://github.com/pedroolivsz/memphis.git
cd memphis
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure a chave da API

Crie um arquivo `.env` na raiz do projeto:

```env
GROQ_API_KEY=sua_chave_aqui
```

> Obtenha sua chave gratuitamente em [console.groq.com](https://console.groq.com).

### 5. (Opcional) Configure o Piper TTS

Para uma voz em português mais natural, baixe o binário do [Piper](https://github.com/rhasspy/piper/releases) e o modelo de voz:

```bash
# Coloque o binário na raiz:
./piper

# Coloque o modelo em:
models/pt_BR-faber-medium.onnx
```

Sem o Piper, o Memphis usará o eSpeak automaticamente como fallback.

---

## Como usar

### Interface gráfica

```bash
python gui.py
```

### Linha de comando (modo texto)

```python
from memphis_core.core.controller.MemphisController import MemphisController

memphis = MemphisController()
resposta = memphis.process_text("Qual a previsão do tempo para hoje?")
print(resposta)
```

### Modo voz

```python
texto, resposta = memphis.process_voice()
```

---

## Ferramentas disponíveis (Tool Calling)

O Memphis usa *function calling* nativo da API para acionar ferramentas automaticamente com base no contexto da conversa:

| Ferramenta | Descrição |
|---|---|
| `buscar_na_web` | Pesquisa no DuckDuckGo com scraping de conteúdo |
| `abrir_app` | Abre aplicativos (Firefox, VS Code, terminal, etc.) |
| `abrir_url` | Abre uma URL no navegador padrão |
| `abrir_caminho` | Abre arquivo ou pasta com app padrão do sistema |
| `abrir_terminal_com_comando` | Abre terminal, opcionalmente executando um comando |
| `fechar_app` | Fecha um aplicativo em execução |
| `listar_rodando` | Lista apps monitorados que estão em execução |

---

## Exemplos de uso

```
Você: Quais são as notícias de hoje?
Memphis: [busca na web e resume os resultados]

Você: Abre o VS Code
Memphis: VS Code aberto com sucesso.

Você: Abre o terminal e roda git status
Memphis: Terminal aberto executando: git status

Você: Fecha o Firefox
Memphis: Aplicativo 'firefox' fechado.

Você: O que está rodando?
Memphis: Rodando agora: terminal, VS Code
```

---

## Configuração avançada

| Parâmetro | Local | Padrão | Descrição |
|---|---|---|---|
| `MAX_HISTORY` | `Memory.py` | `20` | Turnos de histórico enviados ao LLM |
| `model` | `Brain.py` | `llama-3.3-70b-versatile` | Modelo Groq utilizado |
| `model_size` | `Voice.py` | `base` | Modelo Whisper (`tiny`, `small`, `medium`) |
| `DURATION` | `Voice.py` | `6` | Duração da gravação em segundos |
| `MAX_RESULT` | `Web_search.py` | `5` | Número de resultados de busca |

---

## 📦 Dependências principais

```
groq
openai-whisper
sounddevice
soundfile
pyttsx3
customtkinter
duckduckgo-search
python-dotenv
numpy
```

---

## 📄 Licença

Distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

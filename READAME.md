# Memphis 🧠
 
Assistente pessoal de IA inspirado no JARVIS — **100% gratuito**.
 
## Stack
 
| Componente | Tecnologia | Custo |
|---|---|---|
| LLM | Groq API (Llama 3.3 70B) | Gratuito |
| Voz → Texto | Whisper `small` (local) | Gratuito |
| Texto → Voz | pyttsx3 + espeak-ng (local) | Gratuito |
| Memória | SQLite local | Gratuito |
 
---
 
## Setup (Linux)
 
### 1. Dependências do sistema
 
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv espeak-ng libespeak-ng-dev portaudio19-dev ffmpeg
```
 
### 2. Ambiente virtual Python
 
```bash
cd memphis
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
 
### 3. Chave Groq (gratuita)
 
1. Acesse https://console.groq.com e crie uma conta
2. Gere uma API Key
3. Configure a variável de ambiente:
 
```bash
cp .env.example .env
# Edite o .env e cole sua chave
nano .env
```
 
Ou exporte diretamente no terminal:
 
```bash
export GROQ_API_KEY="sua_chave_aqui"
```
 
### 4. Rodar
 
```bash
source .venv/bin/activate
python main.py
```
 
---
 
## Como usar
 
- **Pressione Enter** sem digitar nada → Memphis ouve pelo microfone (6 segundos)
- **Digite sua mensagem** → Memphis responde em texto e voz
- **`sair`** ou **Ctrl+C** → encerra o programa
 
---
 
## Estrutura do projeto
 
```
memphis/
├── main.py              # Ponto de entrada
├── requirements.txt
├── .env.example
├── core/
│   ├── brain.py         # LLM via Groq
│   ├── voice.py         # STT com Whisper
│   ├── speech.py        # TTS com pyttsx3
│   └── memory.py        # Memória SQLite
├── modules/             # Futuras habilidades (busca web, apps, etc.)
└── data/
    └── memphis.db       # Histórico de conversas (gerado automaticamente)
```
 
---
 
## Próximos passos
 
- [ ] **Módulo de busca web** — DuckDuckGo API (gratuita)
- [ ] **Controle de apps** — abrir terminal, browser, música
- [ ] **Wake word** — activar por voz sem precisar pressionar Enter
- [ ] **Interface web** — dashboard leve em Flask
 
---
 
## Solução de problemas
 
**Erro de microfone:**
```bash
# Lista dispositivos de áudio disponíveis
python3 -c "import sounddevice; print(sounddevice.query_devices())"
```
 
**Whisper lento:**
Troque `model_size="small"` por `"tiny"` em `core/voice.py` para maior velocidade (menos precisão).
 
**TTS sem voz em português:**
```bash
sudo apt install -y espeak-ng-data
# Testa a voz:
espeak-ng -v pt-br "Memphis online"
```
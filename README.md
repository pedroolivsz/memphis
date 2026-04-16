# Memphis 
 
Assistente pessoal de IA inspirado no JARVIS — **offline-first com capacidade de busca online em tempo real**.

---

## Inteligência de decisão

O Memphis não apenas responde perguntas — ele decide como responder:

- Usa conhecimento próprio quando suficiente
- Realiza buscas na web quando necessário
- Combina múltiplas fontes para gerar respostas

Isso permite respostas mais precisas e atualizadas.
 
## Stack
 
| Componente | Tecnologia | Custo |
|---|---|---|
| LLM | Groq API (Llama 3.3 70B) | Gratuito |
| Texto → Voz | Piper TTS (neural, offline) + fallback espeak | Gratuito |
| Texto → Voz | pyttsx3 + espeak-ng (local) | Gratuito |
| Memória | SQLite local | Gratuito |
| Busca Web | DuckDuckGo (sem API) + scraping leve | Gratuito |
 
---

## Destaques

- IA com Llama 3.3 70B (via Groq)
- Reconhecimento de voz local com Whisper
- Voz neural offline com Piper (alta qualidade)
- Fallback automático de voz (robustez)
- Memória persistente com SQLite
- Busca inteligente na web em tempo real (sem API paga)
- Capacidade de decidir quando pesquisar ou responder com conhecimento próprio
- Extração automática de conteúdo de páginas (não só links)

---

## Módulo de Busca Web

O Memphis possui um sistema integrado de busca na web totalmente gratuito, utilizando DuckDuckGo sem necessidade de API.

### Funcionalidades

- Busca automática quando necessário (decisão feita pela IA)
- Extração de conteúdo relevante das páginas
- Síntese inteligente dos resultados
- Sem dependência de serviços pagos

### Como funciona

1. O Memphis detecta quando precisa de informação atualizada
2. Executa uma busca usando DuckDuckGo
3. Extrai conteúdo das páginas encontradas
4. Sintetiza a resposta para o usuário

### Exemplo de uso

Usuário: Passou algum jogo na Globo hoje?
Memphis: (busca automaticamente e responde com base nos resultados)

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

### 4. Instalar Piper (voz neural offline)

Baixe o binário:

```bash
wget https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz
tar -xvf piper_linux_x86_64.tar.gz
mv piper memphis/
chmod +x piper
 
### 5. Rodar
 
bash
source .venv/bin/activate
python main.py
 
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
│   ├── piper_engine.py  # TTS neural
│   └── memory.py        # Memória SQLite
├── models/
│   └── pt_BR-faber-medium.onnx
├── modules/
│   └── web_search.py   # Busca na web (DuckDuckGo    scraping)
└── data/
│    └── memphis.db       # Histórico de conversas (gerado automaticamente)
```

```

---

## Ferramentas disponíveis

O Memphis utiliza um sistema de ferramentas integradas que podem ser acionadas automaticamente pela IA.

### Atualmente disponíveis:

- `buscar_na_web` → pesquisa informações atualizadas na internet

A IA decide automaticamente quando utilizar cada ferramenta.

---
 
## Próximos passos
 
- [ ] Controle de apps — abrir terminal, browser, música
- [ ] Wake word — activar por voz sem precisar pressionar Enter
- [ ] Interface web — dashboard leve em Flask
- [ ] Cache de buscas para reduzir latência
- [ ] Busca semântica (melhor relevância)
- [ ] Suporte a múltiplas ferramentas (automação local)
 
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

**Erro: Piper não encontrado**
```bash
chmod +x piper
```

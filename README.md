# Desafio FURIA Chat - CS2 Fan Assistant

Este é o **FURIA_CS**, uma landing com espaço para chat interativo em tempo real inspirado na organização brasileira de esports FURIA, focado em Counter-Strike (CS2). Ele mostra partidas, elenco e permite conversas ao estilo "torcida organizada".

---

## ✨ Funcionalidades

- 🔧 Interface web em Flask com Socket.IO (chat em tempo real)
- 🔥 Armazenar e autenticar usuários com Firebase.
- 🎯 Scraper automatizado que coleta:
  - Elenco atual
  - Partidas recentes
  - Partidas futuras e ao vivo
- 🧠 Integração com modelos LLM via OpenRouter (usando `openai` SDK)
- 🤖 IA com comportamento customizado com "personalidade FURIA"

---
## ⚙️ Configuração
- Pré-requisitos:
  - Python 3.10+
  - Conta no Firebase
  - Chave API do OpenRouter (opcional)

---

## 🚀 Como Rodar o Projeto

### 1. Clone o repositório

```bash
git clone https://github.com/LadonGx/Chatbot-Furia
cd furia-chatbot
```

### 2. Crie e ative um ambiente virtual (Opcional)

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate    # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure variáveis de ambiente (Não obrigatório para o funcionamento do código, apenas do chatbot)

Crie um arquivo `.env` baseado no `.env.example` com:

```
OPENROUTER_API_KEY=sua_chave_openrouter
SECRET_KEY=sua_chave_openrouter
FIREBASE_API_KEY=sua-chave-aqui
FIREBASE_AUTH_DOMAIN=sua-chave-aqui
FIREBASE_PROJECT_ID=sua-chave-aqui
FIREBASE_STORAGE_BUCKET=sua-chave-aqui
FIREBASE_MESSAGING_SENDER_ID=sua-chave-aqui
FIREBASE_APP_ID=sua-chave-aqui
FIREBASE_MEASUREMENT_ID=sua-chave-aqui
FIREBASE_CREDENTIALS_PATH=sua-chave-aqui
```
> 🔑 Obtenha a chave em https://openrouter.ai
> 🤖 O modelo utilizado no projeto foi "deepseek/deepseek-chat-v3-0324:free"
> 🔥 Crie a conta do firebase em https://firebase.google.com
---

### 5. Execute o scraper (opcional para atualizar os dados da FURIA)

```bash
python scraper/furia_scraper.py
```

---

### 6. Inicie o servidor Flask

```bash
python main.py
```

Acesse:

- Página inicial: http://localhost:5000
- Chat: http://localhost:5000/chat

---

## 🧠 Como Usar o Chat

Digite no campo de mensagem:

```
@FuriaBot quem é o IGL?
@FuriaBot quando é o próximo jogo?
@FuriaBot qual foi o último jogo?
```

---

## 🛠 Tecnologias

- Python 3.x
- Flask + Flask-SocketIO
- Firebase
- BeautifulSoup + Cloudscraper (Web Scraping)
- OpenAI SDK via OpenRouter
- HTML/CSS/JS

---


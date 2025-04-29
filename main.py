from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO
from openai import OpenAI
from dotenv import load_dotenv
import json
import os

load_dotenv()
historico_conversa = {}

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
socketio = SocketIO(app, cors_allowed_origins="*")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def carregar_dados_furia():
    caminho_json = os.path.join(os.path.dirname(__file__), 'scraper', 'data', 'furia.json')
    
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        return dados
    except FileNotFoundError:
        print(f"Arquivo {caminho_json} não encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao carregar furia.json: {str(e)}")
        return None

dados_furia = carregar_dados_furia()

if dados_furia:
    elenco = ", ".join([player['nome'] for player in dados_furia.get('elenco', [])])
    ranking = dados_furia.get('ranking', 'Ranking desconhecido')
    partidas = dados_furia.get('partidas_recentes')
    
    system_context = f"""
    Você é o FURIA_BOT, assistente virtual oficial da FURIA Esports (Counter-Strike).
    Seu tom deve ser energético, competitivo e cheio de atitude, refletindo o espírito da FURIA.

    Regras importantes:
    - Mantenha respostas curtas e impactantes quando possível
    - Use gírias de CS:GO quando apropriado (ex: "clutch", "ace", "entry")
    - Mostre paixão pelo time e pelo jogo
    - Não use muitos emojis (máximo 1 por resposta)

    Informações do time:
    - Elenco atual: {elenco}
    - Ranking atual: {ranking}
    - Historico: {partidas}
    - Estilo de jogo: Agressivo, inovador, "FURIA style"

    Responda como um verdadeiro fã da FURIA, com a energia que representa a torcida #DIADEFURIA
    """
else:
    # fallback se der erro
    system_context = """
    Você é o FURIA_BOT, assistente virtual oficial da FURIA Esports (Counter-Strike).
    Seu tom deve ser energético, competitivo e cheio de atitude, refletindo o espírito da FURIA.

    (Informações atualizadas do time indisponíveis no momento.)
    """

def pergunte(question: str, sid: str) -> str:
    try:
        # Inicializa o histórico da sessão se não existir
        if sid not in historico_conversa:
            historico_conversa[sid] = [
                {"role": "system", "content": system_context}
            ]
        
        # Adiciona a pergunta ao histórico
        historico_conversa[sid].append({"role": "user", "content": question})
        
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://furia.gg",
                "X-Title": "FURIA Chatbot",
            },
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=historico_conversa[sid],
            temperature=0.7
        )
        
        print(f"DEBUG - Resposta da API: {completion}")
        
        if not completion or not completion.choices:
            return "Puxa, tive um problema ao processar sua pergunta. Tente novamente! #DIADEFURIA"
        
        response = completion.choices[0].message.content
        
        # Adiciona a resposta ao histórico
        historico_conversa[sid].append({"role": "assistant", "content": response})
        historico_conversa[sid] = historico_conversa[sid][-10:]  # Mantém apenas as últimas 10 mensagens
        
        return response
        
    except Exception as e:
        print(f"ERRO NA API - Detalhes: {str(e)}")
        return f"Estou com problemas técnicos! Erro: {str(e)} 🛠️ #DIADEFURIA"

@app.route("/")
def homepage():
    dados = carregar_dados_furia() or {}
    elenco = dados.get("elenco", [])
    partidas = dados.get("partidas_recentes", [])
    proxima = partidas[0] if partidas else {"adversario": "Desconhecido", "resultado": "?"}

    return render_template("landing.html", elenco=elenco, proxima=proxima)

# Página atual do chatbot
@app.route("/chat")
def chat():
    return render_template("index.html")
active_sessions = set()

# Notifica todos sobre novo usuário
@socketio.on('connect')
def handle_connect():
    active_sessions.add(request.sid)
    print(f"Cliente conectado: {request.sid}")
    socketio.emit('system_message', {
        'message': 'Um novo usuário entrou no chat!',
        'type': 'notification'
    }, skip_sid=request.sid)

#Função para o disconnect
@socketio.on('disconnect')
def handle_disconnect():
    active_sessions.discard(request.sid)
    print(f"Cliente desconectado: {request.sid}")
    socketio.emit('system_message', {
        'message': 'Um usuário saiu do chat.',
        'type': 'notification'
    })

@socketio.on('message')
def handle_message(data):
    if request.sid not in active_sessions:
        return

    message = data['message']
    
    if message.startswith('@FuriaBot'):
        question = message.replace('@FuriaBot', '').strip()
        if question:
            socketio.emit('user_message', {
                'message': message,
                'sender_id': request.sid
            }, to=request.sid)
            
            response = pergunte(question, request.sid)  # Passa o SID da sessão
            socketio.emit('bot_message', {
                'response': response,
                'question': question
            })
    else:
        socketio.emit('user_message', {
            'message': message,
            'sender_id': request.sid
        }, skip_sid=request.sid)

#Limpa Historico quando desconectar
@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in historico_conversa:
        del historico_conversa[request.sid]
    active_sessions.discard(request.sid)
    print(f"Cliente desconectado: {request.sid}")
    socketio.emit('system_message', {
        'message': 'Um usuário saiu do chat.',
        'type': 'notification'
    })

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
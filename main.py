from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
socketio = SocketIO(app, cors_allowed_origins="*")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

system_context = """
Você é o FURIA_BOT, assistente virtual oficial da FURIA Esports (Counter-Strike). 
Seu tom deve ser energético, competitivo e cheio de atitude, refletindo o espírito da FURIA.

Regras importantes:
- Mantenha respostas curtas e impactantes quando possível
- Use gírias de CS:GO quando apropriado (ex: "clutch", "ace", "entry")
- Mostre paixão pelo time e pelo jogo
- Não use muitos emojis (máximo 1 por resposta)

Informações do time:
- Elenco atual: KSCERATO, yuurih, FalleN, Molod, Yekendar (IGL)
- Técnico: Sid
- Principais conquistas: Major finalista, múltiplos títulos internacionais
- Estilo de jogo: Agressivo, inovador, "FURIA style"

Responda como um verdadeiro fã da FURIA, com a energia que representa a torcida #DIADEFURIA
"""

def pergunte(question: str) -> str:
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://furia.gg",
                "X-Title": "FURIA Chatbot",
            },
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[
                {"role": "system", "content": system_context},
                {"role": "user", "content": question}
            ],
            temperature=0.9
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erro ao consultar a API: {str(e)}"

@app.route("/")
def homepage():
    return render_template("index.html")

active_sessions = set()


@socketio.on('connect')
def handle_connect():
    active_sessions.add(request.sid)
    print(f"Cliente conectado: {request.sid}")
    # Notifica todos sobre novo usuário
    socketio.emit('system_message', {
        'message': 'Um novo usuário entrou no chat!',
        'type': 'notification'
    }, skip_sid=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    active_sessions.discard(request.sid)
    print(f"Cliente desconectado: {request.sid}")
    # Notifica todos sobre usuário que saiu
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
            # Envia confirmação apenas para o remetente
            socketio.emit('user_message', {
                'message': message,
                'sender_id': request.sid
            }, to=request.sid)
            
            response = pergunte(question)
            # Envia a resposta do bot para TODOS
            socketio.emit('bot_message', {
                'response': response,
                'question': question
            })
    else:
        # Mensagem normal para todos exceto o remetente
        socketio.emit('user_message', {
            'message': message,
            'sender_id': request.sid
        }, skip_sid=request.sid)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
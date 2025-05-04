from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from flask_socketio import SocketIO
from openai import OpenAI
from dotenv import load_dotenv
import json
import os
from firebase_auth import registrar_usuario, logar_usuario
from firestore_db import salvar_dados_usuario, atualizar_redes_sociais, db
from alerts import FanAlertSystem
from app_factory import create_app


load_dotenv()

app, socketio = create_app()

# Inicializa o sistema de alertas
alert_system = FanAlertSystem(app)


# Adicione isso após as imports
USING_FIREBASE = os.getenv("FIREBASE_API_KEY") is not None

if not USING_FIREBASE:
    print("⚠️ ATENÇÃO: Firebase não configurado. Usando autenticação mockada para desenvolvimento.")
    from firebase_auth import usuarios_mock  # Importa os dados mockados

historico_conversa = {}

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
socketio = SocketIO(app, cors_allowed_origins="*")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Função para carregar dados da FURIA
def carregar_dados_furia():
    caminho_json = os.path.join(os.path.dirname(__file__), 'scraper', 'data', 'furia.json')
    
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        for jogador in dados.get("elenco", []):
            player_id = jogador.get('player_id', '')
            if player_id:
                jogador['foto'] = f"https://www.hltv.org/img/static/player/player_{player_id}.png"
            else:
                jogador['foto'] = url_for('static', filename='images/default_player.png')
            
            jogador['nickname'] = jogador.get('nickname', jogador['nome'].split()[0])
        
        return dados
    except FileNotFoundError:
        print(f"Arquivo {caminho_json} não encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao carregar furia.json: {str(e)}")
        return None

dados_furia = carregar_dados_furia()

if dados_furia:
    elenco = ", ".join([player.get('nome', 'Jogador') for player in dados_furia.get('elenco', [])])
    ranking = dados_furia.get('ranking', 'Ranking desconhecido')
    partidas = dados_furia.get('partidas_recentes', [4])
    
    system_context = f"""
    Você é o FURIA_BOT, assistente virtual oficial da FURIA Esports (Counter-Strike).
    Seu tom deve ser energético, competitivo e cheio de atitude, refletindo o espírito da FURIA.

    Regras importantes:
    -Não utilize muitos **
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
    system_context = """
    Você é o FURIA_BOT, assistente virtual oficial da FURIA Esports (Counter-Strike).
    Seu tom deve ser energético, competitivo e cheio de atitude.
    (Informações atualizadas do time indisponíveis no momento.)
    """

# Função para perguntar ao bot
def pergunte(question: str, sid: str) -> str:
    try:
        if sid not in historico_conversa:
            historico_conversa[sid] = [
                {"role": "system", "content": system_context}
            ]
        
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
        
        if not completion or not completion.choices:
            return "Puxa, tive um problema ao processar sua pergunta. Tente novamente! #DIADEFURIA"
        
        response = completion.choices[0].message.content
        historico_conversa[sid].append({"role": "assistant", "content": response})
        historico_conversa[sid] = historico_conversa[sid][-10:]
        
        return response
        
    except Exception as e:
        print(f"ERRO NA API: {str(e)}")
        return f"Estou com problemas técnicos! Erro: {str(e)} 🛠️ #DIADEFURIA"

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if not email or not senha:
            return render_template('logincadastro.html', error="Preencha todos os campos!")
        
        resultado = logar_usuario(email, senha)
        
        if 'erro' in resultado:
            return render_template('logincadastro.html', error=resultado['erro'])
        
        session['usuario'] = email
        return redirect(url_for('homepage'))
    
    return render_template('logincadastro.html')

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')

        cpf = request.form.get('cpf')
        endereco = request.form.get('endereco')
        interesses = request.form.get('interesses')
        eventos = request.form.get('eventos')
        compras = request.form.get('compras')

        redes = {
            "twitter": request.form.get("twitter"),
            "instagram": request.form.get("instagram"),
            "youtube": request.form.get("youtube"),
            "twitch": request.form.get("twitch")
        }

        perfis_esports = {
            "faceit": request.form.get("faceit"),
            "hltv": request.form.get("hltv")
        }

        # Validação básica
        if not all([nome, email, senha, confirmar_senha, cpf, endereco]):
            return render_template('cadastro.html', error="Preencha todos os campos obrigatórios!")

        if senha != confirmar_senha:
            return render_template('cadastro.html', error="As senhas não coincidem!")

        resultado = registrar_usuario(email, senha, nome)

        if 'erro' in resultado:
            return render_template('cadastro.html', error=resultado['erro'])

        uid = resultado['usuario']['id']
        session['usuario'] = email
        session['nome'] = nome
        session['uid'] = uid  # salva UID no session

        dados_completos = {
            "nome": nome,
            "email": email,
            "cpf": cpf,
            "endereco": endereco,
            "interesses": interesses,
            "eventos": eventos,
            "compras": compras,
            "redes_sociais": redes,
            "perfis_esports": perfis_esports
        }

        sucesso = salvar_dados_usuario(uid, dados_completos)
        session['profile_viewed'] = False  # Isso fará o badge aparecer

        if not sucesso:
            return render_template('cadastro.html', error="Erro ao salvar os dados no Firestore.")

        return redirect(url_for('homepage'))

    return render_template('cadastro.html')

@app.route("/logout")
def logout():
    session.pop('usuario', None)
    session.pop('nome', None)
    return redirect(url_for('homepage'))

@app.route("/analisarfan")
def analisarfan():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    uid = session.get('uid')
    doc = db.collection('usuarios').document(uid).get()
    
    if doc.exists:
        dados = doc.to_dict()
        # Exemplo de análise gerada (substitua por IA real depois)
        analise = f"""
        🎯 Nível de Engajamento: 85/100
        📊 Redes Sociais Ativas: {sum(1 for rede in dados.get('redes_sociais', {}) if rede)}/4
        🔥 Torcedor desde: 2023
        #DIADEFURIA
        """
        return render_template("analise_fan.html", dados=dados, analise=analise)
    
    return redirect(url_for('redes_sociais'))

# Rota principal
@app.route("/")
def homepage():
    dados = carregar_dados_furia() or {}
    elenco = dados.get("elenco", [])

    for jogador in elenco:
        nickname = jogador.get("nickname", "").lower()
        image_path = os.path.join(app.static_folder, 'images', 'players', f"{nickname}.png")
        if os.path.exists(image_path):
            jogador['foto'] = url_for('static', filename=f'images/players/{nickname}.png')
        else:
            jogador['foto'] = url_for('static', filename='images/default_player.png')

    partidas = dados.get("partidas_futuras", [])
    partidas_recentes = dados.get("partidas_recentes", [])

    proxima = None

    # Lógica para determinar a próxima partida (mantida da versão original)
    live = next((p for p in partidas if p.get("status") == "live"), None)
    if live:
        proxima = live
    else:
        upcoming = next((p for p in partidas if p.get("status") == "upcoming"), None)
        if upcoming:
            proxima = upcoming
        elif partidas_recentes:
            ultima = partidas_recentes[0]
            proxima = {
                "adversario": ultima.get("adversario", "Desconhecido"),
                "resultado": ultima.get("resultado", "?"),
                "data": "Último jogo",
                "campeonato": ultima.get("campeonato", "Campeonato não definido"),
                "status": "completed",
                "logo_adversario": ""
            }
        else:
            proxima = {
                "adversario": "Desconhecido",
                "resultado": "?",
                "data": "Em breve",
                "campeonato": "Campeonato não definido",
                "status": "upcoming"
            }

    return render_template("landing.html", elenco=elenco, proxima=proxima)

# Rota do chat (protegida)
@app.route("/chat")
def chat():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template("index.html", nome=session.get('nome', 'Fã da FURIA'))

@app.route("/redes", methods=['GET', 'POST'])
def redes_sociais():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    # Obter UID de forma segura
    uid = session.get('uid')
    if not uid:
        flash("Erro de autenticação. Por favor, faça login novamente.", "error")
        return redirect(url_for('login'))

    # Carrega dados existentes
    doc = db.collection('usuarios').document(uid).get()
    redes = doc.to_dict().get('redes_sociais', {}) if doc.exists else {}

    if request.method == 'POST':
        novas_redes = {
            "twitter": request.form.get("twitter", "").strip(),
            "instagram": request.form.get("instagram", "").strip(),
            "youtube": request.form.get("youtube", "").strip(),
            "twitch": request.form.get("twitch", "").strip()
        }

        # Verifica se pelo menos uma rede foi preenchida
        if not any(novas_redes.values()):
            flash("Por favor, preencha pelo menos uma rede social.", "error")
            return render_template("redes.html", redes=redes)

        try:
            # Atualiza apenas as redes sociais mantendo outros dados
            sucesso = db.collection('usuarios').document(uid).update({
                'redes_sociais': novas_redes
            })
            
            flash("Redes sociais atualizadas com sucesso!", "success")
            return redirect(url_for("analisarfan"))
        except Exception as e:
            print(f"Erro ao atualizar redes sociais: {str(e)}")
            flash("Erro ao salvar redes sociais. Tente novamente.", "error")

    return render_template("redes.html", redes=redes)

@app.route('/alerts')
def view_alerts():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    uid = session.get('uid')
    alerts_ref = db.collection('user_alerts').document(uid)
    alerts_data = alerts_ref.get()
    
    if alerts_data.exists:
        # Marcar como lido
        alerts_ref.update({'read': True})
        return render_template('alerts.html', alerts=alerts_data.to_dict().get('alerts', []))
    
    return render_template('alerts.html', alerts=[])

@app.route("/coletar-dados", methods=['POST'])
def coletar_dados():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    flash("A coleta de dados agora é feita através do Dashboard Standalone", "info")
    return redirect(url_for('redes_sociais'))

@app.route("/coletar-dados-fan")
def coletar_dados_fan():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    flash("A coleta de dados agora é feita através do Dashboard Standalone", "info")
    return redirect(url_for('redes_sociais'))


# WebSocket handlers
active_sessions = set()

@socketio.on('connect')
def handle_connect():
    active_sessions.add(request.sid)
    print(f"Cliente conectado: {request.sid}")
    socketio.emit('system_message', {
        'message': 'Um novo usuário entrou no chat!',
        'type': 'notification'
        
    }, skip_sid=request.sid)

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
            
            response = pergunte(question, request.sid)
            socketio.emit('bot_message', {
                'response': response,
                'question': question
            })
    else:
        socketio.emit('user_message', {
            'message': message,
            'sender_id': request.sid
        }, skip_sid=request.sid)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
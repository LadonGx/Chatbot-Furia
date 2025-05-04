from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

def create_app():
    # Configuração básica do Flask
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
    
    # Configuração do SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    return app, socketio
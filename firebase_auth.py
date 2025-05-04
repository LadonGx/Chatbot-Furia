import pyrebase
import os
from flask import flash
from dotenv import load_dotenv

load_dotenv()

# Configuração do Firebase (com todas as chaves necessárias)
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
    "databaseURL": ""  # Não estamos usando Realtime Database
}

# Inicialização segura do Firebase
try:
    firebase = pyrebase.initialize_app(firebase_config)
    auth = firebase.auth()
    print("🔥 Firebase conectado com sucesso!")
except Exception as e:
    auth = None
    print(f"❌ Falha na conexão com Firebase: {str(e)}")

def registrar_usuario(email, senha, nome=None):
    if not auth:
        return {"erro": "Serviço de autenticação indisponível"}
    
    try:
        user = auth.create_user_with_email_and_password(email, senha)
        return {
            "sucesso": True,
            "usuario": {
                "email": email,
                "nome": nome,
                "id": user['localId'],
                "token": user['idToken']
            }
        }
    except Exception as e:
        error = str(e)
        if "EMAIL_EXISTS" in error:
            return {"erro": "E-mail já cadastrado"}
        elif "WEAK_PASSWORD" in error:
            return {"erro": "Senha deve ter no mínimo 6 caracteres"}
        return {"erro": f"Erro no cadastro: {error}"}

def logar_usuario(email, senha):
    if not auth:
        return {"erro": "Serviço de autenticação indisponível"}
    
    try:
        user = auth.sign_in_with_email_and_password(email, senha)
        return {
            "sucesso": True,
            "usuario": {
                "email": email,
                "id": user['localId'],
                "token": user['idToken']
            }
        }
    except Exception as e:
        error = str(e)
        if "INVALID_EMAIL" in error:
            return {"erro": "E-mail inválido"}
        elif "INVALID_PASSWORD" in error:
            return {"erro": "Senha incorreta"}
        elif "EMAIL_NOT_FOUND" in error:
            return {"erro": "E-mail não cadastrado"}
        return {"erro": f"Erro no login: {error}"}
    

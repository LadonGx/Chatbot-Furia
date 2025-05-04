import os
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializa Firebase Admin SDK
if not firebase_admin._apps:
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-adminsdk.json")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

# Cliente do Firestore
db = firestore.client()

def salvar_dados_usuario(uid, dados):
    try:
        db.collection('usuarios').document(uid).set(dados)
        return True
    except Exception as e:
        print(f"Erro ao salvar dados no Firestore: {e}")
        return False
    
def atualizar_redes_sociais(uid, redes):
    try:
        db.collection('usuarios').document(uid).update({
            'redes_sociais': redes
        })
        return True
    except Exception as e:
        print(f"Erro ao atualizar redes sociais: {e}")
        return False

def get_all_users():
    """
    Retorna todos os usuários da coleção 'users' com seus dados relevantes.
    """
    try:
        users_ref = db.collection("users")
        docs = users_ref.stream()
        user_list = []

        for doc in docs:
            data = doc.to_dict()
            data['uid'] = doc.id  # opcional, para identificar o usuário
            user_list.append(data)

        return user_list

    except Exception as e:
        print(f"Erro ao buscar usuários do Firestore: {e}")
        return []
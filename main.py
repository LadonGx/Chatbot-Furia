from openai import OpenAI
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

from routes import *

api_key=os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("Erro: API key não encontrada! Crie um arquivo .env baseado no .env.example.")

# Configuração do cliente
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

# Contexto do sistema para o chatbot
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
    """Envia pergunta para a API e retorna a resposta"""
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

def main():
    print("""
    🔴⚫ FURIA CS:GO Chatbot ⚫🔴
    --------------------------
    Digite suas perguntas sobre o time (ou 'sair' para encerrar)
    """)
    
    while True:
        user_input = input("\nSua pergunta: ").strip()
        
        if user_input.lower() in ['sair', 'exit', 'quit']:
            print("Até mais, furioso!")
            break
            
        if not user_input:
            print("Por favor, digite uma pergunta válida.")
            continue
            
        print("\nProcessando...", end="\r")
        response = pergunte(user_input)
        print("\nFURIA_BOT:", response)

if __name__ == "__main__":
    app.run(debug=True)

    

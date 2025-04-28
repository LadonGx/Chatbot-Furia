from main import app, pergunte
from flask import request, jsonify
from flask import render_template
from main import os

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/api/pergunte", methods=["POST"])
def api_pergunte():
    data = request.get_json()
    question = data.get("question")
    if not question:
        return jsonify({"error": "Pergunta não fornecida"}), 400
    response = pergunte(question)
    return jsonify({"response": response})

@app.route("/api/set_key", methods=["POST"])
def set_key():
    key = request.json.get("key")
    if key:
        os.environ["OPENROUTER_API_KEY"] = key
        return jsonify({"status": "success"})
    return jsonify({"error": "Chave inválida"}), 400
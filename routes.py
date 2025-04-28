from main import app, pergunte
from flask import request, jsonify
from flask import render_template

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
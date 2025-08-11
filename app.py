import json
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

HISTORICO_PATH = "historico.json"

def pegar_clima_fuso(local):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={local}&appid={API_KEY}&lang=pt_br&units=metric"
    resposta = requests.get(url)
    if resposta.status_code != 200:
        return None
    dados = resposta.json()
    clima = dados['weather'][0]['description'].capitalize()
    temperatura = dados['main']['temp']
    timezone_segundos = dados['timezone']
    utc_now = datetime.utcnow()
    local_time = utc_now + timedelta(seconds=timezone_segundos)
    horario_formatado = local_time.strftime("%H:%M:%S")
    return {
        "clima": clima,
        "temperatura": temperatura,
        "horario": horario_formatado,
        "cidade": dados['name'],
        "pais": dados['sys']['country']
    }

def ler_historico():
    if not os.path.exists(HISTORICO_PATH):
        return []
    with open(HISTORICO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_no_historico(novo_registro):
    historico = ler_historico()
    historico.append(novo_registro)
    with open(HISTORICO_PATH, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

@app.route("/", methods=["GET"])
def home():
    return render_template("homepage.html")

@app.route("/buscar")
def buscar():
    local = request.args.get("local")
    if not local:
        return render_template("homepage.html", erro="Por favor, digite uma cidade.")
    
    resultado = pegar_clima_fuso(local)
    if resultado is None:
        return render_template("homepage.html", erro="Cidade não encontrada ou erro na API.")
    
    registro = {
        "cidade": resultado["cidade"],
        "pais": resultado["pais"],
        "clima": resultado["clima"],
        "temperatura": resultado["temperatura"],
        "horario_local": resultado["horario"],
        "data_busca": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    salvar_no_historico(registro)
    historico = ler_historico()
    return render_template("homepage.html", resultado=resultado, historico=historico)

if __name__ == "__main__":
    app.run(debug=True)


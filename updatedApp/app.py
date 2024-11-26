from flask import Flask, render_template, request, redirect, url_for
import webview
import threading
from datetime import datetime

app = Flask(__name__)

# Variáveis globais
paciente_nome = ""
n_coleta_ruim = 0
n_coleta_bom = 0
n_coleta_forca = 0
coletaRuim = False
coletaBom = False
coletaForca = False

# Rota para a tela inicial
@app.route("/", methods=["GET", "POST"])
def home():
    global paciente_nome
    if request.method == "POST":
        paciente_nome = request.form.get("nome_paciente")
        return redirect(url_for("coleta"))
    return render_template("[0] base.html")

# Rota para a tela de Coleta
@app.route("/testes")
def testes():
    global paciente_nome, n_coleta_ruim, n_coleta_bom, n_coleta_forca
    data_atual = datetime.now().strftime("%d/%m/%Y")
    return render_template(
        "[1.0] coleta.html",
        paciente_nome=paciente_nome,
        data_atual=data_atual,
        n_coleta_ruim=n_coleta_ruim,
        n_coleta_bom=n_coleta_bom,
        n_coleta_forca=n_coleta_forca,
    )

# Rota para a tela de Coleta do braço parético
@app.route("/coleta/paretico")
def coleta_paretico():
    global paciente_nome
    return render_template("[1.1] paretico.html", paciente_nome=paciente_nome)

@app.route("/incrementar_paretico", methods=["POST"])
def incrementar_paretico():
    global n_coleta_ruim
    n_coleta_ruim += 1
    return redirect(url_for("coleta"))

# Rota para a tela de Coleta do braço saudável
@app.route("/coleta/saudavel")
def coleta_saudavel():
    global paciente_nome
    return render_template("[1.2] saudavel.html", paciente_nome=paciente_nome)

@app.route("/incrementar_saudavel", methods=["POST"])
def incrementar_saudavel():
    global n_coleta_bom
    n_coleta_bom += 1
    return redirect(url_for("coleta"))


# Rotas para os outros botões do header
@app.route("/graficos")
def graficos():
    global paciente_nome
    return render_template("[2.0] graficos.html", paciente_nome=paciente_nome)

@app.route("/tabelas")
def tabelas():
    global paciente_nome
    return render_template("[3.0] tabelas.html", paciente_nome=paciente_nome)

@app.route("/area-dev")
def area_dev():
    global paciente_nome
    return render_template("[4.0] area_dev.html", paciente_nome=paciente_nome)

# Iniciar o servidor Flask
def iniciar_servidor():
    app.run(debug=False, port=5000, use_reloader=False)

# Abrir o PyWebview com a aplicação
if __name__ == "__main__":
    threading.Thread(target=iniciar_servidor, daemon=True).start()
    webview.create_window("NHPT+", "http://127.0.0.1:5000")
    webview.start()
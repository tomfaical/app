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
teste_selecionado = ""
dataHoje = datetime.now().strftime("%d/%m/%Y")

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
    global paciente_nome, dataHoje, n_coleta_ruim, n_coleta_bom, n_coleta_forca
    
    return render_template(
        "[1.0] testes.html",
        paciente_nome=paciente_nome,
        dataHoje=dataHoje,
        n_coleta_ruim=n_coleta_ruim,
        n_coleta_bom=n_coleta_bom,
        n_coleta_forca=n_coleta_forca,
    )

@app.route("/testes/iniciar-coleta")
def iniciar_coleta():
    global paciente_nome, dataHoje, teste_selecionado
    return render_template(
        "[1.1] iniciar-coleta.html", 
        paciente_nome=paciente_nome,
        dataHoje=dataHoje,
        teste_selecionado=teste_selecionado,
        n_coleta_ruim=n_coleta_ruim,
        n_coleta_bom=n_coleta_bom,
        n_coleta_forca=n_coleta_forca
        )

# Rota para a tela de Coleta do braço parético
@app.route("/testes/paretico")
def coleta_paretico():
    global paciente_nome, dataHoje, coletaRuim
    return render_template(
        "[1.2] paretico.html", 
        paciente_nome=paciente_nome,
        coletaRuim=coletaRuim,
        dataHoje=dataHoje
        )

@app.route("/incrementar_paretico", methods=["POST"])
def incrementar_paretico():
    global n_coleta_ruim
    n_coleta_ruim += 1
    return redirect(url_for("testes"))

# Rota para a tela de Coleta do braço saudável
@app.route("/testes/saudavel")
def coleta_saudavel():
    global paciente_nome, dataHoje, coletaBom
    return render_template(
        "[1.3] saudavel.html", 
        paciente_nome=paciente_nome,
        coletaBom=coletaBom,
        dataHoje=dataHoje
        )

@app.route("/incrementar_saudavel", methods=["POST"])
def incrementar_saudavel():
    global n_coleta_bom
    n_coleta_bom += 1
    return redirect(url_for("testes"))

# Rota para a tela de Coleta da força
@app.route("/testes/forca")
def coleta_forca():
    global paciente_nome, dataHoje, coletaForca
    return render_template(
        "[1.4] forca.html", 
        paciente_nome=paciente_nome, 
        coletaForca=coletaForca,
        dataHoje=dataHoje
        )

@app.route("/incrementar_forca", methods=["POST"])
def incrementar_forca():
    global n_coleta_forca
    n_coleta_forca += 1
    return redirect(url_for("testes"))

# Rotas para os outros botões do header
@app.route("/graficos")
def graficos():
    global paciente_nome
    return render_template("[2.0] graficos.html", paciente_nome=paciente_nome)

@app.route("/dados")
def tabelas():
    global paciente_nome
    return render_template("[3.0] dados.html", paciente_nome=paciente_nome)

@app.route("/dev")
def area_dev():
    global paciente_nome
    return render_template("[4.0] area-dev.html", paciente_nome=paciente_nome)

# Iniciar o servidor Flask
def iniciar_servidor():
    app.run(debug=False, port=5000, use_reloader=False)

# Abrir o PyWebview com a aplicação
if __name__ == "__main__":
    threading.Thread(target=iniciar_servidor, daemon=True).start()
    webview.create_window("NHPT+", "http://127.0.0.1:5000")
    webview.start()
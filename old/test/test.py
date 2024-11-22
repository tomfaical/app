from flask import Flask, render_template
import webview
import threading

# Criar a aplicação Flask
app = Flask(__name__)

# Rota principal
@app.route("/")
def index():
    return render_template("index.html")

# Função para iniciar o servidor Flask
def iniciar_servidor():
    app.run(debug=False, port=5000, use_reloader=False)

# Função principal
if __name__ == "__main__":
    # Iniciar o servidor Flask em uma thread separada
    threading.Thread(target=iniciar_servidor, daemon=True).start()

    # Criar a janela PyWebview
    webview.create_window("Minha Aplicação", "http://127.0.0.1:5000")
    webview.start()

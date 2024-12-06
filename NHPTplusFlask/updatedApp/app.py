from flask import Flask, render_template, request, redirect, url_for
import webview
import threading
from datetime import datetime
import pandas as pd
import os
from backend import ESPHandler
from flask import jsonify

esp_handler = ESPHandler()


app = Flask(__name__)

# Caminho do arquivo CSV
# CSV_FILE = 'C:/PBL_S4/app/app/NHPTplusFlask/updatedApp/registros.csv'
CSV_FILE = 'registros.csv'

# Colunas do CSV
CSV_COLUMNS = ['nome', 'idade', 'sexo', 'membro_dominante', 'membro_acometido']

# Inicialização do CSV
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        # Cria um DataFrame vazio com as colunas
        df = pd.DataFrame(columns=CSV_COLUMNS)
        df.to_csv(CSV_FILE, index=False)
    else:
        # Carrega o CSV existente para garantir a consistência
        df = pd.read_csv(CSV_FILE)  # Apenas para validar o arquivo
    return df

# Inicializa o CSV na inicialização do servidor
df = initialize_csv()

# Variáveis globais
paciente_nome = ""
n_coleta_esq = 0
n_coleta_dir = 0
n_coleta_forca = 0
coletaEsq = False
coletaDir = False
coletaForca = False
teste_selecionado = ""
dataHoje = datetime.now().strftime("%d/%m/%Y")
nReg = 0

# Rota para a tela de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Captura os valores enviados pelo formulário
        username = request.form.get('username')  # Altere 'usuario' para 'username' conforme o id no HTML
        password = request.form.get('password')  # Altere 'senha' para 'password' conforme o id no HTML

        # Verifica se o usuário e senha estão corretos
        if username == 'admin' and password == 'admin':
            return redirect(url_for('home'))  # Redireciona para a página inicial (home)
        else:
            # Retorna uma mensagem de erro com a página de login
            error_message = "Usuário ou senha inválidos. Tente novamente."
            return render_template('[0.0] login.html', error=error_message)

    # Para requisições GET, apenas exibe o formulário de login
    return render_template('[0.0] login.html')

    

# Rota para a tela inicial
@app.route("/home", methods=["GET", "POST"])
def home():
    global paciente_nome
    if request.method == "POST":
        paciente_nome = request.form.get("nome_paciente")
        return redirect(url_for("testes"))
    
    # Carregar o arquivo CSV
    try:
        pacientes_df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        # Caso o arquivo não exista, criar um DataFrame vazio
        pacientes_df = pd.DataFrame(columns=['nome', 'idade', 'sexo', 'membroDominante', 'membroAcometido'])

    # Renderizar o template e passar os pacientes como contexto
    return render_template('[0.1] base.html', pacientes=pacientes_df)

# Rota para cadastro do paciente
@app.route('/cadastrarPaciente', methods=['POST'])
def cadastrar_paciente():
    global paciente_nome, nReg 

    # Recebendo os dados do formulário
    nome = request.form.get('nome')
    idade = request.form.get('idade')
    sexo = request.form.get('sexo')
    membroDominante = request.form.get('membroDominante')
    membroAcometido = request.form.get('membroAcometido')
    nReg += 1
    
    paciente_nome = nome

     # Criar o DataFrame com os novos dados
    novo_paciente = pd.DataFrame([{
        'ID': nReg,
        'nome': nome,
        'idade': idade,
        'sexo': sexo,
        'membro_dominante': membroDominante,
        'membro_acometido': membroAcometido
    }])

    # Adicionar ao arquivo CSV existente
    df = pd.read_csv(CSV_FILE)
    df = pd.concat([df, novo_paciente], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

    print(f"Paciente cadastrado: {nome}, {idade}, {sexo}, {membroDominante}, {membroAcometido}")
    
    # Redirecionar ou renderizar uma página de sucesso
    return redirect('/testes')  # Ajuste para onde você quer redirecionar



# Deletar paciente
@app.route('/delete-patient/<int:index>', methods=['DELETE'])
def delete_patient(index):
    global df
    if index < len(df):
        df.drop(index, inplace=True)
        df.to_csv(CSV_FILE, index=False)
        return jsonify({"message": "Paciente excluído com sucesso"}), 200
    return jsonify({"error": "Paciente não encontrado"}), 404

# Buscar dados do paciente
@app.route('/get-patient/<int:index>', methods=['GET'])
def get_patient(index):
    global df
    if index < len(df):
        patient = df.iloc[index].to_dict()
        return jsonify(patient), 200
    return jsonify({"error": "Paciente não encontrado"}), 404


@app.route('/edit-patient/<int:index>', methods=['PUT'])
def edit_patient(index):
    global df

    pacientes_df = df

    try:
        # Obtenha os dados enviados na solicitação
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Nenhum dado enviado'}), 400

        # Verifique se o índice é válido
        if index not in pacientes_df.index:
            return jsonify({'error': 'Paciente não encontrado'}), 404

        # Atualize os dados do paciente, verificando cada campo individualmente
        pacientes_df.at[index, 'nome'] = data.get('nome', pacientes_df.at[index, 'nome'])
        pacientes_df.at[index, 'idade'] = data.get('idade', pacientes_df.at[index, 'idade'])
        pacientes_df.at[index, 'sexo'] = data.get('sexo', pacientes_df.at[index, 'sexo'])
        pacientes_df.at[index, 'membro_dominante'] = data.get('membro_dominante', pacientes_df.at[index, 'membro_dominante'])
        pacientes_df.at[index, 'membro_acometido'] = data.get('membro_acometido', pacientes_df.at[index, 'membro_acometido'])

        # Salve as alterações no arquivo CSV
        pacientes_df.to_csv('registros.csv', index=False)

        return jsonify({'success': True}), 200

    except Exception as e:
        print(f"Erro ao editar paciente: {e}")
        return jsonify({'error': 'Erro no servidor'}), 500


# Rota para a tela de Coleta
@app.route("/coletaTemp")
def coleta():
    global df, paciente_nome, dataHoje, n_coleta_esq, n_coleta_dir, n_coleta_forca, teste_selecionado
    
    # Obter o parâmetro patient_id da URL
    patient_id = request.args.get('patient_id')

    # Verificar se patient_id é válido
    if patient_id is not None and patient_id.isdigit():
        patient_id = int(patient_id)

        if 0 <= patient_id < len(df):
            # Atualizar o nome do paciente com base no ID
            paciente_nome = df.iloc[patient_id]['nome']
        else:
            paciente_nome = "Paciente não encontrado"
    else:
        paciente_nome = "Nenhum paciente selecionado"
    
    return render_template(
        "[1.0.1] coletaTemp.html",
        paciente_nome=paciente_nome,
        dataHoje=dataHoje,
        n_coleta_esq=n_coleta_esq,
        n_coleta_dir=n_coleta_dir,
        n_coleta_forca=n_coleta_forca,
        teste_selecionado=teste_selecionado
    )



# Rota para a tela de Coleta
@app.route("/testes", methods=["GET", "POST"])
def testes():
    global df, paciente_nome, dataHoje, n_coleta_esq, n_coleta_dir, n_coleta_forca, teste_selecionado
    
    # Obter o parâmetro patient_id da URL
    patient_id = request.args.get('patient_id')

    # Verificar se patient_id é válido
    if patient_id is not None and patient_id.isdigit():
        patient_id = int(patient_id)

        if 0 <= patient_id < len(df):
            # Atualizar o nome do paciente com base no ID
            paciente_nome = df.iloc[patient_id]['nome']
        else:
            paciente_nome = "Paciente não encontrado"
    else:
        paciente_nome = "Nenhum paciente selecionado"


    if request.method == "POST":
        teste_selecionado = request.form.get("teste_submit")
        print(teste_selecionado)
        return redirect(url_for("testes/iniciar-coleta"))
    
    return render_template(
        "[1.0] testes.html",
        paciente_nome=paciente_nome,
        dataHoje=dataHoje,
        n_coleta_esq=n_coleta_esq,
        n_coleta_dir=n_coleta_dir,
        n_coleta_forca=n_coleta_forca,
        teste_selecionado=teste_selecionado
    )


@app.route("/testes/iniciar-coleta", methods=["GET", "POST"])
def iniciar_coleta():
    global paciente_nome, dataHoje, teste_selecionado, paciente_nome, n_coleta_esq, n_coleta_dir, n_coleta_forca
    if request.method == "POST":
        data = request.get_json()
        teste_selecionado = data.get("teste_selecionado", "Nenhum teste selecionado")
        print("Teste selecionado:", teste_selecionado)  # Log para debug
        return redirect(url_for("iniciar_coleta"))

    # Renderizar a página normalmente no caso de GET
    return render_template(
        "[1.1] iniciar-coleta.html",
        paciente_nome=paciente_nome,
        dataHoje=dataHoje,
        teste_selecionado=teste_selecionado,
        n_coleta_esq=n_coleta_esq,
        n_coleta_dir=n_coleta_dir,
        n_coleta_forca=n_coleta_forca
    )


# Rota para a tela de Coleta do braço esquerdo
@app.route("/testes/esquerdo")
def coleta_esquerdo():
    global paciente_nome, dataHoje, coletaEsq, teste_selecionado
    return render_template(
        "[1.2] esquerdo.html", 
        paciente_nome=paciente_nome,
        coletaEsq=coletaEsq,
        dataHoje=dataHoje,
        teste_selecionado=teste_selecionado
        )

@app.route("/incrementar_esquerdo", methods=["POST"])
def incrementar_esquerdo():
    global n_coleta_esq
    n_coleta_esq += 1
    return redirect(url_for("testes"))

# Rota para a tela de Coleta do braço direito
@app.route("/testes/direito")
def coleta_direito():
    global paciente_nome, dataHoje, coletaDir, teste_selecionado
    return render_template(
        "[1.3] direito.html", 
        paciente_nome=paciente_nome,
        coletaDir=coletaDir,
        dataHoje=dataHoje,
        teste_selecionado=teste_selecionado
        )

@app.route("/incrementar_direito", methods=["POST"])
def incrementar_direito():
    global n_coleta_dir
    n_coleta_dir += 1
    return redirect(url_for("testes"))

# Rota para a tela de Coleta da força
@app.route("/testes/forca")
def coleta_forca():
    global paciente_nome, dataHoje, coletaForca, teste_selecionado
    return render_template(
        "[1.4] forca.html", 
        paciente_nome=paciente_nome, 
        coletaForca=coletaForca,
        dataHoje=dataHoje,
        teste_selecionado=teste_selecionado
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

@app.route("/area-dev")
def area_dev():
    global paciente_nome
    return render_template("[4.0] area-dev.html", paciente_nome=paciente_nome)


# BackEnd implementation

@app.route('/connect', methods=['POST'])
def connect_to_esp():
    port = request.json.get('port')
    success = esp_handler.connect_to_esp(port)
    if success:
        return jsonify({"message": "Conexão estabelecida com sucesso"}), 200
    return jsonify({"error": "Falha ao conectar"}), 500

@app.route('/disconnect', methods=['POST'])
def disconnect_from_esp():
    esp_handler.disconnect_from_esp()
    return jsonify({"message": "Conexão encerrada"}), 200

@app.route('/receive-data', methods=['POST'])
def receive_data():
    condicao = request.json.get('condicao', 'indefinido')
    success = esp_handler.receive_data(condicao)
    if success:
        return jsonify({"message": "Dados recebidos e armazenados"}), 200
    return jsonify({"error": "Erro ao receber dados"}), 500

@app.route('/save-data', methods=['POST'])
def save_data():
    filename = request.json.get('filename', 'dados_coleta.csv')
    esp_handler.save_data_to_csv(filename)
    return jsonify({"message": f"Dados salvos em {filename}"}), 200

@app.route('/load-data', methods=['POST'])
def load_data():
    filename = request.json.get('filename', 'dados_coleta.csv')
    esp_handler.load_data_from_csv(filename)
    return jsonify({"message": f"Dados carregados de {filename}"}), 200






# Iniciar o servidor Flask
def iniciar_servidor():
    app.run(debug=False, port=5000, use_reloader=False)

# Abrir o PyWebview com a aplicação
if __name__ == "__main__":
    app.jinja_env.globals.update(enumerate=enumerate)
    threading.Thread(target=iniciar_servidor, daemon=True).start()
    webview.create_window("NHPT+", "http://127.0.0.1:5000")
    webview.start()
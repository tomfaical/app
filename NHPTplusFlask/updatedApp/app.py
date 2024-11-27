from flask import Flask, render_template, request, redirect, url_for
import webview
import threading
from datetime import datetime
import pandas as pd
import os

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
n_coleta_ruim = 0
n_coleta_bom = 0
n_coleta_forca = 0
coletaRuim = False
coletaBom = False
coletaForca = False
teste_selecionado = ""
dataHoje = datetime.now().strftime("%d/%m/%Y")
nReg = 0

# Rota para a tela inicial
@app.route("/", methods=["GET", "POST"])
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
    return render_template('[0] base.html', pacientes=pacientes_df)

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

from flask import jsonify

from flask import jsonify

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

# # Editar paciente
# @app.route('/edit-patient/<int:index>', methods=['PUT'])
# def edit_patient(index):
#     global df
#     if index < len(df):
#         data = request.json
#         df.loc[index] = [
#             data['nome'],
#             data['idade'],
#             data['sexo'],
#             data['membro_dominante'],
#             data['membro_acometido']
#         ]
#         df.to_csv(CSV_FILE, index=False)
#         return jsonify({"message": "Paciente atualizado com sucesso"}), 200
#     return jsonify({"error": "Paciente não encontrado"}), 404

#     global pacientes_df

#     try:
#         # Obtenha os dados enviados no request
#         data = request.get_json()

#         # Log para verificar os dados recebidos
#         print(f"Recebido para editar paciente com ID {id}: {data}")

#         if not data:
#             return jsonify({'error': 'Nenhum dado enviado'}), 400

#         # Verifique se o ID existe no DataFrame
#         if id not in pacientes_df.index:
#             print(f"Paciente com ID {id} não encontrado no DataFrame.")
#             return jsonify({'error': 'Paciente não encontrado'}), 404

#         # Atualize os campos no DataFrame
#         for key in ['nome', 'idade', 'sexo', 'membro_dominante', 'membro_acometido']:
#             if key in data:
#                 print(f"Atualizando {key} para: {data[key]}")
#                 pacientes_df.at[id, key] = data[key]

#         # Salve o DataFrame no arquivo CSV
#         print("Salvando alterações no arquivo CSV...")
#         pacientes_df.to_csv('registros.csv', index=False)

#         print(f"Paciente com ID {id} atualizado com sucesso.")
#         return jsonify({'success': True}), 200

#     except Exception as e:
#         print(f"Erro ao editar paciente: {e}")
#         return jsonify({'error': 'Erro no servidor', 'details': str(e)}), 500

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
@app.route("/testes", methods=["GET", "POST"])
def testes():
    global df, paciente_nome, dataHoje, n_coleta_ruim, n_coleta_bom, n_coleta_forca, teste_selecionado
    
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
        n_coleta_ruim=n_coleta_ruim,
        n_coleta_bom=n_coleta_bom,
        n_coleta_forca=n_coleta_forca,
        teste_selecionado=teste_selecionado
    )

@app.route("/testes/iniciar-coleta", methods=["GET", "POST"])
def iniciar_coleta():
    global paciente_nome, dataHoje, teste_selecionado, paciente_nome, n_coleta_ruim, n_coleta_bom, n_coleta_forca
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
        n_coleta_ruim=n_coleta_ruim,
        n_coleta_bom=n_coleta_bom,
        n_coleta_forca=n_coleta_forca
    )


# Rota para a tela de Coleta do braço parético
@app.route("/testes/paretico")
def coleta_paretico():
    global paciente_nome, dataHoje, coletaRuim, teste_selecionado
    return render_template(
        "[1.2] paretico.html", 
        paciente_nome=paciente_nome,
        coletaRuim=coletaRuim,
        dataHoje=dataHoje,
        teste_selecionado=teste_selecionado
        )

@app.route("/incrementar_paretico", methods=["POST"])
def incrementar_paretico():
    global n_coleta_ruim
    n_coleta_ruim += 1
    return redirect(url_for("testes"))

# Rota para a tela de Coleta do braço saudável
@app.route("/testes/saudavel")
def coleta_saudavel():
    global paciente_nome, dataHoje, coletaBom, teste_selecionado
    return render_template(
        "[1.3] saudavel.html", 
        paciente_nome=paciente_nome,
        coletaBom=coletaBom,
        dataHoje=dataHoje,
        teste_selecionado=teste_selecionado
        )

@app.route("/incrementar_saudavel", methods=["POST"])
def incrementar_saudavel():
    global n_coleta_bom
    n_coleta_bom += 1
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

# Iniciar o servidor Flask
def iniciar_servidor():
    app.run(debug=False, port=5000, use_reloader=False)

# Abrir o PyWebview com a aplicação
if __name__ == "__main__":
    app.jinja_env.globals.update(enumerate=enumerate)
    threading.Thread(target=iniciar_servidor, daemon=True).start()
    webview.create_window("NHPT+", "http://127.0.0.1:5000")
    webview.start()
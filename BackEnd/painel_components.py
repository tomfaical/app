import serial
import pandas as pd
from datetime import datetime
import streamlit as st
import hydralit_components as hc
import time
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px
import os
import re






def start_session_states():
    if "resgatar_paciente" not in st.session_state:
        st.session_state.resgatar_paciente = False
    if "novo_paciente" not in st.session_state:
        st.session_state.novo_paciente = False
    if "selected_patient" not in st.session_state:
        st.session_state.selected_patient = None
    
    if "ser" not in st.session_state:
        st.session_state.ser = None
    if "coletas" not in st.session_state:
        st.session_state.coletas = {}  # Dicionário para armazenar DataFrames de coletas
    if "coletando" not in st.session_state:
        st.session_state.coletando = False  # Estado da coleta

    if "iterador_paretico_acc" not in st.session_state:
        st.session_state.iterador_paretico_acc = 1  # Iterador para braço parético
    if "iterador_saudavel_acc" not in st.session_state:
        st.session_state.iterador_saudavel_acc = 1  # Iterador para braço saudável
    if "iterador_paretico_forca" not in st.session_state:
        st.session_state.iterador_paretico_forca = 1  # Iterador para braço parético
    if "iterador_saudavel_forca" not in st.session_state:
        st.session_state.iterador_saudavel_forca = 1  # Iterador para braço saudável

    if "dfs_aceleracao" not in st.session_state:
        st.session_state.dfs_aceleracao = {}          # Um dicionário para armazenar dfs
    if "dfs_forca" not in st.session_state:
        st.session_state.dfs_forca = {}               # Um dicionário para armazenar dfs
    if "nome_paciente" not in st.session_state:
        st.session_state.nome_paciente = ''
    if "df_aceleracao" not in st.session_state:  
        st.session_state.df_aceleracao = pd.DataFrame(columns=[
            "tempo", "ax", "ay", "az",'a_abs', 
            'jerk_x', 'jerk_y', 'jerk_z', 'jerk_abs', 
            "condicao", 'lado', 'lateralidade', "n_coleta"
            ]) 
    if "df_forca" not in st.session_state:
        st.session_state.df_forca = pd.DataFrame(columns=[
            'tempo', 'forca', 'df_dt', 'condicao', 'lado', 'lateralidade', 'n_coleta'])

    if 'condicao_memb_esq' not in st.session_state:
        st.session_state.condicao_memb_esq = None
    if 'condicao_memb_dir' not in st.session_state:
        st.session_state.condicao_memb_dir = None
    if 'lateralidade_memb_esq' not in st.session_state:
        st.session_state.lateralidade_memb_esq = None
    if 'lateralidade_memb_dir' not in st.session_state:
        st.session_state.lateralidade_memb_dir = None
    
    if "index_paciente" not in st.session_state:
        st.session_state.index_paciente = None
    if "index_condicao_esq" not in st.session_state:
        st.session_state.index_condicao_esq = None
    if "index_lateralidade_esq" not in st.session_state:
        st.session_state.index_lateralidade_esq = None
    if "index_condicao_dir" not in st.session_state:
        st.session_state.index_condicao_dir = None
    if "index_lateralidade_dir" not in st.session_state:
        st.session_state.index_lateralidade_dir = None
start_session_states()


# Função para conectar à ESP32
def connect_to_serial(port, baudrate):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        st.success(f"Sensor conectado com sucesso (porta {port})")
        return ser
    except serial.SerialException as e:
        st.error(f"Erro ao conectar ao sensor: {e}")
        return None
    

# Função genérica para iniciar a coleta
def start_collection(condicao, teste, lado, lateralidade):
    st.session_state.coletando = True

    if teste == 'Jerk':
        iterador = (
            st.session_state.iterador_paretico_acc
            if condicao == "parético"
            else st.session_state.iterador_saudavel_acc
        )

        st.success(f"Iniciando coleta para braço {condicao} (Coleta {iterador})")
        receive_data_from_esp32_serial(condicao, lado, lateralidade)


    if teste == 'Força':
        iterador = (
        st.session_state.iterador_paretico_forca
        if condicao == "parético"
        else st.session_state.iterador_saudavel_forca
        )

        st.success(f"Iniciando coleta para braço {condicao} (Coleta {iterador})")
        receive_data_from_arduino(condicao, lado, lateralidade)
    


# Função para receber dados do ESP32
def receive_data_from_esp32_serial(condicao, lado , lateralidade):
    ser = st.session_state.ser
    if not ser:
        st.error("Conexão serial não encontrada. Certifique-se de estar conectado.")
        return

    iterador = (
        st.session_state.iterador_paretico_acc
        if condicao == "parético"
        else st.session_state.iterador_saudavel_acc
    )

    try:
        st.info(f"Recebendo dados do ESP32 para braço {condicao}")
        previous_row_1 = None 
        previous_row_2 = None 
        current_row = None
        next_row_1 = None
        next_row_2 = None

        df_temp = pd.DataFrame(columns=[
            "tempo", "ax", "ay", "az", "a_abs", 
            "jerk_x", "jerk_y", "jerk_z", "jerk_abs", 
            "condicao", 'lado', 'lateralidade', "n_coleta"
        ])
        chart_placeholder_aceleracao = st.empty()
        

        while st.session_state.coletando == True:
            data = ser.readline().decode("utf-8").strip()
            if data:
                try:
                    parts = data.split(",")
                    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]
                    ax = float(parts[0].split(":")[1].strip())
                    ay = float(parts[1].split(":")[1].strip())
                    az = float(parts[2].split(":")[1].strip())
                    a_abs = ((ax**2 + ay**2 + az**2)**0.5)-9.81
                    jerk_x = jerk_y = jerk_z = jerk_abs = None
                    
                    #Derivada comum:
                    # if previous_row_1 is not None:
                    #     delta_t = (
                    #         datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S.%f') 
                    #         - datetime.strptime(previous_row_1["tempo"], '%d/%m/%Y %H:%M:%S.%f')
                    #     ).total_seconds()

                    #     if delta_t > 0:  # Evita divisão por zero
                    #         jerk_x = (ax - previous_row_1["ax"]) / delta_t
                    #         jerk_y = (ay - previous_row_1["ay"]) / delta_t
                    #         jerk_z = (az - previous_row_1["az"]) / delta_t
                    #         jerk_abs = (jerk_x**2 + jerk_y**2 + jerk_z**2)**0.5

                    

                    #Derivada de alta acurácia centrada (5 pontos):
                    if previous_row_1 is not None and previous_row_2 is not None and next_row_1 is not None and next_row_2 is not None:
                        
                        delta_t = (
                            datetime.strptime(next_row_2["tempo"], '%d/%m/%Y %H:%M:%S.%f') 
                            - datetime.strptime(previous_row_2["tempo"], '%d/%m/%Y %H:%M:%S.%f')
                        ).total_seconds()

                        if delta_t > 0:  # Evita divisão por zero
                            jerk_x = (-next_row_2['ax'] + 8*next_row_1['ax'] - 8*previous_row_1['ax'] + previous_row_2['ax']) / (12 * delta_t)
                            jerk_y = (-next_row_2['ay'] + 8*next_row_1['ay'] - 8*previous_row_1['ay'] + previous_row_2['ay']) / (12 * delta_t)
                            jerk_z = (-next_row_2['az'] + 8*next_row_1['az'] - 8*previous_row_1['az'] + previous_row_2['az']) / (12 * delta_t)
                            jerk_abs = (jerk_x**2 + jerk_y**2 + jerk_z**2)**0.5

                            # Atualiza os valores de jerk para previous_row_1 no DataFrame
                            st.session_state.df_aceleracao.loc[st.session_state.df_aceleracao.index[-2], ['jerk_x', 'jerk_y', 'jerk_z', 'jerk_abs']] = [
                                jerk_x, jerk_y, jerk_z, jerk_abs]
                            
                            df_temp.loc[df_temp.index[-2], ['jerk_x', 'jerk_y', 'jerk_z', 'jerk_abs']] = [
                                jerk_x, jerk_y, jerk_z, jerk_abs]



                    # Adiciona ao DataFrame da coleta atual
                    # Adiciona ao DataFrame global com as novas colunas
                    new_row = {
                        "tempo": timestamp,
                        "ax": ax,
                        "ay": ay,
                        "az": az,
                        "a_abs": a_abs,      
                        "jerk_x": None,    
                        "jerk_y": None,    
                        "jerk_z": None,    
                        "jerk_abs": None,
                        "condicao": condicao,
                        "lado": lado,
                        'lateralidade': lateralidade,
                        "n_coleta": iterador,
                    }
                    st.session_state.df_aceleracao = pd.concat(
                        [st.session_state.df_aceleracao, pd.DataFrame([new_row])],
                        ignore_index=True,
                    )
                    
                    df_temp = pd.concat(
                        [df_temp, pd.DataFrame([new_row])],
                        ignore_index=True,
                    )
                    
                    ### LINE_PLOT SIMPLES
                    with chart_placeholder_aceleracao.container():
                        show_plots_aceleracao(df_temp)
                    
                    previous_row_2 = previous_row_1
                    previous_row_1 = current_row
                    current_row = next_row_1
                    next_row_1 = next_row_2
                    next_row_2 = new_row
                    store_data('Jerk')
                    
                except (IndexError, ValueError):
                    st.error(f"Erro ao processar os dados: {data}")
    except KeyboardInterrupt:
        st.warning("Coleta interrompida manualmente.")
    finally:
        ser.close()
        st.info(f"Conexão serial fechada para braço {condicao}")


def receive_data_from_arduino(condicao, lado, lateralidade):
    ser = st.session_state.ser  # Conexão serial já estabelecida fora da função
    if not ser:
        st.error("Conexão serial não encontrada. Certifique-se de que o Arduino está conectado.")
        return    

    # Determina o iterador apropriado
    iterador = (
        st.session_state.iterador_paretico_forca
        if condicao == "parético"
        else st.session_state.iterador_saudavel_forca
    )

    st.session_state.coletando = True
    st.info(f"Iniciando coleta de força ({condicao}, Coleta {iterador})...")
    previous_row_1 = None 
    previous_row_2 = None 
    current_row = None
    next_row_1 = None
    next_row_2 = None

    chart_placeholder_forca = st.empty()
    df_temp = pd.DataFrame(columns=[
            'tempo', 'forca', 'df_dt', 'condicao', 'lado', 'lateralidade', 'n_coleta'
            ])
    
    try:
        while st.session_state.coletando:
            data = ser.readline().decode("utf-8").strip()
            if data:
                try:
                    # Processa os dados enviados pelo Arduino
                    if "Força:" in data:
                        forca = float(data.split(":")[1].strip().split(" ")[0])  
                        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]

                        #Derivada de alta acurácia centrada (5 pontos):
                        if previous_row_1 is not None and previous_row_2 is not None and next_row_1 is not None and next_row_2 is not None:
                            
                            delta_t = (
                                datetime.strptime(next_row_2["tempo"], '%d/%m/%Y %H:%M:%S.%f') 
                                - datetime.strptime(previous_row_2["tempo"], '%d/%m/%Y %H:%M:%S.%f')
                            ).total_seconds()

                            if delta_t > 0:  # Evita divisão por zero
                                df_dt = (-next_row_2['forca'] 
                                        + 8*next_row_1['forca'] 
                                        - 8*previous_row_1['forca'] 
                                        + previous_row_2['forca']) / (12 * delta_t)
                                
                                # Atualiza os valores de jerk para previous_row_1 no DataFrame
                                st.session_state.df_forca.loc[st.session_state.df_forca.index[-2], ['df_dt']] = [df_dt]
                                
                                df_temp.loc[df_temp.index[-2], ['df_dt']] = [df_dt]

                        # Adiciona os dados ao DataFrame
                        new_row = {
                            "tempo": timestamp,
                            "forca": forca,
                            "df_dt": None,
                            "condicao": condicao,
                            'lado': lado,
                            'lateralidade': lateralidade,
                            "n_coleta": iterador
                        }
                        st.session_state.df_forca = pd.concat(
                            [st.session_state.df_forca, pd.DataFrame([new_row])],
                            ignore_index=True,
                        )

                        df_temp = pd.concat(
                            [df_temp, pd.DataFrame([new_row])],
                            ignore_index=True,
                        )

                        with chart_placeholder_forca.container():
                            show_plots_forca(df_temp)
                        
                        previous_row_2 = previous_row_1
                        previous_row_1 = current_row
                        current_row = next_row_1
                        next_row_1 = next_row_2
                        next_row_2 = new_row
                        store_data('Força')
                        
                except (IndexError, ValueError) as e:
                    st.error(f"Erro ao processar os dados: {data}")

    except KeyboardInterrupt:
        st.warning("Conexão interrompida manualmente.")
    finally:
        ser.close()
        st.info(f"Conexão serial encerrada para a coleta de força ({condicao}).")


# Função para encerrar a coleta
def stop_collection(condicao, teste):
    if st.session_state.coletando == True:
        st.session_state.coletando = False
        
        if teste == 'Jerk':
            if condicao == "parético":
                st.session_state.iterador_paretico_acc += 1
            elif condicao == "saudável":
                st.session_state.iterador_saudavel_acc += 1
        
        elif teste == 'Força':
            if condicao == "parético":
                st.session_state.iterador_paretico_forca += 1
            elif condicao == "saudável":
                st.session_state.iterador_saudavel_forca += 1
        
        st.success(f"Coleta para braço {condicao} encerrada.")
    else:
        st.warning("Nenhuma coleta está ativa.")


def disconnect_from_serial():
    if st.session_state.ser:
        try:
            st.session_state.ser.close()  # Fecha a conexão serial
            st.session_state.ser = None  # Redefine o estado da conexão
            st.success("Desconectado do Bluetooth com sucesso!")
        except Exception as e:
            st.error(f"Erro ao desconectar: {e}")
    else:
        st.warning("Nenhuma conexão ativa.")


def show_plots_aceleracao(df):
    n = 500
    chart_data = df.tail(n).copy()
    
    chart_data = chart_data[["tempo", "ax", "ay", "az", "a_abs"]]
    chart_data["tempo"] = pd.to_datetime(chart_data["tempo"], format="%d/%m/%Y %H:%M:%S.%f")
    chart_data = chart_data.set_index("tempo")  # Define o índice como tempo

    chart_data2 = df[["tempo", "a_abs"]].tail(n).copy()
    chart_data2["tempo"] = pd.to_datetime(chart_data2["tempo"], format="%d/%m/%Y %H:%M:%S.%f")
    chart_data2 = chart_data2.set_index("tempo")

    ### RGBs:
    red, green, blue = '#ff3b00', '#9dff00', '#009eff'
    purple = '#7d00ff'
    st.line_chart(chart_data, color=[purple, red, green, blue], x_label='Tempo', y_label= 'Aceleração (m/s^2)')
    st.line_chart(chart_data2, color= purple, x_label='Tempo', y_label= 'Aceleração (m/s^2)')
    

def show_plots_forca(df):
    n = 100
    chart_data = df.tail(n)
    st.bar_chart(
        chart_data, x= 'tempo', y= 'forca', 
        x_label='Tempo', y_label='Força (N)')
    st.bar_chart(
        chart_data, x= 'tempo', y= 'df_dt', 
        x_label='Tempo', y_label='Taxa de Desenvolvimento de Força (N/s)')


def store_data(teste):
    if teste == 'Jerk':
        df_completo = st.session_state.df_aceleracao
    elif teste == 'Força':
        df_completo = st.session_state.df_forca
    
    for i in range((st.session_state.iterador_saudavel_acc)+1):
        nome_novo_df = f"df_coleta_{i}_saudavel"
        novo_df = df_completo[(df_completo['n_coleta'] == i) & (df_completo['condicao'] == 'saudável')]

        if not novo_df.empty and df_completo.equals(st.session_state.df_aceleracao):
            st.session_state.dfs_aceleracao[nome_novo_df] = novo_df
        elif not novo_df.empty and df_completo.equals(st.session_state.df_forca):
            st.session_state.dfs_forca[nome_novo_df] = novo_df
        

    for j in range((st.session_state.iterador_paretico_acc)+1):
        nome_novo_df = f"df_coleta_{j}_paretico"
        novo_df = df_completo[(df_completo['n_coleta'] == j) & (df_completo['condicao'] == 'parético')]
        
        if not novo_df.empty and df_completo.equals(st.session_state.df_aceleracao):
            st.session_state.dfs_aceleracao[nome_novo_df] = novo_df
        elif not novo_df.empty and df_completo.equals(st.session_state.df_forca):
            st.session_state.dfs_forca[nome_novo_df] = novo_df


def show_dfs(condicao, teste):
    if teste == 'Jerk':
        if condicao == 'Parético':
            condicao = 'paretico'
        if condicao == 'Saudável':
            condicao = 'saudavel'

        for nome_df, df in st.session_state.dfs_aceleracao.items():
            if nome_df.endswith(condicao):  
                st.subheader(f"Coleta {df['n_coleta'].iloc[0]}:", help= df['condicao'].iloc[0], anchor= False)
                st.write(df)  
                st.divider()
    
    if teste == 'Força':
        if condicao.lower() == 'parético':
            iterador = st.session_state.iterador_paretico_forca
        if condicao.lower() == 'saudável':
            iterador = st.session_state.iterador_saudavel_forca

        for num_coleta in range(0 ,iterador+1):
            df = st.session_state.df_forca
            df = df[(df['condicao'] == condicao.lower()) & (df['n_coleta'] == num_coleta)]
            if not df.empty:
                st.subheader(f"Coleta {num_coleta}:", help= condicao.upper(), anchor= False)
                st.write(df)  
                st.divider()
    

# Botão de download para o DataFrame
def make_csv(df):
    csv = df.to_csv(index=False)
    return csv


def change_names(name):
    name = name.replace("df_", "").replace("_", " ").title()
    return name


@st.dialog("TEM CERTEZA QUE DESEJA VOLTAR?", width='large')
def recomecar_operacao():
    # if st.button("Sair e salvar dados.", type= 'primary'):
    #     st.rerun()  
    if st.button("Retomar análise atual.", type= 'primary'):
        st.rerun()
    if st.button("Sair.", type= 'primary'):
        st.session_state.resgatar_paciente = False
        st.session_state.novo_paciente = False
        st.session_state.nome_paciente = ''
        st.rerun()


def read_all_csvs(folder_path):
    try:
        # Lista todos os arquivos na pasta
        all_files = os.listdir(folder_path)

        # Filtra apenas os arquivos com extensão .csv
        csv_files = []
        for file in all_files:
            if file.endswith('.csv'):
                csv_files.append(file)
        
        patient_files = {}
        for file in csv_files:
            identifier = extrair_nome(file)
            if identifier:
                if identifier not in patient_files:
                    patient_files[identifier] = []
                patient_files[identifier].append(file)

        return patient_files
    except FileNotFoundError:
        st.error("A pasta especificada não foi encontrada.")
        return {}


def extrair_nome(file_name):
    match = re.search(r'(jerk|forca)_(.*?)\.csv', file_name)  # Procura por 'jerk_' ou 'forca_' e captura o identificador
    if match:
        return match.group(2)  # Retorna apenas o identificador extraído
    return None
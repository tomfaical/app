import serial
import pandas as pd
from datetime import datetime
import streamlit as st
import hydralit_components as hc
import time
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px





def start_session_states():
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

    if "dfs" not in st.session_state:
        st.session_state.dfs = {}  # Um dicionário para armazenar dfs
    if "nome_paciente" not in st.session_state:
        st.session_state.nome_paciente = None
    if "df_aceleracao" not in st.session_state:  
        st.session_state.df_aceleracao = pd.DataFrame(columns=[
            "tempo", "ax", "ay", "az",'a_abs', 
            'jerk_x', 'jerk_y', 'jerk_z', 'jerk_abs', 
            "condicao", "n_coleta"
            ]) 
    if "df_forca" not in st.session_state:
        st.session_state.df_forca = pd.DataFrame(columns=['tempo', 'forca', 'condicao', 'n_coleta'])

    if 'condicao_memb_esq' not in st.session_state:
        st.session_state.condicao_memb_esq = None
    if 'condicao_memb_dir' not in st.session_state:
        st.session_state.condicao_memb_dir = None
    if 'lateralidade_memb_esq' not in st.session_state:
        st.session_state.lateralidade_memb_esq = None
    if 'lateralidade_memb_dir' not in st.session_state:
        st.session_state.lateralidade_memb_dir = None
    
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
def start_collection(condicao, teste):
    st.session_state.coletando = True

    if teste == 'Jerk':
        iterador = (
            st.session_state.iterador_paretico_acc
            if condicao == "parético"
            else st.session_state.iterador_saudavel_acc
        )

        st.success(f"Iniciando coleta para braço {condicao} (Coleta {iterador})")
        receive_data_from_esp32_serial(condicao)


    if teste == 'Força':
        iterador = (
        st.session_state.iterador_paretico_forca
        if condicao == "parético"
        else st.session_state.iterador_saudavel_forca
        )

        st.success(f"Iniciando coleta para braço {condicao} (Coleta {iterador})")
        receive_data_from_arduino(condicao)
    


# Função para receber dados do ESP32
def receive_data_from_esp32_serial(condicao):
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
            "tempo", "ax", "ay", "az", "a_abs", "jerk_x", "jerk_y", "jerk_z", "jerk_abs", "condicao", "n_coleta"
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
                    if previous_row_1 is not None:
                        delta_t = (
                            datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S.%f') 
                            - datetime.strptime(previous_row_1["tempo"], '%d/%m/%Y %H:%M:%S.%f')
                        ).total_seconds()

                        if delta_t > 0:  # Evita divisão por zero
                            jerk_x = (ax - previous_row_1["ax"]) / delta_t
                            jerk_y = (ay - previous_row_1["ay"]) / delta_t
                            jerk_z = (az - previous_row_1["az"]) / delta_t
                            jerk_abs = (jerk_x**2 + jerk_y**2 + jerk_z**2)**0.5

                    

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
                                jerk_x, jerk_y, jerk_z, jerk_abs
                            ]
                            df_temp.loc[df_temp.index[-2], ['jerk_x', 'jerk_y', 'jerk_z', 'jerk_abs']] = [
                                jerk_x, jerk_y, jerk_z, jerk_abs
                            ]



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
                        show_plots(df_temp)
                    
                    previous_row_2 = previous_row_1
                    previous_row_1 = current_row
                    current_row = next_row_1
                    next_row_1 = next_row_2
                    next_row_2 = new_row
                    store_data()
                    
                except (IndexError, ValueError):
                    st.error(f"Erro ao processar os dados: {data}")
    except KeyboardInterrupt:
        st.warning("Coleta interrompida manualmente.")
    finally:
        ser.close()
        st.info(f"Conexão serial fechada para braço {condicao}")


def receive_data_from_arduino(condicao):
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

    chart_placeholder_forca = st.empty()
    try:
        while st.session_state.coletando:
            data = ser.readline().decode("utf-8").strip()
            if data:
                try:
                    # Processa os dados enviados pelo Arduino
                    if "Força:" in data:
                        forca = float(data.split(":")[1].strip().split(" ")[0])  
                        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]

                        # Adiciona os dados ao DataFrame
                        new_row = {
                            "tempo": timestamp,
                            "forca": forca,
                            "condicao": condicao,
                            "n_coleta": iterador,
                        }
                        st.session_state.df_forca = pd.concat(
                            [st.session_state.df_forca, pd.DataFrame([new_row])],
                            ignore_index=True,
                        )

                        # Exibe os dados recebidos
                        st.write(st.session_state.df_forca)

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


def show_plots(df):
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
    

def store_data():
    df_completo = st.session_state.df_aceleracao

    for i in range((st.session_state.iterador_saudavel_acc)+1):
        nome_novo_df = f"df_coleta_{i}_saudavel"
        novo_df = df_completo[(df_completo['n_coleta'] == i) & (df_completo['condicao'] == 'saudável')]

        if not novo_df.empty:
            st.session_state.dfs[nome_novo_df] = novo_df
            # st.success(f"df {nome_novo_df} criado com sucesso!")
        
    for j in range((st.session_state.iterador_paretico_acc)+1):
        nome_novo_df = f"df_coleta_{j}_paretico"
        novo_df = df_completo[(df_completo['n_coleta'] == j) & (df_completo['condicao'] == 'parético')]
        if not novo_df.empty:
            st.session_state.dfs[nome_novo_df] = novo_df
            # st.success(f"df {nome_novo_df} criado com sucesso!")


def show_dfs(condicao):
    for nome_df, df in st.session_state.dfs.items():
        if nome_df.endswith(condicao):  
            st.subheader(f"Coleta {df['n_coleta'].iloc[0]}:", help= df['condicao'].iloc[0], anchor= False)
            st.write(df)  
            st.divider()


# Botão de download para os gráficos
def download_graphic():
    # Exemplo fictício para incluir dados de gráfico
    st.download_button(
        label="Download do Gráfico",
        data="Gráfico gerado em tempo real",
        file_name="grafico.txt"
    )


# Botão de download para o DataFrame
def download_dataframe(df):
    csv = df.to_csv(index=False)
    return csv


def change_names(name):
    name = name.replace("df_", "").replace("_", " ").title()
    return name




def criar_forca():
    import pandas as pd
    import random
    from datetime import datetime, timedelta
    columns = ["tempo", "peso", "forca", "condicao", "n_coleta"]
    df = pd.DataFrame(columns=columns)
    
    # Gera 100 linhas de dados aleatórios
    for i in range(100):
        timestamp = (datetime.now() - timedelta(seconds=i)).strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]
        peso = random.uniform(0, 100)  # Massa em kg
        forca = peso * 9.81  # Força em Newtons
        condicao = random.choice(["parético", "saudável"])
        n_coleta = random.randint(1, 10)
        
        new_row = {
            "tempo": timestamp,
            "peso": peso,
            "forca": forca,
            "condicao": condicao,
            "n_coleta": n_coleta,
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    return df
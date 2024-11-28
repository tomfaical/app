import pandas as pd
import serial
from datetime import datetime

def connect_to_serial(port, baudrate):
    """
    Tenta conectar a uma porta serial com a taxa de transmissão especificada.

    :param port: Nome da porta serial (ex.: 'COM3', '/dev/ttyUSB0')
    :param baudrate: Taxa de transmissão (ex.: 9600)
    :return: Objeto da conexão serial em caso de sucesso, ou None em caso de falha
    """
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"Sensor conectado com sucesso (porta {port})")
        return ser
    except serial.SerialException as e:
        print(f"Erro ao conectar ao sensor: {e}")
        return None


def receive_data_from_esp32_serial(ser, condicao, iterador):
    """
    Recebe dados de um ESP32 conectado via serial e armazena em um DataFrame.

    :param ser: Objeto da conexão serial já estabelecida
    :param condicao: Condição (ex.: 'parético', 'saudável')
    :param iterador: Número da coleta atual
    :return: DataFrame com os dados coletados
    """
    # Inicializa o DataFrame com as colunas apropriadas
    df_esp = pd.DataFrame(columns=["tempo", "ax", "ay", "az", "condicao", "n_coleta"])
    
    try:
        print(f"Iniciando coleta de dados do ESP32 para braço {condicao} (Coleta {iterador})...")
        while True:
            # Lê a linha da conexão serial
            data = ser.readline().decode("utf-8").strip()
            if data:
                try:
                    # Divide os dados recebidos e extrai os valores
                    parts = data.split(",")
                    ax = float(parts[0].split(":")[1].strip())
                    ay = float(parts[1].split(":")[1].strip())
                    az = float(parts[2].split(":")[1].strip())
                    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]

                    # Cria um novo registro
                    new_row = {
                        "tempo": timestamp,
                        "ax": ax,
                        "ay": ay,
                        "az": az,
                        "condicao": condicao,
                        "n_coleta": iterador
                    }

                    # Adiciona ao DataFrame
                    df_esp = pd.concat([df_esp, pd.DataFrame([new_row])], ignore_index=True)

                except (IndexError, ValueError):
                    print(f"Erro ao processar os dados: {data}")
                    df_esp = False

    except KeyboardInterrupt:
        print("Coleta interrompida manualmente.")
        df_esp = False
    finally:
        ser.close()
        print(f"Conexão serial encerrada para a coleta do braço {condicao}.")
        df_esp = False
    
    return df_esp


def receive_data_from_arduino(ser, condicao, iterador):
    """
    Recebe dados de um Arduino conectado via serial e armazena em um DataFrame.

    :param ser: Objeto da conexão serial já estabelecida
    :param condicao: Condição (ex.: 'parético', 'saudável')
    :param iterador: Número da coleta atual
    :return: DataFrame com os dados coletados
    """
    # Inicializa o DataFrame com as colunas apropriadas
    df_arduino = pd.DataFrame(columns=["tempo", "forca", "condicao", "n_coleta"])

    try:
        print(f"Iniciando coleta de força do Arduino ({condicao}, Coleta {iterador})...")
        while True:
            # Lê a linha da conexão serial
            data = ser.readline().decode("utf-8").strip()
            if data:
                try:
                    # Verifica se a string contém "Força:"
                    if "Força:" in data:
                        # Extrai o valor de força
                        forca = float(data.split(":")[1].strip().split(" ")[0])
                        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]

                        # Cria um novo registro
                        new_row = {
                            "tempo": timestamp,
                            "forca": forca,
                            "condicao": condicao,
                            "n_coleta": iterador
                        }

                        # Adiciona ao DataFrame
                        df_arduino = pd.concat([df_arduino, pd.DataFrame([new_row])], ignore_index=True)

                except (IndexError, ValueError):
                    print(f"Erro ao processar os dados: {data}")
                    df_arduino = False

    except KeyboardInterrupt:
        print("Coleta interrompida manualmente.")
        df_arduino = False
    finally:
        ser.close()
        print(f"Conexão serial encerrada para a coleta de força ({condicao}).")
        df_arduino = False
    
    return df_arduino

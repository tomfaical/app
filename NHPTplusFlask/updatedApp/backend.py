import serial
import pandas as pd
import os
from datetime import datetime

class ESPHandler:
    def __init__(self):
        self.ser = None
        self.df = pd.DataFrame(columns=["tempo", "ax", "ay", "az", "jerk_abs", "condicao"])

    # def connect_to_esp(self, port: str, baudrate: int = 115200):
    #     """Estabelece a conexão com a ESP32 via porta serial."""
    #     try:
    #         self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=1)
    #         return True
    #     except Exception as e:
    #         print(f"Erro ao conectar à ESP: {e}")
    #         return False

    # def disconnect_from_esp(self):
    #     """Fecha a conexão com a ESP32."""
    #     if self.ser and self.ser.is_open:
    #         self.ser.close()

    # def receive_data(self, condicao: str):
    #     """Recebe dados da ESP, trata e armazena no DataFrame."""
    #     try:
    #         if self.ser and self.ser.is_open:
    #             raw_data = self.ser.readline().decode("utf-8").strip()
    #             if raw_data:
    #                 values = [float(i) for i in raw_data.split(",")]
    #                 if len(values) == 4:  # Supondo que são [tempo, ax, ay, az]
    #                     tempo, ax, ay, az = values
    #                     jerk_abs = (ax**2 + ay**2 + az**2)**0.5
    #                     self.df.loc[len(self.df)] = [tempo, ax, ay, az, jerk_abs, condicao]
    #                     return True
    #         return False
    #     except Exception as e:
    #         print(f"Erro ao receber dados: {e}")
    #         return False

    # def save_data_to_csv(self, filename="dados_coleta.csv"):
    #     """Salva o DataFrame em um arquivo CSV."""
    #     self.df.to_csv(filename, index=False)

    # def load_data_from_csv(self, filename="dados_coleta.csv"):
    #     """Carrega dados de um arquivo CSV existente."""
    #     if os.path.exists(filename):
    #         self.df = pd.read_csv(filename)

    # def get_dataframe(self):
    #     """Retorna o DataFrame atual para manipulação."""
    #     return self.df


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

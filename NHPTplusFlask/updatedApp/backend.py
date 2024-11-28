import serial
import pandas as pd
import os

class ESPHandler:
    def __init__(self):
        self.ser = None
        self.df = pd.DataFrame(columns=["tempo", "ax", "ay", "az", "jerk_abs", "condicao"])

    def connect_to_esp(self, port: str, baudrate: int = 115200):
        """Estabelece a conexão com a ESP32 via porta serial."""
        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=1)
            return True
        except Exception as e:
            print(f"Erro ao conectar à ESP: {e}")
            return False

    def disconnect_from_esp(self):
        """Fecha a conexão com a ESP32."""
        if self.ser and self.ser.is_open:
            self.ser.close()

    def receive_data(self, condicao: str):
        """Recebe dados da ESP, trata e armazena no DataFrame."""
        try:
            if self.ser and self.ser.is_open:
                raw_data = self.ser.readline().decode("utf-8").strip()
                if raw_data:
                    values = [float(i) for i in raw_data.split(",")]
                    if len(values) == 4:  # Supondo que são [tempo, ax, ay, az]
                        tempo, ax, ay, az = values
                        jerk_abs = (ax**2 + ay**2 + az**2)**0.5
                        self.df.loc[len(self.df)] = [tempo, ax, ay, az, jerk_abs, condicao]
                        return True
            return False
        except Exception as e:
            print(f"Erro ao receber dados: {e}")
            return False

    def save_data_to_csv(self, filename="dados_coleta.csv"):
        """Salva o DataFrame em um arquivo CSV."""
        self.df.to_csv(filename, index=False)

    def load_data_from_csv(self, filename="dados_coleta.csv"):
        """Carrega dados de um arquivo CSV existente."""
        if os.path.exists(filename):
            self.df = pd.read_csv(filename)

    def get_dataframe(self):
        """Retorna o DataFrame atual para manipulação."""
        return self.df

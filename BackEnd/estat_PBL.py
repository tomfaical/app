import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks, freqs
from scipy.stats import shapiro, pearsonr, spearmanr, ttest_ind
from sklearn.linear_model import LinearRegression
from scipy.fft import fft, fftfreq
import pandas as pd

# Função de filtragem Butterworth
def filtro_butterworth(data, freq_corte=0.1, fs=1.0, order=5):
    freq_nyquist = 0.5 * fs
    freq_corte_normalizado = freq_corte / freq_nyquist
    b, a = butter(order, freq_corte_normalizado, btype='low', analog=False)
    return filtfilt(b, a, data)

# Função de métricas estatísticas
def estatisticas_calculadas(data):
    mean = np.mean(data)
    sd = np.std(data, ddof=1)
    coef_var = sd / mean
    return mean, sd, coef_var

def phi(m):
        count = 0
        for i in range(N - m):
            template = data[i:i + m]  # Segmento de comprimento m
            for j in range(i + 1, N - m + 1):
                comparison = data[j:j + m]  # Outro segmento
                if np.all(np.abs(template - comparison) <= r):  # Verifica se todos os pontos estão dentro da tolerância
                    count += 1
        return count / (N - m)  # Razão de pares similares

# Função de entropia
def entropia(data, m=2, r=0.2):
    N = len(data)
    r *= np.std(data)  # Define a tolerância como uma fração do desvio padrão
       
    # Razões para padrões de comprimento m e m+1
    phi_m = phi(m)
    phi_m1 = phi(m + 1)
    
    # Evitar divisão por zero
    if phi_m == 0 or phi_m1 == 0:
        return np.inf  # Indica que o sinal é extremamente regular ou caótico
    
    return -np.log(phi_m1 / phi_m)

# Função para análise de fadiga
def analise_fadiga(data):
    picos, _ = find_peaks(data, height=0.5)
    amplitude_picos = data[picos]
    fadiga_indice = (amplitude_picos[0] - amplitude_picos[-1]) / amplitude_picos[0] if len(amplitude_picos) > 1 else 0
    return len(picos), fadiga_indice

# Função para regressão
def regressao(x, y):
    model = LinearRegression().fit(x.reshape(-1, 1), y)
    r2 = model.score(x.reshape(-1, 1), y)
    return model, r2

# Carregar os dados CSV usando pandas

df_carol = pd.read_csv("C:/Users/luizg/OneDrive/PBL/dados_Carolina_Aizawa.csv", parse_dates=['tempo'])
df_ana_laura = pd.read_csv("C:/Users/luizg/OneDrive/PBL/dados_Ana_Laura_Andrade.csv", parse_dates=['tempo'])
df = df_carol
df = df[['tempo', 'ax', 'ay', 'az', 'a_abs']]  # Selecionando as colunas necessárias

# Definir as variáveis de tempo e aceleração
tempo = (df['tempo'] - df['tempo'].iloc[0]).dt.total_seconds()  # Convertendo o tempo para segundos
aceleracao_x = df['ax'].values
aceleracao_y = df['ay'].values
aceleracao_z = df['az'].values
aceleracao_abs = df['a_abs'].values

# Filtrando os dados de aceleração
aceleracao_filtrada = filtro_butterworth(aceleracao_abs)

# Estatísticas Descritivas para Aceleração
mean, sd, coef_var = estatisticas_calculadas(aceleracao_filtrada)
print(f"Aceleração - Média: {mean}, Desvio Padrão: {sd}, Coeficiente de Variação: {coef_var}")

# Teste de Normalidade
stat, p = shapiro(aceleracao_filtrada)
print(f"Aceleração - Teste de Normalidade: p={p}")

# Análise de Fadiga
n_picos, indice_fadiga = analise_fadiga(aceleracao_filtrada)
print(f"Aceleração - Número de Picos: {n_picos}, Índice de Fadiga: {indice_fadiga}")

# Transformada de Fourier para Aceleração
T = tempo[1] - tempo[0]  # Intervalo de amostragem
N = len(aceleracao_filtrada)
fft_values = np.abs(fft(aceleracao_filtrada))
freqs = fftfreq(N, T)

fft_values[0] = 0

plt.figure(1)
plt.plot(freqs[:N // 2], fft_values[:N // 2])
plt.title("FFT - Aceleração")
plt.xlabel("Frequência (Hz)")
plt.ylabel("Amplitude")
plt.show(block=False)

################## Jerk ##################

# Derivação numérica do módulo da aceleração para obter a velocidade
aceleracao_abs_derivada = np.gradient(aceleracao_abs, tempo)  # Derivada da aceleração

# Derivação novamente para calcular o Jerk
jerk_signal = np.gradient(aceleracao_abs_derivada, tempo)

# Filtrando o Jerk
jerk_filtrado = filtro_butterworth(jerk_signal)

# Estatísticas Descritivas para Jerk
mean, sd, coef_var = estatisticas_calculadas(jerk_filtrado)
print(f"Jerk - Média: {mean}, Desvio Padrão: {sd}, Coeficiente de Variação: {coef_var}")

# Teste de Normalidade
stat, p = shapiro(jerk_filtrado)
print(f"Jerk - Teste de Normalidade: p={p}")

# Análise de Fadiga
n_picos, indice_fadiga = analise_fadiga(jerk_filtrado)
print(f"Jerk - Número de Picos: {n_picos}, Índice de Fadiga: {indice_fadiga}")

# Transformada de Fourier para Jerk
N = len(jerk_filtrado)
fft_values = np.abs(fft(jerk_filtrado))

fft_values[0] = 0

plt.figure(2)
plt.plot(freqs[:N // 2], fft_values[:N // 2])
plt.title("FFT - Jerk")
plt.xlabel("Frequência (Hz)")
plt.ylabel("Amplitude")
plt.show(block=False)

################## Correlação ##################

# Correlação de Pearson entre Aceleração e Jerk
corr_a_j, p_a_j = pearsonr(aceleracao_filtrada, jerk_filtrado)
print(f"Correlação Aceleração-Jerk: r={corr_a_j:.2f}, p={p_a_j:.3f}")

############### Aceleração como preditor de Jerk ###############

# Regressão: Aceleração -> Jerk
X_a = aceleracao_filtrada.reshape(-1, 1)  # Variável independente
y_j = jerk_filtrado                        # Variável dependente

model_aj = LinearRegression().fit(X_a, y_j)
r2_aj = model_aj.score(X_a, y_j)
print(f"Regressão Aceleração-Jerk: R²={r2_aj:.2f}")

# Visualização da Regressão
plt.figure(3)
plt.scatter(aceleracao_filtrada, jerk_filtrado, alpha=0.5, label="Dados")
plt.plot(aceleracao_filtrada, model_aj.predict(X_a), color='red', label="Regressão")
plt.title("Regressão: Aceleração -> Jerk")
plt.xlabel("Aceleração")
plt.ylabel("Jerk")
plt.legend()
plt.show(block=False)

################## Força ##################

# Gerar dados de exemplo para força
force_signal = 10 * np.sin(2 * np.pi * tempo) + np.random.normal(scale=0.5, size=len(tempo))
force_filtered = filtro_butterworth(force_signal)

# Estatísticas Descritivas
mean, sd, coef_var = estatisticas_calculadas(force_filtered)
print(f"Força - Média: {mean}, Desvio Padrão: {sd}, Coeficiente de Variação: {coef_var}")

# Teste de Normalidade
stat, p = shapiro(force_filtered)
print(f"Força - Teste de Normalidade: p={p}")

# Análise de Fadiga
n_picos, indice_fadiga = analise_fadiga(force_filtered)
print(f"Força - Número de Picos: {n_picos}, Índice de Fadiga: {indice_fadiga}")

# Transformada de Fourier
N = len(force_filtered)
fft_values = np.abs(fft(force_filtered))

plt.figure(4)
plt.plot(freqs[:N // 2], fft_values[:N // 2])
plt.title("FFT - Força")
plt.xlabel("Frequência (Hz)")
plt.ylabel("Amplitude")
plt.show()
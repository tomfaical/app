import serial
import pandas as pd
from datetime import datetime
import streamlit as st
import hydralit_components as hc
import time
import altair as alt
import plotly.express as px

from painel_components import *
import warnings
import os
warnings.filterwarnings('ignore')
#os.chdir('diretorio')

### Porta BT para Aceleração e Força:
esp32_port_aceleracao = "COM9"
baudrate_aceleracao = 115200

arduino_port_forca = "COM10"
baudrate_forca = 9600

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')
st.title('Plataforma NHPT+')
st.text(' ')


# Inicialização de variáveis no session state
start_session_states()


menu_data = [
    {'icon': "fas fa-home", 'label': "Home"},
    {'icon': "fa fa-chart-line", 'label': "Gráficos"},
    {'icon': "fa fa-table", 'label': "Tabelas"}
    # {'icon': "fab fa-bluetooth-b", 'label': "Conexão"},
    # {'label': '~'*50},  
    # {'icon': "fa fa-code", 'label': "Log de eventos"}
]


over_theme = {'txc_inactive': '#FFFFFF'}
menu_id = hc.nav_bar(
    menu_definition=menu_data,
    override_theme=over_theme,
    hide_streamlit_markers=False,        # Deve ser desativado para melhor visualização
    sticky_nav=True,
    sticky_mode='pinned'
)

opcoes_teste = ["Jerk", "Força"]
opcoes_condicao = ["Parético", "Saudável"]
opcoes_lateralidade = ["Dominante", "Não-Dominante", "Ambi-Destro"]
# Aba Home
if menu_id == "Home":
    # Nome do paciente
    placeholder_nome = st.empty()
    if st.session_state.get("nome_paciente") is None:
        with placeholder_nome.container():            
            st.header("Digite o Nome do Paciente:")
            nome = st.text_input(" ")
            
                
            if nome:  # Apenas atualiza se o usuário digitar algo
                st.session_state.nome_paciente = nome
                placeholder_nome.empty()  # Limpa o placeholder para exibir o próximo conteúdo
                

    if st.session_state.nome_paciente:
        # Exibe o nome do paciente
        st.header(f"Paciente: {st.session_state.nome_paciente}", divider='rainbow')
        
    else:
        st.stop()


    
    col0, col00 = st.columns(2)
    with col0:
        st.subheader('MEMBRO ESQUERDO:')
        with st.popover("CONDIÇÕES", help= 'Use essa caixa para classificar o membro do paciente'):
            
            if st.session_state.condicao_memb_dir == 'Ambi-Destro':
                st.session_state.condicao_memb_esq = 'Ambi-Destro'

            st.session_state.condicao_memb_esq = st.radio(
                "Condição:", opcoes_condicao, 
                index=st.session_state.index_condicao_esq
                )
            st.session_state.lateralidade_memb_esq = st.radio(
                "Membro:", opcoes_lateralidade, 
                index=st.session_state.index_lateralidade_esq
                )
            
            if st.session_state.condicao_memb_esq is not None:
                st.session_state.index_condicao_esq = opcoes_condicao.index(st.session_state.condicao_memb_esq)

                if st.session_state.index_condicao_esq == 0:
                    st.session_state.index_condicao_dir = 1

                elif st.session_state.index_condicao_esq == 1:
                    st.session_state.index_condicao_dir = 0

            if st.session_state.lateralidade_memb_esq is not None:
                st.session_state.index_lateralidade_esq = opcoes_lateralidade.index(st.session_state.lateralidade_memb_esq)

                if st.session_state.index_lateralidade_esq == 0:
                    st.session_state.index_lateralidade_dir = 1

                elif st.session_state.index_lateralidade_esq == 1:
                    st.session_state.index_lateralidade_dir = 0
                
                elif st.session_state.index_lateralidade_esq == 2:
                    st.session_state.index_lateralidade_dir = 2


    with col00:
        st.subheader('MEMBRO DIREITO:')
        with st.popover("CONDIÇÕES", help= 'Use essa caixa para classificar o membro do paciente'):
            
            st.session_state.condicao_memb_dir = st.radio(
                "Condição: ", opcoes_condicao, 
                index=st.session_state.index_condicao_dir
                )
            st.session_state.lateralidade_memb_dir = st.radio(
                "Membro: ", opcoes_lateralidade, 
                index=st.session_state.index_lateralidade_dir
                )
            
            if st.session_state.condicao_memb_dir is not None:
                st.session_state.index_condicao_dir = opcoes_condicao.index(st.session_state.condicao_memb_dir)

                if st.session_state.index_condicao_dir == 0:
                    st.session_state.index_condicao_esq = 1

                elif st.session_state.index_condicao_dir == 1:
                    st.session_state.index_condicao_esq = 0

            if st.session_state.lateralidade_memb_dir is not None:
                st.session_state.index_lateralidade_dir = opcoes_lateralidade.index(st.session_state.lateralidade_memb_dir)

                if st.session_state.index_lateralidade_dir == 0:
                    st.session_state.index_lateralidade_esq = 1

                elif st.session_state.index_lateralidade_dir == 1:
                    st.session_state.index_lateralidade_esq = 0
                
                elif st.session_state.index_lateralidade_dir == 2:
                    st.session_state.index_lateralidade_esq = 2
                
                

    

#############################################################################################################     
    # @st.dialog("TEM CERTEZA QUE DESEJA EXCLUIR ESSE PACIENTE?", width='large')
    # def excluir_dados():
    #     if st.button("Sim, excluir dados e recomeçar cadastro."):
    #         st.rerun()  
    #     if st.button("Não, manter dados e retornar para operação."):
    #         pass
    
    # x = st.checkbox("Excluir paciente")
    # if x:
    #     x = False
    #     excluir_dados()
#############################################################################################################     

    
    st.subheader('',divider='rainbow')
    test_selection = st.segmented_control(" ", opcoes_teste, default='Jerk',)

    col1, col2 = st.columns(2)
    if test_selection == 'Jerk':
        with col1:
            if st.button("Iniciar Coleta do Membro Esquerdo para NHPT+", type='primary', use_container_width=True):
                if st.session_state.condicao_memb_esq is None:
                    st.warning('Insira as condições dos membros superiores antes de iniciar a coleta!')
                else:
                    st.session_state.ser = connect_to_serial(esp32_port_aceleracao, baudrate_aceleracao)


                    if st.session_state.ser:
                        start_collection(st.session_state.condicao_memb_esq.lower(), test_selection)
                    else:
                        st.warning('ESP não conectada! Verificar Conexão.')
                
            if st.button("Encerrar Coleta do Membro Esquerdo"):
                stop_collection(st.session_state.condicao_memb_esq.lower(), test_selection)
                disconnect_from_serial()


        with col2:
            if st.button("Iniciar Coleta do Membro Direito para NHPT+", type='primary', use_container_width=True):
                if st.session_state.condicao_memb_dir is None:
                    st.warning('Insira as condições dos membros superiores antes de iniciar a coleta!')
                else:
                    st.session_state.ser = connect_to_serial(esp32_port_aceleracao, baudrate_aceleracao)

                    if st.session_state.ser:
                        start_collection(st.session_state.condicao_memb_dir.lower(), test_selection)
                    else:
                        st.warning('ESP não conectada! Verificar Conexão.')
            
            if st.button("Encerrar Coleta do Membro Direito"):
                stop_collection(st.session_state.condicao_memb_dir.lower(), test_selection)
                disconnect_from_serial()

        

    if test_selection == 'Força':
        with col1:
            if st.button("Iniciar Coleta do Membro Esquerdo para Força", type='primary', use_container_width=True):
                if st.session_state.condicao_memb_esq is None:
                    st.warning('Insira as condições dos membros superiores antes de iniciar a coleta!')
                else:
                    st.session_state.ser = connect_to_serial(arduino_port_forca, baudrate_forca)

                    if st.session_state.ser:
                        start_collection(st.session_state.condicao_memb_esq.lower(), test_selection)
                    else:
                        st.warning('Arduino não conectado! Verificar Conexão.')

            if st.button("Encerrar Coleta do Membro Esquerdo"):
                stop_collection(st.session_state.condicao_memb_esq.lower(), test_selection)
                disconnect_from_serial()

        with col2:
            if st.button("Iniciar Coleta do Membro Direito para Força", type='primary', use_container_width=True):
                if st.session_state.condicao_memb_dir is None:
                    st.warning('Insira as condições dos membros superiores antes de iniciar a coleta!')
                else:
                    st.session_state.ser = connect_to_serial(arduino_port_forca, baudrate_forca)

                    if st.session_state.ser:
                        start_collection(st.session_state.condicao_memb_dir.lower(), test_selection)
                    else:
                        st.warning('Arduino não conectado! Verificar Conexão.')

            if st.button("Encerrar Coleta do Membro Direito"):
                stop_collection(st.session_state.condicao_memb_dir.lower(), test_selection)
                disconnect_from_serial()


# Aba Gráficos
if menu_id == "Gráficos":
    st.subheader(f"Paciente: {st.session_state.nome_paciente}", divider='rainbow')

    if st.session_state.df_aceleracao.empty and st.session_state.df_forca.empty:
        st.code('NENHUMA COLETA FEITA AINDA!')
    
    else:
        test_selection = st.segmented_control(" ", opcoes_teste, default='Jerk',)

        if test_selection == 'Jerk':
            if st.session_state.df_aceleracao.empty:
                st.code('NENHUMA COLETA FEITA AINDA PARA NHPT+!')
            
            else:
                # selected_dfs = st.multiselect(
                #     'Escolha um gráfico', 
                #     options=list(st.session_state.dfs.keys()), 
                #     placeholder="Escolha o(s) resultado(s) a serem exibido(s)"
                # )

                # # Exibe os DataFrames selecionados
                # if selected_dfs:
                #     for key in selected_dfs:
                #         st.subheader(f"Gráfico: {key}")
                #         st.write(st.session_state.dfs[key])  # Exibe o DataFrame correspondente

                #         st.line_chart()


                    
                formatted_names = {change_names(key): key for key in st.session_state.dfs.keys()}

                # Interface do usuário: seleção de DataFrames
                st.header("Selecione os dados para visualização do Jerk:")
                selected_dfs = st.multiselect(
                    " ",
                    options=list(formatted_names.keys()),
                    placeholder="Selecione os dados que deseja visualizar"
                    )

                # Seleção de colunas
                options=["ax", "ay", "az", "a_abs", "jerk_x", "jerk_y", "jerk_z", "jerk_abs"],
                # selected_columns = st.multiselect(
                #     "Escolha as colunas para o gráfico:",
                #     options=["ax", "ay", "az", "a_abs", "jerk_x", "jerk_y", "jerk_z", "jerk_abs"],
                #     default=["jerk_abs"],
                #     help="Escolha as métricas que deseja visualizar no gráfico"
                # )
                selected_column = 'jerk_abs'

                # Consolidação dos dados selecionados
                if selected_dfs:
                    consolidated_df = pd.DataFrame()
                    for friendly_name in selected_dfs:
                        original_key = formatted_names[friendly_name]
                        df = st.session_state.dfs[original_key]

                        # Filtra a coluna estática selecionada e adiciona contexto
                        filtered_df = df[["tempo", selected_column]].copy()
                        filtered_df = filtered_df.rename(columns={selected_column: "Valor"})
                        filtered_df["Métrica"] = selected_column  # Adiciona a métrica como contexto
                        filtered_df["Origem"] = friendly_name
                        consolidated_df = pd.concat([consolidated_df, filtered_df], ignore_index=True)

                    # Criação do gráfico com Plotly
                    fig = px.line(
                        consolidated_df,
                        x="tempo",
                        y="Valor",
                        color="Origem",
                        labels={"tempo": "Tempo", "Valor": "Valor", "Origem": "Fonte"},
                        title=f"Gráfico Consolidado - {selected_column.capitalize()}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Selecione ao menos uma Coleta para gerar o gráfico.")



        if test_selection == 'Força':
            if st.session_state.df_forca.empty:
                st.code('NENHUMA COLETA FEITA AINDA PARA FORÇA!')
            else:
                st.code('Tem coleta!')






# Aba Tabelas
if menu_id == "Tabelas":
    st.subheader(f"Paciente: {st.session_state.nome_paciente}", divider='rainbow')

    if st.session_state.df_aceleracao.empty and st.session_state.df_forca.empty:
        st.code('NENHUMA COLETA FEITA AINDA!')
    
    else:
        test_selection = st.segmented_control(" ", opcoes_teste, default='Jerk',)

        if test_selection == 'Jerk':
            if st.session_state.df_aceleracao.empty:
                st.code('NENHUMA COLETA FEITA AINDA PARA NHPT+!')
            
            else:
                if st.session_state.condicao_memb_esq == 'Parético':
                    memb_esq = 'paretico'
                    memb_dir = 'saudavel'
                    memb_esq_acentuado = 'PARÉTICO'
                    memb_dir_acentuado = 'SAUDÁVEL'
                else:
                    memb_esq = 'saudavel'
                    memb_dir = 'paretico'
                    memb_esq_acentuado = 'SAUDÁVEL'
                    memb_dir_acentuado = 'PARÉTICO'

                col1, col2 = st.columns(2)
                with col1:
                    st.header('Membro Esquerdo:', help= memb_esq_acentuado, anchor=False)
                    st.divider()
                    show_dfs(memb_esq)

                with col2:
                    st.header('Membro Direito:', help= memb_dir_acentuado, anchor=False)
                    st.divider()
                    show_dfs(memb_dir)
                
                
                st.subheader(f'Clique aqui para fazer download dos dados:')
                # Botão de download
                st.download_button(
                    label="Baixar Dados",
                    data=download_dataframe(st.session_state.df_aceleracao),
                    file_name=f"dados_{st.session_state.nome_paciente}.csv",
                    mime="text/csv"
                )

                st.multiselect('Selecione as Coletas que deseja baixar:',list(st.session_state.dfs.keys()))
        
        if test_selection == 'Força':
            if st.session_state.df_forca.empty:
                st.code('NENHUMA COLETA FEITA AINDA PARA FORÇA')
            
            else:
                st.code('Tem coleta!')
        


# Aba Conexão
if menu_id == 'Conexão':
    st.code('ver se essa parte fica ou não. Se for ficar, melhorar kkk')
    
    if not st.session_state.ser:
        st.session_state.ser = connect_to_serial(esp32_port_aceleracao, baudrate_aceleracao)


    # Exibe o status da conexão e tenta conectar
    if st.session_state.ser:
        st.code("Status da Conexão com ESP32: CONECTADA")
    else:
        st.code("Status da Conexão com ESP32: DESCONECTADA")
    # if st.session_state.ser:
    #     st.success("ESP32 conectado com sucesso!")
    # else:
    #     st.warning("ESP32 não conectado. Clique no botão para tentar novamente.")

    attempts = 1

    if st.button('Reconectar ESP32'):
        st.write(f"Tentando reconectar ({attempts})...")
        st.session_state.ser = connect_to_serial(esp32_port_aceleracao, baudrate_aceleracao)
        attempts = attempts + 1
    
        if attempts >= 5:
            st.subheader(' ', divider='orange')
            st.error('Falha ao conectar com ESP32. Reinicie o programa.')
            st.stop()
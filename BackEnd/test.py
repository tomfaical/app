# streamlit run C:\PBL_S4\app\app\BackEnd\test.py
import serial
import pandas as pd
from datetime import datetime
import streamlit as st
import hydralit_components as hc
import time
import altair as alt
import plotly.express as px
from folium import Map, Marker
import streamlit as st

from streamlit_folium import st_folium


from painel_components import *
import warnings
import os
warnings.filterwarnings('ignore')
#os.chdir('diretorio')

### Porta BT para Aceleração e Força:
esp32_port_aceleracao = "COM9"               # POR BT
# esp32_port_aceleracao = "COM3"                # POR CABO
arduino_port_forca = "COM10"

baudrate_aceleracao = 115200
baudrate_forca = 9600

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')
st.title('Plataforma NHPT+')
st.text(' ')


# Inicialização de variáveis no session state
start_session_states()


menu_data = [
    {'icon': "fa fa-address-card", 'label': "Tela Inicial"},
    {'icon': "fa fa-chart-line", 'label': "Gráficos"},
    {'icon': "fa fa-table", 'label': "Tabelas"},
    {'icon': "fa fa-bullseye", 'label': "Resultados"}
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
if menu_id == "Tela Inicial":
    start_placeholder = st.empty()

    with start_placeholder.container():

        st.title('Selecione o que deseja fazer: ')
        if st.button('Cadastrar novo paciente', type='primary'):
            st.session_state.iterador_paretico_acc = 1
            st.session_state.iterador_saudavel_acc = 1
            st.session_state.iterador_paretico_forca = 1
            st.session_state.iterador_saudavel_forca = 1
            
            st.session_state.dfs_aceleracao = dict()
            st.session_state.dfs_forca = dict()
            st.session_state.df_aceleracao = st.session_state.df_aceleracao.head(0)
            st.session_state.df_forca = st.session_state.df_forca.head(0)

            st.session_state.condicao_memb_esq = None
            st.session_state.condicao_memb_dir = None
            st.session_state.lateralidade_memb_esq = None
            st.session_state.lateralidade_memb_dir = None
            st.session_state.index_condicao_esq = None
            st.session_state.index_lateralidade_esq = None
            st.session_state.index_condicao_dir = None
            st.session_state.index_lateralidade_dir = None
            st.session_state.index_paciente = None

            st.session_state.selected_patient = False

            st.session_state.novo_paciente = True
            st.session_state.resgatar_paciente = False
        
        if st.button('Visualizar paciente já registrado', type='primary'):
            st.session_state.resgatar_paciente = True
            st.session_state.novo_paciente = False
        
        st.divider()


    if st.session_state.resgatar_paciente:
        folder_path = r'BackEnd\resultados_coleta'
        start_placeholder.empty()
    
        patient_files = read_all_csvs(folder_path)

        if patient_files:
            col1, col2 = st.columns([2,1])
            with col1:
                with st.expander("Selecione o Paciente:", expanded=False):   
                    st.session_state.selected_patient = st.selectbox(
                        "Pacientes:",
                        list(patient_files.keys()), 
                        index=st.session_state.index_paciente,
                        placeholder= 'Escolha um paciente',
                        label_visibility='collapsed',
                        help="Escolha um paciente para visualizar os arquivos vinculados."
                    )
                
            with col2:    
                if st.button('☰ VOLTAR PARA O MENU', type='primary', use_container_width=False, key=1):
                    recomecar_operacao()

            if st.session_state.selected_patient is not None:
                st.session_state.index_paciente = list(patient_files.keys()).index(st.session_state.selected_patient)
            
        

        # Exibir os arquivos vinculados ao paciente selecionado
        if st.session_state.selected_patient and st.session_state.selected_patient != "Selecione um paciente":
            #st.write(f"Arquivos vinculados ao paciente {st.session_state.selected_patient}!")
            for file in patient_files[st.session_state.selected_patient]:
                file_path = os.path.join(folder_path, file)
                try:
                    if 'jerk' in file:
                        st.session_state.df_aceleracao = pd.read_csv(file_path)
                    if 'forca' in file:
                        st.session_state.df_forca = pd.read_csv(file_path)
                except Exception as e:
                    st.error(f"Erro ao carregar {file}: {e}")
        else:
            #st.warning("Selecione o Paciente que deseja ver.")
            st.stop()




        st.session_state.nome_paciente = st.session_state.selected_patient
        st.session_state.dfs_aceleracao = dict()
        st.session_state.dfs_forca = dict()

        st.session_state.iterador_paretico_acc = st.session_state.df_aceleracao['n_coleta'].max() + 1
        st.session_state.iterador_saudavel_acc = st.session_state.df_aceleracao['n_coleta'].max() + 1
        st.session_state.iterador_paretico_forca = st.session_state.df_forca['n_coleta'].max()    + 1
        st.session_state.iterador_saudavel_forca = st.session_state.df_forca['n_coleta'].max()    + 1

        if not st.session_state.df_aceleracao[
            (st.session_state.df_aceleracao['condicao'] == 'parético')
            & (st.session_state.df_aceleracao['lado'] == 'esquerdo')].empty:

            st.session_state.index_condicao_esq = 0
            st.session_state.index_condicao_dir = 1
        else:
            st.session_state.index_condicao_esq = 1
            st.session_state.index_condicao_dir = 0 
        
        if not st.session_state.df_aceleracao[
            (st.session_state.df_aceleracao['lateralidade'] == 'dominante')
            & (st.session_state.df_aceleracao['lado'] == 'esquerdo')].empty:

            st.session_state.index_lateralidade_esq = 0
            st.session_state.index_lateralidade_dir = 1
        elif not st.session_state.df_aceleracao[
            (st.session_state.df_aceleracao['lateralidade'] == 'nao_dominante')
            & (st.session_state.df_aceleracao['lado'] == 'esquerdo')].empty:

            st.session_state.index_lateralidade_esq = 1
            st.session_state.index_lateralidade_dir = 2
        else:
            st.session_state.index_lateralidade_esq = 2
            st.session_state.index_lateralidade_dir = 2 
        

        store_data('Jerk')
        store_data('Força')
        
    
        if st.session_state.selected_patient is None:
            st.stop()


    
    if st.session_state.novo_paciente:
        start_placeholder.empty()
        placeholder_nome = st.empty()
        col1, col2 = st.columns(2)

        
        if st.session_state.get("nome_paciente") == '':
            with placeholder_nome.container():
                with col1:          
                    st.header("Digite o Nome do Paciente:",anchor=False)
                    nome = st.text_input(" ", label_visibility= 'collapsed')
                    
                    
                if nome:  # Apenas atualiza se o usuário digitar algo
                    st.session_state.nome_paciente = nome
                    placeholder_nome.empty()  
                    st.rerun()

        with col2:
            st.header('')
            if st.button('☰ VOLTAR PARA O MENU', type='primary', use_container_width=False, key=2):
                recomecar_operacao()

    if st.session_state.nome_paciente and (st.session_state.resgatar_paciente or st.session_state.novo_paciente):
        st.header(f"Paciente: {st.session_state.nome_paciente}",divider='rainbow', anchor=False)
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
                        start_collection(st.session_state.condicao_memb_esq.lower(), 
                                         test_selection, 
                                         lado='esquerdo',
                                         lateralidade=st.session_state.lateralidade_memb_esq.lower().replace('-','_'))
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
                        start_collection(st.session_state.condicao_memb_dir.lower(), 
                                         test_selection, 
                                         lado='direito', 
                                         lateralidade= st.session_state.lateralidade_memb_dir.lower().replace('-','_'))
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
                        start_collection(st.session_state.condicao_memb_esq.lower(), 
                                         test_selection, 
                                         lado='esquerdo', 
                                         lateralidade= st.session_state.lateralidade_memb_esq.lower().replace('-','_'))
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
                        start_collection(st.session_state.condicao_memb_dir.lower(), 
                                         test_selection, 
                                         lado='direito', 
                                         lateralidade= st.session_state.lateralidade_memb_dir.lower().replace('-','_'))
                    else:
                        st.warning('Arduino não conectado! Verificar Conexão.')
                
            if st.button("Encerrar Coleta do Membro Direito"):
                stop_collection(st.session_state.condicao_memb_dir.lower(), test_selection)
                disconnect_from_serial()

    st.title(' ')
    st.title(' ')
    st.title(' ')
    st.header(' ', divider='rainbow')

    


    col3, col4, col5 = st.columns([3,2,1], gap='large')
    with col3:
        st.subheader('')
        st.header('Para mais informações, fale conosco:')
        st.divider()
        st.subheader('MovaX Inc.')
        
        st.write('E-mail: atendimento@movax.com')
        st.write('Fone: +55 (11) 99901-3332')
    
    with col4:
        st.subheader('')
        latitude = -23.595400886122025
        longitude = -46.73720592520606
        mapa = Map(location=[latitude, longitude], zoom_start=13)
        Marker(location=[latitude, longitude]).add_to(mapa)
        st_folium(mapa, width=350, height=350)

        
    with col5:
        st.header(' ')
        st.header(' ')
        st.header(' ')
        st.header(' ')
        st.header(' ')
        
        if st.button('☰ VOLTAR PARA O MENU', type='primary', use_container_width=True, key=3):
            recomecar_operacao()


# Aba Gráficos
if menu_id == "Gráficos":
    st.header(f"Paciente: {st.session_state.nome_paciente}", divider='rainbow', anchor=False)

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
                #     options=list(st.session_state.dfs_aceleracao.keys()), 
                #     placeholder="Escolha o(s) resultado(s) a serem exibido(s)"
                # )

                # # Exibe os DataFrames selecionados
                # if selected_dfs:
                #     for key in selected_dfs:
                #         st.subheader(f"Gráfico: {key}")
                #         st.write(st.session_state.dfs_aceleracao[key])  # Exibe o DataFrame correspondente

                #         st.line_chart()


                    
                formatted_names = {change_names(key): key for key in st.session_state.dfs_aceleracao.keys()}

                # Interface do usuário: seleção de DataFrames
                st.header("Selecione os dados para visualização do Jerk:")
                selected_dfs = st.multiselect(
                    " ",
                    options=list(formatted_names.keys()),
                    placeholder="Selecione as coletas que deseja visualizar",
                    label_visibility='collapsed'
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
                        df = st.session_state.dfs_aceleracao[original_key]

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
                



        if test_selection == 'Força':
            if st.session_state.df_forca.empty:
                st.code('NENHUMA COLETA FEITA AINDA PARA FORÇA!')
            else:
                formatted_names = {change_names(key): key for key in st.session_state.dfs_forca.keys()}

                # Interface do usuário: seleção de DataFrames
                st.header("Selecione os dados para visualização da Força:")
                selected_dfs = st.multiselect(
                    " ",
                    options=list(formatted_names.keys()),
                    placeholder="Selecione as coletas que deseja visualizar",
                    label_visibility='collapsed'
                    )

                # Seleção de colunas
                options=["forca", "df_dt"],
                # selected_columns = st.multiselect(
                #     "Escolha as colunas para o gráfico:",
                #     options=["ax", "ay", "az", "a_abs", "jerk_x", "jerk_y", "jerk_z", "jerk_abs"],
                #     default=["jerk_abs"],
                #     help="Escolha as métricas que deseja visualizar no gráfico"
                # )
                selected_column = 'forca'

                # Consolidação dos dados selecionados
                if selected_dfs:
                    consolidated_df = pd.DataFrame()
                    for friendly_name in selected_dfs:
                        original_key = formatted_names[friendly_name]
                        df = st.session_state.dfs_forca[original_key]

                        # Filtra a coluna estática selecionada e adiciona contexto
                        filtered_df = df[["tempo", selected_column]].copy()
                        filtered_df = filtered_df.rename(columns={selected_column: "Valor"})
                        filtered_df["Métrica"] = selected_column  # Adiciona a métrica como contexto
                        filtered_df["Origem"] = friendly_name
                        consolidated_df = pd.concat([consolidated_df, filtered_df], ignore_index=True)

                    # Criação do gráfico com Plotly
                    fig = px.bar(
                        consolidated_df,
                        x="tempo",
                        y="Valor",
                        color="Origem",
                        labels={"tempo": "Tempo", "Valor": "Valor", "Origem": "Fonte"},
                        title=f"Gráfico Consolidado - {selected_column.capitalize()}"
                    )
                    st.plotly_chart(fig, use_container_width=True)






# Aba Tabelas
if menu_id == "Tabelas":
    if st.session_state.condicao_memb_esq == 'Parético':
        memb_esq_acentuado = 'PARÉTICO'
        memb_dir_acentuado = 'SAUDÁVEL'
    else:
        memb_esq_acentuado = 'SAUDÁVEL'
        memb_dir_acentuado = 'PARÉTICO'
        
    st.header(f"Paciente: {st.session_state.nome_paciente}", divider='rainbow', anchor=False)

    if st.session_state.df_aceleracao.empty and st.session_state.df_forca.empty:
        st.code('NENHUMA COLETA FEITA AINDA!')
    
    else:
        test_selection = st.segmented_control(" ", opcoes_teste, default='Jerk',)

        if test_selection == 'Jerk':
            if st.session_state.df_aceleracao.empty:
                st.code('NENHUMA COLETA FEITA AINDA PARA NHPT+!')
            
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.header('Membro Esquerdo:', help= memb_esq_acentuado, anchor=False)
                    st.divider()
                    show_dfs(st.session_state.condicao_memb_esq, test_selection)

                with col2:
                    st.header('Membro Direito:', help= memb_dir_acentuado, anchor=False)
                    st.divider()
                    show_dfs(st.session_state.condicao_memb_dir, test_selection)
                
                
                st.subheader(f'Clique aqui para fazer download dos dados:')
                # Botão de download
                st.download_button(
                    label="Baixar Dados",
                    data=make_csv(st.session_state.df_aceleracao),
                    file_name=f"dados_jerk_{st.session_state.nome_paciente}.csv",
                    mime="text/csv"
                )
                st.multiselect('Selecione as Coletas que deseja baixar:',list(st.session_state.dfs_aceleracao.keys()))
        
        if test_selection == 'Força':
            if st.session_state.df_forca.empty:
                st.code('NENHUMA COLETA FEITA AINDA PARA FORÇA')
            
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.header('Membro Esquerdo:', help= memb_esq_acentuado, anchor=False)
                    st.divider()
                    show_dfs(st.session_state.condicao_memb_esq, test_selection)

                with col2:
                    st.header('Membro Direito:', help= memb_dir_acentuado, anchor=False)
                    st.divider()
                    show_dfs(st.session_state.condicao_memb_dir, test_selection)
        
                st.subheader(f'Clique aqui para fazer download dos dados:')
                st.download_button(
                    label="Baixar Dados",
                    data=make_csv(st.session_state.df_forca),
                    file_name=f"dados_forca_{st.session_state.nome_paciente}.csv",
                    mime="text/csv"
                )
                



if menu_id == 'Resultados':
    st.header(f"Paciente: {st.session_state.nome_paciente}", divider='rainbow', anchor=False)

    if st.session_state.df_aceleracao.empty and st.session_state.df_forca.empty:
        st.code('NENHUMA COLETA FEITA AINDA!')
    
    else:
        test_selection = st.segmented_control(" ", opcoes_teste, default='Jerk',)

        if test_selection == 'Jerk':
            if st.session_state.df_aceleracao.empty:
                st.code('NENHUMA COLETA FEITA AINDA PARA NHPT+!')
            
            else:
                selection_placeholder = st.empty()
                with selection_placeholder.container():
                    formatted_names = {change_names(key): key for key in st.session_state.dfs_aceleracao.keys()}
                    opcoes_coleta=list(formatted_names.keys())

                    # Interface do usuário: seleção de DataFrames
                    st.header("Selecione os dados para visualização do Jerk:")
                    selected_dfs = st.multiselect(
                        " ",
                        opcoes_coleta,
                        placeholder="Selecione as coletas que deseja visualizar",
                        label_visibility='collapsed'
                        )                    
                    gerar_relatorio = st.button('Gerar Relatório', type='primary')


                # Consolidação dos dados selecionados
                if selected_dfs:
                    col_de_interesse = 'jerk_abs'
                    dfs_para_analise = []
                    
                    for friendly_name in selected_dfs:
                        original_key = formatted_names[friendly_name]
                        dfs_para_analise.append(st.session_state.dfs_aceleracao[original_key])
 
                    index = 0
                    tem_paretico = False
                    tem_saudavel = False
                    for df in dfs_para_analise:
                        if not df[df['condicao'] == 'parético'].empty:
                            tem_paretico = True
                            index_paretico = index
                        if not df[df['condicao'] == 'saudável'].empty:
                            tem_saudavel = True
                            index_saudavel = index
                        
                        index =+1

                    if not tem_saudavel or not tem_paretico:
                        st.warning('Selecione 1 coleta de cada condição.')
                    elif len(dfs_para_analise) > 2:
                        st.error('Selecione no máximo 2 coletas. Uma para cada condição.')
                    else:
##################################### RETIRAR  #####################################
                        gerar_relatorio = True
##################################### RETIRAR  #####################################

                        if gerar_relatorio:
                            selection_placeholder.empty()

                            st.markdown(
                                """
                                <div style="background-color: transparent; padding: 10px; border-radius: 30px; border: 5px cornflowerblue dotted; margin: 50px 20px;">
                                    <h2 style="color: cornflowerblue; text-align: center; margin: 0;">RELATÓRIO DE DESEMPENHO:</h2>
                                </div>
                                """,
                                unsafe_allow_html=True
                                )
                        
                            df_paretico = dfs_para_analise[index_paretico]
                            df_saudavel = dfs_para_analise[index_saudavel]

                            
                            min_jerk_abs = df_paretico['jerk_abs'].min()
                            max_jerk_abs = df_paretico['jerk_abs'].max()
                            df_paretico['jerk_abs_norm'] = ((df_paretico['jerk_abs'] - min_jerk_abs) / (max_jerk_abs - min_jerk_abs))

                            min_jerk_abs = df_saudavel['jerk_abs'].min()
                            max_jerk_abs = df_saudavel['jerk_abs'].max()
                            df_saudavel['jerk_abs_norm'] = ((df_saudavel['jerk_abs'] - min_jerk_abs) / (max_jerk_abs - min_jerk_abs))

                            mean_jerk_norm_saudavel = df_saudavel['jerk_abs_norm'].mean()
                            mean_jerk_norm_paretico = df_paretico['jerk_abs_norm'].mean()
                            std_jerk_norm_saudavel = df_saudavel['jerk_abs_norm'].std()
                            std_jerk_norm_paretico = df_paretico['jerk_abs_norm'].std()

                            # mean_jerk_saudavel = st.number_input('jerk saudavel: ')
                            # mean_jerk_paretico = st.number_input('jerk paretico: ')

                           
                            score_coordenacao =  ((abs(df_paretico['jerk_abs_norm'].mean() - df_saudavel['jerk_abs_norm'].mean())) / df_paretico['jerk_abs_norm'].mean()) * 100
                          

                            classificacoes_jerk = ['Ruim 🚨','Razoável','Intermediário','Bom','Excelente 🔥']
                            if score_coordenacao > 0 and score_coordenacao <= 20:
                                categoria_jerk = classificacoes_jerk[4]

                            elif score_coordenacao > 20 and score_coordenacao <= 40:
                                categoria_jerk = classificacoes_jerk[3] 

                            elif score_coordenacao > 40 and score_coordenacao <= 60:
                                categoria_jerk = classificacoes_jerk[2]

                            elif score_coordenacao > 60 and score_coordenacao <= 80:
                                categoria_jerk = classificacoes_jerk[1]

                            elif score_coordenacao > 80:
                                categoria_jerk = classificacoes_jerk[0] 

                            
                            st.header(f'Percentual de Disparidade da Coordenação: {score_coordenacao:.2f} %')
                            st.subheader(f'Classificação da coordenação: {categoria_jerk}')
                            st.select_slider('', classificacoes_jerk, label_visibility='collapsed', value=categoria_jerk, disabled=False)
                            # st.button(ic)
                        
                        

                       
                



        if test_selection == 'Força':
            if st.session_state.df_forca.empty:
                st.code('NENHUMA COLETA FEITA AINDA PARA FORÇA!')
                
            else:
                selection_placeholder = st.empty()
                with selection_placeholder.container():
                    formatted_names = {change_names(key): key for key in st.session_state.dfs_forca.keys()}
                    opcoes_coleta=list(formatted_names.keys())

                    # Interface do usuário: seleção de DataFrames
                    st.header("Selecione os dados para visualização da Força:")
                    selected_dfs = st.multiselect(
                        " ",
                        opcoes_coleta,
                        placeholder="Selecione as coletas que deseja visualizar",
                        label_visibility='collapsed'
                        )                    
                    gerar_relatorio = st.button('Gerar Relatório', type='primary')


                if selected_dfs:
                    col_de_interesse = 'forca'
                    dfs_para_analise = []

                    for friendly_name in selected_dfs:
                        original_key = formatted_names[friendly_name]
                        dfs_para_analise.append(st.session_state.dfs_forca[original_key])
 
                    index = 0
                    tem_paretico = False
                    tem_saudavel = False
                    for df in dfs_para_analise:
                        if not df[df['condicao'] == 'parético'].empty:
                            tem_paretico = True
                            index_paretico = index
                        if not df[df['condicao'] == 'saudável'].empty:
                            tem_saudavel = True
                            index_saudavel = index
                        
                        index =+1

                    if not tem_saudavel or not tem_paretico:
                        st.warning('Selecione 1 coleta de cada condição.')
                    elif len(dfs_para_analise) > 2:
                        st.error('Selecione no máximo 2 coletas. Uma para cada condição.')
                    else:
##################################### RETIRAR  #####################################
                        gerar_relatorio = True
##################################### RETIRAR  #####################################

                        if gerar_relatorio:
                            selection_placeholder.empty()

                            st.markdown(
                                """
                                <div style="background-color: transparent; padding: 10px; border-radius: 30px; border: 5px cornflowerblue dotted; margin: 50px 20px;">
                                    <h2 style="color: cornflowerblue; text-align: center; margin: 0;">RELATÓRIO DE DESEMPENHO:</h2>
                                </div>
                                """,
                                unsafe_allow_html=True
                                )
                        
                            df_paretico = dfs_para_analise[index_paretico]
                            df_saudavel = dfs_para_analise[index_saudavel]



                            df_paretico
                            df_saudavel



                     

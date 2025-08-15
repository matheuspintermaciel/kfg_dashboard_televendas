import streamlit as st
from config import CSS_STYLES, get_logo_base64
from components.cards import create_status_cards
from components.sidebar import create_sidebar_filters
from components.table_clientes import display_data_table
import pandas as pd
import json
import os

from data.load import CAMINHO_JSON

def main(dados):
    # Verificando o ID do usuário logado
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Por favor, faça o login!")
        st.stop()

    # Lógica de exibição dos dados filtrados
    if 'show_client_dialog' not in st.session_state:
        st.session_state.show_client_dialog = False
    if 'selected_client_id' not in st.session_state:
        st.session_state.selected_client_id = None
    if 'previous_df_editor' not in st.session_state:
        st.session_state.previous_df_editor = pd.DataFrame(columns=['Ação'])

    st.markdown(CSS_STYLES, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(
            f'<a href="/" target="_self"><img src="data:image/png;base64,{get_logo_base64()}" style="width:100%; margin-bottom:1rem;"/></a>',
            unsafe_allow_html=True
        )

    create_status_cards(user_id)

    # Carregar o arquivo JSON de atribuições de clientes
    if os.path.exists(CAMINHO_JSON):
        with open(CAMINHO_JSON, "r") as f:
            clientes_atribuidos = json.load(f)
    else:
        st.warning("Arquivo de atribuições de clientes não encontrado.")
        return
    sel = st.session_state.get('selected_status')
    # Carrega os dados do JSON novamente para buscar os codigos_loja com o status selecionado
    if sel:
        codigos_filtrados = []
        for data, atribuicao in clientes_atribuidos.items():
            if user_id in atribuicao:
                for cliente in atribuicao[user_id]:
                    status = cliente['status']
                    if status not in ['Venda Concluída', 'Venda Perdida']:
                        status_mapeado = 'Entrar em Contato'
                    else:
                        status_mapeado = status

                    if status_mapeado == sel:
                        codigos_filtrados.append(cliente['codigo_loja'])

        dados = dados[dados['codigo_loja'].isin(codigos_filtrados)]


    dados = create_sidebar_filters(dados)
    # Filtrando os clientes atribuídos para o usuário logado
    clientes_atuais = []
    for data, atribuicao in clientes_atribuidos.items():
        if user_id in atribuicao:
            print(user_id)
            clientes_atuais.extend([cliente['codigo_loja'] for cliente in atribuicao[user_id]])

    # Filtrando os dados para mostrar apenas os clientes atribuídos ao usuário
    dados_filtrados = dados[dados['codigo_loja'].isin(clientes_atuais)]

    # Exibindo os dados filtrados na tabela
    display_data_table(dados_filtrados)

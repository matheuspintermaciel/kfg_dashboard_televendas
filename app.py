import streamlit as st
from config import PAGE_CONFIG, CSS_STYLES, get_logo_base64

st.set_page_config(**PAGE_CONFIG)

from data.atribuir_clientes import atribuir_clientes
from home import main as home_main
from login import login
from data.clientes import load_clientes

def app():
    # Verifica se o usuário está logado
    if "user_id" not in st.session_state:
        print("user_id")
        login()  # Chama a função de login, caso o usuário não esteja logado
    else:
        atribuir_clientes()
        # Carregar os dados uma única vez, se ainda não estiver carregado
        if 'dados_clientes' not in st.session_state:
            st.session_state['dados_clientes'] = load_clientes()  # Carrega os dados de clientes uma vez
        dados = st.session_state['dados_clientes']  # Acessa os dados carregados
        print("Carregando Home")
        home_main(dados)  # Exibe a home com os filtros baseados no ID

if __name__ == "__main__":
    app()

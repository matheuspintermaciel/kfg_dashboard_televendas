import streamlit as st
PAGE_CONFIG = {
    "page_title": "Home",
    "page_icon": "📝",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}
st.set_page_config(**PAGE_CONFIG)

from data.atribuir_clientes import atribuir_clientes
from home import main as home_main
from login import login
from data.load import load_data

def app():
    
    # Carregar os dados uma única vez, se ainda não estiver carregado
    if 'dados_clientes' not in st.session_state:
        print("Carregando dados")
        dados_clientes, dados_historico = load_data()
        atribuir_clientes()
        st.session_state['dados_clientes'] = dados_clientes
        st.session_state['dados_historico'] = dados_historico

    dados = st.session_state['dados_clientes']

    # Verifica se o usuário está logado
    if "user_id" not in st.session_state:
        print("user_id")
        login()
        atribuir_clientes()
    else:
        home_main(dados)  # Chama a função de login, caso o usuário não esteja logado

if __name__ == "__main__":
    app()

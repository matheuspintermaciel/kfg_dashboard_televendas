import streamlit as st
import json
from collections import Counter
from config import CARD_STYLES

def create_status_cards(user_id):
    CAMINHO_JSON = "data/clientes_atribuidos.json"
    
    """Cria cards interativos sem navegação, usando botões invisíveis sobre os cards"""
    # Estilos dos cards e posicionamento do botão
    st.markdown(CARD_STYLES, unsafe_allow_html=True)

    # Inicializa estado
    if 'selected_status' not in st.session_state:
        st.session_state.selected_status = None

    # Carregar dados do JSON
    with open(CAMINHO_JSON, "r") as f:
        clientes_atribuidos = json.load(f)
    
    # Coletar todos os status do user_id
    all_status = []
    for data in clientes_atribuidos.values():
        for usuario, clientes in data.items():
            if usuario == user_id:  # Filtra apenas os dados do usuário
                for cliente in clientes:
                    # Ajuste do status: qualquer status que não seja "Venda Concluída" ou "Venda Perdida" será "Entrar em Contato"
                    status = cliente['status']
                    if status not in ['Venda Concluída', 'Venda Perdida']:
                        status = 'Entrar em Contato'
                    all_status.append(status)

    # Contagem de cada status
    status_counts_relevantes = Counter(all_status)
    total = len(all_status)

    # Status configurados para o card
    status_config = {
        'Venda Concluída': '#4CAF50',  # Verde
        'Entrar em Contato': '#2196F3',  # Azul
        'Venda Perdida': '#F44336',  # Vermelho
    }

    # Criação das colunas para os cards
    cols = st.columns(len(status_config))

    # Exibe os cards com as contagens de status
    for idx, (status, color) in enumerate(status_config.items()):
        with cols[idx]:
            count = status_counts_relevantes.get(status, 0)
            rate = (count / total * 100) if total > 0 else 0

            is_selected = (st.session_state.selected_status == status)

            # Container do card + botão overlay
            st.markdown(f'<div class="card-container">', unsafe_allow_html=True)
            # Botão invisível que dispara o toggle
            st.button("", key=f"btn_{status}", on_click=_toggle, args=(status,))
            
            # Renderiza o card
            bg = color if is_selected else 'white'
            border = color
            header_color = 'white' if is_selected else color
            text_color = 'white' if is_selected else '#2c3e50'
            card_html = f"""
            <div class="card" style="background-color:{bg}; border:2px solid {border};">
                <div class="card-header" style="color:{header_color}">{status}</div>
                <div class="card-value" style="color:{text_color}; font-size:1.5rem;">{count}</div>
                <div style="color:{text_color}">Taxa: {rate:.1f}%</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


def _toggle(status):
    """Alterna seleção de status na sessão"""
    if st.session_state.selected_status == status:
        st.session_state.selected_status = None
    else:
        st.session_state.selected_status = status

from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import streamlit as st
import pandas as pd
import json
import os
from data.load import dados_clientes, dados_historico, CAMINHO_JSON
from config import GoogleDriveClient

# Função para atualizar status no JSON
def atualizar_status_cliente(user_id, codigo_loja, status, info_extra=None):
    if not os.path.exists(CAMINHO_JSON):
        st.error("Arquivo de atribuições não encontrado.")
        print(f"[ERROR] Arquivo de atribuições não encontrado em {CAMINHO_JSON}")
        return

    with open(CAMINHO_JSON, "r") as f:
        data_json = json.load(f)
        print(f"[INFO] Dados carregados do arquivo JSON: {data_json}")

    # Procurar cliente pelo user_id e codigo_loja em todos os dias
    cliente_encontrado = False
    for data, usuarios in data_json.items():
        if user_id in usuarios:
            for cliente in usuarios[user_id]:
                if cliente['codigo_loja'] == codigo_loja:
                    cliente['status'] = status
                    print(f"[INFO] Atualizando status do cliente {cliente['codigo_loja']} para {status}")
                    if status == "Venda Concluída":
                        cliente['valor_fechado'] = info_extra.get('valor', 0.0)
                        cliente['observacoes'] = info_extra.get('obs', "")
                        print(f"[INFO] Venda concluída. Valor: {cliente['valor_fechado']}, Observações: {cliente['observacoes']}")
                    elif status == "Venda Perdida":
                        cliente['motivo_perda'] = info_extra.get('motivo', "")
                        cliente['detalhes'] = info_extra.get('detalhes', "")
                        print(f"[INFO] Venda perdida. Motivo: {cliente['motivo_perda']}, Detalhes: {cliente['detalhes']}")
                    cliente_encontrado = True
                    break
        if cliente_encontrado:
            break
    
    if not cliente_encontrado:
        st.warning(f"Cliente {codigo_loja} não encontrado para o usuário {user_id}.")
        print(f"[WARN] Cliente {codigo_loja} não encontrado para o usuário {user_id}.")
        return

    # Salvar as alterações no arquivo JSON
    try:
        with open(CAMINHO_JSON, "w") as f:
            json.dump(data_json, f, indent=4)
        print(f"[INFO] Dados salvos no arquivo JSON com sucesso.")

        # Agora, faz o upload do arquivo JSON atualizado para o Google Drive
        gdrive_client = GoogleDriveClient()
        gdrive_client.upload_file(CAMINHO_JSON, folder_id='1SGB1HO0MQxUoJcBAEicTmxxE4hg_y47E')
        print(f"[INFO] Enviado para o Google Drive com sucesso.")

    except Exception as e:
        print(f"[ERROR] Ocorreu um erro ao salvar ou enviar o arquivo JSON: {e}")


    st.success("Status atualizado com sucesso!")
    st.rerun()

# Containers de Fechamento e Perda
def render_fechamento_perdido(codigo_loja, user_id):
    if st.session_state.get('show_fechado', False):
        st.header("Registrar Fechamento")
        valor = st.number_input("Valor Fechado (R$)", min_value=0.0, format="%.2f")
        observacoes = st.text_area("Observações")

        # Verificar se o valor é maior que zero antes de salvar
        if st.button("Salvar Fechamento", use_container_width=True, type='primary', help="Registrar valor fechado"):
            if valor <= 0:
                st.error("O valor fechado deve ser maior que zero.")
            else:
                st.session_state.show_fechado = False
                # Supondo que a função `atualizar_status_cliente` também seja chamada para o fechamento
                atualizar_status_cliente(
                    user_id=user_id,
                    codigo_loja=codigo_loja,
                    status="Venda Concluída",
                    info_extra={"valor": valor, "obs": observacoes}
                )
                st.success("Fechamento registrado com sucesso!")
    
    elif st.session_state.get('show_perdido', False):
        with st.container():
            st.header("Registrar Perda")
            motivo = st.selectbox("Motivo da Perda", ["Preço", "Prazo", "Qualidade", "Outro"])
            detalhes = st.text_area("Detalhes do Motivo")

            # Verificar se o motivo e os detalhes são informados antes de salvar
            if st.button("Salvar Perda", use_container_width=True, type='secondary', help="Registrar motivo da perda"):
                if not motivo or not detalhes:
                    st.error("Motivo e detalhes são obrigatórios para registrar a perda.")
                else:
                    print(f"[INFO] Salvar perda para cliente {codigo_loja}. Motivo: {motivo}, Detalhes: {detalhes}")
                    atualizar_status_cliente(
                        user_id=user_id,
                        codigo_loja=codigo_loja,
                        status="Venda Perdida",
                        info_extra={"motivo": motivo, "detalhes": detalhes}
                    )
                    st.session_state.show_perdido = False
                    st.success("Perda registrada com sucesso!")


# Visualização com heatmap
def render_heatmap_aggrid(df):
    if df.empty:
        st.warning("Nenhum dado disponível para visualização")
        return

    gb = GridOptionsBuilder.from_dataframe(df)

    cell_style_jscode = JsCode(""" 
        function(params) {
            if (params.value.includes('0 - R$0,00 - 0,00%')) {
                return {
                    'backgroundColor': '#ffcccc',
                    'color': '#ffcccc',
                    'border': '1px solid #666666'
                }
            } else {
                return {
                    'backgroundColor': '#228B22',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'border': '1px solid #1e1a19'
                }
            }
        }
    """)

    for col in df.columns:
        if col in ['Código', 'Descrição']:
            gb.configure_column(col, header_name=col, pinned='left',
                                filter=True, cellStyle={"backgroundColor": "#f8f9fa", "color": "#000000"},
                                width=150, suppressSizeToFit=True)
        else:
            gb.configure_column(col, header_name=col, cellStyle=cell_style_jscode,
                                wrapHeaderText=True, autoHeaderHeight=True,
                                width=120, suppressSizeToFit=True)

    last_col = df.columns[-1]
    custom_js = JsCode(f"""
        function(e) {{
            setTimeout(function () {{
                e.api.ensureColumnVisible("{last_col}");
            }}, 100);
        }}
    """)

    gb.configure_grid_options(
        domLayout='normal',
        suppressHorizontalScroll=False,
        suppressColumnVirtualisation=True,
        onFirstDataRendered=custom_js
    )

    AgGrid(df, gridOptions=gb.build(),
           fit_columns_on_grid_load=False,
           allow_unsafe_jscode=True,
           height=500)

# Dataframe para o heatmap
def criar_heatmap_dataframe(cliente_codigo, loja):
    try:
        cliente_data = dados_historico[ 
            (dados_historico['Cliente_Codigo'].astype(str) == str(cliente_codigo)) & 
            (dados_historico['Loja'] == loja) 
        ].copy()

        if cliente_data.empty:
            return pd.DataFrame()

        date_columns = sorted(
            [col for col in cliente_data.columns if '/' in col],
            key=lambda x: (int(x.split('/')[1]), int(x.split('/')[0]))
        )

        heatmap_df = cliente_data.rename(columns={
            'codigo': 'Código',
            'descrição': 'Descrição'
        })[['Código', 'Descrição'] + date_columns]

        return heatmap_df

    except Exception as e:
        st.error(f"Erro ao processar dados: {str(e)}")
        return pd.DataFrame()

# Renderiza detalhes do cliente
@st.dialog(" ")
def render_cliente_details(id_cliente=None, loja=None, user_id=None, codigo_loja=None):
    print(f"[DEBUG] user_id em uso: {user_id}")

    # Só inicializa se ainda não existir
    st.session_state.setdefault('show_fechado', False)
    st.session_state.setdefault('show_perdido', False)

    cliente_info = dados_clientes[
        (dados_clientes['codigo'].astype(str) == str(id_cliente)) &
        (dados_clientes['loja'] == loja)
    ]

    if cliente_info.empty:
        st.warning("Cliente não encontrado.")
        return

    nome_cliente = cliente_info['nome'].iloc[0]
    loja_cliente = cliente_info['loja'].iloc[0]

    st.markdown("<span class='big-dialog'></span>", unsafe_allow_html=True)
    st.title(f"🔍 Detalhes do Cliente: {nome_cliente} | Loja: {loja_cliente}")

    col1, col2 = st.columns([4, 1])

    with col2:
        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            if st.button("✅ Fechado",
                        use_container_width=True,
                        type='primary',
                        help="Registrar valor fechado"):
                st.session_state.show_fechado = True
                st.session_state.show_perdido = False

        with btn_col2:
            if st.button("❌ Perdido",
                        use_container_width=True,
                        type='secondary',
                        help="Registrar motivo da perda"):
                st.session_state.show_perdido = True
                st.session_state.show_fechado = False

    with col1:
        st.markdown("""
        **📌 Legenda:** 🔢 `Qtd - R$Preço Unitario Médio - % Margem` | 🟢 Compra registrada | 🔴 Nenhuma compra
        """)

    try:
        heatmap_df = criar_heatmap_dataframe(id_cliente, loja)
        render_heatmap_aggrid(heatmap_df)

        user_id = st.session_state.get("user_id")

        render_fechamento_perdido(codigo_loja=codigo_loja, user_id=user_id)

    except Exception as e:
        st.error(f"Erro: {str(e)}")

# CSS dos botões
st.markdown("""
    <style>
        div[data-testid="column"]:nth-of-type(2) {
            display: flex;
            flex-direction: row;
            gap: 10px;
            align-items: start;
        }
        button[kind="primary"] {
            background-color: #2ecc71 !important;
            border-color: #27ae60 !important;
            flex: 1;
        }
        button[kind="secondary"] {
            background-color: #e74c3c !important;
            border-color: #c0392b !important;
            color: white !important;
            flex: 1;
        }
        @media (max-width: 768px) {
            div[data-testid="column"]:nth-of-type(2) {
                flex-direction: column;
            }
        }
    </style>
""", unsafe_allow_html=True)

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, StAggridTheme, GridUpdateMode
from components.cliente_details import render_cliente_details

custom_theme = (  
    StAggridTheme(base="quartz") 
    .withParams(
        fontSize=16,
        rowBorder=False,
        backgroundColor="#FFFFFF"
    )  
    .withParts('iconSetAlpine')  
)

def display_data_table(data):
    """Exibe a tabela de dados formatada com AgGrid"""

    if data.empty:
        st.warning("Nenhum resultado encontrado com os filtros aplicados.")
        return

    st.write("### Tabela de Clientes")

    cell_renderer = JsCode(""" 
    class BtnCellRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            const btn = document.createElement('button');
            btn.innerText = '🔍 Detalhes';
            btn.className = 'btn-simple';
            btn.style = 'color:#fff; background-color:#024528; border:none; padding:5px 10px; border-radius:5px;';
            btn.addEventListener('click', () => {
                // seleciona apenas este node
                params.api.deselectAll();
                params.api.selectNode(params.node, true);
            });
            this.eGui.appendChild(btn);
        }
        getGui() { return this.eGui; }
        refresh()  { return false; }
        destroy()  { /* nada */ }
    }
    """)

    

    gb = GridOptionsBuilder.from_dataframe(data)
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    gb.configure_column("codigo", filter=False, width=110)
    gb.configure_column("loja", filter=False, width=80)
    gb.configure_column("codigo_loja", filter=False, width=80, hide=True)
    gb.configure_column("estado", filter=False, width=80)
    gb.configure_column("nome", filter=False, width=320)
    gb.configure_column("setor", filter=True, width=90)
    gb.configure_column("cidade", filter=True)
    gb.configure_column("status", filter=True, width=140, hide=True)
    gb.configure_column("periodo compra", filter=False, cellStyle={'textAlign': 'center'},width=80)
    gb.configure_column("dias prox compra", filter=False, cellStyle={'textAlign': 'center'},width=80)
    gb.configure_column("Detalhes", cellRenderer=cell_renderer, width=140)

    grid_options = gb.build()

    grid_response = AgGrid(
        data,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        theme=custom_theme,
        height=700,
        fit_columns_on_grid_load=True,
    )

    # Garantir que selected seja uma lista vazia caso não haja seleção
    selected = grid_response.get("selected_rows", [])
    selected = pd.DataFrame(selected)

    print("Selecionado:", selected)  # (para debug)

    if not selected.empty and "codigo" in selected.columns:
        cliente_id = selected.iloc[0]["codigo"]
        loja = selected.iloc[0]["loja"]
        if pd.notna(cliente_id):
            render_cliente_details(
                id_cliente=cliente_id,
                loja=loja,
                user_id=st.session_state.user_id,
                codigo_loja=selected.iloc[0]["codigo_loja"]
                )
        else:
            st.warning("Cliente selecionado não possui ID válido.")

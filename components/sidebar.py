import streamlit as st
from fuzzywuzzy import process
import pandas as pd

def create_sidebar_filters(data):
    """Cria os filtros na sidebar e retorna os valores filtrados."""
    st.sidebar.markdown("### Filtros")
    
    # Filtro por nome (fuzzy)
    busca = st.sidebar.text_input("🔍 Buscar cliente (por nome ou similar):", key="buscar_cliente")
    
    # Filtro por ID
    id_filtro = st.sidebar.text_input("🔍 Filtrar por ID do cliente:", key="filtro_id")
    
    filtered_data = data.copy()
    print(data.columns)
    # Filtro fuzzy apenas se existir uma coluna de nome
    if busca:
        coluna_nome = None
        for col in data.columns:
            print(f"Verificando coluna: '{col}'")  # Verifique o nome da coluna durante a iteração
            if 'nome' in col.lower() or 'razao' in col.lower():
                coluna_nome = col
                break
        
        if coluna_nome:
            # Força a conversão para string para garantir que os dados estejam no formato correto
            data[coluna_nome] = data[coluna_nome].astype(str)
            
            # Realizar busca fuzzy
            nomes = data[coluna_nome].tolist()  # Lista de nomes da coluna
            matches = process.extract(busca, nomes, limit=10)
            
            # Filtro de nomes com score maior que 60
            nomes_filtrados = [nome for nome, score in matches if score > 60]
            
            print(f"Matches encontrados: {matches}")  # Verificando as correspondências
            
            if nomes_filtrados:
                filtered_data = data[data[coluna_nome].isin(nomes_filtrados)]
            else:
                st.sidebar.warning("Nenhum cliente encontrado com esse nome similar.")
        else:
            st.sidebar.warning("Nenhuma coluna relacionada a 'nome' ou 'cliente' encontrada para fazer a busca fuzzy.")

    # Filtro por ID
    if id_filtro:
        coluna_id = None
        for col in data.columns:
            if 'codigo' in col.lower():
                coluna_id = col
                break
        
        if coluna_id:
            # Verificar se o valor da ID é numérico ou string
            filtered_data = filtered_data[filtered_data[coluna_id].astype(str).str.contains(id_filtro)]
        else:
            st.sidebar.warning("Nenhuma coluna de ID encontrada para filtrar.")

    # Filtros de ordenação dinâmicos
    colunas_disponiveis = list(filtered_data.columns)
    col1, col2 = st.sidebar.columns(2)

    with col1:
        coluna_ordenacao = st.selectbox("Ordenar por:", colunas_disponiveis)
    with col2:
        ordem = st.radio("Ordem:", ('Crescente', 'Decrescente'))
    
    ascending = ordem == 'Crescente'

    colunas_esperadas = ["codigo", "Detalhes"]
    for col in colunas_esperadas:
        if col not in filtered_data.columns:
            filtered_data[col] = ""
    filtered_data["codigo"] = filtered_data["codigo"].astype(str)
    print(filtered_data)

    return filtered_data.sort_values(by=coluna_ordenacao, ascending=ascending)

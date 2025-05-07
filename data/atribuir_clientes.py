import pandas as pd
import random
import json
import os
from datetime import date, timedelta
from config import BASE_CLIENTES

# ==== CONFIGURAÇÕES ====
CAMINHO_CLIENTES = BASE_CLIENTES
CAMINHO_JSON = "data/clientes_atribuidos.json"
USUARIOS = ["Franciele", "Julia", "Erica"]
CLIENTES_POR_USUARIO = 15
NUM_DIAS = 5
DATA_INICIAL = date.today()

def atribuir_clientes():
    # Carregar dados de clientes
    df = pd.read_parquet(CAMINHO_CLIENTES)
    
    # Verificando se as colunas necessárias existem
    if 'codigo cliente' not in df.columns or 'status' not in df.columns or 'loja' not in df.columns:
        raise ValueError("O DataFrame deve conter as colunas 'codigo cliente', 'status' e 'loja'")

    # Combina 'codigo cliente' e 'loja' para criar uma chave única
    df['codigo_loja'] = df['codigo cliente'].astype(str) + '_' + df['loja'].astype(str)

    # Selecionar as colunas necessárias e remover duplicatas
    df = df[['codigo_loja', 'status']].drop_duplicates()
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # Embaralhar

    # Ler o arquivo JSON existente
    if os.path.exists(CAMINHO_JSON):
        with open(CAMINHO_JSON, "r") as f:
            clientes_atribuidos = json.load(f)
    else:
        clientes_atribuidos = {}

    # Verificar a última data atribuída
    ultima_data = max([date.fromisoformat(d) for d in clientes_atribuidos.keys()], default=None)

    if ultima_data and ultima_data >= date.today():
        print("Atribuição já realizada para hoje ou futuro.")
        return

    # Filtrar clientes não atribuídos
    clientes_ja_atribuidos = set()
    for dia in clientes_atribuidos.values():
        for clientes_usuario in dia.values():
            for cliente in clientes_usuario:
                clientes_ja_atribuidos.add(cliente['codigo_loja'])

    clientes_disponiveis = df[~df['codigo_loja'].isin(clientes_ja_atribuidos)].copy()

    # Gerar novas atribuições para os próximos dias
    for i in range(NUM_DIAS):
        data_str = str(DATA_INICIAL + timedelta(days=i))
        if data_str in clientes_atribuidos:
            continue  # Pula se já foi gerado

        clientes_atribuidos[data_str] = {}

        for usuario in USUARIOS:
            if len(clientes_disponiveis) < CLIENTES_POR_USUARIO:
                raise ValueError("Não há clientes suficientes para nova atribuição.")

            amostra = clientes_disponiveis.sample(n=CLIENTES_POR_USUARIO, random_state=random.randint(0, 9999))
            clientes_disponiveis = clientes_disponiveis.drop(amostra.index)

            clientes_atribuidos[data_str][usuario] = amostra.to_dict(orient='records')

    # Salvar o arquivo JSON atualizado
    with open(CAMINHO_JSON, "w") as f:
        json.dump(clientes_atribuidos, f, indent=4)

    print(f"✅ Atribuição de clientes concluída para os próximos {NUM_DIAS} dias.")

import pandas as pd
import random
import json
import os
from datetime import date, timedelta
from config import GoogleDriveClient

# ==== CONFIGURAÇÕES ====
CAMINHO_CLIENTES = os.path.join("temp_data", "clientes_dash_televendas.parquet")
CAMINHO_JSON = os.path.join("temp_data", "clientes_atribuidos.json")
USUARIOS = ["Todos","Franciele", "Julia", "Erica", "Laysa", "Lenice"]
CLIENTES_POR_USUARIO = 15
NUM_DIAS = 5
DATA_INICIAL = date.today()

def atribuir_clientes(user_id=None):
    print("🔄 Iniciando atribuição de clientes...")

    # Inicializa o cliente do Google Drive
    gdrive_client = GoogleDriveClient()
    pasta_clientes = '1SGB1HO0MQxUoJcBAEicTmxxE4hg_y47E'
    pasta_atribuidos = '1SGB1HO0MQxUoJcBAEicTmxxE4hg_y47E'

    os.makedirs("temp_data", exist_ok=True)

    # Carrega parquet
    if os.path.exists(CAMINHO_CLIENTES):
        df = pd.read_parquet(CAMINHO_CLIENTES)
    else:
        arquivos = gdrive_client.list_files(folder_id=pasta_clientes)
        arq = next((f for f in arquivos if f['name'] == 'clientes_dash_televendas.parquet'), None)
        if not arq:
            print("❌ Arquivo de clientes não encontrado no Google Drive.")
            return
        gdrive_client.download_file(arq['id'], CAMINHO_CLIENTES)
        df = pd.read_parquet(CAMINHO_CLIENTES)

    # Validação de colunas
    for col in ['codigo cliente', 'status', 'loja', 'setor']:
        if col not in df.columns:
            raise ValueError(f"Coluna faltando: {col}")

    df['codigo_loja'] = df['codigo cliente'].astype(str) + '_' + df['loja'].astype(str)
    df = df[['codigo_loja', 'status', 'setor']].drop_duplicates()
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    df_completo = df.copy()  # <-- snapshot da base para "Todos"

    print(f"📦 Total de clientes únicos: {len(df)}")

    # Regras fixas
    REGRAS_SETOR = {
        "Laysa": ['500', '501', '502', '503', '503', '505', '506', '507'],
        "Lenice": ['210', '239', '225', '242', '244'],
        "Todos": [
            '105', '104', '108', '110', '102',
            '139', '101', '137', '100', '134',
            '106', '103', '122', '112', '114',
            '123', '128', '124', '107', '401',
            '400', '402', '403', '405', '406',
            '404', '424', '411', '407', '410',
            '200', '225', '210', '242', '239',
            '244', '9907', '9906', '9902', '9904',
            '9901', '9900', '9910', '9909', '504',
            '506', '503', '505', '501', '502',
            '507', '500', '1013', '1010', '1011',
            '1008', '1000', '1009', '1004', '1005',
            '1001', '1002', '1003', '1006', '1007',
            '618', '617', '601', '619', '600',
            '602', '614', '615', '612', '608',
            '603', '609', '604', '605', '610',
            '708', '704', '703', '701', '702',
            '705', '711', '710', '707', '709',
            '700', '805', '806', '811', '807',
            '808', '810', '800', '801', '809',
            '803', '804', '802', '908', '902',
            '903', '904', '901', '900', '905',
            '907', '906', '2015', '2017', '2018',
            '2000', '2004', '2003', '2005', '2002',
            '2001', '2006', '2008', '2007', '2014',
            '2012', '2009', '2011', '2010', '10001'
        ]

    }
    USUARIOS_FIXOS = list(REGRAS_SETOR.keys())
    USUARIOS_DISTRIBUICAO = [u for u in USUARIOS if u not in USUARIOS_FIXOS and u != "Todos"]

    # Separa clientes de usuários fixos
    clientes_atribuidos_setor = {}
    for usuario, setores in REGRAS_SETOR.items():
        clientes_usuario = df[df['setor'].isin(setores)].copy()
        df = df[~df.index.isin(clientes_usuario.index)]
        clientes_atribuidos_setor[usuario] = clientes_usuario

    # Histórico
    arquivos_atribuidos = gdrive_client.list_files(folder_id=pasta_atribuidos)
    arquivos_filtrados = [
        f for f in arquivos_atribuidos
        if f['name'].startswith("clientes_atribuidos_") and f['name'].endswith(".json")
    ]
    arquivos_ordenados = sorted(arquivos_filtrados, key=lambda x: x['name'], reverse=True)
    arquivo_mais_recente = arquivos_ordenados[0] if arquivos_ordenados else None

    if arquivo_mais_recente:
        gdrive_client.download_file(arquivo_mais_recente['id'], CAMINHO_JSON)
        with open(CAMINHO_JSON, "r") as f:
            clientes_atribuidos = json.load(f)
    else:
        clientes_atribuidos = {}

    if user_id is None:
        ultima_data = max([date.fromisoformat(d) for d in clientes_atribuidos.keys()], default=None)
        if ultima_data and ultima_data >= date.today():
            print("✅ Atribuições já feitas para hoje ou datas futuras.")
            return

    clientes_ja_atribuidos = set()
    for dia in clientes_atribuidos.values():
        for usuarios in dia.values():
            for cliente in usuarios:
                clientes_ja_atribuidos.add(cliente['codigo_loja'])

    clientes_disponiveis = df[~df['codigo_loja'].isin(clientes_ja_atribuidos)].copy()

    # Loop dias
    for i in range(NUM_DIAS):
        data_str = str(DATA_INICIAL + timedelta(days=i))
        if data_str not in clientes_atribuidos:
            clientes_atribuidos[data_str] = {}

        # Só um usuário
        if user_id:
            if user_id == "Todos":
                clientes_atribuidos[data_str][user_id] = df_completo.to_dict(orient='records')
                continue

            if user_id in clientes_atribuidos[data_str] and clientes_atribuidos[data_str][user_id]:
                continue

            if user_id in USUARIOS_FIXOS:
                setores = REGRAS_SETOR[user_id]
                amostra = df[df['setor'].isin(setores)]
            else:
                if len(clientes_disponiveis) < CLIENTES_POR_USUARIO:
                    continue
                amostra = clientes_disponiveis.sample(n=CLIENTES_POR_USUARIO, random_state=random.randint(0, 9999))
                clientes_disponiveis = clientes_disponiveis.drop(amostra.index)

            clientes_atribuidos[data_str][user_id] = amostra.to_dict(orient='records')

        # Todos usuários
        else:
            for usuario in USUARIOS_FIXOS:
                amostra = clientes_atribuidos_setor[usuario].copy()
                clientes_atribuidos[data_str][usuario] = amostra.to_dict(orient='records')

            # Todos = base completa
            clientes_atribuidos[data_str]["Todos"] = df_completo.to_dict(orient='records')

            for usuario in USUARIOS_DISTRIBUICAO:
                if len(clientes_disponiveis) < CLIENTES_POR_USUARIO:
                    break
                amostra = clientes_disponiveis.sample(n=CLIENTES_POR_USUARIO, random_state=random.randint(0, 9999))
                clientes_disponiveis = clientes_disponiveis.drop(amostra.index)
                clientes_atribuidos[data_str][usuario] = amostra.to_dict(orient='records')

    # Salva
    with open(CAMINHO_JSON, "w") as f:
        json.dump(clientes_atribuidos, f, indent=4)

    gdrive_client.upload_file(CAMINHO_JSON, pasta_atribuidos)
    print("✅ Atribuição concluída!")

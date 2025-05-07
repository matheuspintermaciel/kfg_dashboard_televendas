import base64
from pathlib import Path
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()

# Usa Path para resolver caminhos
BASE_CLIENTES = Path(os.getenv("BASE_CLIENTES")).resolve()
# Usa Path para resolver caminhos
BASE_HISTORICO = Path(os.getenv("BASE_HISTORICO")).resolve()

# Configurações da página
PAGE_CONFIG = {
    "page_title": "Home",
    "page_icon": "📝",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Caminhos de arquivos
ASSETS_PATH = Path("assets")
LOGO_PATH = ASSETS_PATH / "KFG_Distribuidora_logo_CMYK.png"

# Estilos CSS
CSS_STYLES = """
<style>
    /* Modifica a largura da sidebar para 20% da tela */
    .css-1d391kg {  /* Classe da sidebar */
        width: 20% !important;
    }

    /* Ajuste o logo para não afetar a largura da sidebar */
    .css-1d391kg img {
        width: 80px;  /* Tamanho fixo do logo */
        margin-bottom: 1rem;
    }

    /* Modifica o tamanho padrão de modal do streamlit */
    div[data-testid="stDialog"] div[role="dialog"]:has(.big-dialog) {
        width: 95vw;
    }

    /* Esconde elementos da sidebar */
    .st-emotion-cache-y6y7ju.em9zgd018,
    div[data-testid="stSidebarNav"],
    div[data-testid="stSidebarNavItems"],
    div[data-testid="stSidebarNavSeparator"] {
        display: none !important;
    }
    
    /* Garante que cada botão ocupe todo o card e tenha padding bottom */
    .stButton > button {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            padding-bottom: 160px;
            opacity: 0;
            cursor: pointer;
            z-index: 1;
        }
    /* Container relativo para posicionamento do botão */
    .card-container { position: relative; }
</style>
"""

CARD_STYLES = """
<style>
    .card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    .card-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .card-value {
        font-size: 1.5rem;
    }
</style>
"""


def get_logo_base64():
    """Converte a imagem do logo para base64"""
    return base64.b64encode(LOGO_PATH.read_bytes()).decode()
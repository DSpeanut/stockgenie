from pathlib import Path
import os
from fastapi.templating import Jinja2Templates
SRC_DIR = Path(__file__).parent.parent
BASE_DIR = Path(__file__).parent.parent.parent
PROMPTS_PATH = SRC_DIR / "engine" / "prompts.yaml"
TEMPLATE_DIR = BASE_DIR / "templates"
DATA_DIR = BASE_DIR / 'data'
ENV_PATH = BASE_DIR / ".env"
VECDB_PATH = BASE_DIR / "chroma_db"
INVENTORY_PATH = BASE_DIR / 'data' / 'kis_holding_df.csv'
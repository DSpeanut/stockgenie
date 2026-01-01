from pathlib import Path
import os
from fastapi.templating import Jinja2Templates
SRC_DIR = Path(__file__).parent.parent
BASE_DIR = Path(__file__).parent.parent.parent
PROMPTS_PATH = SRC_DIR / "engine" / "prompts.yaml"
# 2. Path to Templates Folder
TEMPLATE_DIR = BASE_DIR / "templates"


print(TEMPLATE_DIR)
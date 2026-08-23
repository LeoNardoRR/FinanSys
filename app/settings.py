import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
STATIC_DIR = PROJECT_DIR / "app" / "static"
TEMPLATE_DIR = PROJECT_DIR / "app" / "templates"
DATABASE_PATH = DATA_DIR / "finansys.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}")
APP_NAME = "FinanSys"
API_TOKEN = os.getenv("FINANSYS_API_TOKEN", "")
HOST = os.getenv("FINANSYS_HOST", "127.0.0.1")
PORT = int(os.getenv("FINANSYS_PORT", "8000"))

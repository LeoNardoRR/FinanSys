from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
STATIC_DIR = PROJECT_DIR / "app" / "static"
TEMPLATE_DIR = PROJECT_DIR / "app" / "templates"
DATABASE_PATH = DATA_DIR / "finansys.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"
APP_NAME = "FinanSys"

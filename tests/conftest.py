import os
from pathlib import Path

_TEST_BACKUP_DIR = Path(__file__).resolve().parent / "backup_test_runtime" / "lifecycle"
os.environ["FINANSYS_BACKUP_DIR"] = str(_TEST_BACKUP_DIR)

from contextlib import closing
import json
import sqlite3
from pathlib import Path
from zipfile import ZipFile

from app.services.automatic_backup import BACKUP_1, BACKUP_2, rotate_automatic_backups

RUNTIME = Path(__file__).resolve().parent / "backup_test_runtime" / "rotation"
DATABASE = RUNTIME / "finansys.db"
BACKUPS = RUNTIME


def reset_runtime() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    for path in RUNTIME.rglob("*"):
        if path.is_file():
            path.unlink()


def create_database(path: Path, value: str) -> None:
    path.touch()
    with closing(sqlite3.connect(path)) as connection:
        connection.execute("CREATE TABLE state (value TEXT)")
        connection.execute("INSERT INTO state VALUES (?)", (value,))
        connection.commit()


def update_database(path: Path, value: str) -> None:
    with closing(sqlite3.connect(path)) as connection:
        connection.execute("UPDATE state SET value = ?", (value,))
        connection.commit()


def read_backup_value(path: Path, extract_dir: Path) -> tuple[str, dict]:
    extracted = extract_dir / "finansys.db"
    extracted.unlink(missing_ok=True)
    with ZipFile(path) as archive:
        archive.extract("finansys.db", extract_dir)
        metadata = json.loads(archive.read("backup_info.json"))
    with closing(sqlite3.connect(extracted)) as connection:
        value = connection.execute("SELECT value FROM state").fetchone()[0]
    return value, metadata


def test_rotating_automatic_backups_keep_two_valid_versions():
    reset_runtime()
    create_database(DATABASE, "primeira")
    first = rotate_automatic_backups("abertura", database_path=DATABASE, target_dir=BACKUPS)
    assert first["success"] is True
    assert (BACKUPS / BACKUP_1).is_file()
    assert (BACKUPS / BACKUP_2).is_file()

    update_database(DATABASE, "segunda")
    second = rotate_automatic_backups("encerramento", database_path=DATABASE, target_dir=BACKUPS)
    assert second["success"] is True

    newest_value, newest_info = read_backup_value(BACKUPS / BACKUP_1, RUNTIME / "newest")
    previous_value, previous_info = read_backup_value(BACKUPS / BACKUP_2, RUNTIME / "previous")
    assert newest_value == "segunda"
    assert previous_value == "primeira"
    assert newest_info["event"] == "encerramento"
    assert previous_info["event"] == "abertura"
    assert not list(BACKUPS.glob(".FinanSys_*"))


def test_missing_database_does_not_replace_backups():
    result = rotate_automatic_backups("abertura", database_path=RUNTIME / "missing.db", target_dir=BACKUPS)
    assert result == {"success": False, "reason": "database_missing"}

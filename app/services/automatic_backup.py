from contextlib import closing
import json
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile

from app.settings import DATABASE_PATH

BACKUP_1 = "FinanSys_backup_1.zip"
BACKUP_2 = "FinanSys_backup_2.zip"


def desktop_directory() -> Path:
    override = os.environ.get("FINANSYS_BACKUP_DIR")
    if override:
        return Path(override).expanduser().resolve()

    if os.name == "nt":
        try:
            import winreg

            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                raw, _ = winreg.QueryValueEx(key, "Desktop")
            resolved = Path(os.path.expandvars(raw)).expanduser()
            if resolved:
                return resolved
        except (OSError, ValueError):
            pass

    candidates = [
        Path.home() / "Desktop",
        Path(os.environ.get("OneDrive", "")) / "Desktop" if os.environ.get("OneDrive") else None,
        Path.home() / "Área de Trabalho",
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate
    return Path.home() / "Desktop"


def automatic_backup_directory() -> Path:
    return desktop_directory() / "Backups FinanSys"


def _sqlite_snapshot(source: Path, destination: Path) -> None:
    with closing(sqlite3.connect(source)) as source_db, closing(sqlite3.connect(destination)) as destination_db:
        source_db.backup(destination_db)
    with closing(sqlite3.connect(destination)) as check_db:
        result = check_db.execute("PRAGMA quick_check").fetchone()
    if not result or result[0] != "ok":
        raise RuntimeError("A verificação de integridade do banco não retornou OK.")


def _create_zip(source: Path, destination: Path, event: str) -> None:
    snapshot = destination.parent / f".FinanSys_snapshot_{uuid4().hex}.db"
    try:
        _sqlite_snapshot(source, snapshot)
        metadata = {
            "application": "FinanSys",
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "event": event,
            "database_file": "finansys.db",
        }
        with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
            archive.write(snapshot, arcname="finansys.db")
            archive.writestr("backup_info.json", json.dumps(metadata, ensure_ascii=False, indent=2))
    finally:
        snapshot.unlink(missing_ok=True)


def rotate_automatic_backups(event: str, database_path: Path = DATABASE_PATH, target_dir: Path | None = None) -> dict:
    if not database_path.is_file():
        return {"success": False, "reason": "database_missing"}

    backup_dir = target_dir or automatic_backup_directory()
    backup_dir.mkdir(parents=True, exist_ok=True)
    newest = backup_dir / BACKUP_1
    previous = backup_dir / BACKUP_2
    new_temp = backup_dir / ".FinanSys_backup_new.zip"
    previous_temp = backup_dir / ".FinanSys_backup_previous.zip"

    new_temp.unlink(missing_ok=True)
    previous_temp.unlink(missing_ok=True)
    try:
        _create_zip(database_path, new_temp, event)
        if newest.exists():
            shutil.copy2(newest, previous_temp)
            os.replace(previous_temp, previous)
        os.replace(new_temp, newest)
        if not previous.exists():
            shutil.copy2(newest, previous)
    finally:
        new_temp.unlink(missing_ok=True)
        previous_temp.unlink(missing_ok=True)

    return {
        "success": True,
        "directory": str(backup_dir),
        "newest": str(newest),
        "previous": str(previous),
        "event": event,
    }

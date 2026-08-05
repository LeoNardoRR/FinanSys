from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_SUFFIXES = {".py", ".html", ".css", ".js", ".md", ".svg", ".txt", ".yml", ".yaml"}
ROOT_TEXT_FILES = ("README.md", "CONTRIBUTING.md", "SECURITY.md", "PROJECT_STATUS.md")
MOJIBAKE_MARKERS = (
    "\u00c3\u00a1", "\u00c3\u00a0", "\u00c3\u00a2", "\u00c3\u00a3", "\u00c3\u00a7",
    "\u00c3\u00a9", "\u00c3\u00aa", "\u00c3\u00ad", "\u00c3\u00b3", "\u00c3\u00b4",
    "\u00c3\u00b5", "\u00c3\u00ba", "\u00c3\u0081", "\u00c3\u0087", "\u00c3\u0093",
    "\u00c2\u00a0", "\u00e2\u20ac\u0093", "\u00e2\u20ac\u0094", "\u00e2\u20ac\u009c",
    "\u00e2\u20ac\u009d", "\u00ef\u00bf\u00bd",
)


def public_text_files():
    for name in ROOT_TEXT_FILES:
        yield ROOT / name
    for directory in (ROOT / "app", ROOT / "docs", ROOT / "tests", ROOT / ".github"):
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                yield path


def test_public_text_files_are_valid_utf8_without_mojibake():
    corrupted = []
    for path in public_text_files():
        text = path.read_text(encoding="utf-8-sig")
        if any(marker in text for marker in MOJIBAKE_MARKERS):
            corrupted.append(str(path.relative_to(ROOT)))
    assert not corrupted, f"Arquivos com possível texto corrompido: {corrupted}"

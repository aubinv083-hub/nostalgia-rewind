from pathlib import Path

from config import DATA_DIR, RAW_DIR, PROCESSED_DIR, HTML_DIR


def ensure_data_dirs() -> None:
    """
    Create data directories if they do not exist.
    """
    for path in (DATA_DIR, RAW_DIR, PROCESSED_DIR, HTML_DIR):
        Path(path).mkdir(parents=True, exist_ok=True)

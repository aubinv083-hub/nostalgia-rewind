from pathlib import Path

from config import DATA_DIR, RAW_DIR, PROCESSED_DIR, HTML_DIR, HTML_CACHE_ENABLED


def ensure_data_dirs() -> None:
    """
    Create data directories if they do not exist.
    """
    paths = [DATA_DIR, RAW_DIR, PROCESSED_DIR]
    if HTML_CACHE_ENABLED:
        paths.append(HTML_DIR)

    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)

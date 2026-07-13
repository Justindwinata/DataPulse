from collections.abc import Iterator
from pathlib import Path
import sqlite3


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[3] / "data" / "datapulse.sqlite3"


def connect(database_path: Path | str = DEFAULT_DATABASE_PATH) -> sqlite3.Connection:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_connection(database_path: Path | str = DEFAULT_DATABASE_PATH) -> Iterator[sqlite3.Connection]:
    connection = connect(database_path)
    try:
        yield connection
    finally:
        connection.close()

"""JSON helpers for database metadata and table rows."""

import json
import re
from pathlib import Path

TABLE_DATA_DIR = Path("data")
_TABLE_NAME = re.compile(r"^[\w-]+$", re.UNICODE)


def load_metadata(filepath: str | Path) -> dict[str, dict[str, str]]:
    """Load table metadata, returning an empty mapping when it does not exist."""
    try:
        with Path(filepath).open(encoding="utf-8") as metadata_file:
            return json.load(metadata_file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str | Path, data: dict[str, dict[str, str]]) -> None:
    """Write table metadata to a JSON file."""
    with Path(filepath).open("w", encoding="utf-8") as metadata_file:
        json.dump(data, metadata_file, ensure_ascii=False, indent=2)
        metadata_file.write("\n")


def _table_data_path(table_name: str) -> Path:
    """Return the JSON path for a safe table name."""
    if not _TABLE_NAME.fullmatch(table_name):
        raise ValueError(f"Некорректное имя таблицы: {table_name}")
    return TABLE_DATA_DIR / f"{table_name}.json"


def load_table_data(table_name: str) -> list[dict[str, str | int | bool]]:
    """Load rows from a table's JSON file, or return an empty table."""
    filepath = _table_data_path(table_name)
    try:
        with filepath.open(encoding="utf-8") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        return []

    if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
        raise ValueError(f"Некорректный формат данных таблицы: {table_name}")
    return data


def save_table_data(
    table_name: str,
    data: list[dict[str, str | int | bool]],
) -> None:
    """Write table rows to data/<table_name>.json."""
    filepath = _table_data_path(table_name)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open("w", encoding="utf-8") as data_file:
        json.dump(data, data_file, ensure_ascii=False, indent=2)
        data_file.write("\n")


def delete_table_data(table_name: str) -> None:
    """Remove a table's JSON file when the table is dropped."""
    try:
        _table_data_path(table_name).unlink()
    except FileNotFoundError:
        pass

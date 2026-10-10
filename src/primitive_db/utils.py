"""JSON helpers for the database metadata file."""

import json
from pathlib import Path


def load_metadata(filepath: str | Path) -> dict[str, dict[str, str]]:
    """Load table metadata, returning an empty mapping when it does not exist."""
    try:
        with Path(filepath).open(encoding="utf-8") as metadata_file:
            return json.load(metadata_file)
    except FileNotFoundError:
        return {}


def save_metadata(
    filepath: str | Path, data: dict[str, dict[str, str]]
) -> None:
    """Write table metadata to a JSON file."""
    with Path(filepath).open("w", encoding="utf-8") as metadata_file:
        json.dump(data, metadata_file, ensure_ascii=False, indent=2)
        metadata_file.write("\n")

"""Shared constants used by the database application."""

import re
from pathlib import Path

META_FILE = Path("db_meta.json")
DATA_DIR = Path("data")
VALID_TYPES = frozenset({"int", "str", "bool"})
TABLE_NAME_PATTERN = re.compile(r"^[\w-]+$", re.UNICODE)

INSERT_COMMAND = re.compile(
    r"insert\s+into\s+([\w-]+)\s+values\s*(\(.*\))\s*",
    re.IGNORECASE | re.DOTALL,
)
SELECT_COMMAND = re.compile(
    r"select\s+from\s+([\w-]+)(?:\s+where\s+(.+))?\s*",
    re.IGNORECASE | re.DOTALL,
)
UPDATE_COMMAND = re.compile(
    r"update\s+([\w-]+)\s+set\s+(.+)\s*",
    re.IGNORECASE | re.DOTALL,
)
DELETE_COMMAND = re.compile(
    r"delete\s+from\s+([\w-]+)\s+where\s+(.+)\s*",
    re.IGNORECASE | re.DOTALL,
)
INFO_COMMAND = re.compile(r"info\s+([\w-]+)\s*", re.IGNORECASE)

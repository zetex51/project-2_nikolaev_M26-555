"""Shared constants used by the database application."""

import re
from pathlib import Path
from types import MappingProxyType

META_FILE = Path("db_meta.json")
DATA_DIR = Path("data")
ID_COLUMN = "ID"
INTEGER_TYPE = "int"
STRING_TYPE = "str"
BOOLEAN_TYPE = "bool"
TYPE_CLASSES = MappingProxyType({
    INTEGER_TYPE: int,
    STRING_TYPE: str,
    BOOLEAN_TYPE: bool,
})
VALID_TYPES = frozenset(TYPE_CLASSES)
TABLE_NAME_PATTERN = re.compile(r"^[\w-]+$", re.UNICODE)
INTEGER_PATTERN = re.compile(r"^[+-]?\d+$")
IDENTIFIER_PATTERN = re.compile(r"^\w+$", re.UNICODE)
TRUE_LITERAL = "true"
FALSE_LITERAL = "false"

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

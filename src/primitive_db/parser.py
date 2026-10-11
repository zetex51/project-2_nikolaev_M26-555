"""Parsers for SQL-like data commands used by the console application."""

import shlex

from primitive_db.constants import (
    FALSE_LITERAL,
    IDENTIFIER_PATTERN,
    INTEGER_PATTERN,
    TRUE_LITERAL,
)


def _split_unquoted(text: str, delimiter: str) -> list[str]:
    """Split on a delimiter outside single- or double-quoted strings."""
    parts: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escaped = False

    for character in text:
        if escaped:
            current.append(character)
            escaped = False
            continue
        if quote is not None and character == "\\":
            current.append(character)
            escaped = True
            continue
        if quote is not None:
            current.append(character)
            if character == quote:
                quote = None
            continue
        if character in {"'", '"'}:
            quote = character
            current.append(character)
        elif character == delimiter:
            parts.append("".join(current).strip())
            current.clear()
        else:
            current.append(character)

    if quote is not None or escaped:
        raise ValueError("незакрытая строка")
    parts.append("".join(current).strip())
    return parts


def _parse_literal(text: str) -> str | int | bool:
    """Parse one quoted string, integer, or boolean literal."""
    value = text.strip()
    if not value:
        raise ValueError("пустое значение")

    if value[0] in {"'", '"'}:
        if len(value) < 2 or value[-1] != value[0]:
            raise ValueError("строковые значения должны быть в кавычках")
        try:
            parsed = shlex.split(value)
        except ValueError as error:
            raise ValueError("некорректная строка") from error
        if len(parsed) != 1:
            raise ValueError("некорректная строка")
        return parsed[0]

    lowered = value.lower()
    if lowered in {TRUE_LITERAL, FALSE_LITERAL}:
        return lowered == TRUE_LITERAL
    if INTEGER_PATTERN.fullmatch(value):
        return int(value)
    raise ValueError(f"строковое значение {value} должно быть в кавычках")


def parse_values(text: str) -> list[str | int | bool]:
    """Parse a parenthesized comma-separated list of values."""
    value_list = text.strip()
    if not (value_list.startswith("(") and value_list.endswith(")")):
        raise ValueError("ожидается список значений в скобках")

    contents = value_list[1:-1].strip()
    if not contents:
        return []
    return [_parse_literal(value) for value in _split_unquoted(contents, ",")]


def _partition_unquoted(text: str, delimiter: str) -> tuple[str, str]:
    """Split once on a delimiter outside quoted strings."""
    parts = _split_unquoted(text, delimiter)
    if len(parts) < 2:
        raise ValueError(f"ожидается разделитель {delimiter}")
    return parts[0], delimiter.join(parts[1:]).strip()


def split_keyword(text: str, keyword: str) -> tuple[str, str]:
    """Split once at a whitespace-delimited keyword outside quoted strings."""
    quote: str | None = None
    escaped = False
    lowered = text.lower()
    keyword = keyword.lower()

    for index, character in enumerate(text):
        if escaped:
            escaped = False
            continue
        if quote is not None and character == "\\":
            escaped = True
            continue
        if quote is not None:
            if character == quote:
                quote = None
            continue
        if character in {"'", '"'}:
            quote = character
            continue

        end = index + len(keyword)
        if (
            lowered[index:end] == keyword
            and index > 0
            and end < len(text)
            and text[index - 1].isspace()
            and text[end].isspace()
        ):
            return text[:index].strip(), text[end:].strip()

    raise ValueError(f"ожидается ключевое слово {keyword}")


def parse_assignments(
    text: str,
    *,
    allow_multiple: bool = True,
) -> dict[str, str | int | bool]:
    """Parse assignments such as ``age = 28`` or ``name = 'Ada', age = 28``."""
    raw_assignments = _split_unquoted(text, ",")
    if not allow_multiple and len(raw_assignments) != 1:
        raise ValueError("в условии допускается только один столбец")

    assignments: dict[str, str | int | bool] = {}
    for raw_assignment in raw_assignments:
        column_name, raw_value = _partition_unquoted(raw_assignment, "=")
        if not IDENTIFIER_PATTERN.fullmatch(column_name):
            raise ValueError(f"некорректное имя столбца: {column_name}")
        if column_name in assignments:
            raise ValueError(f"столбец {column_name} указан несколько раз")
        assignments[column_name] = _parse_literal(raw_value)
    return assignments

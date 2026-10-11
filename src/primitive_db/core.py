"""Core operations for database tables and their rows."""

from primitive_db.constants import TABLE_NAME_PATTERN, VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import load_table_data

Metadata = dict[str, dict[str, str]]
Value = str | int | bool
Row = dict[str, Value]
_select_cache = create_cacher()


def _invalid_value(value: str) -> None:
    print(f"Некорректное значение: {value}. Попробуйте снова.")


@handle_db_errors
def create_table(metadata: Metadata, table_name: str, columns: list[str]) -> Metadata:
    """Create a table, adding an integer ID column when it was not supplied."""
    if not TABLE_NAME_PATTERN.fullmatch(table_name):
        _invalid_value(table_name or "<имя таблицы>")
        return metadata

    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    parsed_columns: dict[str, str] = {}
    for column in columns:
        if ":" not in column:
            _invalid_value(column)
            return metadata

        column_name, column_type = (part.strip() for part in column.split(":", 1))
        if (
            not column_name
            or any(character.isspace() for character in column_name)
            or column_type not in VALID_TYPES
            or column_name in parsed_columns
        ):
            _invalid_value(column)
            return metadata
        parsed_columns[column_name] = column_type

    id_type = parsed_columns.pop("ID", "int")
    if id_type != "int":
        _invalid_value(f"ID:{id_type}")
        return metadata

    table_columns = {"ID": "int", **parsed_columns}
    metadata[table_name] = table_columns
    formatted_columns = ", ".join(
        f"{column_name}:{column_type}"
        for column_name, column_type in table_columns.items()
    )
    print(f'Таблица "{table_name}" успешно создана со столбцами: {formatted_columns}')
    return metadata


def list_tables(metadata: Metadata) -> list[str]:
    """Return table names in their creation order."""
    return list(metadata)


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: Metadata, table_name: str) -> Metadata:
    """Remove a table from metadata if it exists."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def _value_has_type(value: Value, expected_type: str) -> bool:
    """Check a value without treating bool as an int."""
    return {
        "int": type(value) is int,
        "str": type(value) is str,
        "bool": type(value) is bool,
    }.get(expected_type, False)


@handle_db_errors
@log_time
def insert(
    metadata: Metadata,
    table_name: str,
    values: list[Value],
    table_data: list[Row] | None = None,
) -> list[Row]:
    """Append a validated record with the next ID and return all table rows."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data if table_data is not None else []

    rows = list(table_data) if table_data is not None else load_table_data(table_name)
    columns = [name for name in metadata[table_name] if name != "ID"]
    if len(values) != len(columns):
        print(f"Ошибка: ожидалось значений: {len(columns)}, получено: {len(values)}.")
        return rows

    for column_name, value in zip(columns, values, strict=True):
        expected_type = metadata[table_name][column_name]
        if not _value_has_type(value, expected_type):
            print(
                f"Ошибка: столбец {column_name} ожидает тип "
                f"{expected_type}, получен {type(value).__name__}."
            )
            return rows

    ids = [row.get("ID", 0) for row in rows]
    next_id = max((value for value in ids if type(value) is int), default=0) + 1
    record: Row = {"ID": next_id}
    record.update(zip(columns, values, strict=True))
    rows.append(record)
    print(f'Запись с ID={next_id} успешно добавлена в таблицу "{table_name}".')
    return rows


def _matches(row: Row, where_clause: dict[str, Value]) -> bool:
    """Compare values with exact types, so True does not match integer 1."""
    return all(
        key in row and type(row[key]) is type(value) and row[key] == value
        for key, value in where_clause.items()
    )


@handle_db_errors
@log_time
def select(
    table_data: list[Row],
    where_clause: dict[str, Value] | None = None,
) -> list[Row]:
    """Return cached rows matching every requested field."""
    rows_key = tuple(
        tuple((column, row[column]) for column in sorted(row)) for row in table_data
    )
    where_key = None if where_clause is None else tuple(sorted(where_clause.items()))
    cache_key = rows_key, where_key

    def find_rows() -> list[Row]:
        if where_clause is None:
            return [row.copy() for row in table_data]
        return [row.copy() for row in table_data if _matches(row, where_clause)]

    cached_rows = _select_cache(cache_key, find_rows)
    return [row.copy() for row in cached_rows]


@handle_db_errors
def update(
    table_data: list[Row],
    set_clause: dict[str, Value],
    where_clause: dict[str, Value],
) -> list[Row]:
    """Update matching rows in place and return the full updated table."""
    for row in table_data:
        if _matches(row, where_clause):
            row.update(set_clause)
    return table_data


@handle_db_errors
@confirm_action("удаление записей")
def delete(
    table_data: list[Row],
    where_clause: dict[str, Value],
) -> list[Row]:
    """Remove rows matching every requested field and return remaining rows."""
    return [row for row in table_data if not _matches(row, where_clause)]

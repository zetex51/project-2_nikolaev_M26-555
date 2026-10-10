"""Core operations for creating, listing, and dropping database tables."""

Metadata = dict[str, dict[str, str]]
SUPPORTED_TYPES = {"int", "str", "bool"}


def _invalid_value(value: str) -> None:
    print(f"Некорректное значение: {value}. Попробуйте снова.")


def create_table(
    metadata: Metadata, table_name: str, columns: list[str]
) -> Metadata:
    """Create a table, adding an integer ID column when it was not supplied."""
    if not table_name or any(character.isspace() for character in table_name):
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
            or column_type not in SUPPORTED_TYPES
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
    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        f"{formatted_columns}"
    )
    return metadata


def list_tables(metadata: Metadata) -> list[str]:
    """Return table names in their creation order."""
    return list(metadata)


def drop_table(metadata: Metadata, table_name: str) -> Metadata:
    """Remove a table from metadata if it exists."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata

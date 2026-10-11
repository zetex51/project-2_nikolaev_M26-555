"""Application command loop and SQL-like command handling."""

import json
import re
import shlex
from pathlib import Path

import prompt
from prettytable import PrettyTable

from primitive_db.core import (
    Metadata,
    Row,
    Value,
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.parser import parse_assignments, parse_values, split_keyword
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

METADATA_FILE = Path("db_meta.json")
_INSERT = re.compile(
    r"insert\s+into\s+([\w-]+)\s+values\s*(\(.*\))\s*",
    re.IGNORECASE | re.DOTALL,
)
_SELECT = re.compile(
    r"select\s+from\s+([\w-]+)(?:\s+where\s+(.+))?\s*",
    re.IGNORECASE | re.DOTALL,
)
_UPDATE = re.compile(
    r"update\s+([\w-]+)\s+set\s+(.+)\s*",
    re.IGNORECASE | re.DOTALL,
)
_DELETE = re.compile(
    r"delete\s+from\s+([\w-]+)\s+where\s+(.+)\s*",
    re.IGNORECASE | re.DOTALL,
)
_INFO = re.compile(r"info\s+([\w-]+)\s*", re.IGNORECASE)


def print_help() -> None:
    """Print the available table-management and data commands."""
    print("\n***Операции с таблицами и данными***")
    print("Функции:")
    print("<command> create_table <имя> <столбец:тип> ... - создать таблицу")
    print("<command> list_tables - показать список таблиц")
    print("<command> drop_table <имя> - удалить таблицу")
    print("<command> insert into <имя> values (<значение1>, ...) - добавить запись")
    print(
        "<command> select from <имя> [where <столбец> = <значение>] - прочитать записи"
    )
    print(
        "<command> update <имя> set <столбец> = <значение> "
        "where <столбец> = <значение> - обновить записи"
    )
    print("<command> delete from <имя> where <столбец> = <значение> - удалить записи")
    print("<command> info <имя> - показать информацию о таблице")
    print("<command> help - справочная информация")
    print("<command> exit - выход из программы\n")


def _invalid_value(value: str) -> None:
    print(f"Некорректное значение: {value}. Попробуйте снова.")


def _matches_type(value: Value, expected_type: str) -> bool:
    """Check literal types exactly because bool is a subclass of int."""
    return {
        "int": type(value) is int,
        "str": type(value) is str,
        "bool": type(value) is bool,
    }.get(expected_type, False)


def _validate_clause(
    metadata: Metadata,
    table_name: str,
    clause: dict[str, Value],
    *,
    allow_id: bool = True,
) -> bool:
    """Validate field names and values against a table's metadata."""
    schema = metadata.get(table_name)
    if schema is None:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False

    for column_name, value in clause.items():
        if column_name not in schema:
            print(
                f'Ошибка: Столбец "{column_name}" не существует '
                f'в таблице "{table_name}".'
            )
            return False
        if column_name == "ID" and not allow_id:
            print("Ошибка: столбец ID нельзя изменять.")
            return False
        expected_type = schema[column_name]
        if not _matches_type(value, expected_type):
            print(
                f"Ошибка: столбец {column_name} ожидает тип {expected_type}, "
                f"получен {type(value).__name__}."
            )
            return False
    return True


def _load_rows(table_name: str) -> list[Row] | None:
    try:
        return load_table_data(table_name)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f'Ошибка чтения данных таблицы "{table_name}": {error}')
        return None


def _save_rows(table_name: str, rows: list[Row]) -> bool:
    try:
        save_table_data(table_name, rows)
    except (OSError, ValueError) as error:
        print(f'Ошибка сохранения данных таблицы "{table_name}": {error}')
        return False
    return True


def _print_rows(metadata: Metadata, table_name: str, rows: list[Row]) -> None:
    """Render query results as an aligned console table."""
    table = PrettyTable()
    columns = list(metadata[table_name])
    table.field_names = columns
    for row in rows:
        table.add_row([row.get(column_name, "") for column_name in columns])
    print(table)


def _handle_data_command(raw_command: str, metadata: Metadata) -> None:
    """Parse and execute one CRUD or table-information command."""
    command = raw_command.lstrip().split(maxsplit=1)[0].lower()

    if command == "insert":
        match = _INSERT.fullmatch(raw_command.strip())
        if match is None:
            _invalid_value("insert into <имя> values (<значения>)")
            return
        table_name, raw_values = match.groups()
        try:
            values = parse_values(raw_values)
        except ValueError as error:
            _invalid_value(str(error))
            return
        if table_name not in metadata:
            print(f'Ошибка: Таблица "{table_name}" не существует.')
            return
        rows = _load_rows(table_name)
        if rows is None:
            return
        updated_rows = insert(metadata, table_name, values, rows)
        if len(updated_rows) > len(rows):
            _save_rows(table_name, updated_rows)
        return

    if command == "select":
        match = _SELECT.fullmatch(raw_command.strip())
        if match is None:
            _invalid_value("select from <имя> [where <столбец> = <значение>]")
            return
        table_name, raw_where = match.groups()
        if table_name not in metadata:
            print(f'Ошибка: Таблица "{table_name}" не существует.')
            return
        where_clause = None
        if raw_where is not None:
            try:
                where_clause = parse_assignments(raw_where, allow_multiple=False)
            except ValueError as error:
                _invalid_value(str(error))
                return
            if not _validate_clause(metadata, table_name, where_clause):
                return
        rows = _load_rows(table_name)
        if rows is not None:
            _print_rows(metadata, table_name, select(rows, where_clause))
        return

    if command == "update":
        match = _UPDATE.fullmatch(raw_command.strip())
        if match is None:
            _invalid_value(
                "update <имя> set <столбец> = <значение> where <столбец> = <значение>"
            )
            return
        table_name, raw_set_and_where = match.groups()
        try:
            raw_set, raw_where = split_keyword(raw_set_and_where, "where")
        except ValueError:
            _invalid_value("update ... set ... where ...")
            return
        if table_name not in metadata:
            print(f'Ошибка: Таблица "{table_name}" не существует.')
            return
        try:
            set_clause = parse_assignments(raw_set)
            where_clause = parse_assignments(raw_where, allow_multiple=False)
        except ValueError as error:
            _invalid_value(str(error))
            return
        if not set_clause:
            _invalid_value("список изменяемых значений")
            return
        if not _validate_clause(
            metadata, table_name, set_clause, allow_id=False
        ) or not _validate_clause(metadata, table_name, where_clause):
            return
        rows = _load_rows(table_name)
        if rows is None:
            return
        matched = select(rows, where_clause)
        if not matched:
            print(f'Записи в таблице "{table_name}" не найдены.')
            return
        matched_ids = [row["ID"] for row in matched]
        updated_rows = update(rows, set_clause, where_clause)
        if _save_rows(table_name, updated_rows):
            for record_id in matched_ids:
                print(
                    f'Запись с ID={record_id} в таблице "{table_name}" '
                    "успешно обновлена."
                )
        return

    if command == "delete":
        match = _DELETE.fullmatch(raw_command.strip())
        if match is None:
            _invalid_value("delete from <имя> where <столбец> = <значение>")
            return
        table_name, raw_where = match.groups()
        if table_name not in metadata:
            print(f'Ошибка: Таблица "{table_name}" не существует.')
            return
        try:
            where_clause = parse_assignments(raw_where, allow_multiple=False)
        except ValueError as error:
            _invalid_value(str(error))
            return
        if not _validate_clause(metadata, table_name, where_clause):
            return
        rows = _load_rows(table_name)
        if rows is None:
            return
        matched = select(rows, where_clause)
        if not matched:
            print(f'Записи в таблице "{table_name}" не найдены.')
            return
        remaining_rows = delete(rows, where_clause)
        if _save_rows(table_name, remaining_rows):
            for row in matched:
                print(
                    f"Запись с ID={row['ID']} успешно удалена из таблицы "
                    f'"{table_name}".'
                )
        return

    if command == "info":
        match = _INFO.fullmatch(raw_command.strip())
        if match is None:
            _invalid_value("info <имя>")
            return
        table_name = match.group(1)
        if table_name not in metadata:
            print(f'Ошибка: Таблица "{table_name}" не существует.')
            return
        rows = _load_rows(table_name)
        if rows is None:
            return
        columns = ", ".join(
            f"{name}:{column_type}"
            for name, column_type in metadata[table_name].items()
        )
        print(f"Таблица: {table_name}")
        print(f"Столбцы: {columns}")
        print(f"Количество записей: {len(rows)}")


def run() -> None:
    """Run the command loop and persist successful table and row changes."""
    print_help()

    while True:
        try:
            metadata = load_metadata(METADATA_FILE)
        except (OSError, ValueError) as error:
            print(f"Ошибка чтения метаданных: {error}")
            return

        try:
            raw_command = prompt.string("Введите команду: ")
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if not raw_command.strip():
            continue
        command_name = raw_command.lstrip().split(maxsplit=1)[0].lower()
        if command_name in {"insert", "select", "update", "delete", "info"}:
            _handle_data_command(raw_command, metadata)
            continue

        try:
            arguments = shlex.split(raw_command)
        except ValueError:
            _invalid_value("команда")
            continue

        if not arguments:
            continue
        command, *parameters = arguments
        if command == "exit":
            if parameters:
                _invalid_value(" ".join(parameters))
                continue
            return

        if command == "help":
            if parameters:
                _invalid_value(" ".join(parameters))
            else:
                print_help()
            continue

        if command == "create_table":
            if not parameters:
                _invalid_value("<имя таблицы>")
                continue

            table_name, *columns = parameters
            previous_metadata = metadata.copy()
            create_table(metadata, table_name, columns)
            if metadata != previous_metadata:
                try:
                    save_metadata(METADATA_FILE, metadata)
                    save_table_data(table_name, [])
                except (OSError, ValueError) as error:
                    print(f"Ошибка создания таблицы: {error}")
            continue

        if command == "list_tables":
            if parameters:
                _invalid_value(" ".join(parameters))
                continue

            tables = list_tables(metadata)
            if tables:
                for table_name in tables:
                    print(f"- {table_name}")
            else:
                print("Таблиц пока нет.")
            continue

        if command == "drop_table":
            if len(parameters) != 1:
                _invalid_value(" ".join(parameters) or "<имя таблицы>")
                continue

            table_name = parameters[0]
            if table_name in metadata:
                drop_table(metadata, table_name)
                try:
                    save_metadata(METADATA_FILE, metadata)
                    delete_table_data(table_name)
                except (OSError, ValueError) as error:
                    print(f"Ошибка удаления данных таблицы: {error}")
            else:
                drop_table(metadata, table_name)
            continue

        print(f"Функции {command} нет. Попробуйте снова.")

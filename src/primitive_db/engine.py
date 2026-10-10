"""Application command loop and command parsing."""

import shlex
from pathlib import Path

import prompt

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata

METADATA_FILE = Path("db_meta.json")


def print_help() -> None:
    """Print the database command reference."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> <столбец1:тип> .. "
        "- создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def _invalid_value(value: str) -> None:
    print(f"Некорректное значение: {value}. Попробуйте снова.")


def run() -> None:
    """Run the database command loop and persist successful table changes."""
    print_help()

    while True:
        metadata = load_metadata(METADATA_FILE)
        try:
            arguments = shlex.split(prompt.string("Введите команду: "))
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
                save_metadata(METADATA_FILE, metadata)
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
                save_metadata(METADATA_FILE, metadata)
            else:
                drop_table(metadata, table_name)
            continue

        print(f"Функции {command} нет. Попробуйте снова.")

# Primitive DB

Консольная программа для создания и управления таблицами с хранением метаданных
в JSON-файле.

## Запуск

```sh
uv sync
uv run python -m primitive_db.main
uv run database
```

Пакет также предоставляет команду `database`. Метаданные сохраняются в
`db_meta.json` в текущей рабочей директории.

## Управление таблицами

```text
create_table <имя> <столбец:тип> ...
list_tables
drop_table <имя>
help
exit
```

Поддерживаемые типы столбцов: `int`, `str` и `bool`. Столбец `ID:int`
добавляется автоматически в начало таблицы; его также можно задать явно.

Пример:

```text
Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool
Введите команду: list_tables
- users
Введите команду: drop_table users
Таблица "users" успешно удалена.
Введите команду: exit
```

## Установка CLI из собранного пакета

```sh
uv build
uv tool install dist/*.whl
database
```

## Сборка пакета

```sh
uv build
```

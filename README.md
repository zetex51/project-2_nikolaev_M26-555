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
`db_meta.json`, а записи таблиц — в отдельных файлах `data/<имя>.json` в
текущей рабочей директории.

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
Вы уверены, что хотите выполнить "удаление таблицы"? [y/n]: y
Таблица "users" успешно удалена.
Введите команду: exit
```

## CRUD-операции

```text
insert into <имя> values (<значение1>, ...)
select from <имя> [where <столбец> = <значение>]
update <имя> set <столбец> = <значение> [, ...] where <столбец> = <значение>
delete from <имя> where <столбец> = <значение>
info <имя>
```

Строковые значения нужно заключать в одинарные или двойные кавычки. Целые
числа и логические значения `true`/`false` вводятся без кавычек. В условиях
поддерживается одно сравнение на равенство; в `set` можно перечислить несколько
изменений через запятую. Поля при добавлении обязательны, `ID` генерируется
автоматически и не указывается в `insert`.

Пример работы с таблицей `users`:

```text
insert into users values ("Sergei", 28, true)
select from users where age = 28
update users set age = 29 where name = "Sergei"
delete from users where ID = 1
Вы уверены, что хотите выполнить "удаление записей"? [y/n]: y
info users
```

## Декораторы и замыкания

В `primitive_db.decorators` собраны общие обёртки для операций:

- `handle_db_errors` централизованно обрабатывает ошибки базы и валидации.
- `confirm_action` требует ввести `y` перед удалением записи или таблицы;
  любой другой ответ отменяет операцию.
- `log_time` выводит длительность `insert` и `select`.
- `create_cacher()` хранит результаты `select` в замыкании. После изменения
  снимка данных результат вычисляется заново.

Каждая успешно созданная таблица получает файл в каталоге `data/`. Удаление
таблицы командой `drop_table` удаляет и её файл с записями.

## Установка CLI из собранного пакета

```sh
uv build
uv tool install dist/*.whl
database
```

## Демонстрация

[![Декораторы и CRUD-операции](https://asciinema.org/a/mmP4yMmhjgxfyiHU.svg)](https://asciinema.org/a/mmP4yMmhjgxfyiHU)

## Сборка пакета

```sh
uv build
```

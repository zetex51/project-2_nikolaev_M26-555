"""Reusable decorators and closures for database operations."""

import time
from collections.abc import Callable, Hashable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def handle_db_errors(function: Callable[P, R]) -> Callable[P, R | None]:
    """Print database errors consistently and return ``None`` on failure."""

    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return function(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. Возможно, база не инициализирована.")
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None

    return wrapper


def confirm_action(
    action_name: str,
) -> Callable[[Callable[P, R]], Callable[P, R | None]]:
    """Create a decorator that asks for confirmation before an operation."""

    def decorator(function: Callable[P, R]) -> Callable[P, R | None]:
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
            answer = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None
            return function(*args, **kwargs)

        return wrapper

    return decorator


def log_time(function: Callable[P, R]) -> Callable[P, R]:
    """Print the elapsed wall-clock time for a function call."""

    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        started_at = time.monotonic()
        try:
            return function(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - started_at
            print(f"Функция {function.__name__} выполнилась за {elapsed:.3f} секунд")

    return wrapper


def create_cacher() -> Callable[[Hashable, Callable[[], R]], R]:
    """Return a closure that caches the value for each hashable key."""
    cache: dict[Hashable, R] = {}

    def cache_result(key: Hashable, value_func: Callable[[], R]) -> R:
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    return cache_result

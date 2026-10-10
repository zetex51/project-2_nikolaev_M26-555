"""Application startup and command loop."""

import prompt


def welcome() -> None:
    """Show the welcome message and handle the first console commands."""
    print("Первая попытка запустить проект!")
    print()
    print("***")

    while True:
        print("<command> exit - выйти из программы")
        print("<command> help - справочная информация")
        command = prompt.string("Введите команду: ")

        if command == "exit":
            return
        if command == "help":
            continue

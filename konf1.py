#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shlex
import socket
import getpass

class ShellEmulator:
    def __init__(self):
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.current_dir = os.getcwd()
        self.running = True

    def get_prompt(self):
        """Формирует приглашение к вводу в формате username@hostname:directory$"""
        # Получаем относительный путь от домашней директории
        home_dir = os.path.expanduser("~")
        if self.current_dir.startswith(home_dir):
            display_dir = "~" + self.current_dir[len(home_dir):]
        else:
            display_dir = self.current_dir

        return f"{self.username}@{self.hostname}:{display_dir}$ "

    def parse_command(self, command_line):
        """Парсит командную строку с учетом кавычек"""
        try:
            return shlex.split(command_line)
        except ValueError as e:
            print(f"Ошибка парсинга: {e}")
            return None

    def execute_command(self, command_parts):
        """Выполняет команду"""
        if not command_parts:
            return

        command = command_parts[0]
        args = command_parts[1:]

        if command == "exit":
            self.running = False
            print("Выход из эмулятора")

        elif command == "ls":
            print(f"Команда: ls")
            if args:
                print(f"Аргументы: {args}")
            else:
                print("Аргументы отсутствуют")
            # Заглушка - просто выводим информацию
            print("file1.txt  file2.txt  directory1")

        elif command == "cd":
            print(f"Команда: cd")
            if args:
                print(f"Аргументы: {args}")
                # Попытка изменить директорию
                if len(args) > 1:
                    print("cd: слишком много аргументов")
                    return

                target_dir = args[0]
                try:
                    if target_dir == "~":
                        new_dir = os.path.expanduser("~")
                    else:
                        new_dir = os.path.abspath(os.path.join(self.current_dir, target_dir))

                    if os.path.exists(new_dir) and os.path.isdir(new_dir):
                        self.current_dir = new_dir
                    else:
                        print(f"cd: {target_dir}: Нет такой директории")
                except Exception as e:
                    print(f"cd: ошибка при смене директории: {e}")
            else:
                # cd без аргументов - переход в домашнюю директорию
                self.current_dir = os.path.expanduser("~")
                print("Переход в домашнюю директорию")

        else:
            print(f"{command}: команда не найдена")

    def run(self):
        """Основной цикл REPL (Read-Eval-Print Loop)"""
        print("Добро пожаловать в эмулятор командной строки!")
        print("Доступные команды: ls, cd, exit")
        print("Для выхода введите 'exit'")
        print("-" * 50)

        while self.running:
            try:
                # Выводим приглашение и читаем ввод
                command_line = input(self.get_prompt()).strip()

                # Пропускаем пустые строки
                if not command_line:
                    continue

                # Парсим команду
                command_parts = self.parse_command(command_line)
                if command_parts is None:
                    continue

                # Выполняем команду
                self.execute_command(command_parts)

            except KeyboardInterrupt:
                print("\nДля выхода введите 'exit'")
            except EOFError:
                print("\nВыход из эмулятора")
                break
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")


def main():
    """Точка входа в приложение"""
    shell = ShellEmulator()
    shell.run()


if __name__ == "__main__":
    main()
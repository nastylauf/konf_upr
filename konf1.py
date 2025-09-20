#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shlex
import socket
import getpass
from pathlib import Path


class VirtualFileSystem:
    """Виртуальная файловая система"""

    def __init__(self):
        self.root = {
            'type': 'directory',
            'content': {
                'home': {
                    'type': 'directory',
                    'content': {
                        'user': {
                            'type': 'directory',
                            'content': {
                                'documents': {
                                    'type': 'directory',
                                    'content': {
                                        'file1.txt': {'type': 'file', 'content': 'Hello World!'},
                                        'file2.txt': {'type': 'file', 'content': 'Test content'}
                                    }
                                },
                                'pictures': {
                                    'type': 'directory',
                                    'content': {
                                        'photo1.jpg': {'type': 'file', 'content': 'JPEG data'},
                                        'photo2.png': {'type': 'file', 'content': 'PNG data'}
                                    }
                                },
                                'readme.md': {'type': 'file', 'content': '# Welcome\nThis is a readme file.'}
                            }
                        }
                    }
                },
                'etc': {
                    'type': 'directory',
                    'content': {
                        'config.conf': {'type': 'file', 'content': 'key=value\nport=8080'}
                    }
                },
                'tmp': {
                    'type': 'directory',
                    'content': {}
                },
                'var': {
                    'type': 'directory',
                    'content': {
                        'log': {
                            'type': 'directory',
                            'content': {
                                'system.log': {'type': 'file', 'content': 'System started\nEverything OK'}
                            }
                        }
                    }
                }
            }
        }

    def resolve_path(self, current_path, target_path):
        """Разрешает путь относительно текущей директории"""
        if target_path.startswith('/'):
            # Абсолютный путь
            path_parts = target_path.split('/')[1:]
            current_node = self.root
        else:
            # Относительный путь
            path_parts = current_path.split('/')[1:]
            path_parts = [p for p in path_parts if p]  # Убираем пустые части
            current_node = self.root
            for part in path_parts:
                if part in current_node['content'] and current_node['content'][part]['type'] == 'directory':
                    current_node = current_node['content'][part]
                else:
                    return None

        # Обрабатываем специальные пути
        if not path_parts or path_parts[0] == '':
            return '/'

        # Обрабатываем каждую часть пути
        for part in path_parts:
            if part == '..':
                # Переход на уровень выше
                if current_path == '/':
                    continue
                path_parts = current_path.split('/')[1:-1]
                current_node = self.root
                for p in path_parts:
                    current_node = current_node['content'][p]
            elif part == '.':
                # Текущая директория
                continue
            elif part in current_node['content']:
                current_node = current_node['content'][part]
            else:
                return None

        return current_node

    def list_directory(self, path):
        """Список содержимого директории"""
        node = self.resolve_path(path, path)
        if node and node['type'] == 'directory':
            return list(node['content'].keys())
        return None

    def is_directory(self, path):
        """Проверяет, является ли путь директорией"""
        node = self.resolve_path(path, path)
        return node and node['type'] == 'directory'

    def is_file(self, path):
        """Проверяет, является ли путь файлом"""
        node = self.resolve_path(path, path)
        return node and node['type'] == 'file'

    def get_file_content(self, path):
        """Получает содержимое файла"""
        node = self.resolve_path(path, path)
        if node and node['type'] == 'file':
            return node['content']
        return None


class ShellEmulator:
    def __init__(self):
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.vfs = VirtualFileSystem()
        self.current_path = '/home/user'  # Начальный путь в VFS
        self.running = True

    def get_prompt(self):
        """Формирует приглашение к вводу в формате username@hostname:directory$"""
        # Упрощаем путь для отображения
        if self.current_path.startswith('/home/user'):
            display_path = '~' + self.current_path[len('/home/user'):]
        else:
            display_path = self.current_path

        return f"{self.username}@{self.hostname}:{display_path}$ "

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
                target_path = args[0]
                # Пытаемся получить список файлов по указанному пути
                files = self.vfs.list_directory(target_path)
                if files is None:
                    print(f"ls: невозможно получить доступ к '{target_path}': Нет такого файла или каталога")
                else:
                    for file in sorted(files):
                        print(file)
            else:
                print("Аргументы отсутствуют")
                # Показываем содержимое текущей директории
                files = self.vfs.list_directory(self.current_path)
                if files:
                    for file in sorted(files):
                        print(file)

        elif command == "cd":
            print(f"Команда: cd")
            if args:
                print(f"Аргументы: {args}")
                if len(args) > 1:
                    print("cd: слишком много аргументов")
                    return

                target_path = args[0]
                # Обрабатываем специальные пути
                if target_path == "~":
                    target_path = "/home/user"
                elif target_path == "-":
                    # В реальной системе это вернуло бы в предыдущую директорию
                    print("cd: функция не реализована")
                    return

                # Пытаемся перейти по пути
                new_node = self.vfs.resolve_path(self.current_path, target_path)
                if new_node and new_node['type'] == 'directory':
                    # Обновляем текущий путь
                    if target_path.startswith('/'):
                        self.current_path = target_path
                    else:
                        # Для относительных путей нужно вычислить новый абсолютный путь
                        # Это упрощенная реализация
                        if self.current_path == '/':
                            self.current_path = '/' + target_path
                        else:
                            self.current_path = self.current_path + '/' + target_path
                    # Нормализуем путь
                    self.current_path = self.current_path.replace('//', '/')
                    if self.current_path.endswith('/') and len(self.current_path) > 1:
                        self.current_path = self.current_path[:-1]
                else:
                    print(f"cd: {target_path}: Нет такой директории")
            else:
                # cd без аргументов - переход в домашнюю директорию
                self.current_path = "/home/user"
                print("Переход в домашнюю директорию")

        elif command == "pwd":
            print(f"Команда: pwd")
            print(self.current_path)

        elif command == "cat":
            print(f"Команда: cat")
            if args:
                print(f"Аргументы: {args}")
                for file_path in args:
                    content = self.vfs.get_file_content(file_path)
                    if content is not None:
                        print(content)
                    else:
                        print(f"cat: {file_path}: Нет такого файла или каталога")
            else:
                print("cat: отсутствуют аргументы")

        else:
            print(f"{command}: команда не найдена")

    def run(self):
        """Основной цикл REPL (Read-Eval-Print Loop)"""
        print("Добро пожаловать в эмулятор командной строки с VFS!")
        print("Доступные команды: ls, cd, pwd, cat, exit")
        print("Виртуальная файловая система содержит:")
        print("  /home/user/documents/ - файлы документов")
        print("  /home/user/pictures/ - изображения")
        print("  /etc/ - конфигурационные файлы")
        print("  /var/log/ - логи")
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
                print()  # Пустая строка для читаемости

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
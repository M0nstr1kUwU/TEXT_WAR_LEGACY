#!/usr/bin/env python3
"""
Скрипт запуска Mod-Editor для Text War Legacy
"""

from sys import path, exit
from os.path import dirname, abspath
from os import getcwd
from traceback import print_exc
from src.modding.mod_editor.main import main as editor_main
from src.settings.settings_manager import settings

# Добавляем корень проекта в путь для импортов
project_root = dirname(abspath(__file__))
path.insert(0, project_root)

settings.log_info(f"📁 Рабочая директория: {getcwd()}")
settings.log_info(f"📁 Корень проекта: {project_root}")


def main():
    """Главная функция запуска"""
    try:
        settings.log_info("🚀 Запуск Mod-Editor...")
        exit(editor_main())
    except ImportError as e:
        settings.log_error(f"❌ Ошибка импорта: {e}")
        settings.log_tips("📦 Убедитесь, что установлены все зависимости:")
        settings.log_tips("   pip install PyQt5 PyQt5-Qt5 PyQt5-sip QScintilla")
        print_exc()
        return 1
    except Exception as e:
        settings.log_error(f"❌ Неожиданная ошибка: {e}")
        print_exc()
        return 1


if __name__ == "__main__":
    main()

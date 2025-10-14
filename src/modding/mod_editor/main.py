#!/usr/bin/env python3
"""
Главный файл запуска Mod-Editor для Text War Legacy
"""
from sys import path as spath, argv, exit as sexit
from os import path, getcwd
from pathlib import Path
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QApplication
from settings.settings_manager import settings
from modding.mod_editor.ui.main_window import MainWindow
from modding.mod_editor.settings_manager import EditorSettings
from modding.mod_editor.project_manager import ProjectManager

src_path = Path(__file__).parent.parent.parent
if str(src_path) not in spath:
    spath.insert(0, str(src_path))


class ModEditorApplication:
    """Главное приложение Mod-Editor"""

    def __init__(self):

        self.app = QApplication(argv)
        self.settings = EditorSettings()
        self.project_manager = ProjectManager()

        # Настройка стиля приложения
        self.setup_application_style()

    def setup_application_style(self):
        """Настройка стиля приложения в стиле PyCharm"""

        self.app.setStyle('Fusion')

        # Темная тема как в PyCharm
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(43, 43, 43))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        self.app.setPalette(dark_palette)

        # Настройка шрифта
        font = QFont("Consolas", 10)
        self.app.setFont(font)

    def run(self):
        """Запуск приложения"""
        try:
            # Создание главного окна
            self.main_window = MainWindow(self.settings, self.project_manager)
            self.main_window.show()

            # Загрузка последнего проекта если есть
            last_project = self.settings.get('last_project')
            if last_project and path.exists(last_project):
                self.main_window.open_project(last_project)

            return self.app.exec_()

        except Exception as e:
            QMessageBox.critical(None, "Ошибка запуска", f"Не удалось запустить Mod-Editor:\n{str(e)}")
            settings.log_error(f"Не удалось запустить Mod-Editor: {e}")
            return 1


def main():
    """Точка входа в Mod-Editor"""
    print("Запуск Text War Legacy Mod-Editor...")
    settings.log_info("Запуск Text War Legacy Mod-Editor...")
    print("📁 Текущая директория:", getcwd())
    settings.log_info(f"📁 Текущая директория: {getcwd()}")

    editor = ModEditorApplication()
    sexit(editor.run())


if __name__ == "__main__":
    main()


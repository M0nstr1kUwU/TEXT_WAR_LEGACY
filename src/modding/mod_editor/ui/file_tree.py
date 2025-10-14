from pathlib import Path
from PyQt5.QtWidgets import (QTreeWidget, QTreeWidgetItem, QMenu, QAction,
                            QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from settings.settings_manager import settings


class FileTreeWidget(QTreeWidget):
    """Виджет дерева файлов проекта"""

    # Сигналы
    file_double_clicked = pyqtSignal(str)
    file_context_menu = pyqtSignal(str, str)

    def __init__(self, project_manager):
        super().__init__()

        self.project_manager = project_manager
        self.project_path = None

        self.setup_tree()
        self.setup_connections()

    def setup_tree(self):
        """Настройка дерева"""
        self.setHeaderLabel("Файлы проекта")
        self.setColumnCount(1)
        self.setAnimated(True)
        self.setIndentation(15)

        # Настройка контекстного меню
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)  # type: ignore

    def setup_connections(self):
        """Настройка соединений"""
        self.itemDoubleClicked.connect(self.on_item_double_clicked)  # type: ignore

    def refresh_tree(self):
        """Обновление дерева файлов"""
        self.clear()

        if not self.project_manager.is_project_loaded():
            return

        self.project_path = self.project_manager.current_project
        project_root = Path(self.project_path)

        # Создание корневого элемента
        root_item = QTreeWidgetItem(self, [project_root.name])
        root_item.setData(0, Qt.UserRole, str(project_root))
        root_item.setIcon(0, self.get_icon("project"))

        # Добавление файлов проекта
        self.add_files_to_tree(root_item, project_root)

        # Развернуть корневой элемент
        root_item.setExpanded(True)

    def add_files_to_tree(self, parent_item, directory):
        """Добавление файлов и папок в дерево"""
        try:
            for item in sorted(directory.iterdir()):
                if item.name.startswith('.'):
                    continue

                if item.is_dir():
                    # Папка
                    dir_item = QTreeWidgetItem(parent_item, [item.name])
                    dir_item.setData(0, Qt.UserRole, str(item))
                    dir_item.setIcon(0, self.get_icon("folder"))
                    self.add_files_to_tree(dir_item, item)
                else:
                    # Файл
                    file_item = QTreeWidgetItem(parent_item, [item.name])
                    file_item.setData(0, Qt.UserRole, str(item))
                    file_item.setIcon(0, self.get_icon_for_file(item.name))

        except PermissionError:
            pass

    # Временно закомментируем методы с иконками
    def get_icon(self, icon_type: str):
       """Получение иконки"""
       return None

    def get_icon_for_file(self, filename: str):
        """Получение иконки для файла по расширению"""
        return None

    def on_item_double_clicked(self, item, column):
        """Обработчик двойного клика по элементу"""
        file_path = item.data(0, Qt.UserRole)

        if file_path and Path(file_path).is_file():
            self.file_double_clicked.emit(file_path)  # type: ignore

    def show_context_menu(self, position):
        """Показать контекстное меню"""
        item = self.itemAt(position)
        if not item:
            return

        file_path = item.data(0, Qt.UserRole)
        if not file_path:
            return

        context_menu = QMenu(self)

        is_file = Path(file_path).is_file()
        is_directory = Path(file_path).is_dir()

        if is_file:
            # Меню для файлов
            open_action = QAction("Открыть", self)
            open_action.triggered.connect(lambda: self.file_double_clicked.emit(file_path))  # type: ignore
            context_menu.addAction(open_action)

            rename_action = QAction("Переименовать", self)
            rename_action.triggered.connect(lambda: self.rename_item(item))  # type: ignore
            context_menu.addAction(rename_action)

            delete_action = QAction("Удалить", self)
            delete_action.triggered.connect(lambda: self.delete_item(item))  # type: ignore
            context_menu.addAction(delete_action)

            context_menu.addSeparator()

            new_file_action = QAction("Новый файл", self)
            new_file_action.triggered.connect(lambda: self.create_new_file(item))  # type: ignore
            context_menu.addAction(new_file_action)

        elif is_directory:
            # Меню для папок
            new_file_action = QAction("Новый файл", self)
            new_file_action.triggered.connect(lambda: self.create_new_file(item))  # type: ignore
            context_menu.addAction(new_file_action)

            new_folder_action = QAction("Новая папка", self)
            new_folder_action.triggered.connect(lambda: self.create_new_folder(item))  # type: ignore
            context_menu.addAction(new_folder_action)

            context_menu.addSeparator()

            rename_action = QAction("Переименовать", self)
            rename_action.triggered.connect(lambda: self.rename_item(item))  # type: ignore
            context_menu.addAction(rename_action)

            delete_action = QAction("Удалить", self)
            delete_action.triggered.connect(lambda: self.delete_item(item))  # type: ignore
            context_menu.addAction(delete_action)

        context_menu.exec_(self.mapToGlobal(position))

    def create_new_file(self, parent_item):
        """Создание нового файла"""
        parent_path = Path(parent_item.data(0, Qt.UserRole))
        if parent_path.is_file():
            parent_path = parent_path.parent

        file_name, ok = QInputDialog.getText(
            self,
            "Новый файл",
            "Введите имя файла:",
            text="new_mod.py"
        )

        if ok and file_name:
            file_path = parent_path / file_name

            if file_path.exists():
                QMessageBox.warning(self, "Ошибка", "Файл с таким именем уже существует!")
                return

            try:
                # Создаем файл с базовым содержимым
                if file_name.endswith('.py'):
                    content = '"""\nНовый мод\n"""\n\n'
                else:
                    content = ''

                file_path.write_text(content, encoding='utf-8')
                self.refresh_tree()

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать файл:\n{str(e)}")

    def create_new_folder(self, parent_item):
        """Создание новой папки"""
        parent_path = Path(parent_item.data(0, Qt.UserRole))

        if parent_path.is_file():
            parent_path = parent_path.parent

        folder_name, ok = QInputDialog.getText(
            self,
            "Новая папка",
            "Введите имя папки:"
        )

        if ok and folder_name:
            folder_path = parent_path / folder_name

            if folder_path.exists():
                QMessageBox.warning(self, "Ошибка", "Папка с таким именем уже существует!")
                return

            try:
                folder_path.mkdir()
                self.refresh_tree()

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать папку:\n{str(e)}")
                settings.log_error(f"Не удалось создать папку: {str(e)}")

    def rename_item(self, item):
        """Переименование файла или папки"""
        old_path = Path(item.data(0, Qt.UserRole))

        new_name, ok = QInputDialog.getText(
            self,
            "Переименование",
            "Введите новое имя:",
            text=old_path.name
        )

        if ok and new_name and new_name != old_path.name:
            new_path = old_path.parent / new_name

            if new_path.exists():
                QMessageBox.warning(self, "Ошибка", "Файл/папка с таким именем уже существует!")
                return

            try:
                old_path.rename(new_path)
                self.refresh_tree()

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось переименовать:\n{str(e)}")
                settings.log_error(f"Не удалось переименовать: {str(e)}")

    def delete_item(self, item):
        """Удаление файла или папки"""
        path = Path(item.data(0, Qt.UserRole))

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить '{path.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                if path.is_file():
                    path.unlink()
                else:
                    import shutil
                    shutil.rmtree(path)

                self.refresh_tree()

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить:\n{str(e)}")
                settings.log_error(f"Не удалось удалить: {str(e)}")

    def get_current_project_path(self) -> str:
        """Получение пути к текущему проекту"""
        return self.project_path
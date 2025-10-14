from pathlib import Path
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout,
                            QSplitter, QTabWidget,
                            QAction, QMessageBox)
from modding.mod_editor.mod_compiler import ModCompiler
from modding.mod_editor.hook_explorer import HookExplorer
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QInputDialog, QFileDialog
from modding.mod_editor.settings_manager import EditorSettings
from modding.mod_editor.project_manager import ProjectManager
from modding.mod_editor.ui.file_tree import FileTreeWidget
from modding.mod_editor.ui.code_editor import CodeEditor
from modding.mod_editor.ui.status_bar import StatusBar
from modding.mod_editor.ui.toolbars import MainToolBar
from modding.mod_editor.ui.hook_browser import HookBrowser


class MainWindow(QMainWindow):
    """Главное окно Mod-Editor"""

    project_loaded = pyqtSignal(str)
    project_closed = pyqtSignal()
    file_opened = pyqtSignal(str)
    file_saved = pyqtSignal(str) # type: ignore

    def __init__(self, settings: EditorSettings, project_manager: ProjectManager):
        super().__init__()

        self.settings = settings
        self.project_manager = project_manager
        self.current_file = None

        self.setup_ui()
        self.setup_connections()
        self.load_window_settings()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Text War Legacy - Mod Editor")
        self.setMinimumSize(800, 600)

        # Установка размера окна из настроек
        width = self.settings.get('window.width', 1200)
        height = self.settings.get('window.height', 800)
        self.resize(width, height)

        # Создание центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный layout
        main_layout = QHBoxLayout(central_widget)

        # Создание сплиттера
        self.main_splitter = QSplitter(Qt.Horizontal)

        # Левая панель - дерево файлов
        self.file_tree = FileTreeWidget(self.project_manager)

        # Центральная панель - редактор кода
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_tab)# type: ignore

        # Добавление виджетов в сплиттер
        self.main_splitter.addWidget(self.file_tree)
        self.main_splitter.addWidget(self.editor_tabs)
        self.main_splitter.setSizes([300, 700])

        main_layout.addWidget(self.main_splitter)

        # Создание тулбара
        self.setup_toolbar()

        # Создание статусбара
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

        # Создание меню
        self.setup_menus()

    # Добавляем метод в класс MainWindow:
    def show_hook_browser(self):
        """Показать обозреватель хуков"""
        if not hasattr(self, 'hook_browser') or not self.hook_browser:
            self.hook_browser = HookBrowser(self)

            # Подключаем сигнал вставки кода
            self.hook_browser.insert_code_requested.connect(self.insert_code_from_hook)  # type: ignore

        self.hook_browser.show()
        self.hook_browser.raise_()

    def insert_code_from_hook(self, code: str):
        """Вставка кода из обозревателя хуков"""
        current_editor = self.editor_tabs.currentWidget()
        if current_editor and hasattr(current_editor, 'insert'):
            current_editor.insert(code)
            self.status_bar.show_message("Код хука вставлен в редактор")
        else:
            QMessageBox.warning(self, "Вставка кода", "Нет активного редактора для вставки кода")

    def setup_toolbar(self):
        """Настройка главного тулбара"""
        self.toolbar = MainToolBar("Главная панель", self)
        self.addToolBar(self.toolbar)

        # Подключение сигналов тулбара
        self.toolbar.new_project_clicked.connect(self.new_project)
        self.toolbar.open_project_clicked.connect(self.open_project)
        self.toolbar.save_file_clicked.connect(self.save_current_file)
        self.toolbar.run_mod_clicked.connect(self.run_current_mod)

    def setup_editor_connections(self, editor):
        """Настройка соединений для редактора"""
        if hasattr(editor, 'cursorPositionChanged'):
            editor.cursorPositionChanged.connect(self.on_cursor_position_changed)

        if hasattr(editor, 'file_saved'):
            editor.file_saved.connect(self.on_file_saved)

    def on_cursor_position_changed(self, line, index):
        """Обработчик изменения позиции курсора"""
        if self.status_bar:
            self.status_bar.update_cursor_position(line + 1, index + 1)

    def on_file_saved(self, file_path):
        """Обработчик сохранения файла"""
        self.status_bar.show_message(f"Файл сохранен: {Path(file_path).name}")

    def setup_menus(self):
        """Настройка меню"""
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu("Файл")

        new_project_action = QAction("Новый проект", self)
        new_project_action.setShortcut(QKeySequence.New)
        new_project_action.triggered.connect(self.new_project)# type: ignore
        file_menu.addAction(new_project_action)

        open_project_action = QAction("Открыть проект", self)
        open_project_action.setShortcut(QKeySequence.Open)
        open_project_action.triggered.connect(self.open_project)# type: ignore
        file_menu.addAction(open_project_action)

        file_menu.addSeparator()

        save_action = QAction("Сохранить", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_current_file)# type: ignore
        file_menu.addAction(save_action)

        save_all_action = QAction("Сохранить все", self)
        save_all_action.setShortcut("Ctrl+Shift+S")
        save_all_action.triggered.connect(self.save_all_files)# type: ignore
        file_menu.addAction(save_all_action)

        file_menu.addSeparator()

        exit_action = QAction("Выход", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)# type: ignore
        file_menu.addAction(exit_action)

        # Меню Проект
        project_menu = menubar.addMenu("Проект")

        build_action = QAction("Собрать мод", self)
        build_action.setShortcut("Ctrl+B")
        build_action.triggered.connect(self.build_mod)# type: ignore
        project_menu.addAction(build_action)

        run_action = QAction("Запустить мод", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_current_mod)# type: ignore
        project_menu.addAction(run_action)

        # Меню Справка
        help_menu = menubar.addMenu("Справка")

        docs_action = QAction("Документация API", self)
        docs_action.triggered.connect(self.show_api_docs)# type: ignore
        help_menu.addAction(docs_action)

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)# type: ignore
        help_menu.addAction(about_action)

    def setup_connections(self):
        """Настройка соединений сигналов"""
        self.file_tree.file_double_clicked.connect(self.open_file)
        self.project_loaded.connect(self.on_project_loaded) # type: ignore
        self.project_closed.connect(self.on_project_closed) # type: ignore

    def show_hook_documentation(self):
        """Показать документацию хуков"""
        from ..hook_explorer import HookDocumentationDialog

        dialog = HookDocumentationDialog({}, {})
        # Подключаем сигнал вставки кода
        dialog.code_insert_requested.connect(self.insert_code_from_hook)
        dialog.exec_()

    def new_project(self):
        """Создание нового проекта"""
        try:
            # Получаем имя проекта
            project_name, ok = QInputDialog.getText(
                self,
                "Новый проект",
                "Введите название проекта:",
                text="my_awesome_mod"
            )

            if not ok or not project_name.strip():
                return

            project_name = project_name.strip()

            # Получаем путь для сохранения
            project_path = QFileDialog.getExistingDirectory(
                self,
                "Выберите папку для проекта",
                "src/saves/mods/",
                QFileDialog.ShowDirsOnly
            )

            if not project_path:
                return

            print(f"🎯 Создаю проект '{project_name}' в '{project_path}'")

            # Получаем шаблон
            from ..template_manager import TemplateManager
            template_manager = TemplateManager()

            # ✅ ИСПРАВЛЯЕМ: передаем правильные параметры
            if template_manager.create_project_from_template(project_name, project_path, "basic"):
                # Открываем созданный проект
                project_full_path = Path(project_path) / project_name
                self.open_project(str(project_full_path))
                self.status_bar.show_message(f"✅ Проект '{project_name}' создан!")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось создать проект")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка создания проекта:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def open_project(self, project_path=None):
        """Открытие проекта"""
        if not project_path:
            project_path = QFileDialog.getExistingDirectory(
                self,
                "Открыть проект мода",
                "src/saves/mods/",
                QFileDialog.ShowDirsOnly
            )

        if project_path:
            if self.project_manager.open_project(project_path):
                self.settings.add_recent_project(project_path)
                self.project_loaded.emit(project_path) # type: ignore
                self.status_bar.show_message(f"Проект загружен: {project_path}")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось открыть проект")

    def open_file(self, file_path: str):
        """Открытие файла в редакторе"""
        try:
            # Проверяем, не открыт ли уже файл
            for i in range(self.editor_tabs.count()):
                editor = self.editor_tabs.widget(i)
                if hasattr(editor, 'file_path') and editor.file_path == file_path:
                    self.editor_tabs.setCurrentIndex(i)
                    return

            # Создаем новый редактор
            editor = CodeEditor(self.settings)
            self.setup_editor_connections(editor)
            if editor.load_file(file_path):
                # Добавляем вкладку
                file_name = Path(file_path).name
                self.editor_tabs.addTab(editor, file_name)
                self.editor_tabs.setCurrentWidget(editor)

                # Сохраняем путь к файлу
                editor.file_path = file_path
                self.current_file = file_path

                self.file_opened.emit(file_path) # type: ignore
                self.status_bar.show_message(f"Файл открыт: {file_name}")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при открытии файла:\n{str(e)}")

    def save_current_file(self):
        """Сохранение текущего файла"""
        current_editor = self.editor_tabs.currentWidget()
        if current_editor and hasattr(current_editor, 'save_file'):
            if current_editor.save_file():
                self.file_saved.emit(self.current_file) # type: ignore
                self.status_bar.show_message("Файл сохранен")

    def save_all_files(self):
        """Сохранение всех открытых файлов"""
        for i in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(i)
            if hasattr(editor, 'save_file'):
                editor.save_file()

        self.status_bar.show_message("Все файлы сохранены")

    def close_tab(self, index: int):
        """Закрытие вкладки"""
        editor = self.editor_tabs.widget(index)
        if hasattr(editor, 'is_modified') and editor.is_modified:
            reply = QMessageBox.question(
                self,
                "Сохранение файла",
                "Файл был изменен. Сохранить изменения?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                if not editor.save_file():
                    return  # Не закрывать если сохранение не удалось
            elif reply == QMessageBox.Cancel:
                return  # Не закрывать

        self.editor_tabs.removeTab(index)

    def run_current_mod(self):
        """Запуск текущего мода"""
        if not self.project_manager.is_project_loaded():
            QMessageBox.information(self, "Информация", "Сначала откройте проект мода")
            return

        # Сохраняем все файлы
        self.save_all_files()

        # Запуск валидации и тестирования мода
        compiler = ModCompiler()
        result = compiler.compile_and_test(self.project_manager.current_project)

        if result["success"]:
            self.status_bar.show_message("Мод успешно запущен!")
            QMessageBox.information(self, "Успех", "Мод успешно скомпилирован и протестирован!")
        else:
            self.status_bar.show_message("Ошибка компиляции мода")
            QMessageBox.critical(self, "Ошибка", f"Ошибка компиляции:\n{result['error']}")

    def build_mod(self):
        """Сборка мода для распространения"""
        if not self.project_manager.is_project_loaded():
            QMessageBox.information(self, "Информация", "Сначала откройте проект мода")
            return
        compiler = ModCompiler()
        result = compiler.build_package(self.project_manager.current_project)

        if result["success"]:
            self.status_bar.show_message("Мод успешно собран!")
            QMessageBox.information(self, "Успех", f"Мод собран в: {result['output_path']}")
        else:
            self.status_bar.show_message("Ошибка сборки мода")
            QMessageBox.critical(self, "Ошибка", f"Ошибка сборки:\n{result['error']}")

    def show_api_docs(self):
        """Показать документацию API"""
        explorer = HookExplorer()
        explorer.show_documentation(self)

    def show_about(self):
        """Показать информацию о программе"""
        QMessageBox.about(
            self,
            "О программе",
            "Text War Legacy - Mod Editor\n\n"
            "Профессиональная(нет) среда разработки модов\n"
            "Версия: 1.0.0\n\n"
            "Создано для Text War Legacy"
        )

    def on_project_loaded(self, project_path: str):
        """Обработчик загрузки проекта"""
        self.setWindowTitle(f"Text War Legacy - Mod Editor - {Path(project_path).name}")
        self.file_tree.refresh_tree()

    def on_project_closed(self):
        """Обработчик закрытия проекта"""
        self.setWindowTitle("Text War Legacy - Mod Editor")
        self.file_tree.clear()
        self.editor_tabs.clear()

    def load_window_settings(self):
        """Загрузка настроек окна"""
        if self.settings.get('window.maximized', False):
            self.showMaximized()

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        # Сохраняем настройки окна
        self.settings.set('window.width', self.width())
        self.settings.set('window.height', self.height())
        self.settings.set('window.maximized', self.isMaximized())

        # Сохраняем состояние сплиттера
        splitter_sizes = self.main_splitter.sizes()
        self.settings.set('window.splitter_sizes', splitter_sizes)

        # Проверяем несохраненные файлы
        unsaved_files = []
        for i in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(i)
            if hasattr(editor, 'is_modified') and editor.is_modified:
                file_name = self.editor_tabs.tabText(i)
                unsaved_files.append(file_name)

        if unsaved_files:
            reply = QMessageBox.question(
                self,
                "Несохраненные файлы",
                f"Следующие файлы не сохранены:\n{', '.join(unsaved_files)}\n\nВсе равно выйти?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.No:
                event.ignore()
                return

        event.accept()
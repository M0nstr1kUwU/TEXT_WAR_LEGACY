from PyQt5.QtWidgets import QToolBar, QAction, QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QKeySequence


class MainToolBar(QToolBar):
    """Главный тулбар Mod-Editor"""

    # Сигналы
    new_project_clicked = pyqtSignal()
    open_project_clicked = pyqtSignal()
    save_file_clicked = pyqtSignal()
    run_mod_clicked = pyqtSignal()

    def __init__(self, title, parent=None):
        super().__init__(title, parent)

        self.setup_toolbar()

    def setup_toolbar(self):
        """Настройка тулбара"""
        self.setIconSize(QSize(16, 16))
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.setMovable(False)

        # Действие: Новый проект
        new_project_action = QAction("Новый проект", self)
        new_project_action.setShortcut(QKeySequence.New)
        # Подключаем через lambda или напрямую к сигналу
        new_project_action.triggered.connect(lambda: self.new_project_clicked.emit())  # type: ignore
        self.addAction(new_project_action)

        # Действие: Открыть проект
        open_project_action = QAction("Открыть проект", self)
        open_project_action.setShortcut(QKeySequence.Open)
        open_project_action.triggered.connect(lambda: self.open_project_clicked.emit())  # type: ignore
        self.addAction(open_project_action)

        self.addSeparator()

        # Действие: Сохранить
        save_action = QAction("Сохранить", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(lambda: self.save_file_clicked.emit())  # type: ignore
        self.addAction(save_action)

        self.addSeparator()

        # Действие: Запустить мод
        run_action = QAction("Запустить мод", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(lambda: self.run_mod_clicked.emit())  # type: ignore
        self.addAction(run_action)

        # Добавляем растягивающийся разделитель
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.addWidget(spacer)

        # Кнопка справки
        # help_action = QAction("Справка", self)
        # help_action.triggered.connect(lambda: self.show_help)  # type: ignore
        # self.addAction(help_action)

    def show_help(self):
        """Показать справку"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            # "Справка",
            "Text War Legacy Mod-Editor\n\n"
            "Создавайте и редактируйте моды для игры!\n\n"
            "Основные возможности:\n"
            "• Редактор кода с подсветкой синтаксиса\n"
            "• Автодополнение кода\n"
            "• Дерево файлов проекта\n"
            "• Валидация и тестирование модов\n"
            "• Шаблоны для быстрого старта"
        )
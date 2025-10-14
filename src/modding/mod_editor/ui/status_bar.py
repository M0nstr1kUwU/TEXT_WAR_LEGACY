from PyQt5.QtWidgets import QStatusBar, QLabel
from PyQt5.QtCore import Qt, QTimer


class StatusBar(QStatusBar):
    """Кастомный статусбар с дополнительной информацией"""

    def __init__(self):
        super().__init__()

        self.setup_ui()
        self.message_timer = QTimer()
        self.message_timer.timeout.connect(self.clear_message) # type: ignore
        self.message_timer.setSingleShot(True)

    def setup_ui(self):
        """Настройка UI статусбара"""
        # Информация о позиции курсора
        self.cursor_position_label = QLabel("Строка: 1, Колонка: 1")
        self.addPermanentWidget(self.cursor_position_label)

        # Информация о кодировке
        self.encoding_label = QLabel("UTF-8")
        self.addPermanentWidget(self.encoding_label)

        # Информация о режиме редактирования
        self.edit_mode_label = QLabel("INS")
        self.addPermanentWidget(self.edit_mode_label)

    def show_message(self, message: str, timeout: int = 5000):
        """Показать сообщение в статусбаре"""
        self.showMessage(message, timeout)
        self.message_timer.start(timeout)

    def clear_message(self):
        """Очистить сообщение"""
        self.clearMessage()

    def update_cursor_position(self, line: int, column: int):
        """Обновить информацию о позиции курсора"""
        self.cursor_position_label.setText(f"Строка: {line}, Колонка: {column}")

    def update_encoding(self, encoding: str):
        """Обновить информацию о кодировке"""
        self.encoding_label.setText(encoding)

    def update_edit_mode(self, insert_mode: bool):
        """Обновить информацию о режиме редактирования"""
        self.edit_mode_label.setText("INS" if insert_mode else "OVR")

    def update_file_info(self, file_path: str, modified: bool):
        """Обновить информацию о файле"""
        status = "● " if modified else ""
        self.showMessage(f"{status}{file_path}")
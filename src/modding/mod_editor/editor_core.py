"""
Ядро редактора - основные функции и утилиты
"""

from os import path
from typing import Optional, Dict
from ui.code_editor import CodeEditor
from syntax_highlighter import SyntaxHighlighter


class EditorCore:
    """Ядро редактора с общими функциями"""

    def __init__(self):
        self.syntax_highlighter = SyntaxHighlighter()
        self.open_editors: Dict[str, CodeEditor] = {}

    def create_editor(self, settings, file_path: Optional[str] = None) -> CodeEditor:
        """Создание нового редактора"""
        editor = CodeEditor(settings)

        if file_path and path.exists(file_path):
            editor.load_file(file_path)
            self.open_editors[file_path] = editor

        return editor

    def get_lexer_for_file(self, file_path: str):
        """Получение лексера для файла"""
        return self.syntax_highlighter.get_lexer_for_file(file_path)

    def close_editor(self, file_path: str):
        """Закрытие редактора"""
        if file_path in self.open_editors:
            del self.open_editors[file_path]

    def get_open_editors(self) -> Dict[str, CodeEditor]:
        """Получение всех открытых редакторов"""
        return self.open_editors.copy()


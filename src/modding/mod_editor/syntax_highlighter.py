from PyQt5.Qsci import QsciLexerPython, QsciLexerJSON, QsciLexerXML
from PyQt5.QtGui import QColor, QFont


class SyntaxHighlighter:
    """Менеджер подсветки синтаксиса для разных языков"""

    def __init__(self):
        self.python_lexer = self.create_python_lexer()
        self.json_lexer = self.create_json_lexer()
        self.xml_lexer = self.create_xml_lexer()

    def create_python_lexer(self):
        """Создание лексера для Python с темной темой PyCharm"""
        lexer = QsciLexerPython()

        # Базовая настройка
        lexer.setDefaultPaper(QColor("#2b2b2b"))
        lexer.setDefaultColor(QColor("#a9b7c6"))
        lexer.setFont(QFont("Consolas", 10))

        # Цветовая схема PyCharm Dark
        colors = {
            QsciLexerPython.ClassName: QColor("#cc7832"),  # Классы - оранжевый
            QsciLexerPython.FunctionMethodName: QColor("#ffc66d"),  # Функции - желтый
            QsciLexerPython.Keyword: QColor("#9876aa"),  # Ключевые слова - фиолетовый
            QsciLexerPython.Comment: QColor("#6a8759"),  # Комментарии - зеленый
            QsciLexerPython.CommentBlock: QColor("#6a8759"),  # Блочные комментарии
            QsciLexerPython.Number: QColor("#6897bb"),  # Числа - голубой
            QsciLexerPython.DoubleQuotedString: QColor("#6a8759"),  # Строки - зеленый
            QsciLexerPython.SingleQuotedString: QColor("#6a8759"),
            QsciLexerPython.Operator: QColor("#bbb529"),  # Операторы - золотой
            QsciLexerPython.TripleSingleQuotedString: QColor("#a5c25c"),  # Docstrings
            QsciLexerPython.TripleDoubleQuotedString: QColor("#a5c25c"),
            QsciLexerPython.UnclosedString: QColor("#ff6b68"),  # Незакрытые строки - красный
            QsciLexerPython.Decorator: QColor("#bbb529"),  # Декораторы - золотой
        }

        for style, color in colors.items():
            lexer.setColor(color, style)

        return lexer

    def create_json_lexer(self):
        """Создание лексера для JSON"""
        lexer = QsciLexerJSON()
        lexer.setDefaultPaper(QColor("#2b2b2b"))
        lexer.setDefaultColor(QColor("#a9b7c6"))
        return lexer

    def create_xml_lexer(self):
        """Создание лексера для XML"""
        lexer = QsciLexerXML()
        lexer.setDefaultPaper(QColor("#2b2b2b"))
        lexer.setDefaultColor(QColor("#a9b7c6"))
        return lexer

    def get_lexer_for_file(self, file_path: str):
        """Получение лексера для файла по расширению"""
        if file_path.endswith('.py'):
            return self.python_lexer
        elif file_path.endswith('.json'):
            return self.json_lexer
        elif file_path.endswith('.xml'):
            return self.xml_lexer
        return None
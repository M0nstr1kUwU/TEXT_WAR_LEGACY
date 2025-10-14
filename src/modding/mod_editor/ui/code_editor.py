from pathlib import Path
from traceback import print_exc
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont, QColor
from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
from settings.settings_manager import settings


class CodeEditor(QsciScintilla):
    """Продвинутый редактор кода на основе QScintilla"""

    # Сигналы
    file_modified = pyqtSignal(bool)
    file_saved = pyqtSignal(str)

    def __init__(self, settings_manager):
        super().__init__()

        self.settings = settings_manager
        self.file_path = None
        self.is_modified = False
        self.original_content = ""
        self.lexer = None

        self.setup_editor()
        self.setup_lexer()
        self.setup_autocompletion()
        self.setup_connections()

    def setup_editor(self):
        """Настройка базовых параметров редактора"""
        # Настройка шрифта
        font = QFont()
        font.setFamily(self.settings.get('editor.font_family', 'Consolas'))
        font.setFixedPitch(True)
        font.setPointSize(self.settings.get('editor.font_size', 12))
        self.setFont(font)

        # Настройка отступов
        self.setMarginsFont(font)
        self.setMarginWidth(0, "0000")
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#2b2b2b"))
        self.setMarginsForegroundColor(QColor("#787878"))

        # Настройка отображения
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#2f2f2f"))
        self.setCaretForegroundColor(QColor("#ffffff"))

        # Настройка отступов
        self.setIndentationsUseTabs(not self.settings.get('editor.use_spaces', True))
        self.setIndentationWidth(self.settings.get('editor.tab_width', 4))
        self.setTabWidth(self.settings.get('editor.tab_width', 4))
        self.setAutoIndent(True)
        self.setBackspaceUnindents(True)

        # Настройка переноса строк
        self.setWrapMode(QsciScintilla.WrapWord if self.settings.get('editor.word_wrap', False) else QsciScintilla.WrapNone)

        # Цвет выделения
        self.setSelectionBackgroundColor(QColor("#3d3d3d"))
        self.setSelectionForegroundColor(QColor("#ffffff"))

        # Подсветка текущей строки
        if self.settings.get('syntax_highlighting.highlight_current_line', True):
            self.setCaretLineVisible(True)
            self.setCaretLineBackgroundColor(QColor("#323232"))

    def setup_lexer(self):
        """Настройка лексера Python"""
        try:
            self.lexer = QsciLexerPython()
            font = QFont("Consolas", 10)
            self.lexer.setFont(font)

            # Устанавливаем фон и цвет текста по умолчанию
            self.lexer.setPaper(QColor("#2b2b2b"))  # Фон
            self.lexer.setColor(QColor("#a9b7c6"))  # Цвет текста по умолчанию

            # Цвета для разных элементов
            self.lexer.setColor(QColor("#cc7832"), QsciLexerPython.ClassName)  # Классы - оранжевый
            self.lexer.setColor(QColor("#ffc66d"), QsciLexerPython.FunctionMethodName)  # Функции - желтый
            self.lexer.setColor(QColor("#9876aa"), QsciLexerPython.Keyword)  # Ключевые слова - фиолетовый
            self.lexer.setColor(QColor("#6a8759"), QsciLexerPython.Comment)  # Комментарии - зеленый
            self.lexer.setColor(QColor("#6a8759"), QsciLexerPython.CommentBlock)  # Блочные комментарии
            self.lexer.setColor(QColor("#6897bb"), QsciLexerPython.Number)  # Числа - голубой
            self.lexer.setColor(QColor("#6a8759"), QsciLexerPython.DoubleQuotedString)  # Строки - зеленый
            self.lexer.setColor(QColor("#6a8759"), QsciLexerPython.SingleQuotedString)
            self.lexer.setColor(QColor("#bbb529"), QsciLexerPython.Operator)  # Операторы - золотой
            self.lexer.setColor(QColor("#a5c25c"), QsciLexerPython.TripleSingleQuotedString)  # Docstrings
            self.lexer.setColor(QColor("#a5c25c"), QsciLexerPython.TripleDoubleQuotedString)
            self.setLexer(self.lexer)

        except Exception as e:
            settings.log_error(f"⚠️ Ошибка настройки лексера: {e}")

    def setup_autocompletion(self):
        """Настройка автодополнения кода"""
        try:
            from src.modding.mod_editor.code_completion import CodeCompleter

            if self.settings.get('code_completion.enabled', True):
                self.completer = CodeCompleter(self)
                self.setAutoCompletionSource(self.AcsAPIs)
                self.setAutoCompletionCaseSensitivity(not self.settings.get('code_completion.case_sensitive', False))
                self.setAutoCompletionReplaceWord(True)
                self.setAutoCompletionUseSingle(self.AcusAlways)
                self.setAutoCompletionThreshold(2)

                settings.log_info("✅ Автодополнение настроено успешно!")

        except ImportError as e:
            settings.log_error(f"⚠️ Автодополнение недоступно: {e}")
            print_exc()
        except Exception as e:
            settings.log_error(f"⚠️ Ошибка настройки автодополнения: {e}")
            print_exc()

    def setup_python_apis(self):
        """Настройка API для автодополнения Python"""
        try:
            if self.lexer is None:
                settings.log_warning("⚠️ Лексер не установлен для настройки API")
                return

            apis = QsciAPIs(self.lexer)

            # Базовые ключевые слова Python
            python_keywords = [
                "and", "as", "assert", "break", "class", "continue", "def", "del",
                "elif", "else", "except", "False", "finally", "for", "from", "global",
                "if", "import", "in", "is", "lambda", "None", "nonlocal", "not", "or",
                "pass", "raise", "return", "True", "try", "while", "with", "yield"
            ]

            # API Text War Legacy
            twl_api = [
                # Хуки
                "HOOK_REGISTRY", "hook_system", "mod_initialize",
                # Игрок
                "Player", "player", "health", "damage", "shield_hp", "potions",
                # Враги
                "Enemy", "enemy", "choose_entity_for_battle",
                # Битва
                "ActionBattle", "battle_loop", "player_turn", "enemy_turn",
                # AI
                "BaseAI", "AggressiveAI", "DefensiveAI", "BalancedAI", "AdaptiveAI", "BossAI",
                # Хуки функции
                "on_player_created", "on_battle_start", "on_damage_calculation",
                "on_enemy_creation", "on_ai_creation", "on_item_use"
            ]

            # Добавляем все ключевые слова
            for keyword in python_keywords + twl_api:
                apis.add(keyword)

            apis.prepare()

        except Exception as e:
            settings.log_error(f"⚠️ Ошибка настройки автодополнения: {e}")

    def setup_connections(self):
        """Настройка соединений сигналов"""
        self.textChanged.connect(self.on_text_changed)  # type: ignore

    def on_text_changed(self):
        """Обработчик изменения текста"""
        current_content = self.text()
        self.is_modified = (current_content != self.original_content)
        self.file_modified.emit(self.is_modified)  # type: ignore

    def load_file(self, file_path: str) -> bool:
        """Загрузка файла в редактор"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.setText(content)
            self.original_content = content
            self.file_path = file_path
            self.is_modified = False

            if file_path.endswith('.py') and self.lexer:
                self.setLexer(self.lexer)

            return True

        except Exception as e:
            settings.log_error(f"❌ Ошибка загрузки файла {file_path}: {e}")
            return False

    def save_file(self) -> bool:
        """Сохранение файла"""
        if not self.file_path:
            return self.save_file_as()

        try:
            content = self.text()
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.original_content = content
            self.is_modified = False
            self.file_modified.emit(False)  # type: ignore
            self.file_saved.emit(self.file_path)  # type: ignore

            return True

        except Exception as e:
            QMessageBox.critical(None, "Ошибка сохранения", f"Не удалось сохранить файл:\n{str(e)}")
            settings.log_error(f"Не удалось сохранить файл: {str(e)}")
            return False

    def save_file_as(self) -> bool:
        """Сохранение файла как..."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл как",
            self.file_path or "src/saves/mods/",
            "Python Files (*.py);;All Files (*)"
        )

        if file_path:
            self.file_path = file_path
            return self.save_file()

        return False

    def get_file_name(self) -> str:
        """Получение имени файла"""
        if self.file_path:
            return Path(self.file_path).name
        return "Untitled"

    def show_line_numbers(self, show: bool):
        """Показать/скрыть номера строк"""
        self.setMarginWidth(0, "0000" if show else 0)
        self.setMarginLineNumbers(0, show)

    def set_font_size(self, size: int):
        """Установка размера шрифта"""
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)
        self.setMarginsFont(font)

    def toggle_word_wrap(self, enabled: bool):
        """Включить/выключить перенос слов"""
        self.setWrapMode(QsciScintilla.WrapWord if enabled else QsciScintilla.WrapNone)

    def find_text(self, text: str, forward: bool = True, case_sensitive: bool = False) -> bool:
        """Поиск текста в редакторе"""
        return self.findFirst(
            text,
            False,  # regex
            case_sensitive,
            True,  # whole word
            True,  # wrap
            forward
        )

    def replace_text(self, find_text: str, replace_text: str, replace_all: bool = False) -> int:
        """Замена текста"""
        if replace_all:
            # Замена всех вхождений
            self.beginUndoAction()
            count = 0
            if self.findFirst(find_text, False, False, True, True, True):
                count += 1
                self.replace(replace_text)
                while self.findNext():
                    count += 1
                    self.replace(replace_text)
            self.endUndoAction()
            return count
        else:
            # Замена текущего вхождения
            if self.hasSelectedText() and self.selectedText() == find_text:
                self.replace(replace_text)
                return 1
            return 0

    def goto_line(self, line_number: int):
        """Переход к указанной строке"""
        if 0 <= line_number < self.lines():
            self.setCursorPosition(line_number, 0)
            self.ensureLineVisible(line_number)

    def get_current_line_info(self) -> dict:
        """Получение информации о текущей строке"""
        line, index = self.getCursorPosition()
        return {
            'line': line + 1,  # Переводим в 1-базный индекс
            'column': index + 1,
            'total_lines': self.lines(),
            'selected_text': self.selectedText()
        }

    def insert_template(self, template: str):
        """Вставка шаблона кода в текущую позицию"""
        self.insert(template)

    def comment_selection(self):
        """Закомментировать/раскомментировать выделение"""
        if not self.hasSelectedText():
            return

        line_from, index_from, line_to, index_to = self.getSelection()

        # Определяем, нужно комментировать или раскомментировать
        all_commented = True
        for line in range(line_from, line_to + 1):
            line_text = self.text(line).strip()
            if line_text and not line_text.startswith('#'):
                all_commented = False
                break

        self.beginUndoAction()

        if all_commented:
            # Раскомментировать
            for line in range(line_from, line_to + 1):
                line_text = self.text(line)
                if line_text.strip().startswith('#'):
                    # Находим первый #
                    pos = line_text.find('#')
                    self.setSelection(line, pos, line, pos + 1)
                    self.replace('')
        else:
            # Закомментировать
            for line in range(line_from, line_to + 1):
                self.insertAt('# ', line, 0)

        self.endUndoAction()
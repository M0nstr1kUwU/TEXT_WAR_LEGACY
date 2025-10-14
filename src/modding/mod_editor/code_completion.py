from traceback import print_exc
from PyQt5.Qsci import QsciAPIs
from typing import TYPE_CHECKING
from settings.settings_manager import settings

if TYPE_CHECKING:
    from ui.code_editor import CodeEditor


class CodeCompleter:
    """Система автодополнения кода для Text War Legacy API"""

    def __init__(self, editor: "CodeEditor"):
        self.editor = editor
        self.setup_completion()

    def setup_completion(self):
        """Настройка системы автодополнения"""
        try:
            lexer = self.editor.lexer
            if lexer is None:
                print("⚠️ Лексер не найден для редактора")
                settings.log_warning("⚠️ Лексер не найден для редактора")
                return

            self.apis = QsciAPIs(lexer)

            # Базовые ключевые слова Python
            python_keywords = [
                # Ключевые слова
                "and", "as", "assert", "async", "await", "break", "class", "continue",
                "def", "del", "elif", "else", "except", "False", "finally", "for",
                "from", "global", "if", "import", "in", "is", "lambda", "None",
                "nonlocal", "not", "or", "pass", "raise", "return", "True", "try",
                "while", "with", "yield",

                # Встроенные функции
                "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes",
                "callable", "chr", "classmethod", "compile", "complex", "delattr",
                "dict", "dir", "divmod", "enumerate", "eval", "exec", "filter",
                "float", "format", "frozenset", "getattr", "globals", "hasattr",
                "hash", "help", "hex", "id", "input", "int", "isinstance", "issubclass",
                "iter", "len", "list", "locals", "map", "max", "memoryview", "min",
                "next", "object", "oct", "open", "ord", "pow", "print", "property",
                "range", "repr", "reversed", "round", "set", "setattr", "slice",
                "sorted", "staticmethod", "str", "sum", "super", "tuple", "type",
                "vars", "zip", "__init__", "self"
            ]

            # Text War Legacy API
            twl_api = self.get_twl_api()

            # Добавляем все ключевые слова в автодополнение
            for keyword in python_keywords + twl_api:
                self.apis.add(keyword)

            self.apis.prepare()

            # Настраиваем редактор для автодополнения
            self.editor.setAutoCompletionSource(self.editor.AcsAPIs)
            self.editor.setAutoCompletionCaseSensitivity(False)
            self.editor.setAutoCompletionReplaceWord(True)
            self.editor.setAutoCompletionUseSingle(self.editor.AcusAlways)
            self.editor.setAutoCompletionThreshold(2)  # Начинать после 2 символов
            self.editor.setAutoCompletionShowSingle(True)

            print("✅ Система автодополнения настроена успешно!")
            settings.log_info("✅ Система автодополнения настроена успешно!")

        except Exception as e:
            print(f"⚠️ Ошибка настройки автодополнения: {e}")
            settings.log_error(f"⚠️ Ошибка настройки автодополнения: {e}")
            print_exc()

    def get_twl_api(self):
        """Получение API Text War Legacy для автодополнения"""
        return [
            # 🎮 СИСТЕМА ХУКОВ
            "HOOK_REGISTRY", "hook_system", "mod_initialize",

            # 👤 ИГРОК
            "Player", "player", "name", "health", "health_max", "health_repair",
            "damage", "shield_hp", "potions", "coin", "level", "experience",
            "isAlive", "to_dict", "from_dict",

            # 👹 ВРАГИ
            "Enemy", "enemy", "choose_entity_for_battle", "difficulty",
            "gold_reward", "special_ability", "element",

            # ⚔️ БИТВА
            "ActionBattle", "battle_loop", "player_turn", "enemy_turn",
            "heal", "attack", "shield", "potion", "calculate_damage",

            # 🧠 AI СИСТЕМА
            "BaseAI", "AggressiveAI", "DefensiveAI", "BalancedAI",
            "AdaptiveAI", "BossAI", "AIManager", "choose_action",
            "analyze_situation", "update_learning",

            # 🎯 ХУКИ (основные)
            "on_player_created", "on_battle_start", "on_damage_calculation",
            "on_enemy_creation", "on_ai_creation", "on_item_use",
            "on_player_level_up", "on_battle_end", "on_game_initialized",
            "on_main_menu_created", "on_config_loaded",

            # 📦 ИМПОРТЫ (часто используемые)
            "random", "json", "os", "sys", "typing", "pathlib", "abc",
            "Dict", "List", "Any", "Optional", "Union",

            # 🛠️ УТИЛИТЫ
            "print", "input", "len", "str", "int", "float", "bool",
            "list", "dict", "tuple", "set", "range", "enumerate",

            # 🔧 МОДИНГ
            "execute_hook", "register_hook", "load_mods", "get_available_hooks"
        ]

    def add_custom_api(self, keywords):
        """Добавление кастомных ключевых слов для автодополнения"""
        try:
            for keyword in keywords:
                self.apis.add(keyword)
            self.apis.prepare()
        except Exception as e:
            print(f"⚠️ Ошибка добавления кастомного API: {e}")
            settings.log_error(f"⚠️ Ошибка добавления кастомного API: {e}")

    def get_completion_for_context(self, text_before_cursor):
        """Получение подсказок для текущего контекста"""
        suggestions = []

        # Контекстные подсказки для импортов
        if "import" in text_before_cursor or "from" in text_before_cursor:
            suggestions.extend([
                "src.entities.player",
                "src.entities.enemy",
                "src.actions.actions_battle",
                "src.ai_resources.ai_enemy",
                "src.modding.support_mods",
                "src.settings.settings_manager"
            ])

        # Контекстные подсказки для хуков
        if "HOOK_REGISTRY" in text_before_cursor or "hook" in text_before_cursor.lower():
            suggestions.extend([
                "player_created", "battle_start", "damage_calculation",
                "enemy_creation", "ai_creation", "item_use", "player_level_up",
                "battle_end", "game_initialized", "main_menu_created"
            ])

        # Контекстные подсказки для игрока
        if "player." in text_before_cursor:
            suggestions.extend([
                "name", "health", "health_max", "damage", "shield_hp",
                "potions", "coin", "level", "experience", "isAlive"
            ])

        return suggestions

    def update_completion(self):
        """Обновление базы автодополнения"""
        try:
            self.apis.load("")
            self.setup_completion()
        except Exception as e:
            print(f"⚠️ Ошибка обновления автодополнения: {e}")
            settings.log_error(f"⚠️ Ошибка обновления автодополнения: {e}")


class CompletionManager:
    """Менеджер автодополнения для нескольких редакторов"""

    def __init__(self):
        self.completers = {}

    def add_editor(self, editor, editor_id):
        """Добавление редактора для автодополнения"""
        try:
            if editor_id not in self.completers:
                self.completers[editor_id] = CodeCompleter(editor)
                print(f"✅ Добавлен комплитер для редактора {editor_id}")
                settings.log_info(f"✅ Добавлен комплитер для редактора {editor_id}")
        except Exception as e:
            print(f"⚠️ Ошибка добавления редактора {editor_id}: {e}")
            settings.log_error(f"⚠️ Ошибка добавления редактора {editor_id}: {e}")

    def remove_editor(self, editor_id):
        """Удаление редактора из автодополнения"""
        if editor_id in self.completers:
            del self.completers[editor_id]

    def update_editor_completion(self, editor_id, custom_keywords=None):
        """Обновление автодополнения для редактора"""
        try:
            if editor_id in self.completers:
                if custom_keywords:
                    self.completers[editor_id].add_custom_api(custom_keywords)
                self.completers[editor_id].update_completion()
        except Exception as e:
            print(f"⚠️ Ошибка обновления автодополнения для {editor_id}: {e}")
            settings.log_error(f"⚠️ Ошибка обновления автодополнения для {editor_id}: {e}")
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget,
                            QTreeWidgetItem, QTextEdit, QSplitter, QPushButton,
                            QLabel, QLineEdit, QTabWidget, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor


class HookExplorer:
    """Обозреватель хуков для документации и примеров"""

    def __init__(self):
        self.hook_categories = self.load_hook_categories()
        self.hook_examples = self.load_hook_examples()

    def load_hook_categories(self):
        """Загрузка категорий хуков"""
        return {
            "Системные": [
                "game_initialized", "game_shutdown", "config_loaded"
            ],
            "Игрок": [
                "player_created", "player_level_up", "player_stat_update",
                "player_death", "player_revive"
            ],
            "Битва": [
                "battle_start", "battle_end", "round_start", "round_end"
            ],
            "Ходы": [
                "player_turn_start", "player_action_selected", "player_turn_end",
                "enemy_turn_start", "enemy_action_selected", "enemy_turn_end"
            ],
            "Расчеты": [
                "damage_calculation", "healing_calculation", "critical_calculation"
            ],
            "Предметы": [
                "item_use", "item_purchase", "item_drop"
            ],
            "Враги": [
                "enemy_creation", "enemy_defeated", "enemy_ability_use"
            ],
            "AI": [
                "ai_creation", "ai_decision", "ai_behavior_update",
                "ai_special_ability", "ai_learning_update"
            ],
            "Интерфейс": [
                "ui_display", "text_display", "color_scheme"
            ]
        }

    def load_hook_examples(self):
        """Загрузка примеров использования хуков"""
        return {
            "player_created": {
                "description": "Вызывается при создании игрока. Позволяет модифицировать начальные характеристики.",
                "parameters": ["player", "hook_system"],
                "return": "None",
                "example": '''def on_player_created(player, hook_system):
    """Усиливает игрока при создании"""
    if player and hasattr(player, 'damage'):
        player.damage += 2
        player.health_max += 10
        player.health = player.health_max
        print("💪 Игрок усилен модом!")''',
                "notes": "Идеально для изменения стартовых характеристик игрока."
            },
            "battle_start": {
                "description": "Вызывается в начале битвы. Позволяет добавить специальные эффекты или условия.",
                "parameters": ["player", "enemy", "mode", "hook_system"],
                "return": "None",
                "example": '''def on_battle_start(player, enemy, mode, hook_system):
    """Добавляет эффекты в начале битвы"""
    if enemy.name == "🐉 Дракон":
        print("🔥 Дракон извергает пламя!")
        # Можно добавить начальный урон или эффекты''',
                "notes": "Используйте для создания уникальных начальных условий битвы."
            },
            "damage_calculation": {
                "description": "Вызывается при расчете урона. Позволяет модифицировать урон перед применением.",
                "parameters": ["attacker", "defender", "base_damage", "element", "is_critical", "hook_system"],
                "return": "int (модифицированный урон)",
                "example": '''def on_damage_calculation(attacker, defender, base_damage, element, is_critical, hook_system):
    """Добавляет элементные бонусы к урону"""
    element_bonus = {
        'fire': 1.2 if element == 'fire' else 1.0,
        'ice': 1.15 if element == 'ice' else 1.0,
        'nature': 1.1 if element == 'nature' else 1.0
    }
    bonus = element_bonus.get(element, 1.0)
    return int(base_damage * bonus)''',
                "notes": "Должна возвращать целое число - финальный урон."
            },
            "enemy_creation": {
                "description": "Вызывается при создании врага. Позволяет заменить или модифицировать врага.",
                "parameters": ["enemy", "difficulty", "hook_system"],
                "return": "Enemy (оригинальный или модифицированный враг)",
                "example": '''def on_enemy_creation(enemy, difficulty, hook_system):
    """Усиливает боссов и добавляет специальных врагов"""
    if 'boss' in enemy.difficulty.lower():
        # Усиливаем боссов
        enemy.health_max += 20
        enemy.damage += 3
        enemy.health = enemy.health_max
    return enemy''',
                "notes": "Можно вернуть кастомного врага вместо стандартного."
            },
            "ai_creation": {
                "description": "Вызывается при создании AI для врага. Позволяет заменить стандартный AI.",
                "parameters": ["enemy", "difficulty", "hook_system"],
                "return": "BaseAI (кастомная реализация AI)",
                "example": '''def on_ai_creation(enemy, difficulty, hook_system):
    """Заменяет AI на кастомную реализацию"""
    from src.ai_resources.ai_enemy.base_ai import BaseAI
    import random

    class CustomAI(BaseAI):
        def choose_action(self, enemy, player, battle_context):
            if player.health < player.health_max * 0.3:
                return "attack"  # Добить игрока
            return random.choice(["attack", "defend", "heal"])

    return CustomAI(difficulty)''',
                "notes": "Требует импорта BaseAI и создания кастомного класса."
            },
            "item_use": {
                "description": "Вызывается при использовании предмета. Позволяет добавить кастомные предметы.",
                "parameters": ["player", "item_type", "target", "hook_system"],
                "return": "bool (True если предмет обработан, False для стандартной обработки)",
                "example": '''def on_item_use(player, item_type, target, hook_system):
    """Добавляет кастомные предметы"""
    if item_type == "magic_sword":
        player.damage += 5
        print("⚔️ Магический меч увеличивает урон!")
        return True  # Предмет обработан
    return False  # Стандартная обработка''',
                "notes": "Возвращайте True для кастомных предметов, False для стандартных."
            }
        }

    def show_documentation(self, parent=None):
        """Показать документацию хуков"""
        dialog = HookDocumentationDialog(self.hook_categories, self.hook_examples, parent)
        return dialog.exec_()

    def get_hook_info(self, hook_name: str) -> dict:
        """Получить информацию о конкретном хуке"""
        return self.hook_examples.get(hook_name, {
            "description": "Информация о хуке не найдена.",
            "parameters": [],
            "return": "None",
            "example": "# Пример не доступен",
            "notes": ""
        })

    def search_hooks(self, query: str) -> list:
        """Поиск хуков по запросу"""
        results = []
        query = query.lower()

        for hook_name, hook_info in self.hook_examples.items():
            if (query in hook_name.lower() or
                    query in hook_info['description'].lower() or
                    query in hook_info['notes'].lower()):
                results.append(hook_name)

        return results


class HookDocumentationDialog(QDialog):
    """Диалог документации хуков"""

    # Сигналы
    code_insert_requested = pyqtSignal(str)

    def __init__(self, hook_categories, hook_examples, parent=None):
        super().__init__(parent)

        self.hook_categories = hook_categories
        self.hook_examples = hook_examples

        self.setup_ui()

    def setup_ui(self):
        """Настройка UI диалога"""
        self.setWindowTitle("Документация хуков - Text War Legacy")
        self.setMinimumSize(900, 700)

        layout = QVBoxLayout(self)

        # Заголовок
        title_label = QLabel("📚 Документация системы хуков")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # Поиск
        search_layout = QHBoxLayout()
        search_label = QLabel("Поиск:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название хука или ключевое слово...")
        self.search_input.textChanged.connect(self.on_search_changed) # type: ignore

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Основной сплиттер
        main_splitter = QSplitter(Qt.Horizontal)

        # Левая панель - дерево хуков
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        left_layout.addWidget(QLabel("Категории хуков:"))

        self.hook_tree = QTreeWidget()
        self.hook_tree.setHeaderLabel("Хуки")
        self.hook_tree.itemClicked.connect(self.on_hook_selected) # type: ignore

        # Заполнение дерева категорий
        for category, hooks in self.hook_categories.items():
            category_item = QTreeWidgetItem(self.hook_tree, [category])
            for hook in hooks:
                hook_item = QTreeWidgetItem(category_item, [hook])
                hook_item.setData(0, Qt.UserRole, hook)
            category_item.setExpanded(True)

        left_layout.addWidget(self.hook_tree)

        # Правая панель - документация
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        right_layout.addWidget(QLabel("Документация хука:"))

        # Табы для различной информации
        self.tab_widget = QTabWidget()

        # Вкладка описания
        self.description_tab = QTextEdit()
        self.description_tab.setReadOnly(True)
        self.tab_widget.addTab(self.description_tab, "Описание")

        # Вкладка параметров
        self.parameters_tab = QTextEdit()
        self.parameters_tab.setReadOnly(True)
        self.tab_widget.addTab(self.parameters_tab, "Параметры")

        # Вкладка примера
        self.example_tab = QTextEdit()
        self.example_tab.setReadOnly(True)
        self.example_tab.setFontFamily("Consolas")
        self.tab_widget.addTab(self.example_tab, "Пример кода")

        # Вкладка примечаний
        self.notes_tab = QTextEdit()
        self.notes_tab.setReadOnly(True)
        self.tab_widget.addTab(self.notes_tab, "Примечания")

        right_layout.addWidget(self.tab_widget)

        # Кнопка вставки кода
        self.insert_button = QPushButton("Вставить код в редактор")
        self.insert_button.clicked.connect(self.insert_code_to_editor)  # type: ignore
        self.insert_button.setEnabled(False)
        right_layout.addWidget(self.insert_button)

        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([300, 600])

        layout.addWidget(main_splitter)

        # Кнопки закрытия
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept) # type: ignore
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        # Выбираем первый хук
        if self.hook_tree.topLevelItemCount() > 0:
            first_category = self.hook_tree.topLevelItem(0)
            if first_category and first_category.childCount() > 0:
                first_hook = first_category.child(0)
                self.hook_tree.setCurrentItem(first_hook)
                self.on_hook_selected(first_hook, 0)

    def on_search_changed(self, text):
        """Обработчик изменения поискового запроса"""
        if not text.strip():
            for i in range(self.hook_tree.topLevelItemCount()):
                category = self.hook_tree.topLevelItem(i)
                for j in range(category.childCount()):
                    category.child(j).setHidden(False)
            return

        # Скрыть/показать элементы по поиску
        search_text = text.lower()
        for i in range(self.hook_tree.topLevelItemCount()):
            category = self.hook_tree.topLevelItem(i)
            category_matches = False

            for j in range(category.childCount()):
                hook_item = category.child(j)
                hook_name = hook_item.text(0).lower()
                hook_data = hook_item.data(0, Qt.UserRole)

                if hook_data and hook_data in self.hook_examples:
                    hook_info = self.hook_examples[hook_data]
                    matches = (search_text in hook_name or
                               search_text in hook_info['description'].lower() or
                               search_text in hook_info['notes'].lower())

                    hook_item.setHidden(not matches)
                    if matches:
                        category_matches = True

            category.setHidden(not category_matches)

    def on_hook_selected(self, item, column):
        """Обработчик выбора хука"""
        hook_name = item.data(0, Qt.UserRole)
        if not hook_name:
            return

        hook_info = self.hook_examples.get(hook_name)
        if not hook_info:
            return

        # Обновляем описание
        self.description_tab.setText(f"""
<h2>Хук: {hook_name}</h2>
<p><strong>Описание:</strong> {hook_info['description']}</p>
""")

        # Обновляем параметры
        params_text = f"<h3>Параметры функции:</h3><ul>"
        for param in hook_info['parameters']:
            params_text += f"<li><code>{param}</code></li>"
        params_text += f"</ul><p><strong>Возвращаемое значение:</strong> <code>{hook_info['return']}</code></p>"

        self.parameters_tab.setText(params_text)
        self.example_tab.setText(hook_info['example'])
        self.notes_tab.setText(f"<h3>Примечания:</h3><p>{hook_info['notes']}</p>")
        self.current_hook = hook_name
        self.insert_button.setEnabled(True)

    def insert_code_to_editor(self):
        """Вставка кода примера в редактор"""
        if hasattr(self, 'current_hook') and self.current_hook:
            hook_info = self.hook_examples.get(self.current_hook)
            if hook_info:
                example_code = hook_info['example']
                self.code_insert_requested.emit(example_code)  # type: ignore
                self.accept()



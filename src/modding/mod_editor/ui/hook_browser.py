from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QSplitter, QPushButton, QLabel, QLineEdit,
                             QComboBox, QTabWidget, QApplication, QHeaderView,
                             QTableWidget, QTableWidgetItem, QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QSyntaxHighlighter, QTextCharFormat, QBrush
from PyQt5.QtCore import QTimer


class HookBrowser(QWidget):
    """Обозреватель хуков с поиском и фильтрацией"""

    # Сигналы
    hook_selected = pyqtSignal(str, dict)
    insert_code_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.hook_data = self.load_hook_data()
        self.setup_ui()
        self.setup_connections()

    @staticmethod
    def load_hook_data():
        """Загрузка данных о хуках"""
        return {
            "player_created": {
                "category": "Игрок",
                "description": "Вызывается при создании нового игрока",
                "parameters": ["player", "hook_system"],
                "return_type": "None",
                "example": '''def on_player_created(player, hook_system):
    \"\"\"Усиливает игрока при создании\"\"\"
    if player and hasattr(player, 'damage'):
        player.damage += 2
        player.health_max += 10
        player.health = player.health_max
        print("💪 Игрок усилен модом!")''',
                "usage": "Идеально для изменения стартовых характеристик игрока",
                "version": "1.0.0"
            },
            "battle_start": {
                "category": "Битва",
                "description": "Вызывается в начале битвы",
                "parameters": ["player", "enemy", "mode", "hook_system"],
                "return_type": "None",
                "example": '''def on_battle_start(player, enemy, mode, hook_system):
    \"\"\"Добавляет эффекты в начале битвы\"\"\"
    if enemy.name == "🐉 Дракон":
        print("🔥 Дракон извергает пламя!")
    elif enemy.name == "❄️ Ледяной голем":
        print("❄️ Температура падает!")''',
                "usage": "Для создания уникальных начальных условий битвы",
                "version": "1.0.0"
            },
            "damage_calculation": {
                "category": "Расчеты",
                "description": "Вызывается при расчете урона",
                "parameters": ["attacker", "defender", "base_damage", "element", "is_critical", "hook_system"],
                "return_type": "int",
                "example": '''def on_damage_calculation(attacker, defender, base_damage, element, is_critical, hook_system):
    \"\"\"Добавляет элементные бонусы\"\"\"
    element_bonus = {
        'fire': 1.2,
        'ice': 1.15, 
        'nature': 1.1
    }
    bonus = element_bonus.get(element, 1.0)
    return int(base_damage * bonus)''',
                "usage": "Должна возвращать целое число - финальный урон",
                "version": "1.0.0"
            },
            "enemy_creation": {
                "category": "Враги",
                "description": "Вызывается при создании врага",
                "parameters": ["enemy", "difficulty", "hook_system"],
                "return_type": "Enemy",
                "example": '''def on_enemy_creation(enemy, difficulty, hook_system):
    \"\"\"Усиливает боссов\"\"\"
    if 'boss' in enemy.difficulty.lower():
        enemy.health_max += 20
        enemy.damage += 3
        enemy.health = enemy.health_max
    return enemy''',
                "usage": "Можно вернуть кастомного врага вместо стандартного",
                "version": "1.0.0"
            },
            "ai_creation": {
                "category": "AI",
                "description": "Вызывается при создании AI для врага",
                "parameters": ["enemy", "difficulty", "hook_system"],
                "return_type": "BaseAI",
                "example": '''def on_ai_creation(enemy, difficulty, hook_system):
    \"\"\"Заменяет AI на кастомный\"\"\"
    from src.ai_resources.ai_enemy.base_ai import BaseAI

    class CustomAI(BaseAI):
        def choose_action(self, enemy, player, battle_context):
            if player.health < player.health_max * 0.3:
                return "attack"
            return random.choice(["attack", "defend", "heal"])

    return CustomAI(difficulty)''',
                "usage": "Требует импорта BaseAI и создания кастомного класса",
                "version": "1.1.0"
            },
            "item_use": {
                "category": "Предметы",
                "description": "Вызывается при использовании предмета",
                "parameters": ["player", "item_type", "target", "hook_system"],
                "return_type": "bool",
                "example": '''def on_item_use(player, item_type, target, hook_system):
    \"\"\"Добавляет кастомные предметы\"\"\"
    if item_type == "magic_sword":
        player.damage += 5
        print("⚔️ Магический меч увеличивает урон!")
        return True  # Предмет обработан
    return False  # Стандартная обработка''',
                "usage": "Возвращайте True для кастомных предметов, False для стандартных",
                "version": "1.0.0"
            },
            "player_level_up": {
                "category": "Игрок",
                "description": "Вызывается при повышении уровня игрока",
                "parameters": ["player", "old_level", "new_level", "hook_system"],
                "return_type": "None",
                "example": '''def on_player_level_up(player, old_level, new_level, hook_system):
    \"\"\"Дает бонусы за уровень\"\"\"
    if new_level % 5 == 0:  # Каждые 5 уровней
        player.damage += 1
        player.health_max += 5
        print(f"🎯 Достигнут уровень {new_level}!")''',
                "usage": "Для системы прокачки и бонусов за уровень",
                "version": "1.1.0"
            },
            "battle_end": {
                "category": "Битва",
                "description": "Вызывается в конце битвы",
                "parameters": ["player", "enemy", "result", "hook_system"],
                "return_type": "None",
                "example": '''def on_battle_end(player, enemy, result, hook_system):
    \"\"\"Награды за победу\"\"\"
    if result == 'player_win':
        player.coin += enemy.gold_reward
        print(f"💰 Получено {enemy.gold_reward} монет!")
    else:
        print("💀 Нужно тренироваться...")''',
                "usage": "Для наград, достижений и статистики",
                "version": "1.0.0"
            }
        }

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout(self)

        # Заголовок
        title_label = QLabel("🔍 Обозреватель хуков")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # Панель поиска и фильтров
        search_layout = QHBoxLayout()

        search_label = QLabel("Поиск:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название хука или описание...")

        category_label = QLabel("Категория:")
        self.category_combo = QComboBox()
        self.category_combo.addItem("Все категории")
        self.category_combo.addItems(["Игрок", "Битва", "Расчеты", "Враги", "AI", "Предметы"])

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(category_label)
        search_layout.addWidget(self.category_combo)
        search_layout.addStretch()

        layout.addLayout(search_layout)

        # Основной сплиттер
        main_splitter = QSplitter(Qt.Horizontal)

        # Левая панель - список хуков
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        left_layout.addWidget(QLabel("Доступные хуки:"))

        self.hooks_table = QTableWidget()
        self.hooks_table.setColumnCount(3)
        self.hooks_table.setHorizontalHeaderLabels(["Хук", "Категория", "Версия"])
        self.hooks_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.hooks_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.hooks_table.setEditTriggers(QTableWidget.NoEditTriggers)

        left_layout.addWidget(self.hooks_table)

        # Правая панель - детали хука
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        right_layout.addWidget(QLabel("Детали хука:"))

        # Табы с информацией
        self.details_tabs = QTabWidget()

        # Вкладка описания
        self.description_tab = QTextEdit()
        self.description_tab.setReadOnly(True)
        self.details_tabs.addTab(self.description_tab, "Описание")

        # Вкладка параметров
        self.parameters_tab = QTextEdit()
        self.parameters_tab.setReadOnly(True)
        self.details_tabs.addTab(self.parameters_tab, "Параметры")

        # Вкладка примера
        self.example_tab = QTextEdit()
        self.example_tab.setReadOnly(True)
        self.example_tab.setFontFamily("Consolas")
        self.details_tabs.addTab(self.example_tab, "Пример кода")

        # Вкладка использования
        self.usage_tab = QTextEdit()
        self.usage_tab.setReadOnly(True)
        self.details_tabs.addTab(self.usage_tab, "Использование")

        right_layout.addWidget(self.details_tabs)

        # Кнопки действий
        button_layout = QHBoxLayout()

        self.insert_button = QPushButton("Вставить код в редактор")
        self.insert_button.setEnabled(False)

        self.copy_button = QPushButton("Копировать код")
        self.copy_button.setEnabled(False)

        button_layout.addWidget(self.insert_button)
        button_layout.addWidget(self.copy_button)
        button_layout.addStretch()

        right_layout.addLayout(button_layout)

        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([400, 500])

        layout.addWidget(main_splitter)

        # Заполняем таблицу хуков
        self.populate_hooks_table()

    def setup_connections(self):
        """Настройка соединений сигналов"""
        self.search_input.textChanged.connect(self.filter_hooks) # type: ignore
        self.category_combo.currentTextChanged.connect(self.filter_hooks)# type: ignore
        self.hooks_table.itemSelectionChanged.connect(self.on_hook_selected)# type: ignore
        self.insert_button.clicked.connect(self.insert_code)# type: ignore
        self.copy_button.clicked.connect(self.copy_code)# type: ignore

    def populate_hooks_table(self):
        """Заполнение таблицы хуков"""
        self.hooks_table.setRowCount(len(self.hook_data))

        for row, (hook_name, hook_info) in enumerate(self.hook_data.items()):
            # Название хука
            name_item = QTableWidgetItem(hook_name)
            self.hooks_table.setItem(row, 0, name_item)

            # Категория
            category_item = QTableWidgetItem(hook_info['category'])
            self.hooks_table.setItem(row, 1, category_item)

            # Версия
            version_item = QTableWidgetItem(hook_info['version'])
            self.hooks_table.setItem(row, 2, version_item)

        # Авто-размер колонок
        self.hooks_table.resizeColumnsToContents()

    def filter_hooks(self):
        """Фильтрация хуков по поиску и категории"""
        search_text = self.search_input.text().lower()
        category_filter = self.category_combo.currentText()

        for row in range(self.hooks_table.rowCount()):
            hook_name = self.hooks_table.item(row, 0).text()
            hook_category = self.hooks_table.item(row, 1).text()

            # Проверка поиска
            matches_search = (search_text in hook_name.lower() or
                              search_text in self.hook_data[hook_name]['description'].lower())

            # Проверка категории
            matches_category = (category_filter == "Все категории" or
                                category_filter == hook_category)

            # Показываем/скрываем строку
            self.hooks_table.setRowHidden(row, not (matches_search and matches_category))

    def on_hook_selected(self):
        """Обработчик выбора хука"""
        selected_items = self.hooks_table.selectedItems()
        if not selected_items:
            return

        hook_name = selected_items[0].text()
        hook_info = self.hook_data.get(hook_name)

        if not hook_info:
            return

        # Обновляем детали хука
        self.update_hook_details(hook_name, hook_info)

        # Включаем кнопки
        self.insert_button.setEnabled(True)
        self.copy_button.setEnabled(True)

        # Эмитируем сигнал
        self.hook_selected.emit(hook_name, hook_info)  # type: ignore

    def update_hook_details(self, hook_name: str, hook_info: dict):
        """Обновление деталей выбранного хука"""
        # Вкладка описания
        description_html = f"""
        <h2>Хук: {hook_name}</h2>
        <p><strong>Описание:</strong> {hook_info['description']}</p>
        <p><strong>Категория:</strong> {hook_info['category']}</p>
        <p><strong>Версия:</strong> {hook_info['version']}</p>
        """
        self.description_tab.setHtml(description_html)

        # Вкладка параметров
        params_html = f"""
        <h3>Сигнатура функции:</h3>
        <pre>def {hook_name}({', '.join(hook_info['parameters'])}):</pre>

        <h3>Параметры:</h3>
        <ul>
        """
        for param in hook_info['parameters']:
            params_html += f"<li><code>{param}</code></li>"
        params_html += f"""
        </ul>
        <p><strong>Возвращаемое значение:</strong> <code>{hook_info['return_type']}</code></p>
        """
        self.parameters_tab.setHtml(params_html)

        # Вкладка примера
        self.example_tab.setPlainText(hook_info['example'])

        # Вкладка использования
        usage_html = f"""
        <h3>Рекомендации по использованию:</h3>
        <p>{hook_info['usage']}</p>

        <h3>Примечания:</h3>
        <ul>
            <li>Функция должна быть зарегистрирована в HOOK_REGISTRY</li>
            <li>Имя функции может быть любым, главное чтобы оно совпадало с HOOK_REGISTRY</li>
            <li>Все хуки получают hook_system как последний параметр</li>
        </ul>
        """
        self.usage_tab.setHtml(usage_html)

    def insert_code(self):
        """Вставка кода примера в редактор"""
        selected_items = self.hooks_table.selectedItems()
        if not selected_items:
            return

        hook_name = selected_items[0].text()
        hook_info = self.hook_data.get(hook_name)

        if hook_info:
            # Эмитируем сигнал для вставки кода
            self.insert_code_requested.emit(hook_info['example'])  # type: ignore

    def copy_code(self):
        """Копирование кода в буфер обмена"""
        selected_items = self.hooks_table.selectedItems()
        if not selected_items:
            return

        hook_name = selected_items[0].text()
        hook_info = self.hook_data.get(hook_name)

        if hook_info:
            clipboard = QApplication.clipboard()
            clipboard.setText(hook_info['example'])

            # Временное сообщение об успехе
            self.insert_button.setText("✅ Скопировано!")
            QApplication.processEvents()

            # Возвращаем оригинальный текст через 2 секунды
            QTimer.singleShot(2000, lambda: self.insert_button.setText("Вставить код в редактор"))

    def get_hook_categories(self) -> list:
        """Получение списка категорий хуков"""
        categories = set()
        for hook_info in self.hook_data.values():
            categories.add(hook_info['category'])
        return sorted(categories)

    def search_hooks(self, query: str) -> list:
        """Поиск хуков по запросу"""
        results = []
        query = query.lower()

        for hook_name, hook_info in self.hook_data.items():
            if (query in hook_name.lower() or
                    query in hook_info['description'].lower() or
                    query in hook_info['usage'].lower()):
                results.append((hook_name, hook_info))

        return results

    def get_hook_info(self, hook_name: str) -> dict:
        """Получение информации о конкретном хуке"""
        return self.hook_data.get(hook_name, {})
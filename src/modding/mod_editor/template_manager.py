from traceback import print_exc
from ..mod_editor.project_manager import ProjectManager
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                             QTextEdit, QPushButton, QLabel, QListWidgetItem,
                             QSplitter, QWidget)
from PyQt5.QtCore import Qt
from ....main import settings


class TemplateManager:
    """Менеджер шаблонов для быстрого создания модов"""

    def __init__(self):
        self.templates = self.load_templates()

    def load_templates(self):
        """Загрузка доступных шаблонов"""
        return {
            "basic": {
                "name": "Базовый мод",
                "description": "Простой шаблон для начала работы",
                "category": "Основные",
                "file_content": self.get_basic_template()
            },
            "ai_mod": {
                "name": "AI Мод",
                "description": "Шаблон для создания кастомного AI",
                "category": "AI",
                "file_content": self.get_ai_template()
            },
            "hook_mod": {
                "name": "Хук-мод",
                "description": "Шаблон с примерами хуков",
                "category": "Хуки",
                "file_content": self.get_hook_template()
            },
            "item_mod": {
                "name": "Мод предметов",
                "description": "Шаблон для добавления предметов",
                "category": "Предметы",
                "file_content": self.get_item_template()
            },
            "enemy_mod": {
                "name": "Мод врагов",
                "description": "Шаблон для добавления новых врагов",
                "category": "Враги",
                "file_content": self.get_enemy_template()
            }
        }

    def show_template_dialog(self, parent, project_name: str = None):
        """Показать диалог выбора шаблона"""
        dialog = TemplateDialog(self.templates, project_name, parent)
        return dialog.exec_()

    def get_basic_template(self):
        """Базовый шаблон мода"""
        return '''"""
МОД: {mod_name}
Автор: Ваше имя
Версия: 1.0.0
Описание: Краткое описание мода
"""

def mod_initialize(hook_system):
    """Инициализация мода"""
    print(f"✅ Мод '{{mod_name}}' загружен!")
    return True

# РЕГИСТРАЦИЯ ХУКОВ
HOOK_REGISTRY = {{
    # Пример регистрации хуков:
    # 'player_created': on_player_created,
    # 'battle_start': on_battle_start,
}}

# ПРИМЕРЫ ФУНКЦИЙ ХУКОВ (раскомментируйте для использования)

# def on_player_created(player, hook_system):
#     """Усиливает игрока при создании"""
#     if player and hasattr(player, 'damage'):
#         player.damage += 2
#         player.health_max += 10
#         print(f"💪 Мод {{mod_name}}: Игрок усилен!")
#
# def on_battle_start(player, enemy, mode, hook_system):
#     """Добавляет эффекты в начале битвы"""
#     if player and enemy:
#         print(f"🔥 Мод {{mod_name}}: Битва начинается!")
'''

    def get_ai_template(self):
        """Шаблон AI мода"""
        return '''"""
МОД AI: {mod_name}
Автор: Ваше имя  
Версия: 1.0.0
Описание: Мод для кастомного AI поведения
"""

from src.ai_resources.ai_enemy.base_ai import BaseAI
import random

class CustomAI(BaseAI):
    """Кастомный AI для врагов"""

    def __init__(self, difficulty="medium"):
        super().__init__("Кастомный AI", difficulty)

    def choose_action(self, enemy, player, battle_context):
        """Кастомная логика выбора действий"""
        situation = self.analyze_situation(enemy, player)

        # Ваша кастомная логика здесь
        if situation["player_health_low"]:
            return "attack"  # Добить игрока

        return random.choice(["attack", "defend", "heal"])

def mod_initialize(hook_system):
    """Инициализация AI мода"""
    print(f"✅ AI Мод '{{mod_name}}' загружен!")
    return True

def on_ai_creation(enemy, difficulty, hook_system):
    """Заменяет стандартный AI на кастомный"""
    return CustomAI(difficulty)

# РЕГИСТРАЦИЯ ХУКОВ
HOOK_REGISTRY = {{
    'ai_creation': on_ai_creation,
}}
'''

    def get_hook_template(self):
        """Шаблон мода с хуками"""
        return '''"""
МОД ХУКОВ: {mod_name}
Автор: Ваше имя
Версия: 1.0.0
Описание: Мод с примерами различных хуков
"""

def mod_initialize(hook_system):
    """Инициализация мода"""
    print(f"✅ Мод хуков '{{mod_name}}' загружен!")
    return True

# ХУКИ ИГРОКА
def on_player_created(player, hook_system):
    """Вызывается при создании игрока"""
    if player and hasattr(player, 'damage'):
        player.damage += 1
        player.health_max += 5
        print(f"💪 Мод {{mod_name}}: Игрок усилен!")

def on_player_level_up(player, old_level, new_level, hook_system):
    """Вызывается при повышении уровня игрока"""
    print(f"🎯 Мод {{mod_name}}: Игрок достиг уровня {{new_level}}!")

# ХУКИ БИТВЫ
def on_battle_start(player, enemy, mode, hook_system):
    """Вызывается в начале битвы"""
    print(f"⚔️ Мод {{mod_name}}: Началась битва с {{enemy.name}}!")

def on_damage_calculation(attacker, defender, base_damage, element, is_critical, hook_system):
    """Вызывается при расчете урона"""
    # Увеличиваем урон на 10%
    return int(base_damage * 1.1)

def on_battle_end(player, enemy, result, hook_system):
    """Вызывается в конце битвы"""
    if result == 'player_win':
        print(f"🎉 Мод {{mod_name}}: Игрок победил!")
    else:
        print(f"💀 Мод {{mod_name}}: Игрок проиграл...")

# ХУКИ ВРАГОВ
def on_enemy_creation(enemy, difficulty, hook_system):
    """Вызывается при создании врага"""
    if enemy and hasattr(enemy, 'health_max'):
        # Усиливаем боссов
        if 'boss' in enemy.difficulty.lower():
            enemy.health_max += 20
            enemy.damage += 3
            print(f"👹 Мод {{mod_name}}: Босс усилен!")

# РЕГИСТРАЦИЯ ХУКОВ
HOOK_REGISTRY = {{
    'player_created': on_player_created,
    'player_level_up': on_player_level_up,
    'battle_start': on_battle_start,
    'damage_calculation': on_damage_calculation,
    'battle_end': on_battle_end,
    'enemy_creation': on_enemy_creation,
}}
'''

    def get_item_template(self):
        """Шаблон мода предметов"""
        return '''"""
МОД ПРЕДМЕТОВ: {mod_name}
Автор: Ваше имя
Версия: 1.0.0
Описание: Мод для добавления кастомных предметов
"""

# КАСТОМНЫЕ ПРЕДМЕТЫ
CUSTOM_ITEMS = {{
    "magic_sword": {{
        "name": "🪄 Магический меч",
        "damage_bonus": 5,
        "health_bonus": 10,
        "description": "Меч, усиленный магией"
    }},
    "healing_potion": {{
        "name": "❤️ Сильное зелье лечения",
        "heal_amount": 15,
        "description": "Восстанавливает 15 HP"
    }}
}}

def mod_initialize(hook_system):
    """Инициализация мода предметов"""
    print(f"✅ Мод предметов '{{mod_name}}' загружен!")
    return True

def on_item_use(player, item_type, target, hook_system):
    """Обработка использования кастомных предметов"""
    if item_type in CUSTOM_ITEMS:
        item = CUSTOM_ITEMS[item_type]

        if "damage_bonus" in item:
            player.damage += item["damage_bonus"]
            print(f"⚔️ Мод {{mod_name}}: {item['name'} увеличивает урон!")

        if "heal_amount" in item:
            player.health = min(player.health + item["heal_amount"], player.health_max)
            print(f"❤️ Мод {{mod_name}}: {item['name'} восстанавливает здоровье!")

        return True  # Предотвратить стандартную обработку

    return False  # Продолжить стандартную обработку

def on_item_purchase(player, item_type, cost, hook_system):
    """Обработка покупки предметов"""
    if item_type in CUSTOM_ITEMS:
        # Уменьшаем стоимость кастомных предметов
        return cost * 0.8  # 20% скидка

    return cost

# РЕГИСТРАЦИЯ ХУКОВ
HOOK_REGISTRY = {{
    'item_use': on_item_use,
    'item_purchase': on_item_purchase,
}}
'''

    def get_enemy_template(self):
        """Шаблон мода врагов"""
        return '''"""
МОД ВРАГОВ: {mod_name}
Автор: Ваше имя
Версия: 1.0.0
Описание: Мод для добавления новых врагов
"""

from src.entities.enemy import Enemy
import random

# КАСТОМНЫЕ ВРАГИ
CUSTOM_ENEMIES = {{
    'dark_knight': Enemy("⚔️ Тёмный рыцарь", 35, 35, 4, 5, 'rare', random.randint(15, 25)),
    'fire_mage': Enemy("🔥 Огненный маг", 25, 25, 6, 2, 'rare', random.randint(20, 30)),
    'ice_golem': Enemy("❄️ Ледяной голем", 45, 45, 3, 8, 'epic', random.randint(30, 40))
}}

def mod_initialize(hook_system):
    """Инициализация мода врагов"""
    print(f"✅ Мод врагов '{{mod_name}}' загружен!")
    return True

def on_enemy_creation(enemy, difficulty, hook_system):
    """Добавляет кастомных врагов в пул"""
    # Иногда заменяем стандартного врага на кастомного
    if random.random() < 0.3:  # 30% шанс
        custom_enemy = random.choice(list(CUSTOM_ENEMIES.values()))
        return custom_enemy

    return enemy

def on_battle_start(player, enemy, mode, hook_system):
    """Специальные эффекты для кастомных врагов"""
    if enemy.name == "⚔️ Тёмный рыцарь":
        print("🛡️ Тёмный рыцарь излучает ауру страха!")
    elif enemy.name == "🔥 Огненный маг":
        print("🔥 Огненный маг окружает себя пламенем!")
    elif enemy.name == "❄️ Ледяной голем":
        print("❄️ Ледяной голем замораживает воздух вокруг!")

# РЕГИСТРАЦИЯ ХУКОВ
HOOK_REGISTRY = {{
    'enemy_creation': on_enemy_creation,
    'battle_start': on_battle_start,
}}
'''

    def create_project_from_template(self, project_name: str, project_path: str, template_name: str = "basic") -> bool:
        """Создание проекта из шаблона"""
        try:
            project_manager = ProjectManager()
            success = project_manager.create_project(project_name, project_path, template_name)

            if success:
                settings.log_info(f"✅ Проект '{project_name}' создан из шаблона '{template_name}'")
                return True
            else:
                settings.log_error(f"❌ Не удалось создать проект '{project_name}'")
                return False

        except Exception as e:
            settings.log_error(f"❌ Ошибка создания проекта из шаблона: {e}")
            print_exc()
            return False


class TemplateDialog(QDialog):
    """Диалог выбора шаблона"""

    def __init__(self, templates, project_name, parent=None):
        super().__init__(parent)

        self.templates = templates
        self.project_name = project_name
        self.selected_template = None

        self.setup_ui()

    def setup_ui(self):
        """Настройка UI диалога"""
        self.setWindowTitle("Выбор шаблона мода")
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout(self)

        # Заголовок
        title_label = QLabel("Выберите шаблон для нового мода")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title_label)

        # Сплиттер для списка шаблонов и пред просмотра
        splitter = QSplitter(Qt.Horizontal)

        # Список шаблонов
        self.template_list = QListWidget()
        self.template_list.currentItemChanged.connect(self.on_template_selected) # type: ignore

        # Заполнение списка шаблонов
        categories = {}
        for template_id, template_info in self.templates.items():
            category = template_info.get('category', 'Другие')
            if category not in categories:
                categories[category] = []
            categories[category].append((template_id, template_info))

        for category, templates_in_category in categories.items():
            # Добавляем заголовок категории
            category_item = QListWidgetItem(category)
            category_item.setFlags(category_item.flags() & ~Qt.ItemIsSelectable)
            category_item.setBackground(Qt.gray)
            self.template_list.addItem(category_item)

            # Добавляем шаблоны категории
            for template_id, template_info in templates_in_category:
                item = QListWidgetItem(template_info['name'])
                item.setData(Qt.UserRole, template_id)
                self.template_list.addItem(item)

        # Область предпросмотра
        preview_layout = QVBoxLayout()

        preview_title = QLabel("Описание шаблона")
        preview_title.setStyleSheet("font-weight: bold;")
        preview_layout.addWidget(preview_title)

        self.preview_description = QTextEdit()
        self.preview_description.setReadOnly(True)
        self.preview_description.setMaximumHeight(150)
        preview_layout.addWidget(self.preview_description)

        preview_title2 = QLabel("Предпросмотр кода")
        preview_title2.setStyleSheet("font-weight: bold;")
        preview_layout.addWidget(preview_title2)

        self.preview_code = QTextEdit()
        self.preview_code.setReadOnly(True)
        self.preview_code.setFontFamily("Consolas")
        preview_layout.addWidget(self.preview_code)

        preview_widget = QWidget()
        preview_widget.setLayout(preview_layout)

        splitter.addWidget(self.template_list)
        splitter.addWidget(preview_widget)
        splitter.setSizes([250, 450])

        layout.addWidget(splitter)

        # Кнопки
        button_layout = QHBoxLayout()

        self.create_button = QPushButton("Создать мод")
        self.create_button.clicked.connect(self.accept)  # type: ignore
        self.create_button.setEnabled(False)

        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)  # type: ignore

        button_layout.addWidget(self.create_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # Выбираем первый шаблон
        if self.template_list.count() > 1:
            self.template_list.setCurrentRow(1)

    def on_template_selected(self, current, previous):
        """Обработчик выбора шаблона"""
        if current and current.data(Qt.UserRole):
            template_id = current.data(Qt.UserRole)
            template_info = self.templates.get(template_id)

            if template_info:
                self.selected_template = template_id

                # Обновляем описание
                self.preview_description.setText(template_info['description'])

                # Обновляем предпросмотр кода
                code_content = template_info['file_content']
                if self.project_name:
                    code_content = code_content.format(mod_name=self.project_name)
                self.preview_code.setText(code_content)

                self.create_button.setEnabled(True)

    def get_selected_template(self):
        """Получение выбранного шаблона"""
        return self.selected_template

    def get_template_content(self):
        """Получение содержимого выбранного шаблона"""
        if self.selected_template:
            template_info = self.templates.get(self.selected_template)
            if template_info:
                content = template_info['file_content']
                if self.project_name:
                    content = content.format(mod_name=self.project_name)
                return content
        return ""



# [file name]: src/entities/player.py
from json import dump, load
from os import makedirs, path
from traceback import print_exc
from typing import Dict, Any
from classes_entities.skill_tree import skill_tree_manager
from elemental_source.elemental_integration import elemental_integration
from modding.support_mods import hook_system
from elemental_source.elemental_core import ElementType
from classes_entities.classes_core import ClassType, class_system
from utils.helpers_def import clear_console_def
from settings.settings_manager import settings


class Player:

    def __init__(self, name="Игрок", health=20, health_max=20, health_repair=2, damage=3, shield_hp=2, potions=None, coin=0):
        self.name = name
        self.health = health
        self.health_max = health_max
        self.health_repair = health_repair
        self.damage = damage
        self.shield_hp = shield_hp
        self.potions = potions if potions is not None else []
        self.coin = coin
        self.level = 1
        self.experience = 0

        self.player_stats = {
            'battles_won': 0,
            'battles_lost': 0,
            'total_coins_earned': 0,
            'total_damage_dealt': 0,
            'total_healing_done': 0,
            'max_damage_single_battle': 0,
            'max_health': health_max,
            'items_purchased': 0,
            'mystery_box_bonus': False,
            'boss_no_damage': False,
            'classes_used': set(),
            'abilities_used': set(),
            'elements_used': set(),
            'elemental_damage': {}
        }

        self.has_achievement_visibility = False
        self.achievement_visibility = False

        # ЭЛЕМЕНТАЛЬНАЯ СИСТЕМА
        self.element = ElementType.NONE
        self.element_data = None
        self.elemental_resistance = 1.0

        # СИСТЕМА КЛАССОВ
        self.player_class = ClassType.NONE
        self.class_data = None
        self.mana = 10
        self.mana_max = 10
        self.abilities = []
        self.active_effects = []

        # ДЕРЕВО НАВЫКОВ
        self.skill_tree = None
        self.skill_points = 0

        # Хук создания игрока
        hook_system.execute_hook('player_created', self)

    def set_element(self, element_type: ElementType):
        """Устанавливает элемент игроку"""
        elemental_integration.apply_to_entity(self, element_type)

        # Записываем использование элемента
        self.player_stats['elements_used'].add(element_type.value)

        print(f"🎯 {self.name} теперь использует {self.element_data.name}!")

    def get_element_info(self) -> Dict[str, Any]:
        """Получает информацию об элементе игрока"""
        return elemental_integration.get_entity_element_info(self)

    def set_class(self, class_type: ClassType):
        """Устанавливает класс игроку (БЕЗОПАСНАЯ ВЕРСИЯ)"""
        try:
            settings.log_info(f"🎯 Попытка установить класс: {class_type}")

            # Используем улучшенный поиск класса
            class_data = class_system.get_class(class_type)
            if not class_data:
                settings.log_error(f"❌ Ошибка: класс {class_type} не найден в системе!")
                return

            # Если класс найден, устанавливаем его
            self.player_class = class_type
            self.class_data = class_data

            settings.log_info(f"🎯 Найден класс: {self.class_data.name}")

            # Применяем базовые характеристики класса
            class_stats = self.class_data.get_stats_at_level(self.level)
            self.health_max = class_stats['health']
            self.health = self.health_max
            self.damage = class_stats['damage']
            self.mana_max = class_stats['mana']
            self.mana = self.mana_max

            # Устанавливаем предпочитаемый элемент
            elemental_integration.apply_to_entity(self, self.class_data.preferred_element)

            # Загружаем дерево навыков
            self.skill_tree = skill_tree_manager.get_tree(class_type)

            # Обновляем доступные способности
            self.abilities = class_system.get_available_abilities(class_type, self.level)

            # БЕЗОПАСНАЯ ЗАПИСЬ ИСПОЛЬЗОВАНИЯ КЛАССА
            if 'classes_used' not in self.player_stats:
                self.player_stats['classes_used'] = set()
            self.player_stats['classes_used'].add(class_type.value)

            print(f"🎯 {self.name} теперь {self.class_data.name}!")
            print(f"📊 Характеристики: ❤️ {self.health_max} ⚔️ {self.damage} 🔮 {self.mana_max}")

        except Exception as e:
            settings.log_error(f"❌ Критическая ошибка при установке класса: {e}")
            print_exc()
            # Восстанавливаем состояние при ошибке
            self.player_class = ClassType.NONE
            self.class_data = None
            self.abilities = []
            self.skill_tree = None

    def use_ability(self, ability_index: int, target=None) -> Dict[str, Any]:
        """Использует способность класса"""
        if ability_index < 0 or ability_index >= len(self.abilities):
            return {'success': False, 'message': '❌ Неверный индекс способности'}

        ability = self.abilities[ability_index]

        # Проверяем ману
        if self.mana < ability.mana_cost:
            return {'success': False, 'message': '❌ Недостаточно маны'}

        # Проверяем уровень
        if self.level < ability.level_required:
            return {'success': False, 'message': '❌ Недостаточный уровень'}

        # Используем ману
        self.mana -= ability.mana_cost

        # Записываем использование способности
        self.player_stats['abilities_used'].add(ability.name)

        # Хук использования способности
        result = hook_system.execute_hook(
            'ability_used',
            self, ability, target
        )

        if result is not None:
            return result

        # Базовая реализация эффектов способности
        effect_result = {
            'success': True,
            'message': f"🎯 {self.name} использует {ability.icon} {ability.name}!",
            'ability': ability,
            'effect_type': ability.effect_type,
            'power': ability.power
        }

        return effect_result

    def add_skill_point(self):
        """Добавляет очко навыков при повышении уровня"""
        self.skill_points += 1
        if self.skill_tree:
            self.skill_tree.add_skill_points(1)

        print(f"🎯 Получено очко навыков! Всего: {self.skill_points}")

    def apply_skill_effects(self):
        """Применяет эффекты дерева навыков к игроку"""
        if not self.skill_tree:
            return

        effects = self.skill_tree.get_node_effects()

        for effect_key, effect_value in effects.items():
            if effect_key == 'health_bonus':
                self.health_max += effect_value
                self.health = min(self.health, self.health_max)
            elif effect_key == 'damage_bonus':
                self.damage += effect_value
            elif effect_key == 'elemental_damage_bonus':
                # Этот эффект будет применяться в расчетах урона
                pass

    def check_level_up(self):
        """Проверяет повышение уровня с учетом классов"""
        exp_needed = self.calculate_exp_for_level(self.level + 1)
        if self.experience >= exp_needed:
            self.level += 1
            print(f"🎉 Уровень повышен! Теперь у вас {self.level} уровень!")

            # Добавляем очко навыков
            self.add_skill_point()

            # Обновляем характеристики класса
            if self.player_class != ClassType.NONE:
                class_stats = self.class_data.get_stats_at_level(self.level)
                self.health_max = class_stats['health']
                self.mana_max = class_stats['mana']
                self.health = self.health_max  # Восстанавливаем здоровье
                self.mana = self.mana_max      # Восстанавливаем ману

                # Обновляем доступные способности
                self.abilities = class_system.get_available_abilities(self.player_class, self.level)

            # Хук повышения уровня
            hook_system.execute_hook('player_level_up', self)

    def calculate_exp_for_level(self, level):
        """Рассчитывает необходимый опыт для уровня"""
        return int(100 * (1.5 ** (level - 1)))

    def add_experience(self, exp_amount):
        """Добавляет опыт игроку"""
        self.experience += exp_amount
        print(f"📈 Получено {exp_amount} опыта!")
        self.check_level_up()

    def add_coins(self, amount):
        """Добавляет монеты игроку"""
        self.coin += amount
        self.player_stats['total_coins_earned'] += amount
        print(f"💰 Получено {amount} монет!")

    def use_potion(self):
        """Использование зелья"""
        if self.potions:
            potion = self.potions.pop(0)
            self.health = min(self.health + 20, self.health_max)
            print(f"🧪 Использовано зелье! Здоровье: {self.health}/{self.health_max}")
            return True
        else:
            print("❌ Нет зелий!")
            return False

    def defend(self):
        """Защита - блокирует часть урона"""
        self.shield_hp += 5
        print(f"🛡️ Защита усилена! Щит: {self.shield_hp}")

    def take_damage(self, damage):
        """Получение урона с учетом щита"""
        # Сначала урон поглощается щитом
        shield_damage = min(damage, self.shield_hp)
        remaining_damage = damage - shield_damage

        self.shield_hp -= shield_damage
        self.health -= remaining_damage

        # Обновляем максимальное здоровье в статистике
        if self.health_max > self.player_stats['max_health']:
            self.player_stats['max_health'] = self.health_max

        # Хук получения урона
        hook_system.execute_hook('player_stat_update', self)

        return {
            'shield_damage': shield_damage,
            'health_damage': remaining_damage,
            'total_damage': damage
        }

    def heal(self):
        """Лечение - восстанавливает здоровье"""
        heal_amount = min(self.health_repair, self.health_max - self.health)
        self.health += heal_amount
        self.player_stats['total_healing_done'] += heal_amount
        print(f"❤️ Восстановлено {heal_amount} здоровья! Здоровье: {self.health}/{self.health_max}")

        # Хук лечения
        hook_system.execute_hook('player_stat_update', self)

        return heal_amount

    def is_alive(self):
        """Проверяет, жив ли игрок"""
        return self.health > 0

    def record_stat(self, stat_name, value):
        """Записывает статистику для достижений"""
        if stat_name in self.player_stats:
            if isinstance(self.player_stats[stat_name], (int, float)):
                self.player_stats[stat_name] += value
            elif isinstance(self.player_stats[stat_name], set):
                self.player_stats[stat_name].add(value)
            elif isinstance(self.player_stats[stat_name], bool):
                self.player_stats[stat_name] = value
            elif isinstance(self.player_stats[stat_name], dict):
                if stat_name == 'elemental_damage':
                    if value in self.player_stats[stat_name]:
                        self.player_stats[stat_name][value] += 1
                    else:
                        self.player_stats[stat_name][value] = 1

    def has_class(self):
        """Проверяет, есть ли у игрока класс"""
        return self.player_class != ClassType.NONE and self.class_data is not None

    def to_dict(self):
        """Преобразует игрока в словарь для сохранения"""
        serializable_stats = self.player_stats.copy()
        for key in ['classes_used', 'abilities_used', 'elements_used']:
            if key in serializable_stats and isinstance(serializable_stats[key], set):
                serializable_stats[key] = list(serializable_stats[key])

        data = {
            "name": self.name,
            "health": self.health,
            "health_max": self.health_max,
            "health_repair": self.health_repair,
            "damage": self.damage,
            "shield_hp": self.shield_hp,
            "potions": self.potions,
            "coin": self.coin,
            "level": self.level,
            "experience": self.experience,
            "player_stats": serializable_stats,
            "has_achievement_visibility": self.has_achievement_visibility,
            "achievement_visibility": self.achievement_visibility,
            "element": self.element.value if hasattr(self, 'element') else "none",
            "elemental_resistance": getattr(self, 'elemental_resistance', 1.0),
            "player_class": self.player_class.value if hasattr(self, 'player_class') else "none",
            "mana": getattr(self, 'mana', 10),
            "mana_max": getattr(self, 'mana_max', 10),
            "skill_points": getattr(self, 'skill_points', 0),
            "unlocked_abilities": [ability.name for ability in getattr(self, 'abilities', [])],
        }

        if hasattr(self, 'skill_tree') and self.skill_tree:
            data['skill_tree'] = {
                'unlocked_nodes': self.skill_tree.unlocked_nodes,
                'skill_points': self.skill_tree.skill_points,
                'nodes_state': {node_id: node.current_level
                                for node_id, node in self.skill_tree.nodes.items()}
            }

        return data

    @classmethod
    def from_dict(cls, data):
        """Создает игрока из словаря"""
        player = cls(
            name=data.get("name", "Игрок"),
            health=data.get("health", 20),
            health_max=data.get("health_max", 20),
            health_repair=data.get("health_repair", 2),
            damage=data.get("damage", 3),
            shield_hp=data.get("shield_hp", 2),
            potions=data.get("potions", []),
            coin=data.get("coin", 0)
        )

        player.level = data.get("level", 1)
        player.experience = data.get("experience", 0)
        player_stats_data = data.get("player_stats", {})
        player_stats = {}
        default_stats = {
            'battles_won': 0,
            'battles_lost': 0,
            'total_coins_earned': 0,
            'total_damage_dealt': 0,
            'total_healing_done': 0,
            'max_damage_single_battle': 0,
            'max_health': player.health_max,
            'items_purchased': 0,
            'mystery_box_bonus': False,
            'boss_no_damage': False,
            'classes_used': set(),
            'abilities_used': set(),
            'elements_used': set(),
            'elemental_damage': {}
        }

        for key, default_value in default_stats.items():
            if key in player_stats_data:
                if key in ['classes_used', 'abilities_used', 'elements_used']:
                    if isinstance(player_stats_data[key], list):
                        player_stats[key] = set(player_stats_data[key])
                    else:
                        player_stats[key] = set()
                else:
                    player_stats[key] = player_stats_data[key]
            else:
                player_stats[key] = default_value

        player.has_achievement_visibility = data.get("has_achievement_visibility", False)
        player.achievement_visibility = data.get("achievement_visibility", False)

        element_value = data.get("element", "none")
        player.element = ElementType(element_value)
        player.elemental_resistance = data.get("elemental_resistance", 1.0)

        # Применяем элемент
        elemental_integration.apply_to_entity(player, player.element)

        # ЗАГРУЖАЕМ ДАННЫЕ КЛАССА
        class_value = data.get("player_class", "none")
        player.player_class = ClassType(class_value)
        player.mana = data.get("mana", 10)
        player.mana_max = data.get("mana_max", 10)
        player.skill_points = data.get("skill_points", 0)

        # Восстанавливаем класс если он установлен
        if player.player_class != ClassType.NONE:
            player.set_class(player.player_class)

            # Восстанавливаем дерево навыков
            skill_tree_data = data.get('skill_tree', {})
            if skill_tree_data and player.skill_tree:
                player.skill_tree.unlocked_nodes = skill_tree_data.get('unlocked_nodes', [])
                player.skill_tree.skill_points = skill_tree_data.get('skill_points', 0)

                # Восстанавливаем состояние узлов
                nodes_state = skill_tree_data.get('nodes_state', {})
                for node_id, level in nodes_state.items():
                    if node_id in player.skill_tree.nodes:
                        player.skill_tree.nodes[node_id].current_level = level

        return player

    def display_stats(self):
        """Отображает статистику игрока"""
        clear_console_def(1, 0)
        print(f"\n📊 СТАТИСТИКА {self.name}:")
        print(f"❤️ Здоровье: {self.health}/{self.health_max}")
        print(f"⚔️ Урон: {self.damage}")
        print(f"🛡️ Щит: {self.shield_hp}")
        print(f"🔮 Мана: {self.mana}/{self.mana_max}")
        print(f"💰 Монеты: {self.coin}")
        print(f"🎯 Уровень: {self.level}")
        print(f"⭐ Опыт: {self.experience}/{self.calculate_exp_for_level(self.level + 1)}")
        print("🧪 Зелья:", len(self.potions))

        # Информация о классе (с проверкой на None)
        if self.has_class():
            print(f"🎯 Класс: {self.class_data.icon} {self.class_data.name}")
            print(f"🎯 Элемент: {self.element_data.icon} {self.element_data.name}")
        else:
            print(f"🎯 Класс: ❌ Не выбран")

        # Информация о навыках
        if hasattr(self, 'skill_points') and self.skill_points > 0:
            print(f"🌟 Очки навыков: {self.skill_points}")

        # Статистика достижений
        print(f"\n🏆 СТАТИСТИКА ДОСТИЖЕНИЙ:")
        print(f"⚔️ Побед: {self.player_stats['battles_won']}")
        print(f"💀 Поражений: {self.player_stats['battles_lost']}")
        print(f"💰 Всего монет: {self.player_stats['total_coins_earned']}")
        print(f"💥 Макс. урон: {self.player_stats['max_damage_single_battle']}")
        print(f"❤️ Макс. здоровье: {self.player_stats['max_health']}")
        print(f"🛒 Куплено предметов: {self.player_stats['items_purchased']}")

        # Информация о трекере достижений
        print(f"\n🔮 ТРЕКЕР ДОСТИЖЕНИЙ:")
        print(f"   Видимость: {'✅ ВКЛ' if self.achievement_visibility else '❌ ВЫКЛ'}")
        print(f"   Атрибут: {'✅ Установлен' if self.has_achievement_visibility else '❌ Отсутствует'}")

        # Элементальная статистика
        if self.player_stats['elemental_damage']:
            print(f"\n🔮 ЭЛЕМЕНТАЛЬНЫЙ УРОН:")
            for element, damage in self.player_stats['elemental_damage'].items():
                print(f"   {element}: {damage} урона")


def safe_stat_add(self, stat_name, value):
    """Безопасно добавляет значение в статистику"""
    if stat_name not in self.player_stats:
        # Автоматически создаем нужный тип данных
        if stat_name in ['classes_used', 'abilities_used', 'elements_used']:
            self.player_stats[stat_name] = set()
        elif stat_name in ['elemental_damage']:
            self.player_stats[stat_name] = {}
        else:
            self.player_stats[stat_name] = 0

    # Добавляем значение
    if isinstance(self.player_stats[stat_name], set):
        self.player_stats[stat_name].add(value)
    elif isinstance(self.player_stats[stat_name], dict):
        if value in self.player_stats[stat_name]:
            self.player_stats[stat_name][value] += 1
        else:
            self.player_stats[stat_name][value] = 1
    elif isinstance(self.player_stats[stat_name], (int, float)):
        self.player_stats[stat_name] += value

def is_alive(self):
    """Проверяет, жив ли игрок"""
    return self.health > 0

@property
def isAlive(self):
    """Совместимость с кодом, который использует isAlive (будет убран позже)"""
    return self.is_alive()

def safe_stat_get(self, stat_name, default=None):
    """Безопасно получает значение из статистики"""
    return self.player_stats.get(stat_name, default)

def save_player_data(player):
    """Сохранение данных игрока"""
    try:
        makedirs("src/saves/players", exist_ok=True)
        file_path = "src/saves/players/player_data.json"

        # Хук перед сохранением
        hook_system.execute_hook('pre_save_game', player)

        with open(file_path, 'w', encoding='utf-8') as f:
            dump(player.to_dict(), f, indent=2, ensure_ascii=False)

        # Хук после сохранения
        hook_system.execute_hook('post_save_game', player)

        return True
    except Exception as e:
        settings.log_error(f"❌ Ошибка сохранения: {e}")
        return False


def load_player_data():
    """Загрузка данных игрока"""
    try:
        file_path = "src/saves/players/player_data.json"

        if not path.exists(file_path):
            return None

        # Хук перед загрузкой
        hook_system.execute_hook('pre_load_game')

        with open(file_path, 'r', encoding='utf-8') as f:
            data = load(f)

        player = Player.from_dict(data)

        # Хук после загрузки
        hook_system.execute_hook('post_load_game', player)

        return player
    except Exception as e:
        settings.log_error(f"❌ Ошибка загрузки: {e}")
        return None


def set_class(self, class_type: ClassType):
    """Устанавливает класс игроку (БЕЗОПАСНАЯ ВЕРСИЯ)"""
    try:
        settings.log_info(f"🎯 Попытка установить класс: {class_type}")

        # Используем улучшенный поиск класса
        class_data = class_system.get_class(class_type)
        if not class_data:
            settings.log_error(f"❌ Ошибка: класс {class_type} не найден в системе!")
            return

        # Если класс найден, устанавливаем его
        self.player_class = class_type
        self.class_data = class_data

        settings.log_info(f"🎯 Найден класс: {self.class_data.name}")

        # Применяем базовые характеристики класса
        class_stats = self.class_data.get_stats_at_level(self.level)
        self.health_max = class_stats['health']
        self.health = self.health_max
        self.damage = class_stats['damage']
        self.mana_max = class_stats['mana']
        self.mana = self.mana_max

        # Устанавливаем предпочитаемый элемент
        elemental_integration.apply_to_entity(self, self.class_data.preferred_element)
        self.skill_tree = skill_tree_manager.get_tree(class_type)
        self.abilities = class_system.get_available_abilities(class_type, self.level)
        self.safe_stat_add('classes_used', class_type.value)

        print(f"🎯 {self.name} теперь {self.class_data.name}!")
        print(f"📊 Характеристики: ❤️ {self.health_max} ⚔️ {self.damage} 🔮 {self.mana_max}")

    except Exception as e:
        settings.log_error(f"❌ Критическая ошибка при установке класса: {e}")
        print_exc()
        # Восстанавливаем состояние при ошибке
        self.player_class = ClassType.NONE
        self.class_data = None
        self.abilities = []
        self.skill_tree = None


def record_stat(self, stat_name, value):
    """Записывает статистику для достижений (БЕЗОПАСНАЯ ВЕРСИЯ)"""
    self.safe_stat_add(stat_name, value)
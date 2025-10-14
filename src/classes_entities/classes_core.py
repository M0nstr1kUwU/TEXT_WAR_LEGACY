# [file name]: src/classes_entities/classes_core.py
from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass
from elemental_source.elemental_core import ElementType
from settings.settings_manager import settings


class ClassType(Enum):
    """Типы классов"""
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    PALADIN = "paladin"
    HUNTER = "hunter"
    NECROMANCER = "necromancer"
    ELEMENTALIST = "elementalist"
    NONE = "none"


@dataclass
class ClassAbility:
    """Способность класса"""
    name: str
    description: str
    icon: str
    level_required: int
    mana_cost: int = 0
    cooldown: int = 0
    effect_type: str = "buff"  # buff, damage, heal, summon
    power: int = 0


@dataclass
class GameClass:
    """Игровой класс"""
    class_type: ClassType
    name: str
    description: str
    icon: str
    base_health: int
    base_damage: int
    base_mana: int
    preferred_element: ElementType
    abilities: List[ClassAbility]
    stat_growth: Dict[str, float]  # Рост характеристик за уровень

    def get_stats_at_level(self, level: int) -> Dict[str, Any]:
        """Получает характеристики на определенном уровне"""
        health = self.base_health + (self.stat_growth.get('health', 5) * (level - 1))
        damage = self.base_damage + (self.stat_growth.get('damage', 1) * (level - 1))
        mana = self.base_mana + (self.stat_growth.get('mana', 3) * (level - 1))

        return {
            'health': health,
            'damage': damage,
            'mana': mana
        }


class ClassSystem:
    """Система управления классами"""

    def __init__(self):
        self.classes: Dict[ClassType, GameClass] = {}
        self.load_default_classes()

        if ClassType.ELEMENTALIST not in self.classes:
            settings.log_warning("⚠️ Elementalist не загружен, принудительно перезагружаем...")
            self.load_default_classes()

    def load_default_classes(self):
        """Загрузка стандартных классов"""
        default_classes = [
            GameClass(
                class_type=ClassType.WARRIOR,
                name="⚔️ Воин",
                description="Сильный боец ближнего боя с высокой выживаемостью",
                icon="⚔️",
                base_health=30,
                base_damage=5,
                base_mana=10,
                preferred_element=ElementType.NONE,
                abilities=[
                    ClassAbility(
                        name="💥 Мощный удар",
                        description="Наносит двойной урон следующей атакой",
                        icon="💥",
                        level_required=1,
                        mana_cost=5,
                        cooldown=3,
                        effect_type="buff",
                        power=2
                    ),
                    ClassAbility(
                        name="🛡️ Железная воля",
                        description="Увеличивает защиту на 50% на 2 хода",
                        icon="🛡️",
                        level_required=3,
                        mana_cost=8,
                        cooldown=4,
                        effect_type="buff",
                        power=0
                    )
                ],
                stat_growth={'health': 8, 'damage': 2, 'mana': 2}
            ),
            GameClass(
                class_type=ClassType.MAGE,
                name="🔮 Маг",
                description="Мастер магии с мощными заклинаниями",
                icon="🔮",
                base_health=20,
                base_damage=8,
                base_mana=25,
                preferred_element=ElementType.FIRE,
                abilities=[
                    ClassAbility(
                        name="🔥 Огненный шар",
                        description="Наносит огненный урон с шансом поджога",
                        icon="🔥",
                        level_required=1,
                        mana_cost=10,
                        cooldown=2,
                        effect_type="damage",
                        power=15
                    ),
                    ClassAbility(
                        name="❄️ Ледяная броня",
                        description="Создает ледяной щит, снижающий получаемый урон",
                        icon="❄️",
                        level_required=3,
                        mana_cost=12,
                        cooldown=5,
                        effect_type="buff",
                        power=0
                    )
                ],
                stat_growth={'health': 4, 'damage': 3, 'mana': 6}
            ),
            GameClass(
                class_type=ClassType.ROGUE,
                name="🗡️ Разбойник",
                description="Проворный боец с высоким уроном и критическими ударами",
                icon="🗡️",
                base_health=22,
                base_damage=7,
                base_mana=15,
                preferred_element=ElementType.SHADOW,
                abilities=[
                    ClassAbility(
                        name="🎯 Смертельный удар",
                        description="Высокий шанс критического удара",
                        icon="🎯",
                        level_required=1,
                        mana_cost=6,
                        cooldown=3,
                        effect_type="damage",
                        power=12
                    ),
                    ClassAbility(
                        name="👻 Теневой шаг",
                        description="Уклонение от следующей атаки",
                        icon="👻",
                        level_required=3,
                        mana_cost=8,
                        cooldown=4,
                        effect_type="buff",
                        power=0
                    )
                ],
                stat_growth={'health': 5, 'damage': 3, 'mana': 3}
            ),
            GameClass(
                class_type=ClassType.PALADIN,
                name="🛡️ Паладин",
                description="Святой воин с балансом атаки и защиты",
                icon="🛡️",
                base_health=28,
                base_damage=4,
                base_mana=18,
                preferred_element=ElementType.LIGHT,
                abilities=[
                    ClassAbility(
                        name="✨ Божественное исцеление",
                        description="Восстанавливает здоровье себе или союзнику",
                        icon="✨",
                        level_required=1,
                        mana_cost=10,
                        cooldown=3,
                        effect_type="heal",
                        power=12
                    ),
                    ClassAbility(
                        name="🛡️ Щит веры",
                        description="Создает мощный щит, поглощающий урон",
                        icon="🛡️",
                        level_required=3,
                        mana_cost=15,
                        cooldown=5,
                        effect_type="buff",
                        power=0
                    )
                ],
                stat_growth={'health': 7, 'damage': 2, 'mana': 4}
            ),
            GameClass(
                class_type=ClassType.HUNTER,
                name="🏹 Охотник",
                description="Мастер дальнего боя и ловушек",
                icon="🏹",
                base_health=24,
                base_damage=6,
                base_mana=12,
                preferred_element=ElementType.NATURE,
                abilities=[
                    ClassAbility(
                        name="🎯 Меткий выстрел",
                        description="Высокий урон с увеличенным шансом крита",
                        icon="🎯",
                        level_required=1,
                        mana_cost=8,
                        cooldown=2,
                        effect_type="damage",
                        power=10
                    ),
                    ClassAbility(
                        name="🕸️ Опутывающая сеть",
                        description="Замедляет врага на 2 хода",
                        icon="🕸️",
                        level_required=3,
                        mana_cost=10,
                        cooldown=4,
                        effect_type="buff",
                        power=0
                    )
                ],
                stat_growth={'health': 6, 'damage': 3, 'mana': 3}
            ),
            GameClass(
                class_type=ClassType.NECROMANCER,
                name="💀 Некромант",
                description="Мастер темной магии и призыва мертвых",
                icon="💀",
                base_health=18,
                base_damage=7,
                base_mana=20,
                preferred_element=ElementType.SHADOW,
                abilities=[
                    ClassAbility(
                        name="💀 Призыв скелета",
                        description="Призывает скелета для помощи в бою",
                        icon="💀",
                        level_required=1,
                        mana_cost=12,
                        cooldown=5,
                        effect_type="summon",
                        power=1
                    ),
                    ClassAbility(
                        name="🩸 Кровавая жатва",
                        description="Крадет здоровье у врага",
                        icon="🩸",
                        level_required=3,
                        mana_cost=15,
                        cooldown=4,
                        effect_type="damage",
                        power=8
                    )
                ],
                stat_growth={'health': 4, 'damage': 2, 'mana': 5}
            ),
            GameClass(
                class_type=ClassType.ELEMENTALIST,
                name="🌪️ Элементалист",
                description="Мастер стихий с контролем над элементами",
                icon="🌪️",
                base_health=18,
                base_damage=6,
                base_mana=22,
                preferred_element=ElementType.AIR,
                abilities=[
                    ClassAbility(
                        name="🌪️ Смена стихии",
                        description="Меняет текущий элемент на более эффективный",
                        icon="🌪️",
                        level_required=1,
                        mana_cost=8,
                        cooldown=2,
                        effect_type="buff",
                        power=0
                    ),
                    ClassAbility(
                        name="⚡ Элементальный всплеск",
                        description="Наносит урон текущим элементом с бонусом",
                        icon="⚡",
                        level_required=3,
                        mana_cost=12,
                        cooldown=3,
                        effect_type="damage",
                        power=18
                    )
                ],
                stat_growth={'health': 5, 'damage': 2, 'mana': 5}
            )
        ]

        for game_class in default_classes:
            self.classes[game_class.class_type] = game_class
            settings.log_info(f"✅ Загружен класс: {game_class.name}")

    def get_available_abilities(self, class_type: ClassType, level: int) -> List[ClassAbility]:
        """Получает доступные способности для уровня"""
        game_class = self.get_class(class_type)
        if not game_class:
            return []
        return [ability for ability in game_class.abilities if ability.level_required <= level]

    def add_custom_class(self, class_data: Dict[str, Any]) -> bool:
        """Добавляет кастомный класс из мода"""
        try:
            class_type = ClassType(class_data['class_type'])

            if class_type in self.classes:
                return False  # Класс уже существует

            # Преобразуем данные способностей
            abilities = []
            for ability_data in class_data.get('abilities', []):
                abilities.append(ClassAbility(**ability_data))

            game_class = GameClass(
                class_type=class_type,
                name=class_data['name'],
                description=class_data['description'],
                icon=class_data['icon'],
                base_health=class_data['base_health'],
                base_damage=class_data['base_damage'],
                base_mana=class_data['base_mana'],
                preferred_element=ElementType(class_data['preferred_element']),
                abilities=abilities,
                stat_growth=class_data.get('stat_growth', {})
            )

            self.classes[class_type] = game_class
            return True

        except Exception as e:
            settings.log_error(f"❌ Ошибка добавления класса: {e}")
            return False

    def get_class(self, class_type):
        """Получает данные класса с проверкой"""
        settings.log_info(f"🔍 Поиск класса: {class_type} (тип: {type(class_type)})")
        settings.log_info(f"🔍 Доступные классы: {[ct.value for ct in self.classes.keys()]}")

        # ЯВНОЕ СРАВНЕНИЕ КЛЮЧЕЙ
        for key in self.classes.keys():
            if key == class_type:
                settings.log_info(f"✅ Класс найден через явное сравнение: {key}")
                return self.classes[key]

        # Альтернативный метод: сравнение по значению
        for key, value in self.classes.items():
            if key.value == class_type.value:
                settings.log_info(f"✅ Класс найден через сравнение значений: {key}")
                return value

        settings.log_error(f"❌ Класс {class_type} не найден в системе!")
        return None

    @staticmethod
    def ensure_all_classes_loaded():
        """Гарантирует, что все ожидаемые классы загружены"""
        expected_classes = [
            ClassType.WARRIOR, ClassType.MAGE, ClassType.ROGUE,
            ClassType.PALADIN, ClassType.HUNTER, ClassType.NECROMANCER,
            ClassType.ELEMENTALIST
        ]

        missing_classes = []
        for class_type in expected_classes:
            if class_type not in class_system.classes:
                missing_classes.append(class_type.value)

        if missing_classes:
            settings.log_error(f"⚠️ Отсутствующие классы: {missing_classes}")
            settings.log_info("🔄 Перезагружаем классы...")
            class_system.load_default_classes()

            # Повторная проверка
            still_missing = []
            for class_type in expected_classes:
                if class_type not in class_system.classes:
                    still_missing.append(class_type.value)

            if still_missing:
                settings.log_error(f"❌ Не удалось загрузить классы: {still_missing}")
            else:
                settings.log_info("✅ Все классы успешно загружены!")

        return len(missing_classes) == 0

# Глобальный экземпляр системы классов
class_system = ClassSystem()
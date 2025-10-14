# [file name]: src/elemental_source/elemental_core.py
from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass


class ElementType(Enum):
    """Типы элементов"""
    FIRE = "fire"
    WATER = "water"
    EARTH = "earth"
    AIR = "air"
    LIGHTNING = "lightning"
    ICE = "ice"
    NATURE = "nature"
    SHADOW = "shadow"
    LIGHT = "light"
    NONE = "none"


@dataclass
class Element:
    """Класс элемента"""
    element_type: ElementType
    name: str
    description: str
    icon: str
    strengths: List[ElementType]  # Против каких элементов силен
    weaknesses: List[ElementType]  # Против каких элементов слаб
    bonus_damage: float = 1.2
    resistance: float = 0.8

    def calculate_damage_multiplier(self, target_element: 'Element') -> float:
        """Рассчитывает множитель урона против цели"""
        multiplier = 1.0

        # Сильные стороны
        if target_element.element_type in self.strengths:
            multiplier *= self.bonus_damage
            print(f"💥 {self.name} эффективен против {target_element.name}! (+{int((self.bonus_damage - 1) * 100)}%)")

        # Слабые стороны
        if target_element.element_type in self.weaknesses:
            multiplier *= self.resistance
            print(f"🛡️ {self.name} неэффективен против {target_element.name}! (-{int((1 - self.resistance) * 100)}%)")

        # Хук расчета множителя урона
        hook_result = hook_system.execute_hook(
            'elemental_damage_multiplier',
            self, target_element, multiplier
        )
        return hook_result or multiplier


class ElementalSystem:
    """Система управления элементами"""

    def __init__(self):
        self.elements: Dict[ElementType, Element] = {}
        self.load_default_elements()

    def load_default_elements(self):
        """Загрузка стандартных элементов"""
        default_elements = [
            Element(
                element_type=ElementType.FIRE,
                name="🔥 Огонь",
                description="Стихия огня и пламени",
                icon="🔥",
                strengths=[ElementType.NATURE, ElementType.ICE],
                weaknesses=[ElementType.WATER, ElementType.EARTH],
                bonus_damage=1.3,
                resistance=0.7
            ),
            Element(
                element_type=ElementType.WATER,
                name="💧 Вода",
                description="Стихия воды и потоков",
                icon="💧",
                strengths=[ElementType.FIRE, ElementType.EARTH],
                weaknesses=[ElementType.LIGHTNING, ElementType.NATURE],
                bonus_damage=1.25,
                resistance=0.75
            ),
            Element(
                element_type=ElementType.EARTH,
                name="🌍 Земля",
                description="Стихия земли и камня",
                icon="🌍",
                strengths=[ElementType.LIGHTNING, ElementType.WATER],
                weaknesses=[ElementType.NATURE, ElementType.AIR],
                bonus_damage=1.2,
                resistance=0.8
            ),
            Element(
                element_type=ElementType.AIR,
                name="💨 Воздух",
                description="Стихия воздуха и ветра",
                icon="💨",
                strengths=[ElementType.NATURE, ElementType.EARTH],
                weaknesses=[ElementType.ICE, ElementType.LIGHTNING],
                bonus_damage=1.15,
                resistance=0.85
            ),
            Element(
                element_type=ElementType.LIGHTNING,
                name="⚡ Молния",
                description="Стихия молний и электричества",
                icon="⚡",
                strengths=[ElementType.WATER, ElementType.AIR],
                weaknesses=[ElementType.EARTH, ElementType.SHADOW],
                bonus_damage=1.4,
                resistance=0.6
            ),
            Element(
                element_type=ElementType.ICE,
                name="❄️ Лёд",
                description="Стихия льда и холода",
                icon="❄️",
                strengths=[ElementType.AIR, ElementType.NATURE],
                weaknesses=[ElementType.FIRE, ElementType.LIGHT],
                bonus_damage=1.25,
                resistance=0.75
            ),
            Element(
                element_type=ElementType.NATURE,
                name="🌿 Природа",
                description="Стихия природы и жизни",
                icon="🌿",
                strengths=[ElementType.EARTH, ElementType.WATER],
                weaknesses=[ElementType.FIRE, ElementType.ICE],
                bonus_damage=1.2,
                resistance=0.8
            ),
            Element(
                element_type=ElementType.SHADOW,
                name="🌑 Тень",
                description="Стихия тьмы и теней",
                icon="🌑",
                strengths=[ElementType.LIGHT, ElementType.LIGHTNING],
                weaknesses=[ElementType.LIGHT, ElementType.FIRE],
                bonus_damage=1.35,
                resistance=0.65
            ),
            Element(
                element_type=ElementType.LIGHT,
                name="✨ Свет",
                description="Стихия света и сияния",
                icon="✨",
                strengths=[ElementType.SHADOW, ElementType.ICE],
                weaknesses=[ElementType.SHADOW, ElementType.NONE],
                bonus_damage=1.3,
                resistance=0.7
            ),
            Element(
                element_type=ElementType.NONE,
                name="⚪ Нет",
                description="Отсутствие элемента",
                icon="⚪",
                strengths=[],
                weaknesses=[],
                bonus_damage=1.0,
                resistance=1.0
            )
        ]

        for element in default_elements:
            self.elements[element.element_type] = element

    def get_element(self, element_type: ElementType) -> Element:
        """Получает элемент по типу"""
        return self.elements.get(element_type, self.elements[ElementType.NONE])

    def get_elemental_effectiveness(self, attacker_element: ElementType, defender_element: ElementType) -> str:
        """Получает текстовое описание эффективности"""
        attacker = self.get_element(attacker_element)
        defender = self.get_element(defender_element)

        if defender_element in attacker.strengths:
            return "💥 ЭФФЕКТИВНО"
        elif defender_element in attacker.weaknesses:
            return "🛡️ НЕЭФФЕКТИВНО"
        else:
            return "⚖️ НОРМАЛЬНО"

    def add_custom_element(self, element_data: Dict[str, Any]) -> bool:
        """Добавляет кастомный элемент из мода"""
        try:
            element_type = ElementType(element_data['element_type'])

            if element_type in self.elements:
                return False

            element = Element(
                element_type=element_type,
                name=element_data['name'],
                description=element_data['description'],
                icon=element_data['icon'],
                strengths=[ElementType(et) for et in element_data.get('strengths', [])],
                weaknesses=[ElementType(et) for et in element_data.get('weaknesses', [])],
                bonus_damage=element_data.get('bonus_damage', 1.2),
                resistance=element_data.get('resistance', 0.8)
            )

            self.elements[element_type] = element
            return True

        except Exception as e:
            settings.log_error(f"❌ Ошибка добавления элемента: {e}")
            return False


# Глобальный экземпляр системы элементов
elemental_system = ElementalSystem()
# [file name]: src/entities/enemy.py
import random
from typing import Dict, Any
from elemental_source.elemental_integration import elemental_integration
from elemental_source.elemental_core import ElementType


class Enemy:
    def __init__(self, name, health, damage, enemy_type="common", difficulty="medium"):
        self.name = name
        self.health = health
        self.health_max = health
        self.damage = damage
        self.enemy_type = enemy_type  # common, elite, boss, etc.
        self.difficulty = difficulty  # easy, medium, hard, extreme
        self.isAlive = True

        # ДОБАВЛЯЕМ НЕДОСТАЮЩИЕ АТРИБУТЫ
        self.shield_hp = 5  # У врагов изначально 5 HP щита
        self.health_repair = 5  # Базовое лечение для врага
        self.potions = []  # У врагов нет зелий
        self.coin = 0  # Враги не носят монеты

        # Ресурсы для ИИ
        self.hp_count = 5  # Количество лечений
        self.shield_count = 3  # Количество щитов
        self.action_history = []  # История действий

        # Специальные способности
        self.special_ability = self._get_special_ability(enemy_type)
        self.element = self._get_element(enemy_type)

        # ЭЛЕМЕНТАЛЬНАЯ СИСТЕМА
        self.element = self._get_element(enemy_type)
        self.element_data = None
        self.elemental_resistance = 1.0

        # Применяем элемент к врагу
        self.set_element(self.element)

    def _get_special_ability(self, enemy_type):
        """Определение специальной способности по типу врага"""
        abilities = {
            "elite": "lightning_strike",
            "boss": "fire_breath",
            "champion": "ice_shield",
            "legendary": "nature_heal"
        }
        return abilities.get(enemy_type, None)

    def _get_element(self, enemy_type):
        """Определение элемента по типу врага с расширенной логикой"""
        element_map = {
            "common": ElementType.NONE,
            "elite": ElementType.FIRE,
            "boss": ElementType.LIGHTNING,
            "champion": ElementType.ICE,
            "legendary": ElementType.SHADOW
        }
        return element_map.get(enemy_type, ElementType.NONE)

    def set_element(self, element_type):
        """Устанавливает элемент врагу"""
        elemental_integration.apply_to_entity(self, element_type)

    def get_element_info(self) -> Dict[str, Any]:
        """Получает информацию об элементе врага"""
        return elemental_integration.get_entity_element_info(self)

    @classmethod
    def choose_entity_for_battle(cls, difficulty="medium"):
        """ УЛУЧШЕННЫЙ ВЫБОР ВРАГА С РАЗНЫМИ УРОВНЯМИ СЛОЖНОСТИ"""
        enemy_pool = {
            "easy": [
                ("🕷️ Паук-охотник", 15, 3, "common", "easy"),
                ("🐺 Лесной волк", 18, 4, "common", "easy"),
                ("🧌 Гоблин-воин", 20, 5, "common", "easy")
            ],
            "medium": [
                ("⚔️ Рыцарь Тьмы", 150, 16, "elite", "medium"),
                ("🔥 Огненный элементаль", 120, 17, "elite", "medium"),
                ("❄️ Ледяной голем", 130, 20, "elite", "medium")
            ],
            "hard": [
                ("🐉 Молодой дракон", 335, 69, "boss", "hard"),
                ("👹 Демон Бездны", 332, 57, "champion", "hard"),
                ("💀 Лич-некромант", 328, 56, "champion", "hard")
            ],
            "extreme": [
                ("🌋 Повелитель Огня", 840, 89, "legendary", "extreme"),
                ("⚡ Хранитель Молний", 838, 99, "legendary", "extreme"),
                ("🌪️ Древний Элементаль", 845, 100, "legendary", "extreme")
            ],
            "demon": [
                ("💀 Древний Страж", 6000, 500, "champion", "demon"),
                ("💀 Губитель Героев", 10000, 800, "boss", "demon"),
                ("💀 Лорд Демонов", 20000, 1500, "legendary", "demon")
            ]
        }

        enemies = enemy_pool.get(difficulty, enemy_pool["medium"])
        name, health, damage, enemy_type, diff = random.choice(enemies)

        return cls(name, health, damage, enemy_type, diff)

    def is_alive(self):
        """Проверяет, жив ли враг"""
        return self.health > 0

    def take_damage(self, damage):
        """Получение урона врагом"""
        self.health -= damage
        if self.health < 0:
            self.health = 0
        return {
            'shield_damage': 0,
            'health_damage': damage,
            'total_damage': damage
        }

    def defend(self):
        """Защита врага"""
        print(f"🛡️ {self.name} защищается!")

    def heal(self):
        """Лечение врага"""
        heal_amount = min(10, self.health_max - self.health)
        self.health += heal_amount
        return heal_amount

    def choose_action(self, player):
        """ИИ врага выбирает действие"""
        # Простой ИИ: атака с вероятностью 70%, защита 20%, лечение 10%
        rand = random.random()
        if rand < 0.7:
            return 'attack'
        elif rand < 0.9:
            return 'defend'
        else:
            return 'heal'
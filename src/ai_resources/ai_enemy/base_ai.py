# src/ai_resources/ai_enemy/base_ai.py
from abc import ABC, abstractmethod
from typing import Dict, Any
from modding.support_mods import hook_system
from random import random, choice


class BaseAI(ABC):
    """Базовый класс для всех AI врагов"""

    def __init__(self, name: str, difficulty: str = "medium"):
        self.name = name
        self.difficulty = difficulty
        self.personality_traits = {}
        self.learning_data = {
            'battles_fought': 0,
            'player_patterns': {},
            'successful_actions': [],
            'failed_actions': []
        }

    @abstractmethod
    def choose_action(self, enemy, player, battle_context: Dict[str, Any]) -> str:
        """Выбор действия AI реализован в дочерних классах"""
        pass

    def analyze_situation(self, enemy, player) -> Dict[str, Any]:
        """Анализ текущей ситуации в бою - базовая реализация"""
        situation = {
            # Основные показатели здоровья
            "enemy_health": enemy.health,
            "enemy_health_max": enemy.health_max,
            "enemy_health_percent": enemy.health / enemy.health_max if enemy.health_max > 0 else 0,
            "player_health": player.health,
            "player_health_max": player.health_max,
            "player_health_percent": player.health / player.health_max if player.health_max > 0 else 0,

            # Критические состояния
            "enemy_health_low": enemy.health < enemy.health_max * 0.3,
            "enemy_health_critical": enemy.health < enemy.health_max * 0.15,
            "player_health_low": player.health < player.health_max * 0.3,
            "player_health_critical": player.health < player.health_max * 0.15,

            # Состояния щитов
            "enemy_shield_active": getattr(enemy, 'shield_hp', 0) > 0,
            "player_shield_active": getattr(player, 'shield_hp', 0) > 0,
            "enemy_shield_hp": getattr(enemy, 'shield_hp', 0),
            "player_shield_hp": getattr(player, 'shield_hp', 0),

            # Показатели урона
            "enemy_damage": enemy.damage,
            "player_damage": player.damage,
            "damage_ratio": enemy.damage / player.damage if player.damage > 0 else float('inf'),

            # Тактические показатели
            "can_kill_player": enemy.damage >= player.health,
            "can_be_killed": player.damage >= enemy.health,
            "turns_to_kill_player": player.health / enemy.damage if enemy.damage > 0 else float('inf'),
            "turns_to_be_killed": enemy.health / player.damage if player.damage > 0 else float('inf'),

            # Элементальные атрибуты
            "enemy_element": getattr(enemy, 'element', 'none'),
            "player_element": getattr(player, 'element', 'none'),

            # Специальные способности
            "enemy_special_ability": getattr(enemy, 'special_ability', None),
            "player_special_ability": getattr(player, 'special_ability', None),
        }

        # Хук для модификации анализа ситуации
        situation = hook_system.execute_hook('ai_situation_analysis', situation, enemy, player) or situation

        return situation

    def get_ai_description(self) -> str:
        """Описание поведения AI"""
        traits = []
        if self.personality_traits.get('aggressive', 0) > 0.6:
            traits.append("агрессивный")
        if self.personality_traits.get('defensive', 0) > 0.6:
            traits.append("защитный")
        if self.personality_traits.get('adaptive', 0) > 0.6:
            traits.append("адаптивный")
        if self.personality_traits.get('strategic', 0) > 0.6:
            traits.append("стратегический")

        traits_str = ", ".join(traits) if traits else "сбалансированный"
        return f"AI: {self.name} (Сложность: {self.difficulty}, Стиль: {traits_str})"

    def update_learning(self, battle_result: str, player_actions: list):
        """Обновление данных обучения на основе результатов боя"""
        self.learning_data['battles_fought'] += 1

        # Анализ паттернов игрока
        for action in player_actions:
            if action in self.learning_data['player_patterns']:
                self.learning_data['player_patterns'][action] += 1
            else:
                self.learning_data['player_patterns'][action] = 1

        # Обновление успешных/неуспешных действий
        if battle_result == 'enemy_win':
            # Все действия в этой битве считаются успешными
            self.learning_data['successful_actions'].extend(player_actions)
        elif battle_result == 'player_win':
            # Все действия в этой битве считаются неуспешными
            self.learning_data['failed_actions'].extend(player_actions)

        # Ограничение размера истории обучения
        max_history = 1000
        if len(self.learning_data['successful_actions']) > max_history:
            self.learning_data['successful_actions'] = self.learning_data['successful_actions'][-max_history:]
        if len(self.learning_data['failed_actions']) > max_history:
            self.learning_data['failed_actions'] = self.learning_data['failed_actions'][-max_history:]

        # Обновление черт личности на основе успеха
        win_rate = self._calculate_win_rate()
        if win_rate > 0.7:
            self.personality_traits['aggressive'] = min(1.0, self.personality_traits.get('aggressive', 0) + 0.1)
        elif win_rate < 0.3:
            self.personality_traits['defensive'] = min(1.0, self.personality_traits.get('defensive', 0) + 0.1)

        # Хук для кастомного обучения
        hook_system.execute_hook('ai_learning_update', self, battle_result, player_actions)

    def _calculate_win_rate(self) -> float:
        """Расчет коэффициента побед на основе истории обучения"""
        total_battles = self.learning_data['battles_fought']
        if total_battles == 0:
            return 0.5  # Нейтральный рейтинг по умолчанию

        successful_actions = len(self.learning_data['successful_actions'])
        total_actions = successful_actions + len(self.learning_data['failed_actions'])

        if total_actions == 0:
            return 0.5

        return successful_actions / total_actions

    @staticmethod
    def get_recommended_action(situation: Dict[str, Any]) -> str:
        """Рекомендация действия на основе текущей ситуации"""
        # Базовая логика рекомендаций
        if situation["player_health_critical"] and situation["can_kill_player"]:
            return "attack"  # Добить игрока

        if situation["enemy_health_critical"]:
            return "heal"  # Срочное лечение

        if situation["player_shield_active"] and situation["player_shield_hp"] == 1:
            return "attack"  # Сломать щит

        if situation["enemy_health_low"] and not situation["player_health_low"]:
            return choice(["heal", "defend"])  # Оборонительная тактика

        # Стандартная рекомендация
        return choice(["attack", "defend", "heal"])

    def calculate_action_priority(self, action: str, situation: Dict[str, Any]) -> float:
        """Расчет приоритета для действия от 0.0 до 1.0"""
        base_priority = 0.5

        if action == "attack":
            if situation["player_health_low"]:
                base_priority += 0.3
            if situation["can_kill_player"]:
                base_priority += 0.4
            if situation["player_shield_active"]:
                base_priority -= 0.2

        elif action == "defend":
            if situation["enemy_health_low"]:
                base_priority += 0.3
            if situation["can_be_killed"]:
                base_priority += 0.4
            if situation["player_health_critical"]:
                base_priority -= 0.2

        elif action == "heal":
            if situation["enemy_health_low"]:
                base_priority += 0.4
            if situation["enemy_health_critical"]:
                base_priority += 0.3
            if situation["player_health_critical"]:
                base_priority -= 0.3

        # Учет истории обучения
        win_rate = self._calculate_win_rate()
        if win_rate > 0.7:
            # При высоком win rate более агрессивный
            if action == "attack":
                base_priority += 0.1
        elif win_rate < 0.3:
            # При низком win rate более защитный
            if action in ["defend", "heal"]:
                base_priority += 0.1

        return max(0.0, min(1.0, base_priority))

    def should_use_special_ability(self, enemy, player, situation: Dict[str, Any]) -> bool:
        """Определяет, стоит ли использовать специальную способность"""
        if not hasattr(enemy, 'special_ability') or not enemy.special_ability:
            return False

        # Логика использования специальных способностей
        if enemy.special_ability == "fire_breath" and situation["player_health_high"]:
            return random() < 0.3

        if enemy.special_ability == "ice_shield" and situation["enemy_health_low"]:
            return random() < 0.4

        if enemy.special_ability == "nature_heal" and situation["enemy_health_critical"]:
            return random() < 0.6

        return random() < 0.1  # 10% шанс по умолчанию

    def get_personality_trait(self, trait: str) -> float:
        """Получение значения черты личности"""
        return self.personality_traits.get(trait, 0.5)

    def set_personality_trait(self, trait: str, value: float):
        """Установка значения черты личности"""
        self.personality_traits[trait] = max(0.0, min(1.0, value))

    def get_learning_summary(self) -> Dict[str, Any]:
        """Получение сводки обучения AI"""
        return {
            'battles_fought': self.learning_data['battles_fought'],
            'win_rate': self._calculate_win_rate(),
            'player_patterns': self.learning_data['player_patterns'],
            'personality_traits': self.personality_traits,
            'most_used_player_action': max(
                self.learning_data['player_patterns'].items(),
                key=lambda x: x[1],
                default=('unknown', 0)
            )[0]
        }
# src/ai_resources/ai_enemy/adaptive_ai.py
from base_ai import BaseAI
from random import random, choice


class AdaptiveAI(BaseAI):
    """Адаптивный AI - учится на действиях игрока"""

    def __init__(self, difficulty="medium"):
        super().__init__("Адаптивный", difficulty)
        self.player_patterns = {}
        self.last_player_actions = []

    def choose_action(self, enemy, player, battle_context):
        situation = self.analyze_situation(enemy, player)
        self._update_player_patterns(battle_context.get('player_last_action'))

        # Адаптивная логика на основе паттернов игрока
        if self._predict_player_attack():
            if random() < 0.6:
                return "defend"

        if self._predict_player_heal() and situation["player_health_low"]:
            if random() < 0.7:
                return "attack"  # Прервать лечение

        # Базовый сбалансированный выбор
        return choice(["attack", "defend", "heal"])

    def _update_player_patterns(self, player_action):
        if player_action:
            self.last_player_actions.append(player_action)
            if len(self.last_player_actions) > 5:
                self.last_player_actions.pop(0)

    def _predict_player_attack(self):
        """Предсказывает атаку игрока на основе паттернов"""
        if len(self.last_player_actions) < 3:
            return False
        return self.last_player_actions[-2:] == ['attack', 'attack']

    def _predict_player_heal(self):
        """Предсказывает лечение игрока"""
        if not self.last_player_actions:
            return False
        return self.last_player_actions[-1] == 'heal'

    def analyze_situation(self, enemy, player):
        return {
            "enemy_health_percent": enemy.health / enemy.health_max,
            "player_health_percent": player.health / player.health_max,
            "enemy_health_low": enemy.health < enemy.health_max * 0.3,
            "player_health_low": player.health < player.health_max * 0.3,
        }
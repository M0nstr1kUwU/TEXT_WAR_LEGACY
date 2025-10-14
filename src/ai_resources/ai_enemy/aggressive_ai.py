# src/ai_resources/ai_enemy/aggressive_ai.py
from base_ai import BaseAI
from random import random, choice


class AggressiveAI(BaseAI):
    """Агрессивный AI - предпочитает атаку"""

    def __init__(self, difficulty="medium"):
        super().__init__("Агрессивный", difficulty)
        self.attack_chance = 0.7  # 70% шанс атаки

    def choose_action(self, enemy, player, battle_context):
        situation = self.analyze_situation(enemy, player)

        # Агрессивная логика
        if situation["player_health_low"] and random() < 0.8:
            return "attack"  # Добить игрока

        if situation["enemy_health_low"] and random() < 0.4:
            return "heal"  # Иногда лечится когда мало HP

        if random() < self.attack_chance:
            return "attack"
        else:
            return choice(["defend", "heal"])

    def analyze_situation(self, enemy, player):
        return {
            "enemy_health_percent": enemy.health / enemy.health_max,
            "player_health_percent": player.health / player.health_max,
            "enemy_health_low": enemy.health < enemy.health_max * 0.3,
            "player_health_low": player.health < player.health_max * 0.3,
            "player_shield_active": getattr(player, 'shield_hp', 0) > 0
        }
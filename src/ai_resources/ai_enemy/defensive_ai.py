# src/ai_resources/ai_enemy/defensive_ai.py
from base_ai import BaseAI
from random import random, choice


class DefensiveAI(BaseAI):
    """Защитный AI - предпочитает защиту и лечение"""

    def __init__(self, difficulty="medium"):
        super().__init__("Защитный", difficulty)
        self.defense_chance = 0.6

    def choose_action(self, enemy, player, battle_context):
        situation = self.analyze_situation(enemy, player)

        if situation["enemy_health_low"]:
            if random() < 0.7:
                return "heal"

        if situation["player_health_high"] and random() < 0.5:
            return "defend"

        if random() < self.defense_chance:
            return choice(["defend", "heal"])
        else:
            return "attack"

    def analyze_situation(self, enemy, player):
        return {
            "enemy_health_percent": enemy.health / enemy.health_max,
            "player_health_percent": player.health / player.health_max,
            "enemy_health_low": enemy.health < enemy.health_max * 0.4,
            "player_health_high": player.health > player.health_max * 0.7,
        }
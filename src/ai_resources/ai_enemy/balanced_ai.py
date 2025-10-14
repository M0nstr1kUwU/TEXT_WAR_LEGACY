# src/ai_resources/ai_enemy/balanced_ai.py
from base_ai import BaseAI
from random import random, choices


class BalancedAI(BaseAI):
    """Сбалансированный AI - адаптируется под ситуацию"""

    def __init__(self, difficulty="medium"):
        super().__init__("Сбалансированный", difficulty)

    def choose_action(self, enemy, player, battle_context):
        situation = self.analyze_situation(enemy, player)

        # Логика в зависимости от ситуации
        if situation["enemy_health_low"]:
            if random() < 0.6:
                return "heal"

        if situation["player_health_low"]:
            if random() < 0.7:
                return "attack"

        if situation["player_shield_active"] and random() < 0.3:
            return "attack"  # Попытка сломать щит

        # Сбалансированный выбор
        choices_s = ["attack", "defend", "heal"]
        weights = [0.5, 0.3, 0.2]

        return choices(choices_s, weights=weights)[0]

    def analyze_situation(self, enemy, player):
        return {
            "enemy_health_percent": enemy.health / enemy.health_max,
            "player_health_percent": player.health / player.health_max,
            "enemy_health_low": enemy.health < enemy.health_max * 0.4,
            "player_health_low": player.health < player.health_max * 0.4,
            "player_shield_active": getattr(player, 'shield_hp', 0) > 0
        }
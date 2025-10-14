# src/ai_resources/ai_enemy/boss_ai.py
from typing import Dict, Any
from base_ai import BaseAI
from random import random, choice


class BossAI(BaseAI):
    """AI для боссов - использует специальные способности"""

    def __init__(self, difficulty="hard"):
        super().__init__("Босс", difficulty)
        self.special_ability_cooldown = 0
        self.phase = 1

    def choose_action(self, enemy, player, battle_context: Dict[str, Any]) -> str:
        """Выбор действия для босса"""
        situation = self.analyze_situation(enemy, player)

        # Смена фаз у босса
        self._update_phase(situation)

        # Использование специальной способности
        if self.special_ability_cooldown <= 0 and random() < 0.3:
            ability = self._choose_special_ability(situation)
            if ability:
                self.special_ability_cooldown = 3  # КД 3 хода
                return ability

        self.special_ability_cooldown = max(0, self.special_ability_cooldown - 1)

        # Тактика в зависимости от фазы
        if self.phase == 1:
            return self._phase1_strategy(situation)
        elif self.phase == 2:
            return self._phase2_strategy(situation)
        else:
            return self._phase3_strategy(situation)

    def _update_phase(self, situation):
        """Обновление фазы босса"""
        health_percent = situation["enemy_health_percent"]
        if health_percent <= 0.3:
            self.phase = 3
        elif health_percent <= 0.6:
            self.phase = 2
        else:
            self.phase = 1

    def _choose_special_ability(self, situation):
        """Выбор специальной способности"""
        abilities = ["strong_attack", "aoe_attack", "heal_burst"]

        if situation["enemy_health_low"]:
            return "heal_burst"
        elif situation["player_health_high"]:
            return "aoe_attack"
        else:
            return "strong_attack"

    def _phase1_strategy(self, situation):
        """Стратегия фазы 1 - разведка"""
        return choice(["attack", "defend"])

    def _phase2_strategy(self, situation):
        """Стратегия фазы 2 - агрессия"""
        if random() < 0.7:
            return "attack"
        return choice(["defend", "heal"])

    def _phase3_strategy(self, situation):
        """Стратегия фазы 3 - отчаяние"""
        if situation["enemy_health_low"] and random() < 0.8:
            return "heal"
        return "attack"

    def analyze_situation(self, enemy, player):
        return {
            "enemy_health_percent": enemy.health / enemy.health_max,
            "player_health_percent": player.health / player.health_max,
            "enemy_health_low": enemy.health < enemy.health_max * 0.3,
            "player_health_high": player.health > player.health_max * 0.8,
        }
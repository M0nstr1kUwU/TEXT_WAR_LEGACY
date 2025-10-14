# src/ai_resources/ai_enemy/enhanced_ai.py
"""
Улучшенная система ИИ для врагов - адаптированная для текущей версии игры
Интегрирует функционал из advanced_enemy_ai.py
"""

from random import random, choices, choice
from typing import Dict, Any, Optional
from base_ai import BaseAI
from settings.settings_manager import settings
from modding.support_mods import hook_system


class EnhancedAI(BaseAI):
    """Улучшенный ИИ с обучением и адаптацией"""

    def __init__(self, name="Улучшенный ИИ", difficulty="medium"):
        super().__init__(name, difficulty)

        # Система обучения и памяти
        self.player_patterns = {}
        self.action_history = []
        self.learning_rate = self._get_learning_rate()
        self.adaptation_level = 0.5

        # Психологический профиль
        self.aggression = 0.5
        self.caution = 0.5
        self.prediction_accuracy = 0.0

        # Счетчики
        self.turns_analyzed = 0
        self.successful_predictions = 0

        print(f"🤖 Инициализирован {name} (Сложность: {difficulty})")
        settings.log_info(f"🤖 Инициализирован {name} (Сложность: {difficulty})")

    def choose_action(self, enemy, player, battle_context: Dict[str, Any]) -> str:
        """Основной метод выбора действия с поддержкой хуков"""
        situation = self.analyze_situation(enemy, player)
        self.turns_analyzed += 1

        # Базовое решение
        strategy = self._select_strategy(situation, enemy, player)
        base_action = self._execute_strategy(strategy, situation, enemy, player)

        # 🆕 ПРАВИЛЬНЫЙ ВЫЗОВ ХУКА AI_DECISION
        custom_action = hook_system.execute_hook(
            'ai_decision',
            enemy,
            player,
            battle_context.get('round', 0),
            base_action  # Передаем базовое решение как аргумент
        )

        # Используем кастомное действие если оно возвращено, иначе базовое
        action = custom_action if custom_action is not None else base_action

        # Запоминаем действие для анализа
        self.action_history.append(action)
        if len(self.action_history) > 50:
            self.action_history.pop(0)

        # Хук после принятия решения
        hook_system.execute_hook('ai_action_processed', enemy, player, action, "success")

        return action

    def _select_strategy(self, situation: Dict[str, Any], enemy, player) -> str:
        """Выбор стратегии на основе текущей ситуации"""

        # Критические ситуации
        if situation["enemy_health_critical"]:
            return "survival"
        elif situation["player_health_critical"] and situation["can_kill_player"]:
            return "finish"
        elif situation["can_be_killed"]:
            return "defensive"

        # Адаптивная стратегия на основе стиля игрока
        player_style = self._analyze_player_style(player)
        if player_style == "aggressive":
            return "counter_aggressive"
        elif player_style == "defensive":
            return "pressure"
        elif player_style == "balanced":
            return "adaptive"

        # Стандартная стратегия по сложности
        if self.difficulty == "easy":
            return "basic"
        elif self.difficulty == "medium":
            return "balanced"
        elif self.difficulty == "hard":
            return "tactical"
        else:
            return "adaptive"

    def _execute_strategy(self, strategy: str, situation: Dict[str, Any], enemy, player) -> str:
        """Выполнение выбранной стратегии"""

        # Явно указываем типы для методов стратегий
        strategy_map = {
            "survival": self._survival_strategy,
            "finish": self._finish_strategy,
            "defensive": self._defensive_strategy,
            "counter_aggressive": self._counter_aggressive_strategy,
            "pressure": self._pressure_strategy,
            "adaptive": self._adaptive_strategy,
            "basic": self._basic_strategy,
            "balanced": self._balanced_strategy,
            "tactical": self._tactical_strategy,
        }

        if strategy in strategy_map:
            return strategy_map[strategy](situation, enemy, player)
        else:
            return self._adaptive_strategy(situation, enemy, player)

    # Обновляем сигнатуры всех стратегических методов с правильными типами:

    def _survival_strategy(self, situation: Dict[str, Any], enemy, player) -> str:
        """Стратегия выживания"""
        # Код метода без изменений
        if situation["enemy_health_percent"] < 0.2:
            if getattr(enemy, 'hp_count', 0) > 0:
                return "heal"
            elif getattr(enemy, 'shield_count', 0) > 0:
                return "defend"

        if situation["player_damage"] >= getattr(enemy, 'health', 0):
            if getattr(enemy, 'shield_count', 0) > 0:
                return "defend"
            elif random() < 0.7:
                return "heal"

        return "defend" if random() < 0.6 else "attack"

    def _finish_strategy(self, situation: Dict[str, Any], enemy, player) -> str:
        """Стратегия добивания"""
        if situation["can_kill_player"]:
            return "attack"

        if self._predict_player_heal(player) and situation["player_health_percent"] < 0.5:
            return "attack"

        return "attack" if random() < 0.8 else "defend"

    def _defensive_strategy(self, situation: Dict[str, Any], enemy, player) -> str:
        """Защитная стратегия"""
        actions = []
        weights = []

        if getattr(enemy, 'shield_count', 0) > 0:
            actions.append("defend")
            weights.append(0.6)

        if getattr(enemy, 'hp_count', 0) > 0 and situation["enemy_health_percent"] < 0.7:
            actions.append("heal")
            weights.append(0.5)

        actions.append("attack")
        weights.append(0.3)

        if actions:
            return choices(actions, weights=weights)[0]

        return "defend"

    def _counter_aggressive_strategy(self, situation: Dict[str, Any], enemy, player) -> str:
        """Контр-агрессивная стратегия"""
        if self._predict_player_attack(player) and getattr(enemy, 'shield_count', 0) > 0:
            return "defend"

        if self._predict_player_heal(player):
            return "attack"

        return choices(["attack", "defend"], weights=[0.7, 0.3])[0]

    def _pressure_strategy(self, situation: Dict[str, Any], enemy, player) -> str:
        """Стратегия давления"""
        if situation["player_health_percent"] > 0.8:
            return "attack"

        if self.turns_analyzed % 3 == 0 and hasattr(enemy, 'temp_strength'):
            return "special"

        return "attack" if random() < 0.7 else "defend"

    def _adaptive_strategy(self, situation: Dict[str, Any], enemy, player) -> str:
        """Адаптивная стратегия"""
        aggression = self._calculate_dynamic_aggression(situation)

        if aggression > 0.7:
            return "attack"
        elif aggression < 0.3:
            if getattr(enemy, 'hp_count', 0) > 0 and situation["enemy_health_percent"] < 0.8:
                return "heal"
            else:
                return "defend"
        else:
            available_actions = ["attack", "defend"]
            if getattr(enemy, 'hp_count', 0) > 0:
                available_actions.append("heal")
            return choice(available_actions)

    def _basic_strategy(self, situation: Dict[str, Any], enemy, player) -> str:
        """Базовая стратегия"""
        if situation["enemy_health_percent"] < 0.3:
            if getattr(enemy, 'hp_count', 0) > 0 and random() < 0.6:
                return "heal"
            else:
                return "defend"
        return "attack"

    def _balanced_strategy(self, situation: Dict[str, Any], enemy, player) -> str:
        """Сбалансированная стратегия"""
        weights = {
            "attack": 0.5,
            "defend": 0.3,
            "heal": 0.2
        }

        if situation["enemy_health_percent"] < 0.4:
            weights["heal"] = min(0.8, weights["heal"] + 0.3)
            weights["attack"] = max(0.1, weights["attack"] - 0.2)

        if situation["player_health_percent"] < 0.3:
            weights["attack"] = min(0.8, weights["attack"] + 0.3)
            weights["defend"] = max(0.1, weights["defend"] - 0.2)

        available_actions = []
        available_weights = []

        for action, weight in weights.items():
            if self._is_action_available(action, enemy):
                available_actions.append(action)
                available_weights.append(weight)

        if available_actions:
            return choices(available_actions, weights=available_weights)[0]

        return "attack"

    def _tactical_strategy(self, situation: Dict[str, Any], enemy, player) -> str:
        """Тактическая стратегия"""
        planned_action = self._multi_turn_planning(situation, enemy, player)
        if planned_action:
            return planned_action

        if self.should_use_special_ability(enemy, player, situation):
            return "special"

        return self._balanced_strategy(situation, enemy, player)

    def _ensure_required_attributes(self, enemy, player):
        """Обеспечивает наличие необходимых атрибутов у enemy и player"""
        # Для enemy
        if not hasattr(enemy, 'hp_count'):
            enemy.hp_count = 0
        if not hasattr(enemy, 'shield_count'):
            enemy.shield_count = 0
        if not hasattr(enemy, 'action_history'):
            enemy.action_history = []
        if not hasattr(enemy, 'special_ability'):
            enemy.special_ability = None
        if not hasattr(enemy, 'health'):
            enemy.health = getattr(enemy, 'health_max', 0)

        # Для player
        if not hasattr(player, 'action_history'):
            player.action_history = []


    def _analyze_player_style(self, player) -> str:
        """Анализ стиля игры игрока"""
        if not hasattr(player, 'action_history') or len(player.action_history) < 5:
            return "unknown"

        action_counts = {}
        for action in player.action_history[-10:]:
            action_counts[action] = action_counts.get(action, 0) + 1

        total_actions = len(player.action_history[-10:])
        if total_actions == 0:
            return "unknown"

        attack_ratio = action_counts.get("attack", 0) / total_actions
        defend_ratio = action_counts.get("defend", 0) / total_actions
        heal_ratio = action_counts.get("heal", 0) / total_actions

        if attack_ratio > 0.6:
            return "aggressive"
        elif defend_ratio > 0.4 or heal_ratio > 0.4:
            return "defensive"
        else:
            return "balanced"

    def _predict_player_attack(self, player) -> bool:
        """Предсказание атаки игрока"""
        action_history = getattr(player, 'action_history', [])
        if len(action_history) < 3:
            return False

        recent_actions = action_history[-3:]
        return recent_actions.count("attack") >= 2

    def _predict_player_heal(self, player) -> bool:
        """Предсказание лечения игрока"""
        action_history = getattr(player, 'action_history', [])
        if len(action_history) < 2:
            return False

        return action_history[-1] == "heal"

    def _calculate_dynamic_aggression(self, situation: Dict[str, Any]) -> float:
        """Динамический расчет уровня агрессии"""
        base_aggression = {
            "easy": 0.3,
            "medium": 0.5,
            "hard": 0.7
        }.get(self.difficulty, 0.5)

        # Модификаторы на основе ситуации
        modifiers = 0.0

        if situation["player_health_low"]:
            modifiers += 0.3
        if situation["enemy_health_low"]:
            modifiers -= 0.3
        if situation["can_kill_player"]:
            modifiers += 0.2
        if situation["can_be_killed"]:
            modifiers -= 0.2

        # Учет успешности предсказаний
        if self.turns_analyzed > 0:
            accuracy_bonus = (self.successful_predictions / self.turns_analyzed) * 0.2
            modifiers += accuracy_bonus

        return max(0.1, min(0.9, base_aggression + modifiers))

    def _multi_turn_planning(self, situation: Dict[str, Any], enemy, player, depth=2) -> Optional[str]:
        """Планирование на несколько ходов вперед"""
        if depth == 0:
            return None

        best_action = None
        best_score = -9999

        for action in ["attack", "defend", "heal"]:
            if not self._is_action_available(action, enemy):
                continue

            # Упрощенная симуляция
            score = self._simulate_action_score(action, situation, enemy, player, depth)

            if score > best_score:
                best_score = score
                best_action = action

        return best_action

    def _simulate_action_score(self, action: str, situation: Dict[str, Any], enemy, player, depth: int) -> float:
        """Оценка действия через симуляцию"""
        score = 0

        # Базовые оценки действий
        action_scores = {
            "attack": self._evaluate_attack(situation),
            "defend": self._evaluate_defend(situation),
            "heal": self._evaluate_heal(situation)
        }

        score += action_scores.get(action, 0)

        # Рекурсивная симуляция для глубины > 1
        if depth > 1:
            # Упрощенная симуляция следующего хода
            simulated_situation = situation.copy()
            if action == "attack":
                simulated_situation["player_health_percent"] = max(0,
                                                                   simulated_situation["player_health_percent"] - 0.1)
            elif action == "heal":
                simulated_situation["enemy_health_percent"] = min(1,
                                                                  simulated_situation["enemy_health_percent"] + 0.15)

            next_action = self._multi_turn_planning(simulated_situation, enemy, player, depth - 1)
            if next_action:
                score += action_scores.get(next_action, 0) * 0.5

        return score

    def _evaluate_attack(self, situation: Dict[str, Any]) -> float:
        """Оценка атаки"""
        score = 0
        score += (1 - situation["player_health_percent"]) * 50  # Чем меньше HP у игрока, тем лучше
        score += situation["enemy_damage"] * 2  # Учет урона

        if situation["player_health_critical"]:
            score += 30
        if situation["player_shield_active"]:
            score -= 20

        return score

    def _evaluate_defend(self, situation: Dict[str, Any]) -> float:
        """Оценка защиты"""
        score = 0
        score += situation["player_damage"] * 3  # Защита против сильного врага
        score += (1 - situation["enemy_health_percent"]) * 20  # Защита при низком HP

        if situation["can_be_killed"]:
            score += 40
        if self._predict_player_attack:
            score += 25

        return score

    def _evaluate_heal(self, situation: Dict[str, Any]) -> float:
        """Оценка лечения"""
        score = 0
        score += (1 - situation["enemy_health_percent"]) * 60  # Чем меньше HP, тем ценнее лечение

        if situation["enemy_health_critical"]:
            score += 50
        if situation["player_health_percent"] > 0.8:
            score += 20  # Лечение когда игрок сильный

        return score

    def _is_action_available(self, action: str, enemy) -> bool:
        """Проверка доступности действия"""
        if action == "heal":
            return getattr(enemy, 'hp_count', 0) > 0
        elif action == "defend":
            return getattr(enemy, 'shield_count', 0) > 0
        elif action == "special":
            return hasattr(enemy, 'special_ability') and enemy.special_ability
        return True

    def _get_learning_rate(self) -> float:
        """Скорость обучения в зависимости от сложности"""
        return {
            "easy": 0.3,
            "medium": 0.6,
            "hard": 0.9
        }.get(self.difficulty, 0.5)

    # Добавляем вызов хука в метод update_learning:
    def update_learning(self, battle_result: str, player_actions: list):
        """Обновление обучения на основе результатов боя"""
        super().update_learning(battle_result, player_actions)

        # Дополнительное обучение для улучшенного ИИ
        for action in player_actions:
            if action in self.player_patterns:
                self.player_patterns[action] += 1
            else:
                self.player_patterns[action] = 1

        # Обновление точности предсказаний
        if battle_result == 'enemy_win':
            self.successful_predictions += 1

        # Адаптация агрессии
        if battle_result == 'enemy_win':
            self.aggression = min(0.9, self.aggression + 0.05)
        else:
            self.aggression = max(0.1, self.aggression - 0.05)

        hook_system.execute_hook('ai_learning_update', self, battle_result, player_actions)

    def get_ai_description(self) -> str:
        """Описание поведения AI"""
        base_description = super().get_ai_description()

        # Дополнительная информация об обучении
        learning_info = f" | Обучение: {self.learning_rate:.1f}"
        prediction_info = f" | Точность: {self.prediction_accuracy:.1%}"

        return base_description + learning_info + prediction_info

    def should_use_special_ability(self, enemy, player, situation: Dict[str, Any]) -> bool:
        """Улучшенная логика использования специальных способностей"""
        special_ability = getattr(enemy, 'special_ability', None)
        if not special_ability:
            return False

        # Базовая логика из BaseAI
        base_chance = super().should_use_special_ability(enemy, player, situation)
        if base_chance:
            return True

        # Улучшенная логика для разных типов способностей
        ability_strategies = {
            "fire_breath": situation["player_health_percent"] > 0.7,
            "ice_shield": situation["enemy_health_percent"] < 0.4,
            "nature_heal": situation["enemy_health_percent"] < 0.3,
            "lightning_strike": situation["player_health_percent"] < 0.5,
            "earth_protection": situation["can_be_killed"]
        }

        ability_condition = ability_strategies.get(special_ability, False)
        ability_chance = 0.4 if ability_condition else 0.1

        return random() < ability_chance
# src/ai_resources/ai_enemy/ai_manager.py
from base_ai import BaseAI
from enhanced_ai import EnhancedAI
from adaptive_ai import AdaptiveAI
from balanced_ai import BalancedAI
from boss_ai import BossAI
from settings.settings_manager import settings
from modding.support_mods import hook_system


class AIManager:
    """Менеджер AI для врагов"""

    def __init__(self):
        self.ai_types = {
            'easy': BalancedAI,
            'medium': BalancedAI,
            'hard': EnhancedAI,
            'adaptive': AdaptiveAI,
            'enhanced': EnhancedAI,
            'boss': BossAI,
            'extreme': EnhancedAI,
        }

        self.difficulty_settings = {
            'easy': {'ai_type': 'easy', 'intelligence': 0.3},
            'medium': {'ai_type': 'medium', 'intelligence': 0.6},
            'hard': {'ai_type': 'hard', 'intelligence': 0.8},
            'adaptive': {'ai_type': 'adaptive', 'intelligence': 0.9},
            'enhanced': {'ai_type': 'enhanced', 'intelligence': 1.0},
            'boss': {'ai_type': 'boss', 'intelligence': 1.2},
            'extreme': {'ai_type': 'enhanced', 'intelligence': 1.5}
        }

    def create_ai_for_enemy(self, enemy, difficulty="medium"):
        """Создание AI для врага с учетом сложности и хуков"""

        custom_ai = hook_system.execute_hook('ai_creation', enemy, difficulty)
        if custom_ai is not None:
            settings.log_info(f"🤖 Использован кастомный AI от мода")
            return custom_ai

        # Стандартная логика выбора AI
        ai_class = self.ai_types.get(difficulty, BaseAI)
        ai_instance = ai_class(difficulty)

        # Хук после создания AI
        hook_system.execute_hook('ai_created', ai_instance, enemy, difficulty)

        return ai_instance

    def get_ai_info(self, enemy, difficulty):
        """Получение информации об AI"""
        ai_instance = self.create_ai_for_enemy(enemy, difficulty)

        info = {
            "Тип AI": ai_instance.__class__.__name__,
            "Сложность": difficulty,
            "Обучение": "Да" if hasattr(ai_instance, 'learning_rate') else "Нет",
            "Адаптивность": "Да" if hasattr(ai_instance, 'adaptation_level') else "Нет",
            "Предикция": "Да" if hasattr(ai_instance, 'prediction_accuracy') else "Нет"
        }

        return info

    def set_difficulty_preset(self, difficulty, ai_type, intelligence):
        """Установка пресета сложности"""
        self.difficulty_settings[difficulty] = {
            'ai_type': ai_type,
            'intelligence': intelligence
        }
        settings.log_info(f"✅ Пресет сложности '{difficulty}' обновлен!")

    def get_available_ai_types(self):
        """Возвращает доступные типы AI"""
        return list(self.ai_types.keys())

    def get_difficulty_info(self, difficulty):
        """Получение информации о настройках сложности"""
        settings_manager = self.difficulty_settings.get(difficulty, {})
        return {
            "Сложность": difficulty,
            "Тип AI": settings_manager.get('ai_type', 'unknown'),
            "Интеллект": settings_manager.get('intelligence', 0.5),
            "Описание": self._get_difficulty_description(difficulty)
        }

    @staticmethod
    def _get_difficulty_description(difficulty):
        """Описание уровня сложности"""
        descriptions = {
            'easy': "🤖 Базовый ИИ - простые действия, подходит для новичков",
            'medium': "🎯 Стандартный ИИ - сбалансированная сложность",
            'hard': "🧠 Улучшенный ИИ - обучается и адаптируется",
            'adaptive': "🔮 Адаптивный ИИ - подстраивается под стиль игрока",
            'enhanced': "⚡ Продвинутый ИИ - использует сложные стратегии",
            'boss': "👑 Босс ИИ - максимальная сложность с особыми способностями",
            'extreme': "💀 Экстрим ИИ - невероятно сложный противник"
        }
        return descriptions.get(difficulty, "Неизвестная сложность")

    def reset_to_defaults(self):
        """Сброс настроек AI к значениям по умолчанию"""
        self.difficulty_settings = {
            'easy': {'ai_type': 'easy', 'intelligence': 0.3},
            'medium': {'ai_type': 'medium', 'intelligence': 0.6},
            'hard': {'ai_type': 'hard', 'intelligence': 0.8},
            'adaptive': {'ai_type': 'adaptive', 'intelligence': 0.9},
            'enhanced': {'ai_type': 'enhanced', 'intelligence': 1.0},
            'boss': {'ai_type': 'boss', 'intelligence': 1.2},
            'extreme': {'ai_type': 'enhanced', 'intelligence': 1.5}
        }
        print("✅ Настройки AI сброшены к значениям по умолчанию!")
        settings.log_info("✅ Настройки AI сброшены к значениям по умолчанию!")

from json import load
from os import makedirs, path, listdir
import importlib.util
from inspect import signature
from typing import Dict, List, Callable, Any
from settings.settings_manager import settings


class HookSystem:
    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = {}
        self.modules = {}
        self.load_hooks_config()
        self.load_mods()

    def load_hooks_config(self):
        """Загрузка конфигурации хуков"""
        hooks_path = "src/saves/configs/hooks.json"
        if path.exists(hooks_path):
            try:
                with open(hooks_path, 'r', encoding='utf-8') as f:
                    self.hooks_config = load(f)
            except:
                self.hooks_config = {}
        else:
            self.hooks_config = {}

    def load_mods(self):
        """Загрузка всех модов"""
        mods_dir = "src/saves/mods"
        makedirs(mods_dir, exist_ok=True)

        # Создаем пример мода если его нет
        self.create_example_mod()

        # Загружаем все Python файлы из папки модов
        for filename in listdir(mods_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                mod_name = filename[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(mod_name, path.join(mods_dir, filename))
                    mod_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod_module)
                    self.modules[mod_name] = mod_module
                    settings.log_info(f"✅ Мод загружен: {mod_name}")

                    # Регистрируем хуки из мода
                    self.register_mod_hooks(mod_module, mod_name)

                except Exception as e:
                    print(f"❌ Ошибка загрузки мода {mod_name}: {e}")
                    settings.log_error(f"❌ Ошибка загрузки мода {mod_name}: {e}")

    @staticmethod
    def create_example_mod():
        """Создает пример мода для разработчиков"""
        example_mod_path = "src/saves/mods/example_mod.py"
        if not path.exists(example_mod_path):
            example_code = '''"""
ПРИМЕР МОДА ДЛЯ TEXT WAR LEGACY
Этот файл демонстрирует как создавать моды для игры
"""

def mod_initialize(hook_system):
    """Функция инициализации мода"""
    print("🎮 Пример мода загружен!")
    return True

# 🎯 ПРИМЕРЫ ХУКОВ

def on_player_created(player, hook_system):
    """Хук создания игрока - добавляет бонусные характеристики"""
    player.damage += 1
    player.health_max += 5
    player.health = player.health_max
    print(f"💪 Мод: Игрок усилен! Урон: {player.damage}, Здоровье: {player.health_max}")

def on_battle_start(player, enemy, mode, hook_system):
    """Хук начала битвы - добавляет специальные эффекты"""
    print(f"🔥 Мод: Началась эпическая битва! {player.name} vs {enemy.name}")

def on_damage_calculation(attacker, defender, base_damage, element, is_critical, hook_system):
    """Хук расчета урона - добавляет элементные бонусы"""
    element_bonus = {
        'fire': 1.2 if element == 'fire' else 1.0,
        'ice': 1.15 if element == 'ice' else 1.0,
        'nature': 1.1 if element == 'nature' else 1.0
    }
    bonus = element_bonus.get(element, 1.0)
    return base_damage * bonus

def on_enemy_creation(enemy, difficulty, hook_system):
    """Хук создания врага - усиливает боссов"""
    if 'босс' in enemy.difficulty.lower():
        enemy.health_max += 10
        enemy.health = enemy.health_max
        enemy.damage += 2

# ПРИМЕРЫ ХУКОВ AI
def on_ai_creation(enemy, difficulty, hook_system):
    """Хук создания AI для врага"""
    print(f"🤖 Создан AI для {enemy.name} (сложность: {difficulty})")
    # Можно вернуть кастомный AI объект
    return None

def on_ai_decision(enemy, player, current_round, base_decision, hook_system):
    """Хук принятия решения AI - может изменить действие врага"""
    # Пример: всегда атаковать если здоровье игрока ниже 30%
    if hasattr(player, 'health') and hasattr(player, 'health_max'):
        health_percent = player.health / player.health_max
        if health_percent < 0.3:
            return "attack"  # Добивание игрока
    return base_decision  # Или None чтобы использовать стандартную логику

def on_ai_learning_update(ai_instance, battle_result, player_actions, hook_system):
    """Хук обновления обучения AI"""
    print(f"🧠 AI обучается на основе результата: {battle_result}")

# 📋 РЕГИСТРАЦИЯ ХУКОВ
HOOK_REGISTRY = {
    'player_created': on_player_created,
    'battle_start': on_battle_start,
    'damage_calculation': on_damage_calculation,
    'enemy_creation': on_enemy_creation,
    # РЕГИСТРАЦИЯ AI ХУКОВ
    'ai_creation': on_ai_creation,
    'ai_decision': on_ai_decision,
    'ai_learning_update': on_ai_learning_update,
}
'''
            makedirs(path.dirname(example_mod_path), exist_ok=True)
            with open(example_mod_path, 'w', encoding='utf-8') as f:
                f.write(example_code)

    def register_mod_hooks(self, mod_module, mod_name):
        """Регистрирует хуки из мода"""
        if hasattr(mod_module, 'HOOK_REGISTRY'):
            for hook_name, hook_function in mod_module.HOOK_REGISTRY.items():
                self.register_hook(hook_name, hook_function)
                settings.log_info(f"   ✅ Хук зарегистрирован: {hook_name}")

        # Вызываем функцию инициализации мода если есть
        if hasattr(mod_module, 'mod_initialize'):
            try:
                mod_module.mod_initialize(self)
            except Exception as e:
                settings.log_error(f"❌ Ошибка инициализации мода {mod_name}: {e}")

    def register_hook(self, hook_name: str, hook_function: Callable):
        """Регистрация функции хука"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(hook_function)

    def execute_hook(self, hook_name: str, *args, **kwargs) -> Any:
        """Выполнение всех функций зарегистрированных на хук"""
        results = []

        if hook_name in self.hooks:
            for hook_func in self.hooks[hook_name]:
                try:
                    sig = signature(hook_func)
                    if 'hook_system' in sig.parameters:
                        result = hook_func(*args, hook_system=self, **kwargs)
                    else:
                        result = hook_func(*args, **kwargs)

                    if result is not None:
                        results.append(result)

                except Exception as e:
                    settings.log_error(f"❌ Ошибка выполнения хука {hook_name}: {e}")

        # Возвращаем последний результат или None
        return results[-1] if results else None

    def execute_hook_chain(self, hook_name: str, initial_value: Any, *args, **kwargs) -> Any:
        """Выполнение цепочки хуков с передачей результата"""
        current_value = initial_value

        if hook_name in self.hooks:
            for hook_func in self.hooks[hook_name]:
                try:
                    sig = signature(hook_func)
                    if 'hook_system' in sig.parameters:
                        current_value = hook_func(current_value, *args, hook_system=self, **kwargs)
                    else:
                        current_value = hook_func(current_value, *args, **kwargs)
                except Exception as e:
                    settings.log_error(f"❌ Ошибка выполнения хука {hook_name}: {e}")

        return current_value

    @staticmethod
    def get_available_hooks() -> Dict[str, List[str]]:
        """Возвращает список доступных хуков"""
        return {
            'system': [
                'game_initialized', 'game_shutdown', 'config_loaded'
            ],
            'save_load': [
                'pre_save_game', 'post_save_game', 'pre_load_game', 'post_load_game'
            ],
            'menu': [
                'main_menu_created', 'main_menu_selection'
            ],
            'player': [
                'player_created', 'player_level_up', 'player_stat_update',
                'player_death', 'player_revive'
            ],
            'battle': [
                'battle_start', 'battle_end', 'round_start', 'round_end'
            ],
            'turns': [
                'player_turn_start', 'player_action_selected', 'player_turn_end',
                'enemy_turn_start', 'enemy_action_selected', 'enemy_turn_end'
            ],
            'calculations': [
                'damage_calculation', 'healing_calculation', 'critical_calculation'
            ],
            'effects': [
                'effect_application', 'effect_processing', 'effect_removal'
            ],
            'items': [
                'item_use', 'item_purchase', 'item_drop'
            ],
            'enemies': [
                'enemy_creation', 'enemy_defeated', 'enemy_ability_use'
            ],
            'ui': [
                'ui_display', 'text_display', 'color_scheme'
            ],
            'mods': [
                'mod_loaded', 'mod_activated', 'mod_deactivated'
            ],
            # AI ХУКИ
            'ai_system': [
                'ai_creation',           # Создание AI (enemy, difficulty) -> может вернуть кастомный AI
                'ai_created',            # После создания AI (ai_instance, enemy, difficulty)
                'ai_decision',           # Принятие решения AI (enemy, player, current_round, base_decision) -> может изменить решение
                'ai_action_processed',   # Обработка действия AI (enemy, player, action, result)
                'ai_learning_update',    # Обновление обучения AI (ai_instance, battle_result, player_actions)
                'ai_turn_start',         # Начало хода AI (enemy, player)
                'ai_turn_end',           # Конец хода AI (enemy, player, action)
            ]
        }

    def get_loaded_mods(self):
        """Возвращает список загруженных модов"""
        return list(self.modules.keys())

    def reload_mods(self):
        """Перезагрузка всех модов"""
        self.hooks.clear()
        self.modules.clear()
        self.load_mods()
        print("✅ Все моды перезагружены!")
        settings.log_info("✅ Все моды перезагружены!")


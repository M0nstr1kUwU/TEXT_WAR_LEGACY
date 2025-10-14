# [file name]: src/modding/support_mods.py
from json import load
from os import path, makedirs, listdir
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
            except Exception as e:
                settings.log_error(e)
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
                mod_name = filename[:-3]  # Убираем .py
                try:
                    spec = importlib.util.spec_from_file_location(mod_name, path.join(mods_dir, filename))
                    mod_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod_module)
                    self.modules[mod_name] = mod_module
                    print(f"✅ Мод загружен: {mod_name}")
                    settings.log_info(f"✅ Мод загружен: {mod_name}")

                    # Регистрируем хуки из мода
                    self.register_mod_hooks(mod_module, mod_name)

                except Exception as e:
                    settings.log_error(f"❌ Ошибка загрузки мода {mod_name}: {e}")

    def create_example_mod(self):
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
    if player and hasattr(player, 'damage'):
        player.damage += 1
        player.health_max += 5
        player.health = player.health_max
        print(f"💪 Мод: Игрок усилен! Урон: {player.damage}, Здоровье: {player.health_max}")

def on_battle_start(player, enemy, mode, hook_system):
    """Хук начала битвы - добавляет специальные эффекты"""
    if player and enemy:
        print(f"🔥 Мод: Началась эпическая битва! {player.name} vs {enemy.name}")

def on_damage_calculation(attacker, defender, base_damage, element, is_critical, hook_system):
    """Хук расчета урона - добавляет элементные бонусы"""
    element_bonus = {
        'fire': 1.2,
        'ice': 1.15, 
        'nature': 1.1,
        'none': 1.0
    }
    bonus = element_bonus.get(element, 1.0)
    return int(base_damage * bonus)

def on_enemy_creation(enemy, difficulty, hook_system):
    """Хук создания врага - усиливает боссов"""
    if enemy and hasattr(enemy, 'difficulty'):
        if 'boss' in enemy.difficulty.lower() or 'epic' in enemy.difficulty.lower():
            enemy.health_max += 10
            enemy.health = enemy.health_max
            enemy.damage += 2
            print(f"👹 Мод: Враг усилен!")

# 📋 РЕГИСТРАЦИЯ ХУКОВ
HOOK_REGISTRY = {
    'player_created': on_player_created,
    'battle_start': on_battle_start,
    'damage_calculation': on_damage_calculation,
    'enemy_creation': on_enemy_creation
}
'''
            makedirs(path.dirname(example_mod_path), exist_ok=True)
            with open(example_mod_path, 'w', encoding='utf-8') as f:
                f.write(example_code)

    def register_mod_hooks(self, mod_module, mod_name):
        """Регистрирует хуки из мода"""
        if hasattr(mod_module, 'HOOK_REGISTRY'):
            for hook_name, hook_function in mod_module.HOOK_REGISTRY.items():
                if isinstance(hook_function, list):
                    for func in hook_function:
                        if callable(func):
                            self.register_hook(hook_name, func)
                            settings.log_info(f"   ✅ Хук зарегистрирован: {hook_name} (из списка)")
                elif callable(hook_function):
                    self.register_hook(hook_name, hook_function)
                    settings.log_info(f"   ✅ Хук зарегистрирован: {hook_name}")
                else:
                    settings.log_warning(f"   ⚠️ Некорректный хук в моде {mod_name}: {hook_name}")

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
                    if not callable(hook_func):
                        settings.log_warning(f"⚠️ Некорректный хук {hook_name}: {hook_func}")
                        continue

                    sig = signature(hook_func)
                    params = sig.parameters

                    # Подготавливаем аргументы
                    call_kwargs = kwargs.copy()

                    # Добавляем hook_system если функция его принимает
                    if 'hook_system' in params:
                        call_kwargs['hook_system'] = self

                    # Добавляем позиционные аргументы по порядку
                    call_args = list(args)

                    # Выполняем функцию
                    result = hook_func(*call_args, **call_kwargs)

                    if result is not None:
                        results.append(result)

                except Exception as e:
                    func_name = getattr(hook_func, '__name__', 'unknown_function')
                    settings.log_error(f"❌ Ошибка выполнения хука {hook_name} в функции {func_name}: {e}")

        return results[-1] if results else None

    def execute_hook_chain(self, hook_name: str, initial_value: Any, *args, **kwargs) -> Any:
        """Выполнение цепочки хуков с передачей результата"""
        current_value = initial_value

        if hook_name in self.hooks:
            for hook_func in self.hooks[hook_name]:
                try:
                    if not callable(hook_func):
                        continue

                    sig = signature(hook_func)
                    params = list(sig.parameters.keys())

                    if 'hook_system' in params:
                        current_value = hook_func(current_value, *args, hook_system=self, **kwargs)
                    else:
                        current_value = hook_func(current_value, *args, **kwargs)
                except Exception as e:
                    func_name = getattr(hook_func, '__name__', 'unknown_function')
                    print(f"❌ Ошибка выполнения хука {hook_name}: {e}")

        return current_value

    @staticmethod
    def get_available_hooks() -> Dict[str, List[str]]:
        """Возвращает список доступных хуков"""
        return {
            # === СИСТЕМНЫЕ ХУКИ ===
            'system': [
                'game_initialized',  # Игра инициализирована (globals) - можно модифицировать глобальные переменные
                'game_shutdown',  # Игра завершается () - выполнить финальные действия
                'config_loaded',  # Конфигурация загружена (config_data) - можно модифицировать настройки
            ],

            # === СОХРАНЕНИЕ И ЗАГРУЗКА ===
            'save_load': [
                'pre_save_game',  # Перед сохранением игры (player_data) - можно модифицировать данные для сохранения
                'post_save_game',  # После сохранения игры (player_data, success) - уведомление о результате сохранения
                'pre_load_game',  # Перед загрузкой игры (data) - можно модифицировать загружаемые данные
                'post_load_game',  # После загрузки игры (player, success) - уведомление о результате загрузки
            ],

            # === МЕНЮ И ИНТЕРФЕЙС ===
            'menu': [
                'main_menu_created',  # Главное меню создано (menu_instance) - можно модифицировать меню
                'main_menu_selection',  # Выбор в главном меню (choice, result) - может изменить результат выбора
            ],

            # === ИГРОК ===
            'player': [
                'player_created',  # Игрок создан (player) - можно модифицировать характеристики игрока
                'player_level_up',  # Игрок повысил уровень (player) - выполнить действия при повышении уровня
                'player_stat_update',  # Статистика игрока обновлена (player) - можно модифицировать статистику
                'player_death',  # Игрок умер (player, cause) - выполнить действия при смерти
                'player_revive',  # Игрок воскрес (player) - выполнить действия при воскрешении
            ],

            # === БИТВА ===
            'battle': [
                'battle_start',  # Начало битвы (player, enemy, mode) - выполнить действия при начале битвы
                'battle_end',  # Конец битвы (player, enemy, result) - выполнить действия при завершении битвы
                'round_start',  # Начало раунда (player, enemy, round_number) - выполнить действия в начале раунда
                'round_end',  # Конец раунда (player, enemy, round_number) - выполнить действия в конце раунда
            ],

            # === ХОДЫ В БИТВЕ ===
            'turns': [
                'player_turn_start',  # Начало хода игрока (player, enemy) - выполнить действия перед ходом игрока
                'player_action_selected', # Игрок выбрал действие (player, enemy, action) - может изменить выбранное действие
                'player_turn_end',  # Конец хода игрока (player, enemy, action) - выполнить действия после хода игрока
                'enemy_turn_start',  # Начало хода врага (enemy, player) - выполнить действия перед ходом врага
                'enemy_action_selected', # Враг выбрал действие (enemy, player, action) - может изменить выбранное действие врага
                'enemy_turn_end',  # Конец хода врага (enemy, player, action) - выполнить действия после хода врага
            ],

            # === РАСЧЕТЫ И МЕХАНИКИ ===
            'calculations': [
                'damage_calculation', # Расчет урона (attacker, defender, base_damage, element, is_critical) -> может изменить урон
                'healing_calculation',  # Расчет лечения (healer, target, base_heal) -> может изменить лечение
                'critical_calculation', # Расчет критического удара (attacker, defender, base_chance) -> может изменить шанс крита
            ],

            # === ЭФФЕКТЫ И СОСТОЯНИЯ ===
            'effects': [
                'effect_application',  # Применение эффекта (target, effect_type, power) -> может изменить эффект
                'effect_processing',  # Обработка эффекта (target, effect) -> может изменить обработку эффекта
                'effect_removal',  # Удаление эффекта (target, effect_type) -> выполнить действия при удалении эффекта
            ],

            # === ПРЕДМЕТЫ ===
            'items': [
                'item_use',  # Использование предмета (player, item, target) -> может изменить результат использования
                'item_purchase',  # Покупка предмета (player, item, price) -> может изменить цену или отменить покупку
                'item_drop',  # Выпадение предмета (player, item) -> может изменить выпадающий предмет
            ],

            # === ВРАГИ ===
            'enemies': [
                'enemy_creation',  # Создание врага (enemy, difficulty) -> может изменить врага или вернуть кастомного
                'enemy_defeated',  # Враг побежден (enemy, player) - выполнить действия при победе над врагом
                'enemy_ability_use', # Враг использует способность (enemy, player, ability) -> может изменить способность
            ],

            # === ПОЛЬЗОВАТЕЛЬСКИЙ ИНТЕРФЕЙС ===
            'ui': [
                'ui_display',  # Отображение UI (ui_element, data) -> может изменить данные для отображения
                'text_display',  # Отображение текста (text, context) -> может изменить текст
                'color_scheme',  # Цветовая схема (scheme_name) -> может изменить цветовую схему
            ],

            # === МОДЫ ===
            'mods': [
                'mod_loaded',  # Мод загружен (mod_name, mod_instance) - уведомление о загрузке мода
                'mod_activated',  # Мод активирован (mod_name) - выполнить действия при активации мода
                'mod_deactivated',  # Мод деактивирован (mod_name) - выполнить действия при деактивации мода
            ],

            # === СИСТЕМА ИСКУССТВЕННОГО ИНТЕЛЛЕКТА ===
            'ai_system': [
                'ai_creation',  # Создание AI (enemy, difficulty) -> может вернуть кастомный AI объект
                'ai_created',  # После создания AI (ai_instance, enemy, difficulty) - уведомление о создании AI
                'ai_decision', # Принятие решения AI (enemy, player, current_round, base_decision) -> может изменить решение
                'ai_action_processed', # Обработка действия AI (enemy, player, action, result) - уведомление о выполнении действия
                'ai_learning_update', # Обновление обучения AI (ai_instance, battle_result, player_actions) - может модифицировать обучение
                'ai_turn_start',  # Начало хода AI (enemy, player) - выполнить действия перед ходом AI
                'ai_turn_end',  # Конец хода AI (enemy, player, action) - выполнить действия после хода AI
                'ai_special_ability', # Использование специальной способности AI (ai_instance, enemy, player, ability_type) -> может изменить способность
                'ai_phase_change',  # Смена фазы AI (ai_instance, old_phase, new_phase) - уведомление о смене фазы
            ],

            # === ЭЛЕМЕНТАЛЬНАЯ СИСТЕМА ===
            'elemental_system': [
                'element_applied', # Применение элемента к сущности (entity, element_type) - уведомление о применении элемента
                'elemental_damage_multiplier', # Расчет множителя урона (attacker_element, defender_element, multiplier) -> может изменить множитель
                'elemental_damage_calculation', # Расчет элементного урона (attacker, defender, base_damage, multiplier) -> может изменить урон
                'custom_element_creation', # Создание кастомного элемента (element_data) -> может изменить данные элемента
            ],

            # === СИСТЕМА КЛАССОВ ===
            'class_system': [
                'class_selected',  # Выбор класса (player, game_class) - уведомление о выборе класса
                'class_reset',  # Сброс класса (player) - выполнить действия при сбросе класса
                'ability_used', # Использование способности (player, ability, target) -> может изменить результат способности
                'skill_learned',  # Изучение навыка (player, skill_node) - уведомление об изучении навыка
                'skill_points_added',  # Добавление очков навыков (class_type, points) - уведомление о добавлении очков
                'skill_unlocked',  # Разблокировка навыка (class_type, node_id, node) - уведомление о разблокировке
                'custom_class_creation',  # Создание кастомного класса (class_data) -> может изменить данные класса
            ],
        }

    def get_loaded_mods(self) -> List[str]:
        """Возвращает список загруженных модов"""
        return list(self.modules.keys())


# Глобальный экземпляр системы хуков
hook_system = HookSystem()

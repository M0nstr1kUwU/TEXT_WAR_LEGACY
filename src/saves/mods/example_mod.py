"""
МОД: example_mod
Автор: M0nstr1k
Описание: Пример мода для демонстрации
"""
from settings.settings_manager import settings


def mod_initialize(hook_system):
    """Инициализация мода"""
    settings.log_info(f"✅ Мод 'example_mod' загружен!")
    return True


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
            settings.log_info(f"👹 Мод: Враг усилен!")


# 📋 РЕГИСТРАЦИЯ ХУКОВ
HOOK_REGISTRY = {
    'damage_calculation': on_damage_calculation,
    'enemy_creation': on_enemy_creation
}
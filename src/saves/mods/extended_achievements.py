# [file name]: src/saves/mods/extended_achievements.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
"""
🎮 МОД: EXTENDED ACHIEVEMENTS
Автор: Text War Legacy Team
Описание: Добавляет расширенную систему достижений с новыми типами, наградами и визуальными эффектами
Версия: 3.0
"""
from settings.settings_manager import settings


def mod_initialize(hook_system):
    """Инициализация мода с расширенными достижениями"""
    settings.log_info("🎮 Мод 'Extended Achievements' загружен!")

    # Регистрируем кастомные хуки
    register_custom_hooks(hook_system)

    return True


def on_battle_end_custom(player, enemy, result, hook_system):
    """Хук конца битвы для расширенной статистики"""
    try:
        if not hasattr(player, 'extended_stats'):
            player.extended_stats = {
                'combo_critical_streak': 0,
                'current_critical_streak': 0,
                'fast_victories': 0,
                'perfect_victories': 0,
                'low_health_victories': 0,
                'potions_used': 0
            }

        # Обновляем статистику только если битва завершена и игрок жив
        if result == "win" and player.isAlive:
            # Проверяем быструю победу
            if hasattr(enemy, 'battle_turns') and enemy.battle_turns <= 3:
                player.extended_stats['fast_victories'] += 1
                print(f"⚡ Быстрая победа за {enemy.battle_turns} ходов!")

            # Проверяем победу с низким здоровьем
            if player.health <= player.health_max * 0.1:
                player.extended_stats['low_health_victories'] += 1
                print(f"🎲 Победа с низким здоровьем: {player.health}/{player.health_max}")

            # Сбрасываем текущее комбо после битвы
            player.extended_stats['current_critical_streak'] = 0

    except Exception as e:
        print(f"⚠️ Ошибка в статистике битвы: {e}")
        settings.log_error(f"⚠️ Ошибка в статистике битвы: {e}")

    return result


def on_damage_calculated_custom(attacker, defender, damage, is_critical, element, hook_system):
    """Хук расчета урона для комбо-системы"""
    try:
        # Проверяем, является ли атакующий игроком (безопасно)
        if hasattr(attacker, 'name') and hasattr(attacker, 'extended_stats'):
            if is_critical:
                attacker.extended_stats['current_critical_streak'] += 1
                attacker.extended_stats['combo_critical_streak'] = max(
                    attacker.extended_stats['combo_critical_streak'],
                    attacker.extended_stats['current_critical_streak']
                )
                print(f"🔥 Критический удар! Комбо: {attacker.extended_stats['current_critical_streak']}")
            else:
                if attacker.extended_stats['current_critical_streak'] > 0:
                    print(f"💥 Комбо прервано на {attacker.extended_stats['current_critical_streak']}")
                attacker.extended_stats['current_critical_streak'] = 0

    except Exception as e:
        print(f"⚠️ Ошибка в комбо-системе: {e}")
        settings.log_error(f"⚠️ Ошибка в комбо-системе: {e}")

    return damage


def on_item_used_custom(player, item_type, effect, hook_system):
    """Хук использования предмета"""
    if hasattr(player, 'extended_stats') and item_type == 'potion':
        player.extended_stats['potions_used'] += 1
        print(f"🧪 Использовано зелий: {player.extended_stats['potions_used']}")

    return effect


def on_achievement_stat_value_custom(condition, player, player_stats, hook_system):
    """Хук для кастомных условий достижений"""
    if not hasattr(player, 'extended_stats'):
        return None

    extended_stats = player.extended_stats

    # Обрабатываем кастомные условия
    condition_handlers = {
        'combo_critical_streak': lambda: extended_stats.get('combo_critical_streak', 0),
        'perfect_boss_victory': lambda: extended_stats.get('perfect_victories', 0),
        'fast_victory_turns': lambda: 1 if extended_stats.get('fast_victories', 0) > 0 else 0,
        'fast_victories_count': lambda: extended_stats.get('fast_victories', 0),
        'perfect_defense_streak': lambda: player_stats.get('perfect_defenses', 0),
        'low_health_victory': lambda: extended_stats.get('low_health_victories', 0),
        'potions_used_total': lambda: extended_stats.get('potions_used', 0),
        'all_elements_used': lambda: 1 if len(player_stats.get('elements_used', set())) >= 3 else 0,
        'coins_saved': lambda: player.coin,
        'all_shop_categories': lambda: 1 if len(player_stats.get('shop_categories', set())) >= 4 else 0,
        'player_level': lambda: player.level,
        'achievements_unlocked': lambda: len(getattr(player, 'unlocked_achievements', [])),
        'easter_egg_found': lambda: player_stats.get('easter_eggs_found', 0),
        'lucky_critical_streak': lambda: extended_stats.get('combo_critical_streak', 0),
        'dodge_streak': lambda: player_stats.get('dodge_streak', 0),
        'elemental_mastery': lambda: 1 if all(
            dmg >= 1000 for dmg in player_stats.get('elemental_damage', {}).values()) else 0,
    }

    if condition in condition_handlers:
        return condition_handlers[condition]()

    return None


def on_achievement_display_custom(display_data, achievement, player, hook_system):
    """Хук для кастомного отображения достижений"""
    if achievement is None:
        return display_data

    try:
        # Добавляем специальные иконки для скрытых достижений
        if getattr(achievement, 'hidden', False) and not display_data['unlocked']:
            display_data['name'] = "❓ Секретное достижение"
            display_data['description'] = "??? (разблокируйте чтобы увидеть)"
            display_data['reward_text'] = "???"

        # Добавляем анимацию для легендарных достижений
        if (getattr(achievement, 'tier', None) and
                getattr(achievement.tier, 'value', '') == 'legendary' and
                display_data['unlocked']):
            display_data['icon'] = "✨👑✨"

    except AttributeError as e:
        print(f"⚠️ Ошибка в хуке отображения достижений: {e}")
        settings.log_error(f"⚠️ Ошибка в хуке отображения достижений: {e}")

    return display_data


def on_achievement_unlocked_custom(achievement_id, player, hook_system):
    """Хук разблокировки достижения со спецэффектами (ИСПРАВЛЕННАЯ ВЕРСИЯ)"""
    try:
        achievements_manager = getattr(hook_system, 'achievements_manager', None)
        if not achievements_manager:
            return

        achievement = achievements_manager.get_achievement_by_id(achievement_id)
        if not achievement:
            return

        # Специальные эффекты для разных уровней достижений
        achievement_tier = getattr(achievement, 'tier', None)
        if achievement_tier and getattr(achievement_tier, 'value', '') == 'legendary':
            print("\n" + "✨" * 50)
            print(f"✨ ЛЕГЕНДАРНОЕ ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО! ✨")
            print(f"✨ {achievement.name} ✨")
            print("✨" * 50)

            # БЕЗОПАСНОЕ ДОБАВЛЕНИЕ БОНУСОВ
            player.coin += 500  # Это уже int, безопасно
            player.experience += 1000  # Это уже int, безопасно
            print(f"✨ БОНУС: +500 монет, +1000 опыта! ✨")

        elif achievement_tier and getattr(achievement_tier, 'value', '') == 'platinum':
            print(f"\n💎 ПЛАТИНОВОЕ ДОСТИЖЕНИЕ: {achievement.name}")

    except Exception as e:
        print(f"⚠️ Ошибка в хуке разблокировки достижений: {e}")
        settings.log_error(f"⚠️ Ошибка в хуке разблокировки достижений: {e}")


def register_custom_hooks(hook_system):
    """Регистрирует кастомные хуки для расширенных достижений"""
    hook_system.register_hook('battle_end', on_battle_end_custom)
    hook_system.register_hook('damage_calculation', on_damage_calculated_custom)
    hook_system.register_hook('item_use', on_item_used_custom)
    hook_system.register_hook('achievement_stat_value', on_achievement_stat_value_custom)
    hook_system.register_hook('achievement_display', on_achievement_display_custom)
    hook_system.register_hook('achievement_unlocked', on_achievement_unlocked_custom)

    settings.log_info("   ✅ Зарегистрировано 6 кастомных хуков")


# 📋 РЕГИСТРАЦИЯ ХУКОВ
HOOK_REGISTRY = {
    'battle_end': on_battle_end_custom,
    'damage_calculation': on_damage_calculated_custom,
    'item_use': on_item_used_custom,
    'achievement_stat_value': on_achievement_stat_value_custom,
    'achievement_display': on_achievement_display_custom,
    'achievement_unlocked': on_achievement_unlocked_custom
}
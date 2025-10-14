"""
🎮 МОД: EPIC ARTIFACTS
Автор: Text War Legacy Team
Описание: Добавляет мощные артефакты с уникальными способностями
Версия: 2.0 (адаптирован для новой системы)
"""
from settings.settings_manager import settings


def mod_initialize(hook_system):
    """Инициализация мода с эпическими артефактами"""
    settings.log_info("🎮 Мод 'Epic Artifacts' загружен! Доступно 6 уникальных артефактов.")

    # Регистрируем кастомные хуки для способностей
    register_artifact_hooks(hook_system)

    return True


def register_artifact_hooks(hook_system):
    """Регистрирует хуки для работы артефактов"""

    # Хук для Молота Грома (оглушение)
    def thunder_hammer_effect(attacker, defender, damage, is_critical, element, hook_system):
        inventory_manager = getattr(hook_system, 'inventory_manager', None)
        if inventory_manager:
            item_id = "epic_artifacts_thunder_hammer"
            if (inventory_manager.has_item(item_id) and
                inventory_manager.items[item_id].equipped):
                import random
                if random.random() <= 0.3:  # 30% шанс оглушения
                    if hasattr(defender, 'stunned'):
                        defender.stunned = True
                        defender.stun_duration = 1
                        print("⚡ Молот Грома ОГЛУШАЕТ врага на 1 ход!")

                        # Записываем статистику
                        if hasattr(attacker, 'artifact_stats'):
                            attacker.artifact_stats['enemies_stunned'] = attacker.artifact_stats.get('enemies_stunned', 0) + 1
                        else:
                            attacker.artifact_stats = {'enemies_stunned': 1}
        return damage

    # Хук для Доспеха Феникса (воскрешение)
    def phoenix_armor_effect(player, damage, hook_system):
        inventory_manager = getattr(hook_system, 'inventory_manager', None)
        if inventory_manager:
            item_id = "epic_artifacts_phoenix_armor"
            if (inventory_manager.has_item(item_id) and
                inventory_manager.items[item_id].equipped and
                not getattr(player, 'phoenix_used', False) and player.health <= 0):

                player.health = int(player.health_max * 0.5)  # Воскрешение с 50% HP
                player.phoenix_used = True
                print("🔥 Доспех Феникса ВОСКРЕШАЕТ вас с 50% здоровья!")

                # Записываем статистику
                if hasattr(player, 'artifact_stats'):
                    player.artifact_stats['phoenix_resurrections'] = player.artifact_stats.get('phoenix_resurrections', 0) + 1
                else:
                    player.artifact_stats = {'phoenix_resurrections': 1}

                return 0  # Отменяем смерть
        return damage

    # Хук для Амулета Вампира (вампиризм)
    def vampire_amulet_effect(attacker, defender, damage, is_critical, element, hook_system):
        inventory_manager = getattr(hook_system, 'inventory_manager', None)
        if inventory_manager:
            item_id = "epic_artifacts_vampire_amulet"
            if (inventory_manager.has_item(item_id) and
                inventory_manager.items[item_id].equipped):
                heal_amount = int(damage * 0.25)  # 25% вампиризм
                attacker.health = min(attacker.health + heal_amount, attacker.health_max)
                print(f"🦇 Амулет Вампира восстанавливает {heal_amount} HP!")
        return damage

    # Хук для Медальона Времени (дополнительный ход)
    def time_medallion_effect(player, current_turn, hook_system):
        inventory_manager = getattr(hook_system, 'inventory_manager', None)
        if inventory_manager:
            item_id = "epic_artifacts_time_medallion"
            if (inventory_manager.has_item(item_id) and
                inventory_manager.items[item_id].equipped and
                current_turn % 3 == 0):  # Каждый 3-й ход
                print("⏰ Медальон Времени дает дополнительный ход!")
                return True  # Даем дополнительный ход
        return False

    # Хук для Сферы Стихий (случайный элемент)
    def elemental_orb_effect(attacker, defender, damage, is_critical, element, hook_system):
        inventory_manager = getattr(hook_system, 'inventory_manager', None)
        if inventory_manager:
            item_id = "epic_artifacts_elemental_orb"
            if (inventory_manager.has_item(item_id) and
                inventory_manager.items[item_id].equipped):
                import random
                elements = ['fire', 'ice', 'nature']
                random_element = random.choice(elements)
                bonus_damage = 10
                print(f"🌀 Сфера Стихий добавляет {random_element} урон: +{bonus_damage}")

                # Обновляем статистику элементов
                if hasattr(attacker, 'elements_used'):
                    attacker.elements_used.add(random_element)
                else:
                    attacker.elements_used = {random_element}

                return damage + bonus_damage
        return damage

    # Хук для Сундука-Мимика (азартный предмет)
    def mimic_chest_effect(player, item_id, hook_system):
        if item_id == "epic_artifacts_mimic_chest":
            import random
            if random.random() <= 0.5:  # 50% шанс
                reward = 500
                player.coin += reward
                print(f"🎁 Сундук-Мимик: ВЫИГРЫШ! +{reward} монет!")

                # Записываем статистику
                if hasattr(player, 'gambling_stats'):
                    player.gambling_stats['wins'] = player.gambling_stats.get('wins', 0) + 1
                    player.gambling_stats['total_won'] = player.gambling_stats.get('total_won', 0) + reward
                else:
                    player.gambling_stats = {'wins': 1, 'total_won': reward}
            else:
                penalty = 200
                player.coin = max(0, player.coin - penalty)
                print(f"🎁 Сундук-Мимик: ПРОИГРЫШ! -{penalty} монет.")

                # Записываем статистику
                if hasattr(player, 'gambling_stats'):
                    player.gambling_stats['losses'] = player.gambling_stats.get('losses', 0) + 1
                    player.gambling_stats['total_lost'] = player.gambling_stats.get('total_lost', 0) + penalty
                else:
                    player.gambling_stats = {'losses': 1, 'total_lost': penalty}

            # Удаляем предмет после использования (если это consumable)
            inventory_manager = getattr(hook_system, 'inventory_manager', None)
            if inventory_manager and inventory_manager.has_item(item_id):
                inventory_manager.remove_item(item_id)
                print("📦 Сундук-Мимик использован и удален из инвентаря")

            return True  # Предмет использован
        return False

    # Хук для подсчета собранных артефактов
    def artifact_collection_tracker(player, hook_system):
        """Отслеживает количество собранных артефактов"""
        inventory_manager = getattr(hook_system, 'inventory_manager', None)
        if inventory_manager:
            artifact_count = 0
            artifact_items = [
                "epic_artifacts_thunder_hammer",
                "epic_artifacts_phoenix_armor",
                "epic_artifacts_vampire_amulet",
                "epic_artifacts_time_medallion",
                "epic_artifacts_elemental_orb",
                "epic_artifacts_mimic_chest"
            ]

            for artifact_id in artifact_items:
                if inventory_manager.has_item(artifact_id):
                    artifact_count += 1

            # Обновляем статистику
            if hasattr(player, 'artifact_stats'):
                player.artifact_stats['artifacts_collected'] = artifact_count
            else:
                player.artifact_stats = {'artifacts_collected': artifact_count}

            return artifact_count
        return 0

    # Хук для применения эффектов при экипировке
    def on_item_equip(player, item_id, hook_system):
        """Применяет пассивные эффекты артефактов при экипировке"""
        if not item_id.startswith("epic_artifacts_"):
            return

        artifact_effects = {
            "epic_artifacts_thunder_hammer": {"damage": 15},
            "epic_artifacts_phoenix_armor": {"shield_hp": 35},
            "epic_artifacts_vampire_amulet": {"health_bonus": 20},
            "epic_artifacts_time_medallion": {"speed_bonus": 10},
            "epic_artifacts_elemental_orb": {"damage": 8}
        }

        if item_id in artifact_effects:
            effects = artifact_effects[item_id]
            for effect, value in effects.items():
                if hasattr(player, effect):
                    current = getattr(player, effect)
                    setattr(player, effect, current + value)
                    print(f"💫 {item_id.split('_')[-1].title()}: +{value} к {effect}")

    # Хук для снятия эффектов при разэкипировке
    def on_item_unequip(player, item_id, hook_system):
        """Снимает пассивные эффекты артефактов при разэкипировке"""
        if not item_id.startswith("epic_artifacts_"):
            return

        artifact_effects = {
            "epic_artifacts_thunder_hammer": {"damage": 15},
            "epic_artifacts_phoenix_armor": {"shield_hp": 35},
            "epic_artifacts_vampire_amulet": {"health_bonus": 20},
            "epic_artifacts_time_medallion": {"speed_bonus": 10},
            "epic_artifacts_elemental_orb": {"damage": 8}
        }

        if item_id in artifact_effects:
            effects = artifact_effects[item_id]
            for effect, value in effects.items():
                if hasattr(player, effect):
                    current = getattr(player, effect)
                    setattr(player, effect, current - value)
                    print(f"🔻 {item_id.split('_')[-1].title()}: -{value} к {effect}")

    # Регистрируем все хуки
    hook_system.register_hook('damage_calculation', thunder_hammer_effect)
    hook_system.register_hook('player_take_damage', phoenix_armor_effect)
    hook_system.register_hook('damage_calculation', vampire_amulet_effect)
    hook_system.register_hook('battle_turn_start', time_medallion_effect)
    hook_system.register_hook('damage_calculation', elemental_orb_effect)
    hook_system.register_hook('item_use', mimic_chest_effect)
    hook_system.register_hook('player_stat_update', artifact_collection_tracker)
    hook_system.register_hook('item_equipped', on_item_equip)
    hook_system.register_hook('item_unequipped', on_item_unequip)

    settings.log_info("   ✅ Зарегистрировано 8 специальных способностей артефактов")


def on_achievement_stat_value_custom(condition, player, player_stats, hook_system):
    """Хук для кастомных условий достижений артефактов"""

    if not hasattr(player, 'artifact_stats'):
        player.artifact_stats = {}

    artifact_stats = player.artifact_stats

    # Обрабатываем кастомные условия
    condition_handlers = {
        'epic_artifacts_collected': lambda: artifact_stats.get('artifacts_collected', 0),
        'enemies_stunned': lambda: artifact_stats.get('enemies_stunned', 0),
        'phoenix_resurrections': lambda: artifact_stats.get('phoenix_resurrections', 0),
        'gambling_wins': lambda: getattr(player, 'gambling_stats', {}).get('wins', 0),
    }

    if condition in condition_handlers:
        return condition_handlers[condition]()

    return None


def on_player_level_up_custom(player, old_level, new_level, hook_system):
    """Хук повышения уровня для разблокировки артефактов"""
    if new_level >= 5:
        print("💡 Теперь доступен Сундук-Мимик в магазине!")
    if new_level >= 8:
        print("💡 Теперь доступен Амулет Вампира в магазине!")
    if new_level >= 10:
        print("💡 Теперь доступны Молот Грома и Сфера Стихий в магазине!")
    if new_level >= 12:
        print("💡 Теперь доступен Медальон Времени в магазине!")
    if new_level >= 15:
        print("💡 Теперь доступен Доспех Феникса в магазине!")


def on_battle_start_custom(player, enemy, mode, hook_system):
    """Сбрасываем состояния артефактов в начале битвы"""
    # Сбрасываем использование Доспеха Феникса
    if hasattr(player, 'phoenix_used'):
        player.phoenix_used = False

    # Сбрасываем оглушение врага
    if hasattr(enemy, 'stunned'):
        enemy.stunned = False
        enemy.stun_duration = 0


def on_battle_end_custom(player, enemy, result, hook_system):
    """Обработка окончания битвы для статистики артефактов"""
    if result == "win":
        # Обновляем статистику артефактов
        inventory_manager = getattr(hook_system, 'inventory_manager', None)
        if inventory_manager:
            artifact_count = 0
            artifact_items = [
                "epic_artifacts_thunder_hammer",
                "epic_artifacts_phoenix_armor",
                "epic_artifacts_vampire_amulet",
                "epic_artifacts_time_medallion",
                "epic_artifacts_elemental_orb",
                "epic_artifacts_mimic_chest"
            ]

            for artifact_id in artifact_items:
                if inventory_manager.has_item(artifact_id):
                    artifact_count += 1

            # Обновляем статистику игрока
            if hasattr(player, 'artifact_stats'):
                player.artifact_stats['artifacts_collected'] = artifact_count
            else:
                player.artifact_stats = {'artifacts_collected': artifact_count}


def on_player_created_custom(player, hook_system):
    """Инициализация статистики артефактов при создании игрока"""
    if not hasattr(player, 'artifact_stats'):
        player.artifact_stats = {
            'artifacts_collected': 0,
            'enemies_stunned': 0,
            'phoenix_resurrections': 0
        }

    if not hasattr(player, 'gambling_stats'):
        player.gambling_stats = {
            'wins': 0,
            'losses': 0,
            'total_won': 0,
            'total_lost': 0
        }


def on_shop_item_display_custom(item_display, item, player, hook_system):
    """Добавляет специальную подсветку для артефактов в магазине"""
    if item.mod_source == "epic_artifacts":
        if "thunder_hammer" in item.id or "phoenix_armor" in item.id:
            item_display['name'] = "💎 " + item_display['name']
        elif "time_medallion" in item.id or "elemental_orb" in item.id:
            item_display['name'] = "🌟 " + item_display['name']
        else:
            item_display['name'] = "✨ " + item_display['name']

        # Добавляем информацию о редкости
        if hasattr(player, 'level'):
            if player.level < item.requirements.get('level', 0):
                item_display['description'] += f" (Требуется уровень {item.requirements['level']})"

    return item_display


# 📋 РЕГИСТРАЦИЯ ХУКОВ
HOOK_REGISTRY = {
    'damage_calculation': [
        'thunder_hammer_effect',
        'vampire_amulet_effect',
        'elemental_orb_effect'
    ],
    'player_take_damage': ['phoenix_armor_effect'],
    'battle_turn_start': ['time_medallion_effect'],
    'item_use': ['mimic_chest_effect'],
    'player_stat_update': ['artifact_collection_tracker'],
    'item_equipped': ['on_item_equip'],
    'item_unequipped': ['on_item_unequip'],
    'achievement_stat_value': ['on_achievement_stat_value_custom'],
    'player_level_up': ['on_player_level_up_custom'],
    'battle_start': ['on_battle_start_custom'],
    'battle_end': ['on_battle_end_custom'],
    'player_created': ['on_player_created_custom'],
    'shop_item_display': ['on_shop_item_display_custom']
}
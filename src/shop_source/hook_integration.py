# [file name]: src/shop_source/hook_integration.py
"""
Интеграция магазина с системой хуков
"""


def setup_shop_hooks(hook_system, shop_manager):
    """Настраивает хуки для магазина"""

    # Добавляем хуки магазина в список доступных
    shop_hooks = {
        'shop': [
            'pre_shop_display',  # Перед отображением магазина (player)
            'post_shop_display',  # После отображения магазина (player, items)
            'shop_item_display',  # Модификация отображения предмета (item_display, item, player)
            'shop_item_availability',  # Проверка доступности предмета (item, player, default_available)
            'shop_items_filter',  # Фильтрация списка предметов (items, player)
            'pre_purchase_selection',  # Перед выбором покупки (item_id, player, default_result)
            'pre_item_purchase',  # Перед покупкой (item, player, default_result)
            'post_item_purchase',  # После покупки (item, player, success)
            'shop_purchase_success',  # При успешной покупке (item_id, player)
            'shop_purchase_failed',  # При неудачной покупке (item_id, player, reason)
            'shop_purchase_completed',  # После завершения покупки (item_id, player)
        ]
    }

    # Регистрируем хуки в системе
    for category, hooks in shop_hooks.items():
        hook_system.available_hooks[category] = hooks


# Пример мода с предметами для магазина
MOD_SHOP_ITEMS_EXAMPLE = '''
"""
ПРИМЕР МОДА С ПРЕДМЕТАМИ ДЛЯ МАГАЗИНА
"""

def mod_initialize(hook_system):
    """Инициализация мода с предметами"""
    # Предметы можно добавлять через JSON файл или напрямую через API
    shop_items = [
        {
            "id": "magic_sword",
            "name": "🔮 Магический меч",
            "description": "+8 к урону, требует уровень 5",
            "price": 200,
            "type": "weapon", 
            "effects": {"damage": 8},
            "requirements": {"level": 5}
        },
        {
            "id": "super_potion",
            "name": "🌟 Супер-зелье",
            "description": "Восстанавливает 50 HP",
            "price": 40,
            "type": "potion",
            "effects": {"health": 50}
        }
    ]

    # Регистрируем предметы
    for item_data in shop_items:
        hook_system.shop_manager.add_mod_item(item_data, "example_shop_mod")

    return True

# Хуки для модификации магазина
def on_shop_item_display(item_display, item, player, hook_system):
    """Добавляет специальную иконку для дорогих предметов"""
    if item.price > 150:
        item_display['name'] = "💎 " + item_display['name']
    return item_display

def on_shop_items_filter(items, player, hook_system):
    """Скрывает некоторые предметы для низкоуровневых игроков"""
    if player.level < 3:
        return [item for item in items if item.price < 100]
    return items

# Регистрация хуков
HOOK_REGISTRY = {
    'shop_item_display': on_shop_item_display,
    'shop_items_filter': on_shop_items_filter,
}
'''
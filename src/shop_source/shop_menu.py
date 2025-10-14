# [file name]: src/shop_source/shop_menu.py
from utils.helpers_def import clear_console_def
from inventory.inventory_manager import InventoryManager, ItemCategory
from shop_source.shop_manager import ShopManager
from settings.settings_manager import settings


class ShopMenu:
    """Меню магазина для покупки предметов"""

    def __init__(self, hook_system):
        self.hook_system = hook_system
        self.shop_manager = ShopManager(hook_system)
        self.inventory_manager = InventoryManager(hook_system)

    def load_shop_items(self):
        """Загружает предметы магазина"""
        base_items = [
            {
                "id": "health_potion",
                "name": "🧪 Зелье здоровья",
                "description": "Восстанавливает 20 HP",
                "price": 15,
                "type": ItemCategory.POTION,
                "effects": {"health": 20}
            },
            {
                "id": "strength_potion",
                "name": "💪 Зелье силы",
                "description": "+2 к урону навсегда",
                "price": 50,
                "type": ItemCategory.POTION,
                "effects": {"damage": 2}
            },
            {
                "id": "vitality_potion",
                "name": "❤️ Зелье жизненности",
                "description": "+10 к максимальному здоровью",
                "price": 75,
                "type": ItemCategory.POTION,
                "effects": {"health_max": 10}
            },
            {
                "id": "mystery_box",
                "name": "🎁 Таинственная коробка",
                "description": "Случайный бонус!",
                "price": 200,
                "type": ItemCategory.SPECIAL,
                "effects": {"random_bonus": True}
            }
        ]

        # 🆕 ДОБАВЛЯЕМ ПРЕДМЕТЫ ИЗ МОДОВ
        mod_items = self.load_mod_shop_items()
        return base_items + mod_items

    @staticmethod
    def load_mod_shop_items():
        """Загружает предметы магазина из модов"""
        mod_items = []
        try:
            mods_dir = "src/saves/mods"
            import os
            import json

            for filename in os.listdir(mods_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(mods_dir, filename), 'r', encoding='utf-8') as f:
                            mod_data = json.load(f)

                        if 'shop_items' in mod_data:
                            for item_data in mod_data['shop_items']:
                                # Конвертируем тип предмета
                                type_map = {
                                    'weapon': ItemCategory.WEAPON,
                                    'armor': ItemCategory.ARMOR,
                                    'potion': ItemCategory.POTION,
                                    'special': ItemCategory.SPECIAL,
                                    'consumable': ItemCategory.CONSUMABLE
                                }
                                item_type = type_map.get(item_data.get('type', 'special'), ItemCategory.SPECIAL)

                                mod_item = {
                                    "id": item_data["id"],
                                    "name": item_data["name"] + " [MOD]",
                                    "description": item_data["description"],
                                    "price": item_data["price"],
                                    "type": item_type,
                                    "effects": item_data["effects"]
                                }
                                mod_items.append(mod_item)
                                settings.log_info(f"   ✅ Загружен предмет из мода: {item_data['name']}")

                    except Exception as e:
                        print(f"❌ Ошибка загрузки предметов из мода {filename}: {e}")
                        settings.log_error(e)

        except Exception as e:
            print(f"❌ Ошибка доступа к папке модов: {e}")
            settings.log_error(e)

        return mod_items

    def display_menu(self, player):
        """Отображает меню магазина с информацией об ограничениях"""
        while True:
            clear_console_def(1, 0)

            print("=" * 50)
            print("🛒 МАГАЗИН TEXT WAR LEGACY")
            print("=" * 50)
            print(f"💰 Ваши монеты: {player.coin}")
            print(f"🎯 Уровень: {player.level} | ❤️ Здоровье: {player.health}/{player.health_max}")
            print(f"⚔️ Урон: {player.damage} | 🛡️ Защита: {player.shield_hp}")
            print("-" * 50)
            print("📦 ДОСТУПНЫЕ ПРЕДМЕТЫ:")
            print("-" * 50)

            # 🆕 ИСПОЛЬЗУЕМ НОВУЮ СИСТЕМУ ОТОБРАЖЕНИЯ
            shop_display = self.shop_manager.get_shop_display(player)

            if not shop_display:
                print("📭 Нет доступных предметов для покупки")
                settings.log_tips("💡 Повысьте уровень или заработайте больше монет!")
            else:
                for item_data in shop_display:
                    print(f"{item_data['index']}. {item_data['type_icon']} {item_data['name']}{item_data['mod_indicator']}{item_data['purchase_info']}")
                    print(f"   📝 {item_data['description']}")
                    print(f"   💰 Цена: {item_data['price']} монет")

                    inventory_item_id = item_data['id']
                    if self.inventory_manager.has_item(inventory_item_id):
                        print(f"   📦 Уже есть в инвентаре")
                    print()

            print("0. 🔙 Назад")
            print("=" * 50)

            try:
                choice = input("Выберите предмет для покупки: ").strip()

                if choice == "0":
                    break

                choice_idx = int(choice)
                selected_item = None
                for item_data in shop_display:
                    if item_data['index'] == choice_idx:
                        selected_item = item_data
                        break

                if selected_item:
                    self.process_purchase(player, selected_item['id'])
                else:
                    print("❌ Неверный выбор!")

            except ValueError:
                print("❌ Введите число!")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                settings.log_error(e)

            input("\nНажмите Enter чтобы продолжить...")

    def process_purchase(self, player, item_id):
        """Обрабатывает покупку предмета через ShopManager"""
        success, message = self.shop_manager.process_purchase(item_id, player)

        if success:
            print(f"✅ {message}")

            if hasattr(self.hook_system, 'achievements_manager'):
                self.hook_system.achievements_manager.record_stat('items_purchased', 1)

                item = self.shop_manager.items.get(item_id)
                if item:
                    self.hook_system.achievements_manager.record_stat('total_coins_earned', item.price)

                    player.player_stats['items_purchased'] = player.player_stats.get('items_purchased', 0) + 1
                    player.player_stats['total_coins_earned'] = player.player_stats.get('total_coins_earned', 0) + item.price

                    # Проверяем достижения
                    self.hook_system.achievements_manager.check_all_achievements(player)
        else:
            print(f"❌ {message}")
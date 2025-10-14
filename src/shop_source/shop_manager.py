# [file name]: src/shop_source/shop_manager.py
from json import load, dump
from os import path, makedirs, listdir
from typing import Dict, List, Any
from pathlib import Path
from shop_source.shop_core import ShopCore, ShopItem, ItemType, PurchaseLimit
from settings.settings_manager import settings


class ShopManager:
    """Менеджер магазина для интеграции с игрой"""

    def __init__(self, hook_system):
        self.core = ShopCore(hook_system)
        self.hook_system = hook_system
        self.purchase_history = {}
        self.load_purchase_history()
        self.load_mod_items()

    def load_purchase_history(self):
        """Загружает историю покупок"""
        try:
            history_file = Path("src/saves/configs/shop_history.json")
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.purchase_history = load(f)
        except Exception as e:
            settings.log_error(f"⚠️ Ошибка загрузки истории покупок: {e}")
            self.purchase_history = {}

    def save_purchase_history(self):
        """Сохраняет историю покупок"""
        try:
            history_file = Path("src/saves/configs/shop_history.json")
            history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(history_file, 'w', encoding='utf-8') as f:
                dump(self.purchase_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            settings.log_error(f"⚠️ Ошибка сохранения истории покупок: {e}")

    def record_purchase(self, item_id: str, player_id: str = "global"):
        """Записывает покупку в историю"""
        if player_id not in self.purchase_history:
            self.purchase_history[player_id] = {}

        if item_id not in self.purchase_history[player_id]:
            self.purchase_history[player_id][item_id] = 0

        self.purchase_history[player_id][item_id] += 1
        self.save_purchase_history()

    def get_purchase_count(self, item_id: str, player_id: str = "global") -> int:
        """Получает количество покупок предмета"""
        return self.purchase_history.get(player_id, {}).get(item_id, 0)

    def can_purchase_item(self, item: ShopItem, player_id: str = "global") -> tuple[bool, str]:
        """Проверяет, можно ли купить предмет с учетом ограничений"""
        if item.purchase_limit.max_purchases != -1:
            current_purchases = self.get_purchase_count(item.id, "global")
            if current_purchases >= item.purchase_limit.max_purchases:
                return False, "❌ Этот предмет распродан!"

        if item.purchase_limit.player_specific:
            player_purchases = self.get_purchase_count(item.id, player_id)
            if player_purchases >= item.purchase_limit.max_purchases:
                return False, "❌ Вы уже купили этот предмет максимальное количество раз!"

        return True, "✅ Можно купить"

    def process_purchase(self, item_id: str, player) -> tuple[bool, str]:
        """Обрабатывает покупку предмета с учетом ограничений"""
        if item_id not in self.core.items:
            return False, "❌ Предмет не найден!"

        item = self.core.items[item_id]

        # Проверяем ограничения
        can_purchase, message = self.can_purchase_item(item, getattr(player, 'name', 'global'))
        if not can_purchase:
            return False, message

        success, message = self.core.purchase_item(item_id, player)

        if success:
            self.record_purchase(item_id, getattr(player, 'name', 'global'))

            # Хук обработки результата покупки
            self.hook_system.execute_hook('shop_purchase_success', item_id, player)
        else:
            self.hook_system.execute_hook('shop_purchase_failed', item_id, player, message)

        return success, message

    def get_shop_display(self, player) -> List[dict]:
        """Получает данные для отображения магазина с информацией об ограничениях"""
        available_items = self.core.get_available_items(player)
        display_data = []

        for i, item in enumerate(available_items, 1):
            purchase_info = ""
            purchase_count = self.get_purchase_count(item.id, getattr(player, 'name', 'global'))

            if item.purchase_limit.max_purchases != -1:
                remaining = item.purchase_limit.max_purchases - purchase_count
                if remaining <= 0:
                    continue  # Пропускаем полностью распроданные предметы
                purchase_info = f" (Осталось: {remaining})"
            elif purchase_count > 0:
                purchase_info = f" (Куплено: {purchase_count})"

            item_display = {
                'index': i,
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'type_icon': self.get_type_icon(item.item_type),
                'mod_indicator': " [MOD]" if item.mod_source != "vanilla" else "",
                'purchase_info': purchase_info,
                'can_purchase': self.can_purchase_item(item, getattr(player, 'name', 'global'))[0]
            }

            # Хук модификации отображения
            item_display = self.hook_system.execute_hook(
                'shop_item_display',
                item_display, item, player
            ) or item_display

            if not item_display.get('can_purchase', True):
                continue

            display_data.append(item_display)

        return display_data

    def load_mod_items(self):
        """Загрузка предметов из модов"""
        mods_dir = "src/saves/mods"

        makedirs(mods_dir, exist_ok=True)

        for filename in listdir(mods_dir):
            if filename.endswith('.json'):
                mod_name = filename[:-5]
                try:
                    with open(path.join(mods_dir, filename), 'r', encoding='utf-8') as f:
                        mod_data = load(f)

                    if 'shop_items' in mod_data:
                        for item_data in mod_data['shop_items']:
                            self.add_mod_item(item_data, mod_name)
                        settings.log_info(f"✅ Загружены предметы из мода: {mod_name}")

                except Exception as e:
                    settings.log_error(f"❌ Ошибка загрузки предметов из {filename}: {e}")

    def add_mod_item(self, item_data: Dict[str, Any], mod_name: str):
        """Добавляет предмет из мода с поддержкой ограничений"""
        try:
            item_type_str = item_data.get('type', 'special')
            item_type = self.convert_item_type(item_type_str)

            purchase_limit_data = item_data.get('purchase_limit', {})
            purchase_limit = PurchaseLimit(
                max_purchases=purchase_limit_data.get('max_purchases', 1),
                player_specific=purchase_limit_data.get('player_specific', False)
            )

            item = ShopItem(
                id=f"{mod_name}_{item_data['id']}",
                name=item_data['name'],
                description=item_data['description'],
                price=item_data['price'],
                item_type=item_type,
                effects=item_data['effects'],
                requirements=item_data.get('requirements'),
                mod_source=mod_name,
                purchase_limit=purchase_limit
            )
            self.core.items[item.id] = item
            settings.log_info(f"   ✅ Загружен предмет: {item.name} ({item_type.value})")
            return True
        except Exception as e:
            settings.log_error(f"❌ Ошибка добавления предмета из мода {mod_name}: {e}")
            return False

    def get_type_icon(self, item_type: ItemType) -> str:
        """Получает иконку для типа предмета"""
        icons = {
            ItemType.WEAPON: "⚔️",
            ItemType.ARMOR: "🛡️",
            ItemType.POTION: "🧪",
            ItemType.SPECIAL: "🎁",
            ItemType.MOD: "🔮"
        }
        return icons.get(item_type, "📦")

    @property
    def items(self):
        """Доступ к предметам магазина через core"""
        return self.core.items

    @staticmethod
    def convert_item_type(item_type_str: str) -> ItemType:
        """Конвертирует строковый тип в ItemType"""
        type_map = {
            'weapon': ItemType.WEAPON,
            'armor': ItemType.ARMOR,
            'potion': ItemType.POTION,
            'special': ItemType.SPECIAL,
            'mod': ItemType.MOD,
            'accessory': ItemType.SPECIAL,
            'consumable': ItemType.POTION,
        }
        return type_map.get(item_type_str.lower(), ItemType.SPECIAL)
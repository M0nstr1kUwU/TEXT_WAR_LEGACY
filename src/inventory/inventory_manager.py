# [file name]: src/inventory/inventory_manager.py
from json import load, dump
from typing import Dict, List, Any
from pathlib import Path
from enum import Enum

from settings.settings_manager import settings


class ItemCategory(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    SPECIAL = "special"
    CONSUMABLE = "consumable"


class InventoryItem:
    """Класс предмета инвентаря"""

    def __init__(self, item_id: str, name: str, description: str, category: ItemCategory, effects: Dict[str, Any], quantity: int = 1, equipped: bool = False):
        self.id = item_id
        self.name = name
        self.description = description
        self.category = category
        self.effects = effects
        self.quantity = quantity
        self.equipped = equipped

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "effects": self.effects,
            "quantity": self.quantity,
            "equipped": self.equipped
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            item_id=data["id"],
            name=data["name"],
            description=data["description"],
            category=ItemCategory(data["category"]),
            effects=data["effects"],
            quantity=data.get("quantity", 1),
            equipped=data.get("equipped", False)
        )


class InventoryManager:
    """Менеджер инвентаря игрока"""

    def __init__(self, hook_system):
        self.hook_system = hook_system
        self.items: Dict[str, InventoryItem] = {}
        self.inventory_file = Path("src/saves/configs/inventory.json")
        self.MAX_EQUIPPED_ITEMS = 3
        self.load_inventory()

    def load_inventory(self):
        """Загружает инвентарь из файла"""
        try:
            if self.inventory_file.exists():
                with open(self.inventory_file, 'r', encoding='utf-8') as f:
                    data = load(f)
                    for item_data in data.get("items", []):
                        item = InventoryItem.from_dict(item_data)
                        self.items[item.id] = item
                settings.log_info(f"✅ Инвентарь загружен: {len(self.items)} предметов")
        except Exception as e:
            settings.log_error(f"❌ Ошибка загрузки инвентаря: {e}")
            self.items = {}

    def save_inventory(self):
        """Сохраняет инвентарь в файл"""
        try:
            self.inventory_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "items": [item.to_dict() for item in self.items.values()]
            }
            with open(self.inventory_file, 'w', encoding='utf-8') as f:
                dump(data, f, ensure_ascii=False, indent=2)
            settings.log_info(f"✅ Инвентарь сохранен: {len(self.items)} предметов")
        except Exception as e:
            settings.log_error(f"❌ Ошибка сохранения инвентаря: {e}")

    def add_item(self, item_id: str, name: str, description: str, category: ItemCategory,
                 effects: Dict[str, Any], quantity: int = 1) -> bool:
        """Добавляет предмет в инвентарь"""
        try:
            if item_id in self.items:
                self.items[item_id].quantity += quantity
            else:
                self.items[item_id] = InventoryItem(
                    item_id=item_id,
                    name=name,
                    description=description,
                    category=category,
                    effects=effects,
                    quantity=quantity
                )

            self.save_inventory()
            print(f"✅ Предмет добавлен: {name} (x{quantity})")
            settings.log_info(f"✅ Предмет добавлен: {name} (x{quantity})")
            return True
        except Exception as e:
            settings.log_error(f"❌ Ошибка добавления предмета: {e}")
            return False

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Удаляет предмет из инвентаря"""
        if item_id in self.items:
            if self.items[item_id].quantity <= quantity:
                del self.items[item_id]
            else:
                self.items[item_id].quantity -= quantity
            self.save_inventory()
            return True
        return False

    def equip_item(self, item_id: str, player) -> bool:
        """Экипирует предмет на игрока (ИСПРАВЛЕННАЯ ВЕРСИЯ)"""
        if item_id not in self.items:
            print(f"❌ Предмет {item_id} не найден в инвентаре!")
            settings.log_error(f"❌ Предмет {item_id} не найден в инвентаре!")
            return False

        equipped_count = len(self.get_equipped_items())
        if equipped_count >= self.MAX_EQUIPPED_ITEMS:
            print(f"❌ Достигнут лимит экипированных предметов ({self.MAX_EQUIPPED_ITEMS})!")
            settings.log_error(f"❌ Достигнут лимит экипированных предметов ({self.MAX_EQUIPPED_ITEMS})!")
            return False

        item = self.items[item_id]

        if item.equipped:
            print(f"❌ Предмет {item.name} уже экипирован!")
            settings.log_error(f"❌ Предмет {item.name} уже экипирован!")
            return False

        # Экипируем выбранный предмет
        item.equipped = True

        # Применяем эффекты к игроку
        self.apply_item_effects(player, item)

        self.save_inventory()
        print(f"✅ Предмет экипирован: {item.name}")
        return True

    def unequip_item(self, item_id: str, player) -> bool:
        """Снимает предмет с игрока"""
        if item_id not in self.items or not self.items[item_id].equipped:
            print(f"❌ Предмет {item_id} не экипирован!")
            return False

        item = self.items[item_id]
        item.equipped = False
        self.remove_item_effects(player, item)
        self.save_inventory()
        print(f"✅ Предмет снят: {item.name}")
        return True

    def apply_item_effects(self, player, item: InventoryItem):
        """Применяет эффекты предмета к игроку (ИСПРАВЛЕННАЯ ВЕРСИЯ)"""
        print(f"🔮 Применение эффектов предмета: {item.name}")

        for effect, value in item.effects.items():
            if effect == 'achievement_visibility' and value:
                setattr(player, 'has_achievement_visibility', True)
                setattr(player, 'achievement_visibility', True)

                if not hasattr(player, 'special_effects'):
                    player.special_effects = {}
                player.special_effects['achievement_visibility'] = True

                print(f"   ✅ ТРЕКЕР ДОСТИЖЕНИЙ АКТИВИРОВАН!")
                continue

            # Обычная обработка других эффектов
            if hasattr(player, effect):
                current = getattr(player, effect)
                if isinstance(value, bool):
                    setattr(player, f"has_{effect}", value)
                    print(f"   ✅ Булевый эффект: {effect} = {value}")
                    settings.log_info(f"   ✅ Булевый эффект: {effect} = {value}")
                else:
                    setattr(player, effect, current + value)
                    print(f"   ✅ Числовой эффект: {effect} + {value}")
                    settings.log_info(f"   ✅ Числовой эффект: {effect} + {value}")
            else:
                if isinstance(value, bool):
                    setattr(player, f"has_{effect}", value)
                    print(f"   ✅ Создан булевый эффект: has_{effect} = {value}")
                    settings.log_info(f"   ✅ Создан булевый эффект: has_{effect} = {value}")
                else:
                    setattr(player, effect, value)
                    print(f"   ✅ Создан числовой эффект: {effect} = {value}")
                    settings.log_info(f"   ✅ Создан числовой эффект: {effect} = {value}")

    def remove_item_effects(self, player, item: InventoryItem):
        """Убирает эффекты предмета с игрока"""
        print(f"🔮 Снятие эффектов предмета: {item.name}")

        for effect, value in item.effects.items():
            if effect == 'achievement_visibility' and value:
                setattr(player, 'has_achievement_visibility', False)
                setattr(player, 'achievement_visibility', False)
                if hasattr(player, 'special_effects'):
                    player.special_effects['achievement_visibility'] = False
                print(f"   🔻 Трекер достижений деактивирован")
                settings.log_info(f"   🔻 Трекер достижений деактивирован")
                continue

            if hasattr(player, effect):
                current = getattr(player, effect)
                if isinstance(value, bool):
                    setattr(player, f"has_{effect}", False)
                    print(f"   🔻 Деактивирован эффект: {effect}")
                    settings.log_info(f"   🔻 Деактивирован эффект: {effect}")
                else:
                    setattr(player, effect, current - value)
                    print(f"   🔻 Снят эффект: {effect} - {value}")
                    settings.log_info(f"   🔻 Снят эффект: {effect} - {value}")

    def get_equipped_items(self) -> List[InventoryItem]:
        """Возвращает список экипированных предметов"""
        return [item for item in self.items.values() if item.equipped]

    def get_inventory_display(self) -> List[dict]:
        """Возвращает данные для отображения инвентаря"""
        display_data = []

        for item in self.items.values():
            item_display = {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'category': item.category.value,
                'quantity': item.quantity,
                'equipped': item.equipped,
                'effects': item.effects,
                'icon': self.get_category_icon(item.category)
            }
            display_data.append(item_display)

        return display_data

    def get_category_icon(self, category: ItemCategory) -> str:
        """Возвращает иконку для категории предмета"""
        icons = {
            ItemCategory.WEAPON: "⚔️",
            ItemCategory.ARMOR: "🛡️",
            ItemCategory.POTION: "🧪",
            ItemCategory.SPECIAL: "🔮",
            ItemCategory.CONSUMABLE: "🎁"
        }
        return icons.get(category, "📦")

    def get_equipped_count(self) -> int:
        """Возвращает количество экипированных предметов"""
        return len(self.get_equipped_items())

    def has_item(self, item_id: str) -> bool:
        """Проверяет, есть ли предмет в инвентаре"""
        return item_id in self.items

    def get_item_quantity(self, item_id: str) -> int:
        """Возвращает количество предмета в инвентаре"""
        if item_id in self.items:
            return self.items[item_id].quantity
        return 0

    def clear_inventory(self):
        """Очищает инвентарь"""
        self.items.clear()
        self.save_inventory()
        print("🗑️ Инвентарь очищен")

    def get_items_by_category(self, category: ItemCategory) -> List[InventoryItem]:
        """Возвращает предметы по категории"""
        return [item for item in self.items.values() if item.category == category]
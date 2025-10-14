# [file name]: src/shop_source/shop_core.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from inventory.inventory_manager import ItemCategory
from settings.settings_manager import settings


class ItemType(Enum):
    """Типы предметов в магазине"""
    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    SPECIAL = "special"
    MOD = "mod"


@dataclass
class PurchaseLimit:
    """Ограничения на покупку предмета"""
    max_purchases: int = -1
    purchases_count: int = 0
    player_specific: bool = False

@dataclass
class ShopItem:
    """Класс предмета магазина"""
    id: str
    name: str
    description: str
    price: int
    item_type: ItemType
    effects: Dict[str, Any]
    requirements: Optional[Dict[str, int]] = None
    mod_source: str = "vanilla"
    purchase_limit: PurchaseLimit = None

    def __post_init__(self):
        """Инициализация ограничений по умолчанию"""
        if self.purchase_limit is None:
            if self.item_type == ItemType.POTION:
                self.purchase_limit = PurchaseLimit(max_purchases=-1)
            else:
                self.purchase_limit = PurchaseLimit(max_purchases=1)

    def can_purchase(self, player) -> tuple[bool, str]:
        """Проверяет, может ли игрок купить предмет. Возвращает (успех, сообщение)"""
        if self.purchase_limit.max_purchases != -1:
            if self.purchase_limit.purchases_count >= self.purchase_limit.max_purchases:
                return False, "❌ Этот предмет больше нельзя купить!"

        if player.coin < self.price:
            return False, "❌ Недостаточно монет!"

        if self.requirements:
            for attr, value in self.requirements.items():
                if hasattr(player, attr):
                    if getattr(player, attr) < value:
                        return False, f"❌ Требуется {attr}: {value}"

        return True, "✅ Можно купить"

    def apply_effect(self, player):
        """Применяет эффект предмета к игроку"""
        for effect, value in self.effects.items():
            if hasattr(player, effect):
                current = getattr(player, effect)
                if effect in ['health_max', 'damage', 'shield_hp']:
                    setattr(player, effect, current + value)
                elif effect == 'health':
                    new_health = min(current + value, player.health_max)
                    setattr(player, effect, new_health)
                elif effect == 'potions':
                    setattr(player, effect, current + value)

    def record_purchase(self):
        """Записывает факт покупки"""
        if self.purchase_limit.max_purchases != -1:
            self.purchase_limit.purchases_count += 1


class ShopCore:
    """Ядро системы магазина"""

    def __init__(self, hook_system):
        self.hook_system = hook_system
        self.items: Dict[str, ShopItem] = {}
        self.load_vanilla_items()

    def load_vanilla_items(self):
        """Загрузка стандартных предметов магазина"""
        vanilla_items = [
            ShopItem(
                id="health_potion",
                name="🧪 Зелье здоровья",
                description="Восстанавливает 20 HP",
                price=15,
                item_type=ItemType.POTION,
                effects={"health": 20}
            ),
            ShopItem(
                id="strength_potion",
                name="💪 Зелье силы",
                description="+2 к урону навсегда",
                price=50,
                item_type=ItemType.POTION,
                effects={"damage": 2}
            ),
            ShopItem(
                id="vitality_potion",
                name="❤️ Зелье жизненности",
                description="+10 к максимальному здоровью",
                price=75,
                item_type=ItemType.POTION,
                effects={"health_max": 10, "health": 10}
            ),
            ShopItem(
                id="iron_sword",
                name="⚔️ Железный меч",
                description="Постоянно увеличивает урон на 5",
                price=120,
                item_type=ItemType.WEAPON,
                effects={"damage": 5},
                requirements={"level": 3}
            ),
            ShopItem(
                id="steel_shield",
                name="🛡️ Стальной щит",
                description="+15 к защите",
                price=100,
                item_type=ItemType.ARMOR,
                effects={"shield_hp": 15},
                requirements={"level": 2}
            ),
            ShopItem(
                id="mystery_box",
                name="🎁 Таинственная коробка",
                description="Случайный бонус!",
                price=200,
                item_type=ItemType.SPECIAL,
                effects={"random_bonus": True}
            )
        ]

        for item in vanilla_items:
            self.items[item.id] = item

    def add_mod_item(self, item_data: Dict[str, Any], mod_name: str):
        """Добавляет предмет из мода"""
        try:
            item = ShopItem(
                id=f"{mod_name}_{item_data['id']}",
                name=item_data['name'],
                description=item_data['description'],
                price=item_data['price'],
                item_type=ItemType(item_data.get('type', 'special')),
                effects=item_data['effects'],
                requirements=item_data.get('requirements'),
                mod_source=mod_name
            )
            self.items[item.id] = item
            return True
        except Exception as e:
            settings.log_error(f"❌ Ошибка добавления предмета из мода {mod_name}: {e}")
            return False

    def get_available_items(self, player) -> List[ShopItem]:
        """Получает доступные для игрока предметы"""
        available = []

        for item in self.items.values():
            # Хук проверки доступности предмета
            hook_result = self.hook_system.execute_hook(
                'shop_item_availability',
                item, player, True
            )

            if hook_result is not None:
                if not hook_result:
                    continue

            can_buy, _ = item.can_purchase(player)
            if can_buy:
                available.append(item)

        # Хук фильтрации предметов
        available = self.hook_system.execute_hook(
            'shop_items_filter',
            available, player
        ) or available

        return available

    # В методе purchase_item добавляем:
    def purchase_item(self, item_id: str, player) -> tuple[bool, str]:
        """Покупка предмета игроком"""
        if item_id not in self.items:
            return False, "❌ Предмет не найден!"

        item = self.items[item_id]

        # Хук предварительной покупки
        hook_result = self.hook_system.execute_hook(
            'pre_item_purchase',
            item, player, None
        )
        if hook_result is not None:
            return False, hook_result

        # Проверка возможности покупки
        can_buy, message = item.can_purchase(player)
        if not can_buy:
            return False, message

        # Списание денег
        player.coin -= item.price

        try:
            # Получаем менеджер инвентаря через hook_system
            inventory_manager = getattr(self.hook_system, 'inventory_manager', None)
            if inventory_manager:

                # Конвертируем тип предмета магазина в тип инвентаря
                category_map = {
                    ItemType.WEAPON: ItemCategory.WEAPON,
                    ItemType.ARMOR: ItemCategory.ARMOR,
                    ItemType.POTION: ItemCategory.POTION,
                    ItemType.SPECIAL: ItemCategory.SPECIAL,
                    ItemType.MOD: ItemCategory.SPECIAL
                }

                inventory_category = category_map.get(item.item_type, ItemCategory.SPECIAL)

                inventory_item_id = item.id
                if item.mod_source != "vanilla":
                    inventory_item_id = f"{item.mod_source}_{item.id}"

                success = inventory_manager.add_item(
                    item_id=inventory_item_id,
                    name=item.name,
                    description=item.description,
                    category=inventory_category,
                    effects=item.effects,
                    quantity=1
                )

                if success:
                    print(f"🎒 Предмет добавлен в инвентарь: {item.name}")
                else:
                    print(f"⚠️ Не удалось добавить предмет в инвентарь: {item.name}")

        except Exception as e:
            settings.log_error(f"⚠️ Ошибка добавления в инвентарь: {e}")

        # Применяем эффект предмета (для зелий и мгновенных эффектов)
        if item.item_type == ItemType.POTION or 'instant_effect' in item.effects:
            if 'random_bonus' in item.effects:
                # Случайный бонус для таинственной коробки
                import random
                bonuses = [
                    {"damage": random.randint(1, 3)},
                    {"health_max": random.randint(5, 15)},
                    {"shield_hp": random.randint(5, 10)},
                    {"coin": random.randint(10, 30)}  # Возврат части денег
                ]
                random_bonus = random.choice(bonuses)
                for effect, value in random_bonus.items():
                    if hasattr(player, effect):
                        current = getattr(player, effect)
                        setattr(player, effect, current + value)
            else:
                item.apply_effect(player)

        # Хук после покупки
        self.hook_system.execute_hook(
            'post_item_purchase',
            item, player, True
        )

        return True, f"✅ Куплено: {item.name}"
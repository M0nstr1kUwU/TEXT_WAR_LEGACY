# [file name]: src/inventory/inventory_menu.py
from inventory.inventory_manager import InventoryManager
from utils.helpers_def import clear_console_def, timeout_def
from settings.settings_manager import settings


class InventoryMenu:
    """Меню инвентаря для управления предметами"""

    def __init__(self, hook_system):
        self.manager = InventoryManager(hook_system)
        self.hook_system = hook_system

    def display_menu(self, player):
        """Отображает меню инвентаря"""
        while True:
            clear_console_def(1, 0)

            print("=" * 50)
            print("🎒 ИНВЕНТАРЬ ИГРОКА")
            print("=" * 50)

            equipped_count = self.manager.get_equipped_count()
            max_equipped = self.manager.MAX_EQUIPPED_ITEMS
            print(f"📊 Экипировано: {equipped_count}/{max_equipped} предметов")

            # Показываем экипированные предметы
            equipped_items = self.manager.get_equipped_items()
            if equipped_items:
                print("\n🔰 ЭКИПИРОВАННЫЕ ПРЕДМЕТЫ:")
                for item in equipped_items:
                    status_icon = "✅" if item.equipped else "❌"
                    print(f"   {status_icon} {self.manager.get_category_icon(item.category)} {item.name}")
                    print(f"      📝 {item.description}")
                    if item.effects:
                        effects_text = ", ".join([f"{k}: {v}" for k, v in item.effects.items()])
                        print(f"      💫 Эффекты: {effects_text}")
                print("-" * 50)

            # Показываем все предметы
            inventory = self.manager.get_inventory_display()
            if inventory:
                print("📦 ВАШ ИНВЕНТАРЬ:")
                for i, item in enumerate(inventory, 1):
                    equipped_indicator = " ✅" if item['equipped'] else ""
                    print(f"{i}. {item['icon']} {item['name']} (x{item['quantity']}){equipped_indicator}")
                    print(f"   📝 {item['description']}")
                    if item['effects']:
                        effects_text = ", ".join([f"{k}: {v}" for k, v in item['effects'].items()])
                        print(f"   💫 Эффекты: {effects_text}")
                    print()
            else:
                print("📭 Инвентарь пуст")
                print("💡 Посетите магазин чтобы купить предметы!")

            print("1. 🎯 Экипировать предмет")
            print("2. 🚫 Снять предмет")
            print("3. 🔍 Информация о трекере")
            print("0. 🔙 Назад")
            print("=" * 50)

            choice = input("Выберите опцию: ").strip()

            if choice == "0":
                break
            elif choice == "1":
                self.equip_item_menu(player)
            elif choice == "2":
                self.unequip_item_menu(player)
            elif choice == "3":
                self.show_tracker_info(player)
            else:
                print("❌ Неверный выбор!")
                timeout_def(3, 0)

    def equip_item_menu(self, player):
        """Меню экипировки предмета"""
        inventory = self.manager.get_inventory_display()
        equipable_items = [item for item in inventory if not item['equipped']]

        if not equipable_items:
            print("❌ Нет предметов для экипировки!")
            timeout_def(3, 0)
            return

        equipped_count = self.manager.get_equipped_count()
        if equipped_count >= self.manager.MAX_EQUIPPED_ITEMS:
            print(f"❌ Достигнут лимит экипированных предметов ({self.manager.MAX_EQUIPPED_ITEMS})!")
            settings.log_error(f"❌ Достигнут лимит экипированных предметов ({self.manager.MAX_EQUIPPED_ITEMS})!")
            settings.log_tips("💡 Снимите один из предметов чтобы экипировать новый.")
            timeout_def(3, 0)
            return

        clear_console_def(1, 0)
        print("=" * 50)
        print("🎯 ЭКИПИРОВКА ПРЕДМЕТА")
        print("=" * 50)
        print(f"📊 Свободно слотов: {self.manager.MAX_EQUIPPED_ITEMS - equipped_count}")

        for i, item in enumerate(equipable_items, 1):
            print(f"{i}. {item['icon']} {item['name']}")
            print(f"   📝 {item['description']}")
            if item['effects']:
                effects_text = ", ".join([f"{k}: {v}" for k, v in item['effects'].items()])
                print(f"   💫 Эффекты: {effects_text}")
            print()

        try:
            choice = int(input("Выберите предмет для экипировки: ")) - 1
            if 0 <= choice < len(equipable_items):
                item_id = equipable_items[choice]['id']
                if self.manager.equip_item(item_id, player):
                    print(f"✅ Предмет экипирован: {equipable_items[choice]['name']}")

                    if 'трекер' in equipable_items[choice]['name'].lower() or 'tracker' in equipable_items[choice][
                        'name'].lower():
                        print("🎯 Трекер достижений активирован! Теперь видны все секретные достижения!")
                else:
                    print("❌ Ошибка экипировки предмета!")
            else:
                print("❌ Неверный выбор!")
        except ValueError:
            print("❌ Введите число!")

        timeout_def(3, 0)

    def unequip_item_menu(self, player):
        """Меню снятия предмета"""
        equipped_items = self.manager.get_equipped_items()

        if not equipped_items:
            print("❌ Нет экипированных предметов!")
            timeout_def(3, 0)
            return

        clear_console_def(1, 0)
        print("=" * 50)
        print("🚫 СНЯТИЕ ПРЕДМЕТА")
        print("=" * 50)

        for i, item in enumerate(equipped_items, 1):
            print(f"{i}. {self.manager.get_category_icon(item.category)} {item.name}")
            print(f"   📝 {item.description}")
            print()

        try:
            choice = int(input("Выберите предмет для снятия: ")) - 1
            if 0 <= choice < len(equipped_items):
                item_id = equipped_items[choice].id
                if self.manager.unequip_item(item_id, player):
                    print(f"✅ Предмет снят: {equipped_items[choice].name}")

                    if 'трекер' in equipped_items[choice].name.lower() or 'tracker' in equipped_items[
                        choice].name.lower():
                        print("🔒 Трекер достижений деактивирован! Секретные достижения скрыты.")
                        settings.log_info("🔒 Трекер достижений деактивирован! Секретные достижения скрыты.")
                else:
                    print("❌ Ошибка снятия предмета!")
            else:
                print("❌ Неверный выбор!")
        except ValueError:
            print("❌ Введите число!")

        timeout_def(3, 0)

    def show_tracker_info(self, player):
        """Показывает информацию о состоянии трекера достижений"""
        clear_console_def(1, 0)
        print("=" * 50)
        print("🔍 ИНФОРМАЦИЯ О ТРЕКЕРЕ ДОСТИЖЕНИЙ")
        print("=" * 50)

        # Проверяем наличие трекера в инвентаре
        has_tracker_item = any(
            'трекер' in item.name.lower() or 'tracker' in item.name.lower()
            for item in self.manager.items.values()
        )

        # Проверяем экипирован ли трекер
        equipped_tracker = any(
            item.equipped and ('трекер' in item.name.lower() or 'tracker' in item.name.lower())
            for item in self.manager.get_equipped_items()
        )

        # Проверяем атрибуты игрока
        has_visibility_attr = getattr(player, 'has_achievement_visibility', False)
        visibility_attr = getattr(player, 'achievement_visibility', False)
        special_effects = getattr(player, 'special_effects', {})

        print("📊 СТАТУС ТРЕКЕРА:")
        print(f"   📦 В инвентаре: {'✅ Есть' if has_tracker_item else '❌ Нет'}")
        print(f"   🎯 Экипирован: {'✅ Да' if equipped_tracker else '❌ Нет'}")
        print(f"   🔮 Атрибут has_achievement_visibility: {'✅ True' if has_visibility_attr else '❌ False'}")
        print(f"   🔮 Атрибут achievement_visibility: {'✅ True' if visibility_attr else '❌ False'}")
        print(f"   🎪 Special effects: {special_effects}")

        # Общий статус
        tracker_active = has_visibility_attr or visibility_attr or equipped_tracker
        print(f"\n🎯 ОБЩИЙ СТАТУС: {'✅ АКТИВЕН' if tracker_active else '❌ НЕАКТИВЕН'}")

        if tracker_active:
            print("💡 Все секретные достижения теперь видны!")
        else:
            print("💡 Экипируйте трекер достижений чтобы увидеть секретные достижения!")

        timeout_def(3, 0)
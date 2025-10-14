# [file name]: src/classes_entities/classes_menu.py
from utils.helpers_def import clear_console_def, timeout_def
from classes_entities.classes_core import class_system, ClassType
from modding.support_mods import hook_system
from settings.settings_manager import settings


class ClassesMenu:
    """Меню системы классов"""

    def __init__(self, hook_system):
        self.hook_system = hook_system

    def display_menu(self, player):
        """Отображает меню классов"""
        while True:
            clear_console_def(1, 0)
            print("=" * 50)
            print("🎯 СИСТЕМА КЛАССОВ")
            print("=" * 50)

            # Информация о текущем классе
            self.show_current_class_info(player)

            print("\n📋 ДОСТУПНЫЕ КЛАССЫ:")
            print("-" * 50)

            classes = [
                (ClassType.WARRIOR, "⚔️ Воин", "Сильный и выносливый боец"),
                (ClassType.MAGE, "🔮 Маг", "Мощные заклинания и контроль стихий"),
                (ClassType.ROGUE, "🗡️ Разбойник", "Ловкость и критические удары"),
                (ClassType.HUNTER, "🏹 Охотник", "Точные выстрелы на расстоянии"),
                (ClassType.PALADIN, "🛡️ Паладин", "Защита и исцеление"),
                (ClassType.NECROMANCER, "💀 Некромант", "Темная магия и призыв существ"),
                (ClassType.ELEMENTALIST, '🌪️ Элементалист', "Мастер стихий")
            ]

            for i, (class_type, name, description) in enumerate(classes, 1):
                print(f"{i}. {name}")
                print(f"   📝 {description}")
                print()

            print("8. 🔄 Сбросить класс")
            print("9. 🌟 Прокачка навыков")
            print("0. 🔙 Назад")
            print("=" * 50)

            try:
                choice = input("Выберите класс: ").strip()

                if choice == "0":
                    break
                elif choice == "8":
                    self.reset_class(player)
                elif choice == "9":
                    self.display_skill_tree_menu(player)
                elif choice.isdigit():
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(classes):
                        selected_class = classes[choice_idx][0]
                        self.select_class(player, selected_class)
                    else:
                        print("❌ Неверный выбор!")
                else:
                    print("❌ Введите число!")

            except Exception as e:
                settings.log_error(f"❌ Ошибка: {e}")

            timeout_def(3, 0)

    @staticmethod
    def show_current_class_info(player):
        """Показывает информацию о текущем классе"""
        if player.player_class != ClassType.NONE and player.class_data:
            class_data = player.class_data
            print(f"🎯 Текущий класс: {class_data.icon} {class_data.name}")
            print(f"📊 Уровень: {player.level}")
            print(f"❤️ Здоровье: {player.health}/{player.health_max}")
            print(f"⚔️ Урон: {player.damage}")
            print(f"🔮 Мана: {player.mana}/{player.mana_max}")

            # Показываем доступные способности
            if player.abilities:
                print(f"\n🎯 Доступные способности:")
                for ability in player.abilities:
                    print(f"   {ability.icon} {ability.name} - {ability.description}")
        else:
            print("🎯 Текущий класс: ❌ Не выбран")
            settings.log_tips("💡 Выберите класс чтобы получить уникальные способности!")

        print("-" * 50)

    def display_skill_tree_menu(self, player):
        """Меню дерева навыков"""
        if not player.has_class():
            print("❌ Сначала выберите класс!")
            return

        while True:
            clear_console_def(1, 0)
            print("=" * 50)
            print("🌟 ДЕРЕВО НАВЫКОВ")
            print("=" * 50)
            print(f"🎯 Класс: {player.class_data.icon} {player.class_data.name}")
            print(f"⭐ Доступно очков: {player.skill_points}")
            print(f"🔓 Разблокировано узлов: {len(player.skill_tree.unlocked_nodes)}")
            print("-" * 50)

            # Показываем доступные узлы
            available_nodes = player.skill_tree.get_available_nodes()

            if available_nodes:
                print("📋 ДОСТУПНЫЕ НАВЫКИ:")
                for i, node in enumerate(available_nodes, 1):
                    level_info = f" (Ур. {node.current_level}/{node.max_level})" if node.max_level > 1 else ""
                    print(f"{i}. {node.icon} {node.name}{level_info}")
                    print(f"   📝 {node.description}")
                    print(f"   💰 Стоимость: {node.cost} очков")
                    print()
            else:
                print("📭 Нет доступных навыков для разблокировки")
                settings.log_tips("💡 Повышайте уровень для получения очков навыков!")

            print("0. 🔙 Назад")
            print("=" * 50)

            choice = input("Выберите навык для изучения: ").strip()

            if choice == "0":
                clear_console_def(1, 0)
                break
            elif choice.isdigit():
                clear_console_def(1, 0)
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(available_nodes):
                    self.unlock_skill(player, available_nodes[choice_idx])
                else:
                    print("❌ Неверный выбор!")
            else:
                print("❌ Введите число!")

            timeout_def(3, 0)

    def unlock_skill(self, player, node):
        """Разблокирует навык"""
        if player.skill_tree.unlock_node(node.node_id):
            print(f"✅ Навык разблокирован: {node.icon} {node.name}")

            # Применяем эффекты навыка к игроку
            player.apply_skill_effects()

            # Показываем эффекты
            effects = player.skill_tree.get_node_effects()
            if effects:
                print("💫 Активные эффекты:")
                for effect, value in effects.items():
                    print(f"   {effect}: +{value}")
        else:
            print("❌ Не удалось разблокировать навык!")

    def select_class(self, player, class_type):
        """Выбирает класс для игрока"""
        settings.log_info(f"🔍 Выбран класс: {class_type}")
        if class_type not in class_system.classes:
            settings.log_error(f"❌ Класс {class_type} не загружен в систему!")
            settings.log_info(f"🔍 Доступные классы: {[ct.value for ct in class_system.classes.keys()]}")
            return

        if player.player_class == class_type:
            print(f"❌ Вы уже выбрали этот класс!")
            return

        clear_console_def(1, 0)
        print("=" * 50)
        print("🎯 ВЫБОР КЛАССА")
        print("=" * 50)

        class_data = class_system.get_class(class_type)
        if not class_data:
            print(f"❌ Класс {class_type} не найден!")
            return

        print(f"📦 Класс: {class_data.icon} {class_data.name}")
        print(f"📝 Описание: {class_data.description}")

        # Показываем базовые характеристики
        stats = class_data.get_stats_at_level(1)
        print(f"\n📊 Базовые характеристики:")
        print(f"❤️ Здоровье: {stats['health']}")
        print(f"⚔️ Урон: {stats['damage']}")
        print(f"🔮 Мана: {stats['mana']}")
        print(f"🎯 Предпочитаемый элемент: {class_data.preferred_element.value}")

        # Показываем способности 1 уровня
        abilities = class_system.get_available_abilities(class_type, 1)
        if abilities:
            print(f"\n🎯 Способности 1 уровня:")
            for ability in abilities:
                print(f"   {ability.icon} {ability.name} - {ability.description}")

        print("\n⚠️ Вы уверены что хотите выбрать этот класс?")
        print("❌ Внимание: смена класса сбросит ваши текущие характеристики!")

        confirm = input("\nПодтвердите выбор (y/д - да, n/н - нет): ").strip().lower()

        if confirm in ['y', 'д', 'yes', 'да']:
            player.set_class(class_type)
            print(f"✅ Класс выбран: {class_data.icon} {class_data.name}!")

            # Хук выбора класса
            hook_system.execute_hook('class_selected', player, class_type)
        else:
            print("❌ Выбор отменен.")

    def reset_class(self, player):
        """Сбрасывает класс игрока"""
        if player.player_class == ClassType.NONE:
            print("❌ У вас нет активного класса!")
            return

        clear_console_def(1, 0)
        print("=" * 50)
        print("🔄 СБРОС КЛАССА")
        print("=" * 50)
        print(f"⚠️ Вы уверены что хотите сбросить класс {player.class_data.icon} {player.class_data.name}?")
        print("❌ Все характеристики и способности будут сброшены!")

        confirm = input("\nПодтвердите сброс (y/д - да, n/н - нет): ").strip().lower()

        if confirm in ['y', 'д', 'yes', 'да']:
            old_class = player.player_class

            # Сбрасываем характеристики к базовым
            player.player_class = ClassType.NONE
            player.class_data = None
            player.abilities = []
            player.skill_tree = None

            # Восстанавливаем базовые характеристики
            player.health_max = 20
            player.health = min(player.health, player.health_max)
            player.damage = 3
            player.mana_max = 10
            player.mana = player.mana_max

            print("✅ Класс сброшен! Характеристики восстановлены к базовым.")

            # Хук сброса класса
            hook_system.execute_hook('class_reset', player, old_class)
        else:
            print("❌ Сброс отменен.")
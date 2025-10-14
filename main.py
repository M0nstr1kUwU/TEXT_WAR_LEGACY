from json import load, dump
import os
from sys import path, executable
from subprocess import run
from traceback import print_exc
from src.utils.path_manager import path_manager
from src.utils.helpers_def import clear_console_def, timeout_def
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.actions.actions_battle import ActionBattle
from src.settings.settings_menu import SettingsMenu
from src.modding.support_mods import hook_system
from src.settings.settings_manager import settings
from src.settings.support_list import GameHandbook
from src.achievements_source.achievements_menu import AchievementsMenu
from src.inventory.inventory_menu import InventoryMenu
from src.elemental_source.elemental_core import elemental_system
from src.classes_entities.classes_menu import ClassesMenu
from src.classes_entities.classes_core import class_system, ClassType
from src.shop_source.shop_menu import ShopMenu
from src.shop_source.shop_manager import ShopManager

# Добавляем src в путь для импортов
path.append(os.path.join(os.path.dirname(__file__), 'src'))


def save_player_data(player):
    """Сохранение данных игрока в JSON с хуками"""
    global player_data
    try:
        player_data = player.to_dict()

        # Хук предварительного сохранения
        player_data = hook_system.execute_hook('pre_save_game', player_data) or player_data

        save_path = str(path_manager.player_data_file)

        with open(save_path, 'w', encoding='utf-8') as f:
            dump(player_data, f, ensure_ascii=False, indent=2)

        # Хук после сохранения
        hook_system.execute_hook('post_save_game', player_data, True)

        # СОХРАНЯЕМ СТАТИСТИКУ ДОСТИЖЕНИЙ
        if hasattr(hook_system, 'achievements_manager'):
            hook_system.achievements_manager.save_achievements_progress()

        print("✅ Прогресс успешно сохранен!")
        settings.log_info("✅ Прогресс успешно сохранен!")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        hook_system.execute_hook('post_save_game', player_data, False)
        settings.log_error(e)
        return False


def load_player_data():
    """Загрузка данных игрока из JSON с хуками"""
    save_path = str(path_manager.player_data_file)

    if os.path.exists(save_path):
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                data = load(f)

            # Хук предварительной загрузки
            data = hook_system.execute_hook('pre_load_game', data) or data

            player = Player.from_dict(data)

            # Хук после загрузки
            hook_system.execute_hook('post_load_game', player, True)

            # Хук создания игрока
            hook_system.execute_hook('player_created', player)

            if hasattr(hook_system, 'achievements_manager'):
                hook_system.achievements_manager.sync_with_player_data(player)

            return player
        except Exception as e:
            print(f"❌ Ошибка загрузки игрока: {e}")
            hook_system.execute_hook('post_load_game', None, False)
            settings.log_error(e)
            return None
    return None


def create_new_player():
    """Создание нового игрока"""
    name = input("Введите имя игрока: ").strip()
    if not name:
        name = "Игрок"

    player = Player(name=name)

    # Хук создания игрока
    hook_system.execute_hook('player_created', player)

    # ЗАПИСЫВАЕМ СТАТИСТИКУ ПЕРВОГО ВХОДА
    if hasattr(hook_system, 'achievements_manager'):
        hook_system.achievements_manager.record_stat('menus_visited', 1)

    return player


def start_battle():
    """Запуск битвы с поддержкой улучшенного ИИ"""
    # Загрузка или создание игрока
    player = load_player_data()
    if not player:
        player = create_new_player()
        save_player_data(player)
    clear_console_def(1, 0)
    print("🎮 Начинается битва! Приготовьтесь!")

    # УЛУЧШЕННЫЙ ВЫБОР СЛОЖНОСТИ
    print("\n🎯 Выберите сложность:")
    print("1. 🔰 Легкая (для новичков)")
    print("2. ⚔️ Средняя (сбалансированная)")
    print("3. 🔥 Сложная (опытные игроки)")
    print("4. 💀 Экстрим (испытание для мастеров)")

    difficulty_choice = input("Выберите сложность (1-4): ").strip()
    difficulty_map = {
        "1": "easy",
        "2": "medium",
        "3": "hard",
        "4": "extreme"
    }
    difficulty = difficulty_map.get(difficulty_choice, "medium")

    print(f"🎯 Выбрана сложность: {difficulty.upper()}")

    # Создание врага с выбранной сложностью
    enemy = Enemy.choose_entity_for_battle(difficulty)

    # Хук создания врага
    enemy = hook_system.execute_hook('enemy_creation', enemy, difficulty) or enemy

    print(f"Встречен враг: {enemy.name} (Уровень: {enemy.enemy_type})")

    # ИНФОРМАЦИЯ О ИИ ВРАГА
    if hasattr(enemy, 'difficulty') and enemy.difficulty in ['hard', 'extreme']:
        settings.log_tips("⚠️  Этот враг использует продвинутый ИИ с обучением!")
        if enemy.special_ability:
            print(f'💫 Особые способности: {enemy.special_ability}')

    # Создание системы боя
    battle_system = ActionBattle()

    # Запуск цикла битвы
    battle_result = battle_system.battle_loop(player, enemy)

    # ОБНОВЛЯЕМ СТАТИСТИКУ ПОСЛЕ БИТВЫ
    if hasattr(hook_system, 'achievements_manager'):
        if battle_result == "win":
            hook_system.achievements_manager.record_stat('battles_won', 1)
        elif battle_result == "lose":
            hook_system.achievements_manager.record_stat('battles_lost', 1)

        # Проверяем достижения после битвы
        hook_system.achievements_manager.check_all_achievements(player)

    # Сохранение после битвы
    save_player_data(player)

    timeout_def(3, 0)


def show_mods_menu():
    """Меню управления модами"""
    while True:
        clear_console_def(1, 0)
        print("\n" + "=" * 40)
        print("🎮 УПРАВЛЕНИЕ МОДАМИ")
        print("=" * 40)
        print("1. 📋 Список загруженных модов")
        print("2. 📖 Доступные хуки")
        print("3. 🔧 Создать новый мод")
        print("4. 🔙 Назад")

        choice = input("Выберите опцию: ")

        if choice == "1":
            clear_console_def(1, 0)
            print("\n📋 ЗАГРУЖЕННЫЕ МОДЫ:")
            mods = hook_system.get_loaded_mods()
            if mods:
                for mod_name in mods:
                    print(f"  ✅ {mod_name}")
            else:
                print("  📭 Моды не загружены")

        elif choice == "2":
            clear_console_def(1, 0)
            print("\n📖 ДОСТУПНЫЕ ХУКИ:")
            available_hooks = hook_system.get_available_hooks()
            for category, hooks in available_hooks.items():
                print(f"\n{category.upper()}:")
                for hook in hooks[:3]:
                    print(f"  📎 {hook}")
                if len(hooks) > 3:
                    print(f"  ... и еще {len(hooks) - 3} хуков")

        elif choice == "3":
            clear_console_def(1, 0)
            create_new_mod()
        elif choice == "4":
            break
        else:
            print("❌ Неверный выбор!")
            clear_console_def(2, 1)


def create_new_mod():
    """Создание шаблона нового мода"""
    print("\n🔧 СОЗДАНИЕ НОВОГО МОДА")
    mod_name = input("Введите название мода (английскими буквами): ").strip()

    if not mod_name:
        settings.log_warning("❌ Название не может быть пустым!")
        return

    mod_path = f"src/saves/mods/{mod_name}.py"

    if os.path.exists(mod_path):
        settings.log_warning("❌ Мод с таким названием уже существует!")
        return

    template = f'''"""
МОД: {mod_name}
Автор: Ваше имя
Описание: Краткое описание мода
"""

def mod_initialize(hook_system):
    """Инициализация мода"""
    print(f"✅ Мод '{{mod_name}}' загружен!")
    return True

# ПРИМЕР ХУКА - раскомментируйте для использования
# def on_player_created(player, hook_system):
#     """Усиливает игрока при создании"""
#     if player and hasattr(player, 'damage'):
#         player.damage += 2
#         player.health_max += 10
#         print(f"💪 Мод {{mod_name}}: Игрок усилен!")
#
# def on_battle_start(player, enemy, mode, hook_system):
#     """Добавляет эффекты в начале битвы"""
#     if player and enemy:
#         print(f"🔥 Мод {{mod_name}}: Битва начинается!")
#
# # РЕГИСТРАЦИЯ ХУКОВ
# HOOK_REGISTRY = {{
#     'player_created': on_player_created,
#     'battle_start': on_battle_start,
# }}
'''
    try:
        with open(mod_path, 'w', encoding='utf-8') as f:
            f.write(template)
        settings.log_info(f"✅ Шаблон мода создан: {mod_path}")
        settings.log_info("📝 Отредактируйте файл чтобы добавить функциональность!")
    except Exception as e:
        settings.log_error(f"❌ Ошибка создания мода: {e}")


def main_menu():
    """Главное меню игры с поддержкой хуков"""
    settings_menu = SettingsMenu()
    handbook = GameHandbook()
    achievements_menu = AchievementsMenu(hook_system)
    inventory_menu = InventoryMenu(hook_system)
    hook_system.inventory_manager = inventory_menu.manager
    hook_system.achievements_manager = achievements_menu.manager
    classes_menu = ClassesMenu(hook_system)
    shop_manager = ShopManager(hook_system)
    shop_menu = ShopMenu(hook_system)
    hook_system.shop_manager = shop_manager

    while True:
        clear_console_def(1, 0)
        print("\n" + "=" * 40)
        print("🎮 TEXT WAR LEGACY")
        print("=" * 40)
        print("1. 🚀 Начать битву")
        print("2. 📊 Статистика игрока")
        print("3. 🎒 Инвентарь")
        print("4. 🛒 Магазин")
        print('5. 🏆 Достижения')
        print("6. 🎯 Классы и навыки")
        print("7. ⚙️ Настройки")
        print("8. 🎮 Моды")
        print("9. 📚 Полный справочник")
        print("10. 🔧 Редактор модов")
        print("0. 🚪 Выход")
        settings.log_tips("💡 Ознакомьтесь со справочником, если зашли впервые!")

        try:
            choice = input("Выберите опцию: ")

            # Хук выбора в меню
            result = hook_system.execute_hook('main_menu_selection', choice, None)
            if result is not None:
                continue

            if choice == "1":
                start_battle()
            elif choice == "2":
                player = load_player_data()
                if player:
                    print(f"\n📊 Статистика {player.name}:")
                    print(f"❤️ Здоровье: {player.health}/{player.health_max}")
                    print(f"⚔️ Урон: {player.damage}")
                    print(f"🛡️ Щит: {player.shield_hp}")
                    print(f"🔮 Мана: {player.mana}/{player.mana_max}")
                    print(f"💰 Монеты: {player.coin}")
                    print(f"🎯 Уровень: {player.level}")
                    print(f'⭐ Опыт: {player.experience}')
                    print("🧪 Зелья:", player.potions)
                    if player.has_class():
                        print(f"🎯 Класс: {player.class_data.icon} {player.class_data.name}")
                        print(f"🎯 Элемент: {player.element_data.icon} {player.element_data.name}")
                    else:
                        print(f"🎯 Класс: ❌ Не выбран")
                    if hasattr(player, 'skill_points') and player.skill_points > 0:
                        print(f"🌟 Очки навыков: {player.skill_points}")
                    if hasattr(player, 'player_stats'):
                        print(f"\n🎯 Игровая статистика:")
                        print(f"   Побед: {player.player_stats.get('battles_won', 0)}")
                        print(f"   Покупок: {player.player_stats.get('items_purchased', 0)}")
                        print(f"   Макс. урон: {player.player_stats.get('max_damage_single_battle', 0)}")
                    print(f"\n🔮 Трекер достижений: {'✅ АКТИВЕН' if player.achievement_visibility else '❌ НЕАКТИВЕН'}")
                    timeout_def(3, 0)
                else:
                    settings.log_warning("❌ Данные игрока не найдены!")
                    timeout_def(3, 0)
            elif choice == "3":
                player = load_player_data()
                if player:
                    inventory_menu.display_menu(player)
                    save_player_data(player)
                else:
                    settings.log_warning("❌ Сначала создайте персонажа в битве!")
                    timeout_def(3, 0)
            elif choice == "4":
                player = load_player_data()
                if player:
                    shop_menu.display_menu(player)
                    save_player_data(player)
                else:
                    settings.log_warning("❌ Сначала создайте персонажа в битве!")
                    timeout_def(3, 0)
            elif choice == "5":
                player = load_player_data()
                if player:
                    try:
                        achievements_menu.manager.sync_with_player_data(player)
                        achievements_menu.manager.refresh_mod_achievements()
                        achievements_menu.display_menu(player)
                        save_player_data(player)
                    except Exception as e:
                        settings.log_error(f"❌ Ошибка в системе достижений: {e}")
                        print_exc()
                        timeout_def(3, 0)
                else:
                    settings.log_warning("❌ Сначала создайте персонажа в битве!")
                    timeout_def(3, 0)
            elif choice == "6":
                player = load_player_data()
                if player:
                    class_system.ensure_all_classes_loaded()
                    classes_menu.display_menu(player)
                    save_player_data(player)
                else:
                    settings.log_warning("❌ Сначала создайте персонажа в битве!")
                    settings.log_tips("💡 Выберите опцию '1. 🚀 Начать битву' чтобы создать персонажа")
                    timeout_def(3, 0)
            elif choice == "7":
                settings_menu.display_menu()
            elif choice == "8":
                show_mods_menu()
            elif choice == "9":
                handbook.display_full_handbook()
                timeout_def(3, 0)
            elif choice == "10":
                launch_mod_editor()
            elif choice == "0":
                break
            else:
                print("❌ Неверный выбор!")

            # ЗАПИСЫВАЕМ СТАТИСТИКУ ПОСЕЩЕНИЯ МЕНЮ
            if hasattr(hook_system, 'achievements_manager'):
                hook_system.achievements_manager.record_stat('menus_visited', 1)

        except Exception as e:
            settings.log_error(f"❌ Критическая ошибка: {e}")
            print_exc()
            timeout_def(3, 0)


def launch_mod_editor():
    """Запуск Mod-Editor"""
    try:
        settings.log_info("🚀 Запуск Mod-Editor...")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        editor_script = os.path.join(current_dir, "run_mod_editor.py")

        settings.log_info(f"📁 Ищу файл: {editor_script}")

        if not os.path.exists(editor_script):
            settings.log_error(f"❌ Файл не найден: {editor_script}")
            # Пробуем альтернативный путь
            editor_script = os.path.join(os.getcwd(), "run_mod_editor.py")
            settings.log_info(f"📁 Пробую альтернативный путь: {editor_script}")

        if os.path.exists(editor_script):
            # Запускаем в отдельном процессе
            python_exe = executable
            settings.log_info(f"🐍 Запускаем: {python_exe} {editor_script}")
            run([python_exe, editor_script])
        else:
            settings.log_error("❌ Файл run_mod_editor.py не найден в корне проекта!")
            settings.log_error("📁 Создайте файл run_mod_editor.py в той же папке где main.py")

    except Exception as e:
        settings.log_error(f"❌ Ошибка запуска редактора: {e}")
        settings.log_tips("📦 Убедитесь, что установлены зависимости:")
        settings.log_tips("   pip install PyQt5 QScintilla")


def defend(self):
    """Защита - блокирует часть урона"""
    self.shield_hp += 5
    print(f"🛡️ Защита усилена! Щит: {self.shield_hp}")


def heal(self):
    """Лечение - восстанавливает здоровье"""
    heal_amount = min(self.health_repair, self.health_max - self.health)
    self.health += heal_amount
    self.player_stats['total_healing_done'] += heal_amount
    print(f"❤️ Восстановлено {heal_amount} здоровья! Здоровье: {self.health}/{self.health_max}")
    return heal_amount


def has_class(self):
    """Проверяет, есть ли у игрока класс"""
    return self.player_class != ClassType.NONE and self.class_data is not None


def main():
    settings.log_info("Запуск TEXT WAR LEGACY!")

    settings.log_info("🔮 Инициализация элементной системы...")
    settings.log_info(f"✅ Загружено элементов: {len(elemental_system.elements)}")

    settings.log_info("🎯 Инициализация системы классов...")
    settings.log_info(f"✅ Загружено классов: {len(class_system.classes)}")

    settings.log_info("\n🎯 ЗАГРУЖЕННЫЕ КЛАССЫ:")
    for class_type, game_class in class_system.classes.items():
        settings.log_info(f"   ✅ {game_class.icon} {game_class.name} ({class_type.value})")

    # Хук инициализации игры
    hook_system.execute_hook('game_initialized', globals())

    # Запуск главного меню
    main_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        settings.log_info("\n\nИгра завершена пользователем")
    except Exception as e:
        settings.log_error(f"\n❌ Критическая ошибка: {e}")
        print_exc()
        timeout_def(3, 0)
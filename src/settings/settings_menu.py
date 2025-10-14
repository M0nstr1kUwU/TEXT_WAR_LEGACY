# src/settings/settings_menu.py
from settings.settings_manager import SettingsManager
from utils.helpers_def import clear_console_def
from settings.support_list import (
    GameHandbook,
    show_ai_tips,
    show_quick_guide,
    show_modding_tips,
    show_economy_guide,
    show_progression_guide,
    show_achievements_creation_tips,
    show_achievement_example,
    show_items_creation_tips,
    show_item_example,
    show_mods_creation_tips,
    show_python_mod_example
)


class SettingsMenu:
    def __init__(self):
        self.settings_manager = SettingsManager()
        self.difficulty_options = ["easy", "medium", "hard", "extreme"]
        self.ai_difficulty_options = ["easy", "medium", "hard", "adaptive", "enhanced", "boss"]
        self.handbook = GameHandbook()

    def display_menu(self):
        """Главное меню настроек"""
        while True:
            print("\n" + "=" * 50)
            print("⚙️ НАСТРОЙКИ ИГРЫ")
            print("=" * 50)
            print("1. 🎯 Настройки логирования")
            print("2. 🎮 Настройки игры")
            print("3. 🤖 Расширенные настройки AI")
            print("4. 🔧 Полезные функции")
            print("5. 📚 Справочник и помощь")
            print("6. 📊 Информация о системе")
            print("7. 💾 Сохранить настройки")
            print("0. 🔙 Назад в главное меню")

            choice = input("Выберите опцию: ").strip()
            clear_console_def(1, 0)

            if choice == "1":
                self.logging_settings()
            elif choice == "2":
                self.game_settings()
            elif choice == "3":
                self.advanced_ai_settings()
            elif choice == "4":
                self.utility_functions()
            elif choice == "5":
                self.help_and_guide()
            elif choice == "6":
                self.system_info()
            elif choice == "7":
                if self.settings_manager.save_settings():
                    print("✅ Настройки успешно сохранены!")
                else:
                    print("❌ Ошибка сохранения настроек!")
                clear_console_def(2, 2)
            elif choice == "0":
                break
            else:
                print("❌ Неверный выбор!")

    def logging_settings(self):
        """Настройки логирования"""
        while True:
            print("\n" + "-" * 40)
            print("📝 НАСТРОЙКИ ЛОГИРОВАНИЯ")
            print("-" * 40)
            logging_settings = self.settings_manager.settings["logging"]

            print(f"1. ⚠️  Предупреждения: {'ВКЛ' if logging_settings['warning'] else 'ВЫКЛ'}")
            print(f"2. ❌ Ошибки: {'ВКЛ' if logging_settings['error'] else 'ВЫКЛ'}")
            print(f"3. ℹ️  Информация: {'ВКЛ' if logging_settings['info'] else 'ВЫКЛ'}")
            print(f"4. 🐛 Отладочная информация: {'ВКЛ' if logging_settings['debug'] else 'ВЫКЛ'}")
            print("0. 🔙 Назад")

            choice = input("Выберите опцию для переключения: ").strip()
            clear_console_def(1, 0)

            if choice == "1":
                logging_settings['warning'] = not logging_settings['warning']
                status = "✅ включены" if logging_settings['warning'] else "❌ выключены"
                print(f"✅ Предупреждения {status}")
            elif choice == "2":
                logging_settings['error'] = not logging_settings['error']
                status = "✅ включены" if logging_settings['error'] else "❌ выключены"
                print(f"✅ Ошибки {status}")
            elif choice == "3":
                logging_settings['info'] = not logging_settings['info']
                status = "✅ включена" if logging_settings['info'] else "❌ выключена"
                print(f"✅ Информация {status}")
            elif choice == "4":
                logging_settings['debug'] = not logging_settings['debug']
                status = "✅ включена" if logging_settings['debug'] else "❌ выключена"
                print(f"✅ Отладочная информация {status}")
            elif choice == "0":
                break
            else:
                print("❌ Неверный выбор!")

    def game_settings(self):
        """Настройки игры"""
        while True:
            print("\n" + "-" * 40)
            print("🎮 НАСТРОЙКИ ИГРЫ")
            print("-" * 40)
            game_settings = self.settings_manager.settings["game"]
            ai_settings = self.settings_manager.settings["ai"]

            print(f"1. 🎯 Сложность игры: {game_settings['difficulty'].upper()}")
            print(f"2. 🤖 Сложность AI: {ai_settings['enemy_ai_difficulty'].upper()}")
            print(f"3. 💾 Автосохранение: {'ВКЛ' if game_settings['auto_save'] else 'ВЫКЛ'}")
            print(f"4. 🧠 Обучение AI: {'ВКЛ' if ai_settings['ai_learning'] else 'ВЫКЛ'}")
            print(f"5. 🌐 Язык: {game_settings['language']}")
            print("6. 🔙 Назад")

            choice = input("Выберите опцию: ").strip()
            clear_console_def(1, 0)

            if choice == "1":
                self.change_difficulty()
            elif choice == "2":
                self.change_ai_difficulty()
            elif choice == "3":
                game_settings['auto_save'] = not game_settings['auto_save']
                status = "включено" if game_settings['auto_save'] else "выключено"
                print(f"✅ Автосохранение {status}")
            elif choice == "4":
                ai_settings['ai_learning'] = not ai_settings['ai_learning']
                status = "включено" if ai_settings['ai_learning'] else "выключено"
                print(f"✅ Обучение AI {status}")
            elif choice == "5":
                print("🌐 Смена языка (в разработке)")
            elif choice == "6":
                break
            else:
                print("❌ Неверный выбор!")

    def change_difficulty(self):
        """Изменение сложности игры"""
        print("\nВыберите сложность:")
        for i, diff in enumerate(self.difficulty_options, 1):
            print(f"{i}. {diff.upper()}")

        try:
            choice = int(input("Ваш выбор: ")) - 1
            if 0 <= choice < len(self.difficulty_options):
                self.settings_manager.settings["game"]["difficulty"] = self.difficulty_options[choice]
                print(f"✅ Сложность изменена на: {self.difficulty_options[choice].upper()}")
                self.settings_manager.log_info(f"Сложность изменена на {self.difficulty_options[choice]}")
            else:
                print("❌ Неверный выбор!")
                clear_console_def(2, 2)
        except ValueError:
            print("❌ Введите число!")
            clear_console_def(2, 2)

    def change_ai_difficulty(self):
        """Изменение сложности AI"""
        print("\nВыберите сложность AI:")
        for i, diff in enumerate(self.ai_difficulty_options, 1):
            print(f"{i}. {diff.upper()}")

        try:
            choice = int(input("Ваш выбор: ")) - 1
            if 0 <= choice < len(self.ai_difficulty_options):
                self.settings_manager.settings["ai"]["enemy_ai_difficulty"] = self.ai_difficulty_options[choice]
                print(f"✅ Сложность AI изменена на: {self.ai_difficulty_options[choice].upper()}")
                self.settings_manager.log_info(f"Сложность AI изменена на {self.ai_difficulty_options[choice]}")
            else:
                print("❌ Неверный выбор!")
        except ValueError:
            print("❌ Введите число!")

    def advanced_ai_settings(self):
        """Расширенные настройки AI"""
        while True:
            print("\n" + "-" * 40)
            print("🤖 РАСШИРЕННЫЕ НАСТРОЙКИ AI")
            print("-" * 40)
            ai_settings = self.settings_manager.settings["ai"]

            print(f"1. 🧠 Улучшенный ИИ: {'✅ ВКЛ' if ai_settings['enhanced_ai_enabled'] else '❌ ВЫКЛ'}")
            print(f"2. 📚 Обучение ИИ: {'✅ ВКЛ' if ai_settings['ai_learning'] else '❌ ВЫКЛ'}")
            print(f"3. 🔄 Адаптивное поведение: {'✅ ВКЛ' if ai_settings['adaptive_behavior'] else '❌ ВЫКЛ'}")
            print(f"4. ⚔️ Уровень агрессии: {ai_settings['ai_aggression_level']:.1f}")
            print(f"5. 🎯 Точность предсказаний: {ai_settings['ai_prediction_accuracy']:.1f}")
            print(f"6. 💾 Размер памяти ИИ: {ai_settings['ai_memory_size']}")
            print(f"7. 🔮 Особые способности: {'✅ ВКЛ' if ai_settings['special_abilities_enabled'] else '❌ ВЫКЛ'}")
            print("8. 📖 Советы по противодействию ИИ")
            print("0. 🔙 Назад")

            choice = input("Выберите опцию: ").strip()
            clear_console_def(1, 0)

            if choice == "1":
                ai_settings['enhanced_ai_enabled'] = not ai_settings['enhanced_ai_enabled']
                status = "включен" if ai_settings['enhanced_ai_enabled'] else "выключен"
                print(f"✅ Улучшенный ИИ {status}")
            elif choice == "2":
                ai_settings['ai_learning'] = not ai_settings['ai_learning']
                status = "включено" if ai_settings['ai_learning'] else "выключено"
                print(f"✅ Обучение ИИ {status}")
            elif choice == "3":
                ai_settings['adaptive_behavior'] = not ai_settings['adaptive_behavior']
                status = "включено" if ai_settings['adaptive_behavior'] else "выключено"
                print(f"✅ Адаптивное поведение {status}")
            elif choice == "4":
                try:
                    new_value = float(input("Введите уровень агрессии (0.1-0.9): "))
                    if 0.1 <= new_value <= 0.9:
                        ai_settings['ai_aggression_level'] = new_value
                        print(f"✅ Уровень агрессии изменен на: {new_value:.1f}")
                    else:
                        print("❌ Значение должно быть от 0.1 до 0.9!")
                except ValueError:
                    print("❌ Введите число!")
            elif choice == "5":
                try:
                    new_value = float(input("Введите точность предсказаний (0.1-1.0): "))
                    if 0.1 <= new_value <= 1.0:
                        ai_settings['ai_prediction_accuracy'] = new_value
                        print(f"✅ Точность предсказаний изменена на: {new_value:.1f}")
                    else:
                        print("❌ Значение должно быть от 0.1 до 1.0!")
                except ValueError:
                    print("❌ Введите число!")
            elif choice == "6":
                try:
                    new_value = int(input("Введите размер памяти ИИ (10-100): "))
                    if 10 <= new_value <= 100:
                        ai_settings['ai_memory_size'] = new_value
                        print(f"✅ Размер памяти ИИ изменен на: {new_value}")
                    else:
                        print("❌ Значение должно быть от 10 до 100!")
                except ValueError:
                    print("❌ Введите целое число!")
            elif choice == "7":
                ai_settings['special_abilities_enabled'] = not ai_settings['special_abilities_enabled']
                status = "включены" if ai_settings['special_abilities_enabled'] else "выключены"
                print(f"✅ Особые способности {status}")
            elif choice == "8":
                show_ai_tips()
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == "0":
                break
            else:
                print("❌ Неверный выбор!")

    def utility_functions(self):
        """Полезные функции"""
        while True:
            print("\n" + "-" * 40)
            print("🔧 ПОЛЕЗНЫЕ ФУНКЦИИ")
            print("-" * 40)
            print("1. 🔄 Сбросить настройки к базовым")
            print("2. 📤 Экспорт настроек")
            print("3. 📥 Импорт настроек")
            print("4. 🗑️  Очистить логи")
            print("5. 🔧 Советы по созданию модов")
            print("0. 🔙 Назад")

            choice = input("Выберите опцию: ").strip()
            clear_console_def(1, 0)

            if choice == "1":
                if input("⚠️ Вы уверены? (y/n): ").lower() == 'y':
                    if self.settings_manager.reset_to_defaults():
                        print("✅ Настройки сброшены!")
                    else:
                        print("❌ Ошибка сброса!")
                    clear_console_def(2, 2)
            elif choice == "2":
                if self.settings_manager.export_settings():
                    print("✅ Настройки экспортированы!")
                else:
                    print("❌ Ошибка экспорта!")
                clear_console_def(2, 2)
            elif choice == "3":
                file_path = input("Введите путь к файлу настроек: ")
                if self.settings_manager.import_settings(file_path):
                    print("✅ Настройки импортированы!")
                else:
                    print("❌ Ошибка импорта!")
                clear_console_def(2, 2)
            elif choice == "4":
                if input("⚠️ Очистить все логи? (y/n): ").lower() == 'y':
                    if self.settings_manager.clear_logs():
                        print("✅ Логи очищены!")
                    else:
                        print("❌ Ошибка очистки!")
                    clear_console_def(2, 2)
            elif choice == "5":
                show_modding_tips()
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == "0":
                break
            else:
                print("❌ Неверный выбор!")
                clear_console_def(2, 2)

    def help_and_guide(self):
        """Раздел справки и помощи"""
        while True:
            print("\n" + "-" * 40)
            print("📚 СПРАВОЧНИК И ПОМОЩЬ")
            print("-" * 40)
            print("1. 🚀 Быстрый старт")
            print("2. 🎮 Основы игры")
            print("3. 🛒 Магазин и предметы")
            print("4. 🤖 Система ИИ")
            print("5. 🔧 Модификации")
            print("6. ⚙️ Настройки")
            print("7. 🔧 Решение проблем")
            print("8. 💰 Экономика игры")
            print("9. 📈 Прогрессия")
            print("10. 🏆 Система достижений")
            print("11. 🎯 Создание достижений")
            print("12. 📦 Создание предметов")
            print("13. 🐍 Создание модов")
            print("14. 📖 Полный справочник")
            print("0. 🔙 Назад")

            choice = input("Выберите опцию: ").strip()
            clear_console_def(1, 0)

            if choice == "1":
                show_quick_guide()
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == "2":
                self.handbook.display_section("game")
                input("\nНажмиte Enter чтобы продолжить...")
            elif choice == "3":
                self.handbook.display_section("shop")
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == "4":
                self.handbook.display_section("ai")
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == "5":
                self.handbook.display_section("modding")
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == "6":
                self.handbook.display_section("settings")
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == "7":
                self.handbook.display_section("troubleshooting")
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == "8":
                show_economy_guide()
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == "9":
                show_progression_guide()
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == "10":
                self.handbook.display_section("achievements")
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == "11":
                self.handbook.display_section("create_achievements")
                show_achievements_creation_tips()
                show_achievement_example()
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == "12":
                self.handbook.display_section("create_items")
                show_items_creation_tips()
                show_item_example()
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == "13":
                self.handbook.display_section("create_mods")
                show_mods_creation_tips()
                show_python_mod_example()
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == "14":
                self.handbook.display_full_handbook()
                input("\nНажмите Enter чтобы продолжить...")
            elif choice == "0":
                break
            else:
                print("❌ Неверный выбор!")

    def system_info(self):
        """Информация о системе"""
        print("\n" + "-" * 40)
        print("📊 СИСТЕМНАЯ ИНФОРМАЦИЯ")
        print("-" * 40)

        system_info = self.settings_manager.get_system_info()
        for key, value in system_info.items():
            print(f"{key}: {value}")

        # Информация о настройках логирования
        print(f"\n📝 Состояние логирования:")
        logging_settings = self.settings_manager.settings["logging"]
        for key, value in logging_settings.items():
            status = "✅ ВКЛ" if value else "❌ ВЫКЛ"
            print(f"  {key}: {status}")

        # Информация о путях
        print(f"\n📁 Пути к файлам:")
        print(f"  Настройки: {self.settings_manager.get_settings_path()}")
        print(f"  Логи: {self.settings_manager.get_logs_path()}")
        print(f"  Конфиги: {self.settings_manager.get_configs_path()}")

        input("\nНажмите Enter чтобы продолжить...")

    def get_ai_difficulty_description(self, difficulty):
        """Получение описания сложности AI"""
        descriptions = {
            'easy': "🤖 Базовый ИИ - простые предсказуемые действия",
            'medium': "🎯 Стандартный ИИ - сбалансированная сложность",
            'hard': "🧠 Улучшенный ИИ - обучается и адаптируется",
            'adaptive': "🔮 Адаптивный ИИ - подстраивается под стиль игрока",
            'enhanced': "⚡ Продвинутый ИИ - использует сложные стратегии",
            'boss': "👑 Босс ИИ - максимальная сложность с особыми способностями"
        }
        return descriptions.get(difficulty, "Неизвестная сложность")

    def show_ai_difficulty_info(self):
        """Показать информацию о сложностях AI"""
        print("\n" + "=" * 50)
        print("🤖 ИНФОРМАЦИЯ О СЛОЖНОСТЯХ AI")
        print("=" * 50)

        for difficulty in self.ai_difficulty_options:
            description = self.get_ai_difficulty_description(difficulty)
            print(f"\n{difficulty.upper()}:")
            print(f"  {description}")

        input("\nНажмите Enter чтобы продолжить...")

    def backup_settings(self):
        """Создание резервной копии настроек"""
        import shutil
        import os
        from datetime import datetime

        backup_dir = "src/saves/backups"
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"settings_backup_{timestamp}.json")

        try:
            shutil.copy2(self.settings_manager.settings_file, backup_file)
            print(f"✅ Резервная копия создана: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания резервной копии: {e}")
            return False

    def restore_backup(self):
        """Восстановление настроек из резервной копии"""
        import os

        backup_dir = "src/saves/backups"
        if not os.path.exists(backup_dir):
            print("❌ Папка с резервными копиями не найдена!")
            return False

        backups = [f for f in os.listdir(backup_dir) if f.startswith("settings_backup_") and f.endswith(".json")]

        if not backups:
            print("❌ Резервные копии не найдены!")
            return False

        print("\n📂 Доступные резервные копии:")
        for i, backup in enumerate(sorted(backups, reverse=True)[:5], 1):  # Показываем последние 5
            print(f"{i}. {backup}")

        try:
            choice = int(input("\nВыберите резервную копию для восстановления: ")) - 1
            if 0 <= choice < len(backups):
                backup_file = os.path.join(backup_dir, sorted(backups, reverse=True)[choice])

                if input(f"⚠️ Восстановить настройки из {backup_file}? (y/n): ").lower() == 'y':
                    import shutil
                    shutil.copy2(backup_file, self.settings_manager.settings_file)
                    print("✅ Настройки восстановлены! Перезапустите игру.")
                    return True
            else:
                print("❌ Неверный выбор!")
        except ValueError:
            print("❌ Введите число!")

        return False


# Дополнительные утилиты для быстрого доступа
def show_settings_quick_tips():
    """Быстрые подсказки по настройкам"""
    tips = [
        "🎯 Сложность игры влияет на силу врагов и награды",
        "🤖 Сложность AI определяет интеллект противников",
        "💾 Автосохранение сохраняет прогресс автоматически",
        "🧠 Обучение AI позволяет врагам адаптироваться к вашему стилю",
        "📝 Логирование помогает в отладке проблем",
        "🔧 Расширенные настройки AI для тонкой настройки баланса",
        "📚 Используйте справочник для изучения всех возможностей"
    ]

    print("\n⚡ БЫСТРЫЕ ПОДСКАЗКИ ПО НАСТРОЙКАМ:")
    for tip in tips:
        print(f"• {tip}")


def show_ai_settings_explanation():
    """Объяснение настроек AI"""
    print("\n🤖 ПОЯСНЕНИЕ НАСТРОЕК AI:")
    print("• 🧠 Улучшенный ИИ: Враги используют сложные стратегии")
    print("• 📚 Обучение ИИ: Враги запоминают ваши действия и адаптируются")
    print("• 🔄 Адаптивное поведение: Враги меняют тактику по ситуации")
    print("• ⚔️ Уровень агрессии: Частота атак врагов (0.1-0.9)")
    print("• 🎯 Точность предсказаний: Точность предсказания ваших действий")
    print("• 💾 Размер памяти ИИ: Сколько ходов помнят враги")
    print("• 🔮 Особые способности: Использование уникальных атак боссами")
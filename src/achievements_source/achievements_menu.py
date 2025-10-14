# [file name]: src/achievements_source/achievements_menu.py
from achievements_source.achievements_manager import AchievementsManager
from utils.helpers_def import clear_console_def, timeout_def
from settings.settings_manager import settings


class AchievementsMenu:
    """Меню достижений для взаимодействия с игроком"""

    def __init__(self, hook_system):
        self.manager = AchievementsManager(hook_system)
        self.hook_system = hook_system

    def display_menu(self, player):
        """Отображает меню достижений"""
        while True:
            clear_console_def(1, 0)
            self.manager.sync_with_player_data(player)
            self.manager.refresh_mod_achievements()

            # Хук предварительного отображения
            self.hook_system.execute_hook('pre_achievements_display', player)

            print("=" * 50)
            print("🏆 ДОСТИЖЕНИЯ TEXT WAR LEGACY")
            print("=" * 50)

            has_tracker = self.check_achievement_tracker(player)
            if has_tracker:
                print("🔮 Трекер достижений активен - все достижения видны!")
            else:
                settings.log_tips("💡 Экипируйте 📊 Трекер достижений чтобы увидеть скрытые достижения!")

            # Общий прогресс
            progress = self.manager.get_player_progress(player)
            print(f"📊 Прогресс: {progress['unlocked']}/{progress['total']} ({progress['progress_percent']:.1f}%)")

            # Прогресс по уровням
            print("\n🎯 Достижения по уровням:")
            for tier, data in progress['by_tier'].items():
                tier_progress = (data['unlocked'] / data['total'] * 100) if data['total'] > 0 else 0
                print(f"   {self.get_tier_icon(tier)} {tier.title()}: {data['unlocked']}/{data['total']} ({tier_progress:.1f}%)")

            print("-" * 50)
            print("1. 📋 Список всех достижений")
            print("2. ✅ Проверить выполненные")
            print("3. 🎁 Получить награды")
            print("4. 🔄 Перезагрузить моды")
            print("0. 🔙 Назад")
            print("=" * 50)

            # Хук пост-отображения
            self.hook_system.execute_hook('post_achievements_display', player, progress)

            choice = input("Выберите опцию: ").strip()

            if choice == "0":
                break
            elif choice == "1":
                self.show_all_achievements(player)
            elif choice == "2":
                self.check_completed_achievements(player)
            elif choice == "3":
                self.claim_rewards(player)
            elif choice == "4":
                self.force_reload_mods(player)
            else:
                print("❌ Неверный выбор!")
                timeout_def(3, 0)

    def show_all_achievements(self, player):
        """Показывает все достижения"""
        clear_console_def(1, 0)
        print("=" * 50)
        print("📋 ВСЕ ДОСТИЖЕНИЯ")
        print("=" * 50)

        has_tracker = self.check_achievement_tracker(player)
        print(f"🔮 Трекер достижений: {'АКТИВЕН ✅' if has_tracker else 'НЕАКТИВЕН ❌'}")

        settings.log_info(f"🔍 Отладка трекера:")
        settings.log_info(f"   - has_achievement_visibility: {getattr(player, 'has_achievement_visibility', 'НЕТ')}")
        settings.log_info(f"   - achievement_visibility: {getattr(player, 'achievement_visibility', 'НЕТ')}")
        if hasattr(player, 'special_effects'):
            settings.log_info(f"   - special_effects: {player.special_effects}")

        achievements = self.manager.get_achievements_display(player)

        # Группируем по уровням
        by_tier = {}
        for achievement in achievements:
            tier = achievement['tier']
            if tier not in by_tier:
                by_tier[tier] = []
            by_tier[tier].append(achievement)

        # Сортируем по уровню (от легких к сложным)
        tier_order = ['Бронзовое', 'Серебряное', 'Золотое', 'Платиновое', 'Легендарное']

        for tier in tier_order:
            if tier in by_tier:
                print(f"\n{tier.upper()} ДОСТИЖЕНИЯ:")
                print("-" * 40)

                for achievement in by_tier[tier]:
                    should_show = has_tracker or achievement['unlocked'] or not achievement['hidden']

                    if achievement['hidden'] and not should_show:
                        print(f"{achievement['icon']} ❓ Секретное достижение 🔒")
                        print("   📝 ??? (разблокируйте чтобы увидеть)")
                        print("   🎁 Награда: ???")
                    else:
                        status = "✅" if achievement['unlocked'] else f"{achievement['progress'] * 100:.1f}%"
                        mod_indicator = achievement['mod_indicator']
                        hidden_indicator = " 🔒" if achievement['hidden'] and not achievement['unlocked'] else ""

                        print(f"{achievement['icon']} {achievement['name']}{mod_indicator}{hidden_indicator} [{status}]")
                        print(f"   📝 {achievement['description']}")

                        if not achievement['unlocked'] and achievement['reward_text']:
                            print(f"   🎁 Награда: {achievement['reward_text']}")
                    print()

        timeout_def(3, 0)

    def check_achievement_tracker(self, player):
        """Проверяет, есть ли у игрока трекер достижений (ИСПРАВЛЕННАЯ ВЕРСИЯ)"""
        try:
            inventory_manager = getattr(self.hook_system, 'inventory_manager', None)
            if inventory_manager:
                equipped_items = inventory_manager.get_equipped_items()
                for item in equipped_items:
                    if item.effects and item.effects.get('achievement_visibility'):
                        return True

                    if any(keyword in item.name.lower() for keyword in ['трекер', 'tracker', '📊']):
                        return True

            if getattr(player, 'achievement_visibility', False):
                return True

            if getattr(player, 'has_achievement_visibility', False):
                return True

            return False

        except Exception as e:
            settings.log_error(f"⚠️ Ошибка проверки трекера: {e}")
            return False

    def check_completed_achievements(self, player):
        """Проверяет и разблокирует выполненные достижения"""
        clear_console_def(1, 0)
        print("=" * 50)
        print("✅ ПРОВЕРКА ДОСТИЖЕНИЙ")
        print("=" * 50)

        newly_unlocked = self.manager.check_all_achievements(player)

        if newly_unlocked:
            print("🎉 Разблокированы новые достижения:")
            for achievement_id, message in newly_unlocked:
                print(f"   • {message}")
        else:
            print("📭 Новых достижений для разблокировки нет.")

        timeout_def(3, 0)

    def claim_rewards(self, player):
        """Позволяет получить награды за достижения"""
        clear_console_def(1, 0)
        print("=" * 50)
        print("🎁 ПОЛУЧЕНИЕ НАГРАД")
        print("=" * 50)

        achievements = self.manager.get_achievements_display(player)
        claimable = [a for a in achievements if a['completed'] and not a['unlocked']]

        if not claimable:
            print("📭 Нет достижений готовых для получения наград.")
            timeout_def(3, 0)
            return

        print("Доступные для получения наград достижения:")
        for i, achievement in enumerate(claimable, 1):
            print(f"{i}. {achievement['icon']} {achievement['name']}")
            print(f"   📝 {achievement['description']}")
            print(f"   🎁 Награда: {achievement['reward_text']}")
            print()

        try:
            choice = int(input("Выберите достижение для получения награды: ")) - 1
            if 0 <= choice < len(claimable):
                achievement_id = claimable[choice]['id']
                success, message = self.manager.process_achievement_unlock(achievement_id, player)
                print(f"\n{message}")
            else:
                print("❌ Неверный выбор!")
        except ValueError:
            print("❌ Введите число!")

        timeout_def(3, 0)

    def force_reload_mods(self, player):
        """Принудительно перезагружает моды"""
        clear_console_def(1, 0)
        print("=" * 50)
        print("🔄 ПЕРЕЗАГРУЗКА МОДОВ")
        print("=" * 50)

        print("Перезагружаем достижения из модов...")
        self.manager.refresh_mod_achievements()

        # Обновляем статистику
        self.manager.sync_with_player_data(player)

        total_achievements = self.manager.get_total_count()
        unlocked_achievements = self.manager.get_unlocked_count()

        print(f"✅ Система обновлена!")
        print(f"📊 Всего достижений: {total_achievements}")
        print(f"🎯 Разблокировано: {unlocked_achievements}")

        timeout_def(3, 0)

    @staticmethod
    def get_tier_icon(tier: str) -> str:
        """Получает иконку для уровня достижения"""
        icons = {
            'bronze': "🥉",
            'silver': "🥈",
            'gold': "🥇",
            'platinum': "💎",
            'legendary': "👑"
        }
        return icons.get(tier.lower(), "🎯")

    def debug_tracker_info(self, player):
        """Выводит отладочную информацию о трекере"""
        settings.log_info("\n🔧 ОТЛАДОЧНАЯ ИНФОРМАЦИЯ О ТРЕКЕРЕ:")
        settings.log_info(f"   has_achievement_visibility: {getattr(player, 'has_achievement_visibility', 'NOT SET')}")
        settings.log_info(f"   achievement_visibility: {getattr(player, 'achievement_visibility', 'NOT SET')}")

        if hasattr(player, 'special_effects'):
            settings.log_info(f"   special_effects: {player.special_effects}")
        else:
            settings.log_info("   special_effects: NOT SET")

        inventory_manager = getattr(self.hook_system, 'inventory_manager', None)
        if inventory_manager:
            equipped_items = inventory_manager.get_equipped_items()
            settings.log_info(f"   Экипировано предметов: {len(equipped_items)}")
            for item in equipped_items:
                settings.log_info(f"     - {item.name}: {item.effects}")
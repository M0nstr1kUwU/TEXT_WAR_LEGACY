# [file name]: src/achievements_source/achievements_manager.py
import json
import os
from datetime import datetime
from shutil import move, copy2
from typing import List, Any, Optional
from pathlib import Path
from achievements_source.achievements_core import AchievementSystem, Achievement
from settings.settings_manager import settings


class AchievementsManager:
    """Менеджер достижений для интеграции с игрой"""

    def __init__(self, hook_system):
        self.system = AchievementSystem(hook_system)
        self.hook_system = hook_system
        self.unlocked_achievements: List[str] = []
        self.achievements_file = Path("src/saves/configs/achievements.json")
        self.load_achievements_progress()
        self.load_mod_achievements()

    def save_achievements_progress(self):
        """Сохраняет прогресс достижений в файл"""
        try:
            self.achievements_file.parent.mkdir(parents=True, exist_ok=True)

            serializable_stats = {}
            for key, value in self.system.player_stats.items():
                if isinstance(value, set):
                    serializable_stats[key] = list(value)
                else:
                    serializable_stats[key] = value

            data = {
                "unlocked_achievements": list(self.unlocked_achievements),
                "player_stats": serializable_stats
            }

            with open(self.achievements_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            settings.log_info(f"✅ Прогресс сохранен: {len(self.unlocked_achievements)} достижений")
        except Exception as e:
            settings.log_error(f"❌ Ошибка сохранения прогресса достижений: {e}")

    def load_achievements_progress(self):
        """Загружает прогресс достижений из файла с обработкой ошибок"""
        try:
            if not self.achievements_file.exists():
                settings.log_info("📁 Файл достижений не найден, создаем новый...")
                self.unlocked_achievements = []
                self.system.player_stats = {}
                return

            with open(self.achievements_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.unlocked_achievements = data.get("unlocked_achievements", [])
            player_stats_data = data.get("player_stats", {})
            self.system.player_stats = {}

            default_stats = {
                'battles_won': 0,
                'battles_lost': 0,
                'total_coins_earned': 0,
                'total_damage_dealt': 0,
                'total_healing_done': 0,
                'max_damage_single_battle': 0,
                'max_health': 0,
                'items_purchased': 0,
                'mystery_box_bonus': False,
                'boss_no_damage': False,
                'classes_used': set(),
                'abilities_used': set(),
                'elements_used': set(),
                'elemental_damage': {},
                'menus_visited': 0,
                'unique_items_collected': 0,
                'perfect_defenses': 0,
                'dodge_streak': 0
            }

            for key, default_value in default_stats.items():
                if key in player_stats_data:
                    if key in ['classes_used', 'abilities_used', 'elements_used']:
                        if isinstance(player_stats_data[key], list):
                            self.system.player_stats[key] = set(player_stats_data[key])
                        else:
                            self.system.player_stats[key] = set()
                    else:
                        self.system.player_stats[key] = player_stats_data[key]
                else:
                    self.system.player_stats[key] = default_value

            settings.log_info(f"✅ Загружен прогресс достижений: {len(self.unlocked_achievements)} разблокированных")

        except json.JSONDecodeError as e:
            settings.log_error(f"❌ Ошибка формата JSON в файле достижений: {e}")
            self.create_backup_and_reset()
        except Exception as e:
            settings.log_error(f"❌ Ошибка загрузки прогресса достижений: {e}")
            self.unlocked_achievements = []
            self.system.player_stats = {}

    def create_backup_and_reset(self):
        """Создает резервную копию поврежденного файла и сбрасывает прогресс"""
        try:
            if self.achievements_file.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self.achievements_file.parent / f"achievements_backup_{timestamp}.json"

                copy2(self.achievements_file, backup_file)
                print(f"📦 Создана резервная копия: {backup_file.name}")

                # ПЕРЕИМЕНОВЫВАЕМ ПОВРЕЖДЕННЫЙ ФАЙЛ
                corrupted_file = self.achievements_file.parent / f"achievements_corrupted_{timestamp}.json"
                move(self.achievements_file, corrupted_file)
                print(f"🚨 Поврежденный файл перемещен: {corrupted_file.name}")

        except Exception as backup_error:
            settings.log_error(f"⚠️ Ошибка создания резервной копии: {backup_error}")

        self.unlocked_achievements = []
        self.system.player_stats = {}
        print("🔄 Прогресс достижений сброшен из-за ошибки файла")
        settings.log_info("🔄 Прогресс достижений сброшен из-за ошибки файла")

    def process_achievement_unlock(self, achievement_id: str, player) -> tuple[bool, str]:
        """Обрабатывает разблокировку достижения"""
        if achievement_id in self.unlocked_achievements:
            return False, "❌ Достижение уже разблокировано!"

        completed, _ = self.system.check_achievement_progress(achievement_id, player)
        if not completed:
            return False, "❌ Достижение еще не выполнено!"

        success, message = self.system.unlock_achievement(achievement_id, player)

        if success:
            self.unlocked_achievements.append(achievement_id)
            self.save_achievements_progress()
            # Хук успешной разблокировки
            self.hook_system.execute_hook('achievement_unlocked', achievement_id, player)

        return success, message

    def record_stat(self, stat_name: str, value: Any = 1, increment: bool = True):
        """Записывает статистику для достижений (ИСПРАВЛЕННАЯ ВЕРСИЯ)"""

        safe_value = int(value) if isinstance(value, (int, float, str)) and str(value).isdigit() else 0
        current = self.system.player_stats.get(stat_name, 0)
        safe_current = int(current) if isinstance(current, (int, float, str)) and str(current).isdigit() else 0

        if increment:
            self.system.player_stats[stat_name] = safe_current + safe_value
        else:
            self.system.player_stats[stat_name] = max(safe_value, safe_current)
        self.save_achievements_progress()

        # Хук записи статистики
        self.hook_system.execute_hook('achievement_stat_recorded', stat_name, safe_value, increment)

    def load_mod_achievements(self):
        """Загрузка достижений из модов (ИСПРАВЛЕННАЯ ВЕРСИЯ)"""
        mods_dir = Path("src/saves/mods")

        if not mods_dir.exists():
            settings.log_info("📁 Папка модов не найдена, создаем...")
            mods_dir.mkdir(parents=True, exist_ok=True)
            return

        loaded_count = 0
        for filename in os.listdir(mods_dir):
            if filename.endswith('.json'):
                mod_name = filename[:-5]  # Убираем .json
                try:
                    mod_path = mods_dir / filename
                    with open(mod_path, 'r', encoding='utf-8') as f:
                        mod_data = json.load(f)

                    if 'achievements' in mod_data:
                        for achievement_data in mod_data['achievements']:
                            success = self.system.add_mod_achievement(achievement_data, mod_name)
                            if success:
                                loaded_count += 1
                                settings.log_info(f"   ✅ Загружено: {achievement_data['name']}")

                except Exception as e:
                    settings.log_error(f"❌ Ошибка загрузки мода {filename}: {e}")

        if loaded_count > 0:
            settings.log_info(f"✅ Загружено {loaded_count} достижений из модов")

    def get_achievements_display(self, player) -> List[dict]:
        """Получает данные для отображения достижений"""
        display_data = []

        for achievement in self.system.achievements.values():
            completed, progress = self.system.check_achievement_progress(achievement.id, player)
            unlocked = achievement.id in self.unlocked_achievements

            achievement_display = {
                'id': achievement.id,
                'name': achievement.name,
                'description': achievement.description,
                'icon': achievement.icon,
                'tier': achievement.tier_name,
                'progress': progress,
                'completed': completed,
                'unlocked': unlocked,
                'hidden': achievement.hidden and not unlocked,
                'mod_indicator': " [MOD]" if achievement.mod_source != "vanilla" else "",
                'reward_text': self.get_reward_text(achievement)
            }

            # Хук модификации отображения
            achievement_display = self.hook_system.execute_hook(
                'achievement_display',
                achievement_display, achievement, player
            ) or achievement_display

            display_data.append(achievement_display)

        return display_data

    @staticmethod
    def get_reward_text(achievement: Achievement) -> str:
        """Получает текст награды достижения"""
        rewards = []
        if achievement.reward_coins > 0:
            rewards.append(f"💰 {achievement.reward_coins}")
        if achievement.reward_xp > 0:
            rewards.append(f"⭐ {achievement.reward_xp}")
        if achievement.reward_item:
            rewards.append(f"🎁 {achievement.reward_item}")

        return " + ".join(rewards) if rewards else ""

    def check_all_achievements(self, player):
        """Проверяет все достижения на выполнение"""
        newly_unlocked = []

        for achievement_id in self.system.achievements:
            if achievement_id not in self.unlocked_achievements:
                completed, _ = self.system.check_achievement_progress(achievement_id, player)
                if completed:
                    success, message = self.process_achievement_unlock(achievement_id, player)
                    if success:
                        newly_unlocked.append((achievement_id, message))
                        print(f"🎉 Достижение разблокировано: {message}")

        return newly_unlocked

    def get_player_progress(self, player) -> dict:
        """Получает общий прогресс по достижениям"""
        total = len(self.system.achievements)
        unlocked = len(self.unlocked_achievements)
        by_tier = {}
        for achievement in self.system.achievements.values():
            tier = achievement.tier.value
            if tier not in by_tier:
                by_tier[tier] = {'total': 0, 'unlocked': 0}

            by_tier[tier]['total'] += 1
            if achievement.id in self.unlocked_achievements:
                by_tier[tier]['unlocked'] += 1

        return {
            'total': total,
            'unlocked': unlocked,
            'progress_percent': (unlocked / total * 100) if total > 0 else 0,
            'by_tier': by_tier
        }

    def refresh_mod_achievements(self):
        """Принудительно перезагружает достижения из модов"""
        print("🔄 Перезагрузка достижений из модов...")
        settings.log_info("🔄 Перезагрузка достижений из модов...")


        # Удаляем старые мод-достижения
        achievements_to_remove = []
        for achievement_id, achievement in self.system.achievements.items():
            if achievement.mod_source != "vanilla":
                achievements_to_remove.append(achievement_id)

        for achievement_id in achievements_to_remove:
            del self.system.achievements[achievement_id]
        self.load_mod_achievements()

        print(f"✅ Перезагружено достижений: {len(self.system.achievements)}")
        settings.log_info(f"✅ Перезагружено достижений: {len(self.system.achievements)}")

    def sync_with_player_data(self, player):
        """Синхронизирует данные с игроком"""
        if hasattr(player, 'unlocked_achievements'):
            for achievement_id in player.unlocked_achievements:
                if achievement_id not in self.unlocked_achievements:
                    self.unlocked_achievements.append(achievement_id)

        if hasattr(player, 'player_stats'):
            self.system.player_stats.update(player.player_stats)

    def get_achievement_by_id(self, achievement_id: str) -> Optional[Achievement]:
        """Возвращает достижение по ID"""
        return self.system.achievements.get(achievement_id)

    def get_unlocked_count(self) -> int:
        """Возвращает количество разблокированных достижений"""
        return len(self.unlocked_achievements)

    def get_total_count(self) -> int:
        """Возвращает общее количество достижений"""
        return len(self.system.achievements)


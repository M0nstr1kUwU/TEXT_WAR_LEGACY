# [file name]: src/achievements_source/achievements_core.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from settings.settings_manager import settings


class AchievementTier(Enum):
    """Уровни достижений"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    LEGENDARY = "legendary"


@dataclass
class Achievement:
    """Класс достижения"""
    id: str
    name: str
    description: str
    tier: AchievementTier
    condition: str  # Тип условия для проверки
    target_value: Any  # Целевое значение для выполнения
    reward_coins: int = 0
    reward_xp: int = 0
    reward_item: Optional[str] = None
    hidden: bool = False
    mod_source: str = "vanilla"  # Источник достижения

    @property
    def icon(self) -> str:
        """Иконка достижения в зависимости от уровня"""
        icons = {
            AchievementTier.BRONZE: "🥉",
            AchievementTier.SILVER: "🥈",
            AchievementTier.GOLD: "🥇",
            AchievementTier.PLATINUM: "💎",
            AchievementTier.LEGENDARY: "👑"
        }
        return icons.get(self.tier, "🎯")

    @property
    def tier_name(self) -> str:
        """Название уровня достижения"""
        names = {
            AchievementTier.BRONZE: "Бронзовое",
            AchievementTier.SILVER: "Серебряное",
            AchievementTier.GOLD: "Золотое",
            AchievementTier.PLATINUM: "Платиновое",
            AchievementTier.LEGENDARY: "Легендарное"
        }
        return names.get(self.tier, "Достижение")


class AchievementSystem:
    """Система управления достижениями"""

    def __init__(self, hook_system):
        self.hook_system = hook_system
        self.achievements: Dict[str, Achievement] = {}
        self.player_stats: Dict[str, Any] = {}
        self.load_vanilla_achievements()

    def load_vanilla_achievements(self):
        """Загрузка стандартных достижений"""
        vanilla_achievements = [
            # Базовые достижения
            Achievement(
                id="first_victory",
                name="Первая кровь",
                description="Одержите первую победу в битве",
                tier=AchievementTier.BRONZE,
                condition="battles_won",
                target_value=1,
                reward_coins=10,
                reward_xp=50
            ),
            Achievement(
                id="veteran",
                name="Ветеран",
                description="Выиграйте 10 битв",
                tier=AchievementTier.SILVER,
                condition="battles_won",
                target_value=10,
                reward_coins=50,
                reward_xp=200
            ),
            Achievement(
                id="champion",
                name="Чемпион",
                description="Выиграйте 50 битв",
                tier=AchievementTier.GOLD,
                condition="battles_won",
                target_value=50,
                reward_coins=200,
                reward_xp=1000
            ),

            # Экономические достижения
            Achievement(
                id="first_coin",
                name="Первая монета",
                description="Заработайте первую монету",
                tier=AchievementTier.BRONZE,
                condition="total_coins_earned",
                target_value=1,
                reward_coins=5,
                reward_xp=25
            ),
            Achievement(
                id="rich",
                name="Богач",
                description="Накопите 1000 монет",
                tier=AchievementTier.SILVER,
                condition="total_coins_earned",
                target_value=1000,
                reward_coins=100,
                reward_xp=500
            ),

            # Боевые достижения
            Achievement(
                id="damage_dealer",
                name="Наносящий урон",
                description="Нанесите 100 урона за одну битву",
                tier=AchievementTier.SILVER,
                condition="max_damage_single_battle",
                target_value=100,
                reward_coins=75,
                reward_xp=300
            ),
            Achievement(
                id="tank",
                name="Танк",
                description="Имейте 50 максимального здоровья",
                tier=AchievementTier.GOLD,
                condition="max_health",
                target_value=50,
                reward_coins=150,
                reward_xp=750
            ),

            # Магазинные достижения
            Achievement(
                id="first_purchase",
                name="Первая покупка",
                description="Купите первый предмет в магазине",
                tier=AchievementTier.BRONZE,
                condition="items_purchased",
                target_value=1,
                reward_coins=20,
                reward_xp=100
            ),
            Achievement(
                id="shopaholic",
                name="Шопоголик",
                description="Купите 20 предметов в магазине",
                tier=AchievementTier.GOLD,
                condition="items_purchased",
                target_value=20,
                reward_coins=300,
                reward_xp=1500
            ),

            # Скрытые достижения
            Achievement(
                id="lucky",
                name="Везунчик",
                description="Получите бонус из таинственной коробки",
                tier=AchievementTier.SILVER,
                condition="mystery_box_bonus",
                target_value=1,
                reward_coins=100,
                reward_xp=400,
                hidden=True
            ),
            Achievement(
                id="immortal",
                name="Бессмертный",
                description="Победите босса не получив урона",
                tier=AchievementTier.PLATINUM,
                condition="boss_no_damage",
                target_value=1,
                reward_coins=500,
                reward_xp=2500,
                hidden=True
            ),
            Achievement(
                id="explorer",
                name="Исследователь",
                description="Посетите все меню игры",
                tier=AchievementTier.BRONZE,
                condition="menus_visited",
                target_value=5,
                reward_coins=30,
                reward_xp=100,
                hidden=False
            ),
            Achievement(
                id="collector",
                name="Коллекционер",
                description="Соберите 10 различных предметов",
                tier=AchievementTier.SILVER,
                condition="unique_items_collected",
                target_value=10,
                reward_coins=150,
                reward_xp=400,
                hidden=False
            ),
            Achievement(
                id="first_class",
                name="Первый выбор",
                description="Выберите свой первый класс",
                tier=AchievementTier.BRONZE,
                condition="classes_used",
                target_value=1,
                reward_coins=25,
                reward_xp=100,
                hidden=False
            ),
            Achievement(
                id="class_master",
                name="Мастер классов",
                description="Испробуйте все доступные классы",
                tier=AchievementTier.GOLD,
                condition="classes_used",
                target_value=5,
                reward_coins=200,
                reward_xp=500,
                hidden=False
            ),
            Achievement(
                id="ability_user",
                name="Пользователь способностей",
                description="Используйте 10 различных способностей классов",
                tier=AchievementTier.SILVER,
                condition="abilities_used",
                target_value=10,
                reward_coins=100,
                reward_xp=300,
                hidden=False
            ),
            Achievement(
                id="elemental_novice",
                name="Новичок стихий",
                description="Используйте 3 различных элемента",
                tier=AchievementTier.BRONZE,
                condition="elements_used",
                target_value=3,
                reward_coins=50,
                reward_xp=150,
                hidden=False
            ),
            Achievement(
                id="elemental_master",
                name="Мастер стихий",
                description="Используйте все доступные элементы",
                tier=AchievementTier.PLATINUM,
                condition="elements_used",
                target_value=8,
                reward_coins=300,
                reward_xp=800,
                hidden=False
            ),
        ]

        for achievement in vanilla_achievements:
            self.achievements[achievement.id] = achievement

    def add_mod_achievement(self, achievement_data: Dict[str, Any], mod_name: str):
        """Добавляет достижение из мода"""
        try:
            achievement_id = f"{mod_name}_{achievement_data['id']}"
            if achievement_id in self.achievements:
                return False

            achievement = Achievement(
                id=achievement_id,
                name=achievement_data['name'],
                description=achievement_data['description'],
                tier=AchievementTier(achievement_data['tier']),
                condition=achievement_data['condition'],
                target_value=achievement_data['target_value'],
                reward_coins=achievement_data.get('reward_coins', 0),
                reward_xp=achievement_data.get('reward_xp', 0),
                reward_item=achievement_data.get('reward_item'),
                hidden=achievement_data.get('hidden', False),
                mod_source=mod_name
            )
            self.achievements[achievement.id] = achievement
            return True
        except Exception as e:
            settings.log_error(f"❌ Ошибка добавления достижения из мода {mod_name}: {e}")
            return False

    def update_player_stats(self, stats: Dict[str, Any]):
        """Обновление статистики игрока"""
        self.player_stats.update(stats)

        # Хук обновления статистики
        self.hook_system.execute_hook('achievement_stats_updated', self.player_stats)

    def check_achievement_progress(self, achievement_id: str, player) -> tuple[bool, float]:
        """Проверяет прогресс выполнения достижения"""
        if achievement_id not in self.achievements:
            return False, 0.0

        achievement = self.achievements[achievement_id]
        current_value = self.get_stat_value(achievement.condition, player)
        target_value = achievement.target_value

        # Хук проверки прогресса
        hook_result = self.hook_system.execute_hook(
            'achievement_progress_check',
            achievement, current_value, target_value, player
        )
        if hook_result is not None:
            current_value, target_value = hook_result

        if isinstance(target_value, (int, float)) and isinstance(current_value, (int, float)):
            progress = min(current_value / target_value, 1.0) if target_value > 0 else 1.0
            completed = current_value >= target_value
        else:
            progress = 1.0 if current_value == target_value else 0.0
            completed = current_value == target_value

        return completed, progress

    def get_stat_value(self, condition: str, player) -> Any:
        """Получает значение статистики по условию"""
        stat_map = {
            'battles_won': lambda p: self.player_stats.get('battles_won', 0),
            'total_coins_earned': lambda p: self.player_stats.get('total_coins_earned', 0),
            'max_damage_single_battle': lambda p: self.player_stats.get('max_damage_single_battle', 0),
            'max_health': lambda p: p.health_max,
            'items_purchased': lambda p: self.player_stats.get('items_purchased', 0),
            'mystery_box_bonus': lambda p: self.player_stats.get('mystery_box_bonus', 0),
            'boss_no_damage': lambda p: self.player_stats.get('boss_no_damage', 0),
            'player_level': lambda p: p.level,
            'total_experience': lambda p: p.experience,
            'first_victory': lambda p: 1 if self.player_stats.get('battles_won', 0) >= 1 else 0,
            'menus_visited': lambda p: self.player_stats.get('menus_visited', 0),
            'unique_items_collected': lambda p: self.player_stats.get('unique_items_collected', 0),

            # УСЛОВИЯ ДЛЯ МОДОВ
            'combo_critical_streak': lambda p: getattr(p, 'extended_stats', {}).get('combo_critical_streak', 0),
            'fast_victory_turns': lambda p: 1 if getattr(p, 'extended_stats', {}).get('fast_victories', 0) > 0 else 0,
            'fast_victories_count': lambda p: getattr(p, 'extended_stats', {}).get('fast_victories', 0),
            'perfect_defense_streak': lambda p: self.player_stats.get('perfect_defenses', 0),
            'low_health_victory': lambda p: getattr(p, 'extended_stats', {}).get('low_health_victories', 0),
            'potions_used_total': lambda p: getattr(p, 'extended_stats', {}).get('potions_used', 0),
            'all_elements_used': lambda p: 1 if len(self.player_stats.get('elements_used', set())) >= 3 else 0,
            'coins_saved': lambda p: p.coin,
            'all_shop_categories': lambda p: 1 if len(self.player_stats.get('shop_categories', set())) >= 4 else 0,
            'achievements_unlocked': lambda p: len(getattr(p, 'unlocked_achievements', [])),
            'easter_egg_found': lambda p: self.player_stats.get('easter_eggs_found', 0),
            'lucky_critical_streak': lambda p: getattr(p, 'extended_stats', {}).get('combo_critical_streak', 0),
            'dodge_streak': lambda p: self.player_stats.get('dodge_streak', 0),
            'elemental_mastery': lambda p: 1 if all(dmg >= 1000 for dmg in self.player_stats.get('elemental_damage', {}).values()) else 0,
            'classes_used': lambda p: len(p.player_stats.get('classes_used', set())),
            'abilities_used': lambda p: len(p.player_stats.get('abilities_used', set())),
            'elements_used': lambda p: len(p.player_stats.get('elements_used', set())),
        }

        if condition in stat_map:
            return stat_map[condition](player)

        # Хук для кастомных условий
        hook_result = self.hook_system.execute_hook(
            'achievement_stat_value',
            condition, player, self.player_stats
        )
        if hook_result is not None:
            return hook_result

        return 0

    def unlock_achievement(self, achievement_id: str, player) -> tuple[bool, str]:
        """Разблокирует достижение и выдает награды"""
        if achievement_id not in self.achievements:
            return False, "❌ Достижение не найдено!"

        achievement = self.achievements[achievement_id]

        # УБЕДИТЕСЬ ЧТО ДОСТИЖЕНИЕ ЕЩЕ НЕ РАЗБЛОКИРОВАНО
        if hasattr(player, 'unlocked_achievements') and achievement_id in player.unlocked_achievements:
            return False, "❌ Достижение уже разблокировано!"

        # Проверяем выполнено ли достижение
        completed, _ = self.check_achievement_progress(achievement_id, player)
        if not completed:
            return False, "❌ Достижение еще не выполнено!"

        # Хук предварительной разблокировки
        hook_result = self.hook_system.execute_hook(
            'pre_achievement_unlock',
            achievement, player, None
        )
        if hook_result is not None:
            return False, hook_result

        # Выдаем награды (ИСПРАВЛЕННАЯ ЧАСТЬ)
        rewards = []

        if achievement.reward_coins > 0:
            reward_coins = int(achievement.reward_coins) if isinstance(achievement.reward_coins, (int, float, str)) else 0
            player.coin += reward_coins
            rewards.append(f"{reward_coins} монет")

        if achievement.reward_xp > 0:
            reward_xp = int(achievement.reward_xp) if isinstance(achievement.reward_xp, (int, float, str)) else 0
            player.experience += reward_xp
            rewards.append(f"{reward_xp} опыта")

        # Проверяем уровень после добавления опыта
        self.check_level_up(player)

        # Добавляем в разблокированные достижения игрока
        if hasattr(player, 'unlocked_achievements'):
            if achievement_id not in player.unlocked_achievements:
                player.unlocked_achievements.append(achievement_id)

        # Хук после разблокировки
        self.hook_system.execute_hook(
            'post_achievement_unlock',
            achievement, player, True
        )

        reward_text = f" ({', '.join(rewards)})" if rewards else ""
        return True, f"🎉 Достижение разблокировано: {achievement.name}{reward_text}"

    def check_level_up(self, player):
        """Проверяет повышение уровня игрока"""
        exp_needed = self.calculate_exp_for_level(player.level + 1)
        if player.experience >= exp_needed:
            player.level += 1
            print(f"🎉 Уровень повышен! Теперь у вас {player.level} уровень!")

            # Хук повышения уровня
            self.hook_system.execute_hook('player_level_up', player)

    @staticmethod
    def calculate_exp_for_level(level: int) -> int:
        """Рассчитывает необходимое количество опыта для уровня"""
        return level * 100  # Базовая формула: 100 опыта за уровень

    def get_total_achievements_count(self) -> int:
        """Возвращает общее количество достижений"""
        return len(self.achievements)

    def get_achievements_by_tier(self) -> Dict[str, List[Achievement]]:
        """Группирует достижения по уровням"""
        by_tier = {}
        for achievement in self.achievements.values():
            tier = achievement.tier.value
            if tier not in by_tier:
                by_tier[tier] = []
            by_tier[tier].append(achievement)
        return by_tier
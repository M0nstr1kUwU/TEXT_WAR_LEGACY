# [file name]: src/actions/actions_battle.py
from random import random
from utils.helpers_def import clear_console_def, timeout_def
from modding.support_mods import hook_system


class ActionBattle:
    """Система боя с поддержкой хуков"""

    def __init__(self):
        self.current_round = 0

    def battle_loop(self, player, enemy):
        """Основной цикл битвы"""
        # Хук начала битвы
        hook_system.execute_hook('battle_start', player, enemy, "normal")

        print("\n⚔️ НАЧАЛО БИТВЫ!")
        print(f"{player.name}: {player.name} (❤️ {player.health}) vs {enemy.name} (❤️ {enemy.health})")

        # Информация об элементах
        player_element = getattr(player, 'element_data', None)
        enemy_element = getattr(enemy, 'element_data', None)

        if player_element and enemy_element:
            print(f"🎯 Элементы: {player_element.icon} {player.name} vs {enemy_element.icon} {enemy.name}")
            effectiveness = self.calculate_elemental_effectiveness(player_element, enemy_element)
            print(f"📊 Эффективность: {effectiveness}")

        timeout_def(3, 0)

        # Основной цикл битвы
        while player.is_alive() and enemy.is_alive():
            self.current_round += 1
            clear_console_def(1, 0)

            print(f"\n🎯 РАУНД {self.current_round}")
            print("=" * 40)
            print(f"{player.name}: ❤️ {player.health}/{player.health_max} | ⚔️ {player.damage} | 🛡️ {player.shield_hp}")
            print(f"{enemy.name}: ❤️ {enemy.health}/{enemy.health_max} | ⚔️ {enemy.damage} | 🛡️ {getattr(enemy, 'shield_hp', 0)}")
            print("=" * 40)

            # Ход игрока
            player_action = self.player_turn(player, enemy)
            if not player.is_alive() or not enemy.is_alive():
                break

            # Ход врага
            if enemy.is_alive():
                self.enemy_turn(player, enemy)

            timeout_def(3, 0)

        # Определение результата битвы
        if player.is_alive():
            result = self.battle_victory(player, enemy)
        else:
            result = self.battle_defeat(player, enemy)

        # Хук конца битвы
        hook_system.execute_hook('battle_end', player, enemy, result)

        return result

    def player_turn(self, player, enemy):
        """Ход игрока"""
        print(f"\nХОД {player.name}:")

        # Хук начала хода игрока
        hook_system.execute_hook('player_turn_start', player, enemy)

        # Показываем доступные действия
        actions = self.get_player_actions(player)

        for i, action in enumerate(actions, 1):
            print(f"{i}. {action['name']} - {action['description']}")

        # Выбор действия
        while True:
            try:
                choice = input("\nВыберите действие: ").strip()
                if choice.isdigit():
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(actions):
                        selected_action = actions[choice_idx]
                        break
                    else:
                        print("❌ Неверный выбор!")
                else:
                    print("❌ Введите число!")
            except ValueError:
                print("❌ Введите число!")

        # Хук выбора действия
        hook_system.execute_hook('player_action_selected', player, enemy, selected_action['type'])

        # Выполнение действия
        if selected_action['type'] == 'attack':
            self.player_attack(player, enemy)
        elif selected_action['type'] == 'defend':
            self.player_defend(player)
        elif selected_action['type'] == 'heal':
            self.player_heal(player)
        elif selected_action['type'] == 'ability':
            self.player_use_ability(player, enemy, selected_action.get('ability_index', 0))
        elif selected_action['type'] == 'potion':
            self.player_use_potion(player)

        # Хук конца хода игрока
        hook_system.execute_hook('player_turn_end', player, enemy, selected_action['type'])

        return selected_action['type']

    @staticmethod
    def get_player_actions(player):
        """Получает доступные действия игрока"""
        actions = [
            {'type': 'attack', 'name': '⚔️ Атака', 'description': 'Нанести урон врагу'},
            {'type': 'defend', 'name': '🛡️ Защита', 'description': 'Увеличить защиту'},
            {'type': 'heal', 'name': '❤️ Лечение', 'description': 'Восстановить здоровье'},
        ]

        # Добавляем способности если есть
        if hasattr(player, 'abilities') and player.abilities:
            for i, ability in enumerate(player.abilities):
                actions.append({
                    'type': 'ability',
                    'name': f"{ability.icon} {ability.name}",
                    'description': f"{ability.description} (🔮 {ability.mana_cost} маны)",
                    'ability_index': i
                })

        # Добавляем использование зелий если есть
        if player.potions:
            actions.append({
                'type': 'potion',
                'name': '🧪 Зелье',
                'description': 'Использовать зелье здоровья'
            })

        # Хук модификации действий
        actions = hook_system.execute_hook('player_actions_available', actions, player) or actions

        return actions

    @staticmethod
    def player_attack(player, enemy):
        """Атака игрока"""
        print(f"\n⚔️ {player.name} атакует {enemy.name}!")

        # Базовый урон
        base_damage = player.damage

        # Хук расчета урона
        element = getattr(player, 'element', 'none')
        is_critical = random() < 0.1  # 10% шанс крита

        final_damage = hook_system.execute_hook(
            'damage_calculation',
            player, enemy, base_damage, element, is_critical
        ) or base_damage

        # Применяем урон
        damage_result = enemy.take_damage(final_damage)

        print(f"💥 Нанесено урона: {damage_result['total_damage']}")

        if is_critical:
            print("🎯 Критический удар!")

        # Обновляем статистику
        player.player_stats['total_damage_dealt'] += damage_result['total_damage']
        if damage_result['total_damage'] > player.player_stats['max_damage_single_battle']:
            player.player_stats['max_damage_single_battle'] = damage_result['total_damage']

    @staticmethod
    def player_defend(player):
        """Защита игрока"""
        print(f"\n🛡️ {player.name} защищается!")
        player.defend()

    @staticmethod
    def player_heal(player):
        """Лечение игрока"""
        print(f"\n❤️ {player.name} лечится!")
        heal_amount = player.heal()
        print(f"💚 Восстановлено {heal_amount} здоровья!")

    @staticmethod
    def player_use_ability(player, enemy, ability_index):
        """Использование способности игроком"""
        if ability_index < len(player.abilities):
            ability = player.abilities[ability_index]
            result = player.use_ability(ability_index, enemy)
            print(f"\n{result['message']}")

    @staticmethod
    def player_use_potion(player):
        """Использование зелья игроком"""
        if player.potions:
            success = player.use_potion()
            if success:
                print(f"\n🧪 {player.name} использовал зелье здоровья!")
            else:
                print(f"\n❌ У {player.name} нет зелий!")
        else:
            print(f"\n❌ У {player.name} нет зелий!")

    def enemy_turn(self, player, enemy):
        """Ход врага"""
        print(f"\nХОД {enemy.name}:")

        # Хук начала хода врага
        hook_system.execute_hook('enemy_turn_start', enemy, player)

        # ИИ врага выбирает действие
        action = enemy.choose_action(player)

        # Хук выбора действия врага
        hook_system.execute_hook('enemy_action_selected', enemy, player, action)

        # Выполнение действия
        if action == 'attack':
            self.enemy_attack(player, enemy)
        elif action == 'defend':
            self.enemy_defend(enemy)
        elif action == 'heal':
            self.enemy_heal(enemy)
        elif action == 'special':
            self.enemy_special_ability(player, enemy)

        # Хук конца хода врага
        hook_system.execute_hook('enemy_turn_end', enemy, player, action)

    @staticmethod
    def enemy_attack(player, enemy):
        """Атака врага"""
        print(f"\n⚔️ {enemy.name} атакует {player.name}!")

        # Базовый урон
        base_damage = enemy.damage

        # Хук расчета урона
        element = getattr(enemy, 'element', 'none')
        is_critical = random() < 0.1  # 10% шанс крита для врага

        final_damage = hook_system.execute_hook(
            'damage_calculation',
            enemy, player, base_damage, element, is_critical
        ) or base_damage

        # Применяем урон
        damage_result = player.take_damage(final_damage)

        print(f"\n💥 Получено урона: {damage_result['total_damage']}")
        print(f"   🛡️ Поглощено щитом: {damage_result['shield_damage']}")
        print(f"   ❤️ Урон здоровью: {damage_result['health_damage']}")

        if is_critical:
            print("🎯 Критический удар врага!")

    @staticmethod
    def enemy_defend(enemy):
        """Защита врага"""
        print(f"\n🛡️ {enemy.name} защищается!")
        enemy.defend()

    @staticmethod
    def enemy_heal(enemy):
        """Лечение врага"""
        print(f"\n❤️ {enemy.name} лечится!")
        heal_amount = enemy.heal()
        print(f"💚 Восстановлено {heal_amount} здоровья!")

    @staticmethod
    def enemy_special_ability(player, enemy):
        """Особая способность врага"""
        if hasattr(enemy, 'special_ability') and enemy.special_ability:
            print(f"\n💫 {enemy.name} использует {enemy.special_ability}!")
            # Здесь будет добавлена логика особых способностей врага! v1.1+

    def battle_victory(self, player, enemy):
        """Обработка победы"""
        print(f"\n🎉 ПОБЕДА! {player.name} победил {enemy.name}!")

        # Награды
        coins_earned = self.calculate_reward(enemy)
        exp_earned = self.calculate_experience(enemy)

        player.add_coins(coins_earned)
        player.add_experience(exp_earned)
        player.player_stats['battles_won'] += 1

        print(f"💰 Получено монет: {coins_earned}")
        print(f"⭐ Получено опыта: {exp_earned}")

        # Хук победы в битве
        hook_system.execute_hook('battle_victory', player, enemy, coins_earned, exp_earned)

        return "win"

    @staticmethod
    def battle_defeat(player, enemy):
        """Обработка поражения"""
        print(f"\n💀 ПОРАЖЕНИЕ! {player.name} был побежден {enemy.name}!")

        player.player_stats['battles_lost'] += 1

        # Частичная потеря монет при поражении
        coins_lost = min(player.coin // 10, 50)  # Максимум 10% или 50 монет
        player.coin -= coins_lost

        if coins_lost > 0:
            print(f"💰 Потеряно монет: {coins_lost}")

        # Хук поражения в битве
        hook_system.execute_hook('battle_defeat', player, enemy, coins_lost)

        return "lose"

    @staticmethod
    def calculate_reward(enemy):
        """Рассчитывает награду за победу"""
        base_reward = {
            'common': 10,
            'elite': 25,
            'boss': 50,
            'champion': 75,
            'legendary': 100
        }

        reward = base_reward.get(enemy.enemy_type, 10)

        # Модификатор за сложность
        difficulty_multiplier = {
            'easy': 0.8,
            'medium': 1.0,
            'hard': 1.2,
            'extreme': 1.5,
            'demon': 2
        }

        if hasattr(enemy, 'difficulty'):
            multiplier = difficulty_multiplier.get(enemy.difficulty, 1.0)
            reward = int(reward * multiplier)

        return reward

    @staticmethod
    def calculate_experience(enemy):
        """Рассчитывает опыт за победу"""
        base_exp = {
            'common': 15,
            'elite': 30,
            'boss': 60,
            'champion': 90,
            'legendary': 120
        }

        exp = base_exp.get(enemy.enemy_type, 15)

        # Модификатор за сложность
        difficulty_multiplier = {
            'easy': 0.8,
            'medium': 1.0,
            'hard': 1.2,
            'extreme': 1.5,
            'demon': 2
        }

        if hasattr(enemy, 'difficulty'):
            multiplier = difficulty_multiplier.get(enemy.difficulty, 1.0)
            exp = int(exp * multiplier)

        return exp

    @staticmethod
    def calculate_elemental_effectiveness(player_element, enemy_element):
        """Рассчитывает эффективность элементов"""
        # Простая система эффективности
        effectiveness_map = {
            ('fire', 'nature'): '🔥 ЭФФЕКТИВНО',
            ('nature', 'water'): '💧 ЭФФЕКТИВНО',
            ('water', 'fire'): '⚡ ЭФФЕКТИВНО',
            ('fire', 'water'): '❌ НЕЭФФЕКТИВНО',
            ('nature', 'fire'): '⚠️ СЛАБО',
            ('water', 'nature'): '🌱 СЛАБО'
        }

        result = effectiveness_map.get(
            (player_element.element_type.value, enemy_element.element_type.value),
            '⚖️ НОРМАЛЬНО'
        )

        return result
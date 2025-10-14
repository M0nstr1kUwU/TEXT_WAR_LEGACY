# [file name]: src/classes_entities/skill_tree.py
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum
from modding.support_mods import hook_system


class SkillNodeType(Enum):
    """Типы узлов навыков"""
    STAT_BOOST = "stat_boost"
    ABILITY = "ability"
    PASSIVE = "passive"
    ELEMENTAL = "elemental"


@dataclass
class SkillNode:
    """Узел дерева навыков"""
    node_id: str
    name: str
    description: str
    icon: str
    node_type: SkillNodeType
    cost: int
    requirements: List[str]
    effect: Dict[str, Any]
    max_level: int = 1
    current_level: int = 0


class SkillTree:
    """Дерево навыков класса"""

    def __init__(self, class_type):
        self.class_type = class_type
        self.nodes: Dict[str, SkillNode] = {}
        self.unlocked_nodes: List[str] = []
        self.skill_points: int = 0
        self.load_default_tree()

    def load_default_tree(self):
        """Загружает стандартное дерево навыков для класса"""
        base_nodes = {
            "health_boost": SkillNode(
                node_id="health_boost",
                name="💪 Усиленное здоровье",
                description="Увеличивает максимальное здоровье на 5",
                icon="💪",
                node_type=SkillNodeType.STAT_BOOST,
                cost=1,
                requirements=[],
                effect={"health_bonus": 5},
                max_level=5
            ),
            "damage_boost": SkillNode(
                node_id="damage_boost",
                name="⚔️ Сила атаки",
                description="Увеличивает базовый урон на 1",
                icon="⚔️",
                node_type=SkillNodeType.STAT_BOOST,
                cost=1,
                requirements=[],
                effect={"damage_bonus": 1},
                max_level=5
            ),
            "elemental_mastery": SkillNode(
                node_id="elemental_mastery",
                name="🔮 Мастер стихий",
                description="Увеличивает элементный урон на 10%",
                icon="🔮",
                node_type=SkillNodeType.ELEMENTAL,
                cost=2,
                requirements=["health_boost", "damage_boost"],
                effect={"elemental_damage_bonus": 0.1}
            )
        }

        # Добавляем специализированные узлы в зависимости от класса
        if self.class_type.value == "warrior":
            base_nodes.update({
                "berserker_rage": SkillNode(
                    node_id="berserker_rage",
                    name="😠 Ярость берсерка",
                    description="Увеличивает урон на 25% при здоровье ниже 30%",
                    icon="😠",
                    node_type=SkillNodeType.PASSIVE,
                    cost=3,
                    requirements=["damage_boost"],
                    effect={"berserker_bonus": 0.25}
                )
            })
        elif self.class_type.value == "mage":
            base_nodes.update({
                "spell_power": SkillNode(
                    node_id="spell_power",
                    name="✨ Сила заклинаний",
                    description="Увеличивает урон от способностей на 20%",
                    icon="✨",
                    node_type=SkillNodeType.PASSIVE,
                    cost=3,
                    requirements=["elemental_mastery"],
                    effect={"spell_power_bonus": 0.2}
                )
            })

        self.nodes = base_nodes

    def can_unlock_node(self, node_id: str) -> bool:
        """Проверяет, можно ли разблокировать узел"""
        if node_id not in self.nodes:
            return False

        node = self.nodes[node_id]

        # Проверяем требования
        for req in node.requirements:
            if req not in self.unlocked_nodes:
                return False

        # Проверяем стоимость
        if self.skill_points < node.cost:
            return False

        # Проверяем максимальный уровень
        if node.current_level >= node.max_level:
            return False

        return True

    def unlock_node(self, node_id: str) -> bool:
        """Разблокирует узел дерева навыков"""
        if not self.can_unlock_node(node_id):
            return False

        node = self.nodes[node_id]
        self.skill_points -= node.cost
        node.current_level += 1
        self.unlocked_nodes.append(node_id)

        # Хук разблокировки навыка
        hook_system.execute_hook('skill_unlocked', self.class_type, node_id, node)

        return True

    def get_available_nodes(self) -> List[SkillNode]:
        """Получает доступные для разблокировки узлы"""
        return [node for node_id, node in self.nodes.items()
                if self.can_unlock_node(node_id)]

    def get_node_effects(self) -> Dict[str, Any]:
        """Получает суммарные эффекты всех разблокированных узлов"""
        effects = {}

        for node_id in self.unlocked_nodes:
            node = self.nodes[node_id]
            for effect_key, effect_value in node.effect.items():
                if effect_key in effects:
                    if isinstance(effect_value, (int, float)):
                        effects[effect_key] += effect_value * node.current_level
                    else:
                        effects[effect_key] = effect_value
                else:
                    effects[effect_key] = effect_value * node.current_level

        return effects

    def add_skill_points(self, points: int):
        """Добавляет очки навыков"""
        self.skill_points += points

        # Хук добавления очков навыков
        hook_system.execute_hook('skill_points_added', self.class_type, points)


class SkillTreeManager:
    """Менеджер деревьев навыков"""

    def __init__(self):
        self.trees: Dict[str, SkillTree] = {}

    def get_tree(self, class_type) -> SkillTree:
        """Получает дерево навыков для класса"""
        tree_key = class_type.value

        if tree_key not in self.trees:
            self.trees[tree_key] = SkillTree(class_type)

        return self.trees[tree_key]

    def reset_tree(self, class_type):
        """Сбрасывает дерево навыков класса"""
        tree_key = class_type.value
        if tree_key in self.trees:
            del self.trees[tree_key]

skill_tree_manager = SkillTreeManager()
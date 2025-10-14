# [file name]: src/elemental_source/elemental_integration.py
from elemental_source.elemental_core import ElementType, elemental_system
from modding.support_mods import hook_system
from settings.settings_manager import settings


class ElementalIntegration:
    """Интеграция системы элементов с другими системами"""
    def __init__(self):
        self.hook_system = hook_system

    @staticmethod
    def apply_to_entity(entity, element_type: ElementType):
        """Применяет элемент к сущности"""
        try:
            entity.element = element_type
            entity.element_data = elemental_system.elements.get(element_type)

            if entity.element_data:
                print(f"🎯 Применен элемент: {entity.element_data.icon} {entity.element_data.name}")
            else:
                settings.log_warning(f"⚠️ Элемент {element_type} не найден, установлен по умолчанию")
                entity.element_data = elemental_system.elements[ElementType.NONE]

        except Exception as e:
            settings.log_error(f"❌ Ошибка применения элемента: {e}")
            entity.element = ElementType.NONE
            entity.element_data = elemental_system.elements[ElementType.NONE]

    def calculate_elemental_damage(self, attacker, defender, base_damage: int) -> int:
        """Рассчитывает урон с учетом элементов"""
        if not hasattr(attacker, 'element'):
            attacker.element = ElementType.NONE
        if not hasattr(defender, 'element'):
            defender.element = ElementType.NONE

        attacker_element = elemental_system.get_element(attacker.element)
        defender_element = elemental_system.get_element(defender.element)

        # Базовый множитель
        multiplier = attacker_element.calculate_damage_multiplier(defender_element)

        # Хук модификации множителя
        multiplier = self.hook_system.execute_hook(
            'elemental_damage_calculation',
            attacker, defender, base_damage, multiplier
        ) or multiplier

        elemental_damage = int(base_damage * multiplier)

        # Записываем статистику элементального урона
        if hasattr(attacker, 'player_stats'):
            element_key = f"{attacker.element.value}_damage"
            attacker.player_stats['elemental_damage'][element_key] = \
                attacker.player_stats['elemental_damage'].get(element_key, 0) + elemental_damage

        return elemental_damage

    @staticmethod
    def get_entity_element_info(entity):
        """Получает информацию об элементе сущности"""
        return {
            'element_type': getattr(entity, 'element', ElementType.NONE),
            'element_data': getattr(entity, 'element_data', None),
            'elemental_resistance': getattr(entity, 'elemental_resistance', 1.0)
        }

    # Создаем экземпляр для импорта
    elemental_integration = type('ElementalIntegration', (), {
        'apply_to_entity': apply_to_entity,
        'get_entity_element_info': get_entity_element_info
    })()


elemental_integration = ElementalIntegration()

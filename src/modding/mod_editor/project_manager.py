from datetime import datetime
from json import dumps, load
from pathlib import Path
from traceback import print_exc
from typing import Dict, Any, List, Optional
from settings.settings_manager import settings


class ProjectManager:
    """Менеджер проектов модов"""

    def __init__(self):
        self.current_project: Optional[str] = None
        self.project_data: Dict[str, Any] = {}

    def create_project(self, project_name: str, project_path: str, template: str = "basic") -> bool:
        """Создание нового проекта мода"""
        try:
            project_dir = Path(project_path) / project_name
            project_dir.mkdir(parents=True, exist_ok=True)

            settings.log_info(f"📁 Создаю проект в: {project_dir}")

            # Создание структуры проекта
            self.project_data = {
                "name": project_name,
                "path": str(project_dir),
                "type": "mod",
                "version": "1.0.0",
                "author": "",
                "description": "",
                "created_date": "",
                "files": [],
                "dependencies": []
            }

            # Создание основного файла мода
            mod_file = project_dir / f"{project_name}.py"
            template_content = self._get_template(template, project_name)
            mod_file.write_text(template_content, encoding='utf-8')
            settings.log_info(f"📄 Создан файл: {mod_file}")

            # Создание конфигурационного файла проекта
            config_file = project_dir / "mod_project.json"
            self.project_data["files"].append(str(mod_file.name))
            self.project_data["created_date"] = self._get_current_date()

            config_file.write_text(dumps(self.project_data, indent=2, ensure_ascii=False), encoding='utf-8')
            settings.log_info(f"⚙️ Создан конфиг: {config_file}")

            self.current_project = str(project_dir)
            return True

        except Exception as e:
            settings.log_error(f"❌ Ошибка создания проекта: {e}")
            print_exc()
            return False

    @staticmethod
    def _get_current_date():
        """Получение текущей даты"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def open_project(self, project_path: str) -> bool:
        """Открытие существующего проекта"""
        try:
            project_path = Path(project_path)
            config_file = project_path / "mod_project.json"

            settings.log_info(f"📁 Открываю проект: {project_path}")

            if not config_file.exists():
                settings.log_warning("⚠️ Файл конфигурации не найден, пробую создать проект из папки...")
                # Если это папка с Python файлами, создаем проект автоматически
                return self._create_project_from_folder(project_path)

            with open(config_file, 'r', encoding='utf-8') as f:
                self.project_data = load(f)

            self.current_project = str(project_path)
            settings.log_info(f"✅ Проект загружен: {self.project_data['name']}")
            return True

        except Exception as e:
            settings.log_error(f"❌ Ошибка открытия проекта: {e}")
            print_exc()
            return False

    def _create_project_from_folder(self, folder_path: Path) -> bool:
        """Создание проекта из существующей папки"""
        try:
            project_name = folder_path.name
            python_files = list(folder_path.glob("*.py"))

            if not python_files:
                return False

            self.project_data = {
                "name": project_name,
                "path": str(folder_path),
                "type": "mod",
                "version": "1.0.0",
                "author": "",
                "description": "Автоматически созданный проект",
                "created_date": "",
                "files": [f.name for f in python_files],
                "dependencies": []
            }

            # Создание конфигурационного файла
            config_file = folder_path / "mod_project.json"
            config_file.write_text(dumps(self.project_data, indent=2, ensure_ascii=False), encoding='utf-8')

            self.current_project = str(folder_path)
            return True

        except Exception as e:
            settings.log_error(f"❌ Ошибка создания проекта из папки: {e}")
            return False

    def get_project_files(self) -> List[str]:
        """Получение списка файлов проекта"""
        if not self.current_project:
            return []

        project_path = Path(self.current_project)
        python_files = list(project_path.glob("*.py"))
        return [str(f) for f in python_files]

    def save_project_data(self):
        """Сохранение данных проекта"""
        if not self.current_project:
            return False

        try:
            config_file = Path(self.current_project) / "mod_project.json"
            config_file.write_text(dumps(self.project_data, indent=2, ensure_ascii=False), encoding='utf-8')
            return True
        except Exception as e:
            settings.log_error(f"❌ Ошибка сохранения проекта: {e}")
            return False

    def _get_template(self, template_name: str, project_name: str) -> str:
        """Получение шаблона мода"""
        templates = {
            "basic": f'''"""
МОД: {project_name}
Автор: Ваше имя
Версия: 1.0.0
Описание: Краткое описание мода
"""

def mod_initialize(hook_system):
    """Инициализация мода"""
    print(f"✅ Мод '{{project_name}}' загружен!")
    return True

# РЕГИСТРАЦИЯ ХУКОВ
HOOK_REGISTRY = {{
    # Пример регистрации хуков:
    # 'player_created': on_player_created,
    # 'battle_start': on_battle_start,
}}

# ПРИМЕРЫ ФУНКЦИЙ ХУКОВ (раскомментируйте для использования)

# def on_player_created(player, hook_system):
#     """Усиливает игрока при создании"""
#     if player and hasattr(player, 'damage'):
#         player.damage += 2
#         player.health_max += 10
#         print(f"💪 Мод {{project_name}}: Игрок усилен!")
#
# def on_battle_start(player, enemy, mode, hook_system):
#     """Добавляет эффекты в начале битвы"""
#     if player and enemy:
#         print(f"🔥 Мод {{project_name}}: Битва начинается!")
''',
            "ai_mod": f'''"""
МОД AI: {project_name}
Автор: Ваше имя  
Версия: 1.0.0
Описание: Мод для кастомного AI поведения
"""

from src.ai_resources.ai_enemy.base_ai import BaseAI
import random

class CustomAI(BaseAI):
    """Кастомный AI для врагов"""

    def __init__(self, difficulty="medium"):
        super().__init__("Кастомный AI", difficulty)

    def choose_action(self, enemy, player, battle_context):
        """Кастомная логика выбора действий"""
        situation = self.analyze_situation(enemy, player)

        # Ваша кастомная логика здесь
        if situation["player_health_low"]:
            return "attack"  # Добить игрока

        return random.choice(["attack", "defend", "heal"])

def mod_initialize(hook_system):
    """Инициализация AI мода"""
    print(f"✅ AI Мод '{{project_name}}' загружен!")
    return True

def on_ai_creation(enemy, difficulty, hook_system):
    """Заменяет стандартный AI на кастомный"""
    return CustomAI(difficulty)

# РЕГИСТРАЦИЯ ХУКОВ
HOOK_REGISTRY = {{
    'ai_creation': on_ai_creation,
}}
'''
        }

        return templates.get(template_name, templates["basic"])

    def is_project_loaded(self) -> bool:
        """Проверка загружен ли проект"""
        return self.current_project is not None

    def get_project_info(self) -> Dict[str, Any]:
        """Получение информации о текущем проекте"""
        return self.project_data.copy()
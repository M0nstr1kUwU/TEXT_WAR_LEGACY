from json import load, dump
from os import makedirs, path
from typing import Dict, Any
from settings.settings_manager import settings


class EditorSettings:
    """Менеджер настроек Mod-Editor"""

    def __init__(self):
        self.settings_file = "src/saves/configs/editor_settings.json"
        self.default_settings = {
            "editor": {
                "font_family": "Consolas",
                "font_size": 12,
                "theme": "dark",
                "line_numbers": True,
                "word_wrap": False,
                "auto_indent": True,
                "tab_width": 4,
                "use_spaces": True
            },
            "window": {
                "width": 1200,
                "height": 800,
                "maximized": False,
                "window_state": None
            },
            "projects": {
                "recent_projects": [],
                "last_project": None,
                "auto_load_last": True
            },
            "code_completion": {
                "enabled": True,
                "auto_trigger": True,
                "case_sensitive": False
            },
            "syntax_highlighting": {
                "enabled": True,
                "highlight_current_line": True,
                "highlight_matching_braces": True
            },
            "mod_development": {
                "auto_validate": True,
                "show_hook_documentation": True,
                "template_language": "russian"
            }
        }
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Загрузка настроек из файла"""
        makedirs(path.dirname(self.settings_file), exist_ok=True)

        if path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = load(f)
                    return self.merge_settings(loaded_settings)
            except Exception as e:
                settings.log_error(f"⚠️ Ошибка загрузки настроек: {e}")

        return self.default_settings.copy()

    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                dump(self.settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            settings.log_error(f"❌ Ошибка сохранения настроек: {e}")
            return False

    def merge_settings(self, loaded_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Объединение загруженных настроек с настройками по умолчанию"""
        result = self.default_settings.copy()

        def recursive_merge(default, loaded):
            for key, value in loaded.items():
                if key in default:
                    if isinstance(value, dict) and isinstance(default[key], dict):
                        recursive_merge(default[key], value)
                    else:
                        default[key] = value

        recursive_merge(result, loaded_settings)
        return result

    def get(self, key: str, default=None):
        """Получение значения настройки"""
        keys = key.split('.')
        value = self.settings

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value):
        """Установка значения настройки"""
        keys = key.split('.')
        settings_dict = self.settings

        for k in keys[:-1]:
            if k not in settings_dict:
                settings_dict[k] = {}
            settings_dict = settings_dict[k]

        settings_dict[keys[-1]] = value
        self.save_settings()

    def add_recent_project(self, project_path: str):
        """Добавление проекта в список недавних"""
        recent = self.get('projects.recent_projects', [])

        if project_path in recent:
            recent.remove(project_path)

        recent.insert(0, project_path)
        recent = recent[:10]  # Ограничение до 10 проектов

        self.set('projects.recent_projects', recent)
        self.set('projects.last_project', project_path)

    def get_recent_projects(self) -> list:
        """Получение списка недавних проектов"""
        return self.get('projects.recent_projects', [])
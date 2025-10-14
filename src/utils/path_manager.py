# src/utils/path_manager.py
from pathlib import Path


class PathManager:
    """Менеджер путей для всего проекта"""

    def __init__(self):
        # Базовые пути
        self.project_root = Path(__file__).parent.parent.parent
        self.src_root = self.project_root / "src"

        # Основные директории
        self.entities_dir = self.src_root / "entities"
        self.actions_dir = self.src_root / "actions"
        self.settings_dir = self.src_root / "settings"
        self.hooks_dir = self.src_root / "hooks"
        self.ai_dir = self.src_root / "ai_resources" / "ai_enemy"
        self.modding_dir = self.src_root / "modding"
        self.utils_dir = self.src_root / "utils"

        # Директории для сохранения
        self.saves_dir = self.src_root / "saves"
        self.configs_dir = self.saves_dir / "configs"
        self.logs_dir = self.saves_dir / "logs"
        self.mods_dir = self.saves_dir / "mods"

        # Файлы конфигурации
        self.settings_file = self.configs_dir / "settings.json"
        self.hooks_config_file = self.configs_dir / "hooks.json"
        self.player_data_file = self.configs_dir / "player_data.json"
        self.editor_settings_file = self.configs_dir / "editor_settings.json"

        # Создаем необходимые директории
        self._create_directories()

    def _create_directories(self):
        """Создает все необходимые директории"""
        directories = [
            self.entities_dir,
            self.actions_dir,
            self.settings_dir,
            self.hooks_dir,
            self.ai_dir,
            self.modding_dir,
            self.utils_dir,
            self.saves_dir,
            self.configs_dir,
            self.logs_dir,
            self.mods_dir
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get_absolute_path(self, relative_path):
        """Возвращает абсолютный путь относительно корня проекта"""
        return self.project_root / relative_path

    def get_relative_path(self, absolute_path):
        """Возвращает относительный путь от корня проекта"""
        return Path(absolute_path).relative_to(self.project_root)

    @staticmethod
    def ensure_dir_exists(path):
        """Убеждается, что директория существует"""
        path = Path(path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return path


# Экспорт часто используемых путей для удобства
path_manager = PathManager()
PROJECT_ROOT = path_manager.project_root
SRC_ROOT = path_manager.src_root
SAVES_DIR = path_manager.saves_dir
CONFIGS_DIR = path_manager.configs_dir
LOGS_DIR = path_manager.logs_dir
MODS_DIR = path_manager.mods_dir
SETTINGS_FILE = path_manager.settings_file
PLAYER_DATA_FILE = path_manager.player_data_file



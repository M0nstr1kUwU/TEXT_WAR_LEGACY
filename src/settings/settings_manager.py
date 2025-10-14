# src/settings/settings_manager.py
import json
import os
import platform
from datetime import datetime


class SettingsManager:
    def __init__(self):
        self.settings_file = "src/saves/configs/settings.json"
        self.logs_dir = "src/saves/logs"
        self.configs_dir = "src/saves/configs"

        # Создаем необходимые директории
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.configs_dir, exist_ok=True)

        # Загружаем настройки
        self.settings = self.load_settings()

    def load_settings(self):
        """Загрузка настроек из файла"""
        default_settings = {
            "logging": {
                "warning": False,
                "error": False,
                "info": False,
                "debug": False,
                "tips": True
            },
            "game": {
                "difficulty": "medium",
                "auto_save": True,
                "language": "ru"
            },
            "ai": {
                "enemy_ai_difficulty": "medium",
                "ai_learning": True,
                "adaptive_behavior": True,
                "ai_aggression_level": 0.5,
                "ai_prediction_accuracy": 0.7,
                "ai_memory_size": 20,
                "enhanced_ai_enabled": True,
                "special_abilities_enabled": True
            }
        }

        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Объединяем с настройками по умолчанию
                    return self.merge_settings(default_settings, loaded_settings)
        except Exception as e:
            self.log_error(f"Ошибка загрузки настроек: {e}")

        return default_settings

    def merge_settings(self, default, loaded):
        """Рекурсивное объединение настроек"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_settings(result[key], value)
            else:
                result[key] = value
        return result

    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.log_error(f"Ошибка сохранения настроек: {e}")
            return False

    def reset_to_defaults(self):
        """Сброс настроек к значениям по умолчанию"""
        try:
            if os.path.exists(self.settings_file):
                os.remove(self.settings_file)
            self.settings = self.load_settings()
            return True
        except Exception as e:
            self.log_error(f"Ошибка сброса настроек: {e}")
            return False

    def export_settings(self, file_path=None):
        """Экспорт настроек в файл"""
        if file_path is None:
            file_path = f"settings_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.log_error(f"Ошибка экспорта настроек: {e}")
            return False

    def import_settings(self, file_path):
        """Импорт настроек из файла"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_settings = json.load(f)
                self.settings = self.merge_settings(self.settings, imported_settings)
                self.save_settings()
                return True
        except Exception as e:
            self.log_error(f"Ошибка импорта настроек: {e}")
        return False

    def clear_logs(self):
        """Очистка логов"""
        try:
            for filename in os.listdir(self.logs_dir):
                file_path = os.path.join(self.logs_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            return True
        except Exception as e:
            self.log_error(f"Ошибка очистки логов: {e}")
            return False

    def get_system_info(self):
        """Получение системной информации"""
        return {
            "Операционная система": platform.system(),
            "Версия ОС": platform.release(),
            "Архитектура": platform.architecture()[0],
            "Процессор": platform.processor(),
            "Python версия": platform.python_version(),
            "Путь к настройкам": os.path.abspath(self.settings_file),
            "Путь к логам": os.path.abspath(self.logs_dir)
        }

    def get_settings_path(self):
        """Получение пути к файлу настроек"""
        return os.path.abspath(self.settings_file)

    def get_logs_path(self):
        """Получение пути к логам"""
        return os.path.abspath(self.logs_dir)

    def get_configs_path(self):
        """Получение пути к конфигам"""
        return os.path.abspath(self.configs_dir)

    def log_info(self, message):
        """Логирование информации"""
        if self.settings["logging"]["info"]:
            self._log_message("INFO", message)

    def log_warning(self, message):
        """Логирование предупреждения"""
        if self.settings["logging"]["warning"]:
            self._log_message("WARNING", message)

    def log_error(self, message):
        """Логирование ошибки"""
        if self.settings["logging"]["error"]:
            self._log_message("ERROR", message)

    def log_debug(self, message):
        """Логирование отладочной информации"""
        if self.settings["logging"]["debug"]:
            self._log_message("DEBUG", message)

    def log_tips(self, message):
        """Логирование подсказок"""
        if self.settings["logging"]["tips"]:
            self._log_message("TIPS", message)

    def _log_message(self, level, message):
        """Внутренний метод логирования"""
        try:
            log_file = os.path.join(self.logs_dir, f"game_{datetime.now().strftime('%Y%m%d')}.log")
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] [{level}] {message}\n")
        except Exception as e:
            print(f"❌ Ошибка записи в лог: {e}")


settings = SettingsManager()

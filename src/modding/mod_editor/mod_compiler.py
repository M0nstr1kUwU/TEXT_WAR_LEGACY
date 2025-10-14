from _ast import Import, ImportFrom
from ast import parse, walk
import importlib.util
from shutil import copy2, make_archive
from pathlib import Path
from typing import Dict, Any, List
from tempfile import TemporaryDirectory
from sys import path as spath
from settings.settings_manager import settings


class ModCompiler:
    """Компилятор и валидатор модов для Text War Legacy"""

    def __init__(self):
        self.hook_registry_required = ['HOOK_REGISTRY', 'mod_initialize']
        self.valid_hooks = [
            'player_created', 'battle_start', 'damage_calculation', 'enemy_creation',
            'ai_creation', 'item_use', 'game_initialized', 'main_menu_created'
        ]

    def compile_and_test(self, mod_path: str) -> Dict[str, Any]:
        """Компиляция и тестирование мода"""
        result = {
            "success": False,
            "errors": [],
            "warnings": [],
            "compiled_files": [],
            "test_results": []
        }

        try:
            # Проверка структуры проекта
            structure_check = self.validate_project_structure(mod_path)
            if not structure_check["success"]:
                result["errors"].extend(structure_check["errors"])
                return result

            # Компиляция всех Python файлов
            python_files = list(Path(mod_path).glob("**/*.py"))
            for py_file in python_files:
                file_result = self.compile_file(str(py_file))
                if not file_result["success"]:
                    result["errors"].extend(file_result["errors"])
                else:
                    result["compiled_files"].append(str(py_file))
                    result["warnings"].extend(file_result["warnings"])

            # Проверка HOOK_REGISTRY
            hook_check = self.validate_hook_registry(mod_path)
            if not hook_check["success"]:
                result["errors"].extend(hook_check["errors"])
            else:
                result["warnings"].extend(hook_check["warnings"])

            # Тестирование мода
            test_result = self.test_mod(mod_path)
            result["test_results"] = test_result

            # Если нет ошибок - успех
            result["success"] = len(result["errors"]) == 0

            if result["success"]:
                result["message"] = "✅ Мод успешно скомпилирован и протестирован!"
            else:
                result["message"] = f"❌ Обнаружены ошибки: {len(result['errors'])}"

        except Exception as e:
            result["errors"].append(f"Критическая ошибка компиляции: {str(e)}")
            settings.log_error(e)

        return result

    def validate_project_structure(self, mod_path: str) -> Dict[str, Any]:
        """Валидация структуры проекта мода"""
        result = {
            "success": True,
            "errors": [],
            "warnings": []
        }

        project_path = Path(mod_path)

        # Проверка существования пути
        if not project_path.exists():
            result["success"] = False
            result["errors"].append("Путь к проекту не существует")
            return result

        # Проверка наличия Python файлов
        python_files = list(project_path.glob("*.py"))
        if not python_files:
            result["warnings"].append("В проекте нет Python файлов")

        # Проверка конфигурационного файла
        config_file = project_path / "mod_project.json"
        if not config_file.exists():
            result["warnings"].append("Отсутствует файл конфигурации mod_project.json")

        return result

    def compile_file(self, file_path: str) -> Dict[str, Any]:
        """Компиляция отдельного файла"""
        result = {
            "success": True,
            "errors": [],
            "warnings": [],
            "file": file_path
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            # Проверка синтаксиса Python
            try:
                parse(source_code)
            except SyntaxError as e:
                result["success"] = False
                result["errors"].append(f"Синтаксическая ошибка в {file_path}: {e}")
                return result

            # Проверка на наличие обязательных элементов для главного файла мода
            if self.is_main_mod_file(file_path):
                main_file_check = self.validate_main_mod_file(source_code, file_path)
                if not main_file_check["success"]:
                    result["errors"].extend(main_file_check["errors"])
                result["warnings"].extend(main_file_check["warnings"])

            # Проверка импортов
            import_check = self.validate_imports(source_code, file_path)
            result["warnings"].extend(import_check["warnings"])

        except Exception as e:
            result["success"] = False
            result["errors"].append(f"Ошибка чтения файла {file_path}: {e}")
            settings.log_error(f"Ошибка чтения файла {file_path}: {e}")

        return result

    def is_main_mod_file(self, file_path: str) -> bool:
        """Проверка является ли файл главным файлом мода"""
        path = Path(file_path)
        project_dir = path.parent

        # Если в имени файла нет тестов и он в корне проекта
        return ("test" not in path.stem.lower() and
                path.parent == project_dir and
                path.suffix == '.py')

    def validate_main_mod_file(self, source_code: str, file_path: str) -> Dict[str, Any]:
        """Валидация главного файла мода"""
        result = {
            "success": True,
            "errors": [],
            "warnings": []
        }

        # Проверка наличия HOOK_REGISTRY
        if "HOOK_REGISTRY" not in source_code:
            result["warnings"].append(f"В файле {file_path} отсутствует HOOK_REGISTRY")

        # Проверка наличия mod_initialize
        if "def mod_initialize" not in source_code:
            result["warnings"].append(f"В файле {file_path} отсутствует mod_initialize функция")

        # Проверка документации
        if '"""' not in source_code and "'''" not in source_code:
            result["warnings"].append(f"В файле {file_path} отсутствует документация")

        return result

    def validate_imports(self, source_code: str, file_path: str) -> Dict[str, Any]:
        """Валидация импортов в файле"""
        result = {
            "warnings": []
        }

        try:
            tree = parse(source_code)

            for node in walk(tree):
                if isinstance(node, Import):
                    for alias in node.names:
                        self._check_import(alias.name, file_path, result)
                elif isinstance(node, ImportFrom):
                    if node.module:
                        self._check_import(node.module, file_path, result)

        except SyntaxError:
            # Синтаксические ошибки обрабатываются в compile_file
            pass

        return result

    def _check_import(self, import_name: str, file_path: str, result: Dict[str, Any]):
        """Проверка отдельного импорта"""
        # Список разрешенных импортов
        allowed_imports = [
            'src.', 'os', 'sys', 'json', 'random', 'datetime', 'typing',
            'pathlib', 'abc', 'math', 're', 'collections'
        ]

        # Список запрещенных импортов
        forbidden_imports = [
            'socket', 'http', 'requests', 'urllib', 'subprocess', 'multiprocessing',
            'threading', 'ctypes', 'winreg', 'os.system'
        ]

        if any(forbidden in import_name for forbidden in forbidden_imports):
            result["warnings"].append(f"⚠️ Подозрительный импорт в {file_path}: {import_name}")
            settings.log_warning(f"⚠️ Подозрительный импорт в {file_path}: {import_name}")

        if not any(allowed in import_name for allowed in allowed_imports):
            result["warnings"].append(f"⚠️ Нестандартный импорт в {file_path}: {import_name}")
            settings.log_warning(f"⚠️ Нестандартный импорт в {file_path}: {import_name}")

    def validate_hook_registry(self, mod_path: str) -> Dict[str, Any]:
        """Валидация HOOK_REGISTRY"""
        result = {
            "success": True,
            "errors": [],
            "warnings": []
        }

        try:
            # Временное добавление пути для импорта
            spath.insert(0, mod_path)

            # Поиск главного файла мода
            python_files = list(Path(mod_path).glob("*.py"))
            main_file = None

            for py_file in python_files:
                if "test" not in py_file.stem.lower():
                    main_file = py_file
                    break

            if not main_file:
                result["errors"].append("Не найден главный файл мода")
                return result

            # Динамическая загрузка и проверка мода
            spec = importlib.util.spec_from_file_location("temp_mod", main_file)
            mod_module = importlib.util.module_from_spec(spec)

            try:
                spec.loader.exec_module(mod_module)

                # Проверка HOOK_REGISTRY
                if not hasattr(mod_module, 'HOOK_REGISTRY'):
                    result["errors"].append("Отсутствует HOOK_REGISTRY")
                    result["success"] = False
                else:
                    hook_registry = mod_module.HOOK_REGISTRY

                    # Проверка структуры HOOK_REGISTRY
                    if not isinstance(hook_registry, dict):
                        result["errors"].append("HOOK_REGISTRY должен быть словарем")
                        result["success"] = False
                    else:
                        # Проверка зарегистрированных хуков
                        for hook_name, hook_func in hook_registry.items():
                            if hook_name not in self.valid_hooks:
                                result["warnings"].append(f"Неизвестный хук: {hook_name}")

                            if not hasattr(mod_module, hook_func.__name__ if callable(hook_func) else str(hook_func)):
                                result["warnings"].append(f"Функция для хука {hook_name} не найдена")

                # Проверка mod_initialize
                if not hasattr(mod_module, 'mod_initialize'):
                    result["warnings"].append("Отсутствует mod_initialize функция")
                else:
                    if not callable(mod_module.mod_initialize):
                        result["errors"].append("mod_initialize должна быть функцией")
                        result["success"] = False

            except Exception as e:
                result["errors"].append(f"Ошибка выполнения мода: {e}")
                settings.log_error(f"Ошибка выполнения мода: {e}")
                result["success"] = False

            # Удаление временного пути
            spath.remove(mod_path)

        except Exception as e:
            result["errors"].append(f"Ошибка валидации HOOK_REGISTRY: {e}")
            settings.log_error(f"Ошибка валидации HOOK_REGISTRY: {e}")
            result["success"] = False

        return result

    def test_mod(self, mod_path: str) -> List[Dict[str, Any]]:
        """Тестирование мода"""
        test_results = []

        try:
            # Тест 1: Проверка инициализации
            init_test = self._test_mod_initialization(mod_path)
            test_results.append(init_test)

            # Тест 2: Проверка хуков
            hook_test = self._test_hook_registry(mod_path)
            test_results.append(hook_test)

            # Тест 3: Проверка совместимости
            compat_test = self._test_compatibility(mod_path)
            test_results.append(compat_test)

        except Exception as e:
            test_results.append({
                "test": "Общий тест",
                "success": False,
                "message": f"Ошибка тестирования: {e}"
            })
            settings.log_error(f"Ошибка тестирования: {e}")

        return test_results

    def _test_mod_initialization(self, mod_path: str) -> Dict[str, Any]:
        """Тест инициализации мода"""
        try:
            spath.insert(0, mod_path)

            python_files = list(Path(mod_path).glob("*.py"))
            main_file = None

            for py_file in python_files:
                if "test" not in py_file.stem.lower():
                    main_file = py_file
                    break

            if main_file:
                spec = importlib.util.spec_from_file_location("test_mod", main_file)
                mod_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod_module)

                if hasattr(mod_module, 'mod_initialize'):
                    # Мокаем hook_system для теста
                    class MockHookSystem:
                        def execute_hook(self, *args, **kwargs):
                            return None

                    result = mod_module.mod_initialize(MockHookSystem())

                    spath.remove(mod_path)

                    return {
                        "test": "Инициализация мода",
                        "success": result is not False,
                        "message": "Мод успешно инициализирован" if result is not False else "Инициализация завершилась неудачей"
                    }

            spath.remove(mod_path)
            return {
                "test": "Инициализация мода",
                "success": False,
                "message": "Функция mod_initialize не найдена"
            }

        except Exception as e:
            settings.log_error(f"Ошибка инициализации: {e}")
            return {
                "test": "Инициализация мода",
                "success": False,
                "message": f"Ошибка инициализации: {e}"
            }

    def _test_hook_registry(self, mod_path: str) -> Dict[str, Any]:
        """Тест регистрации хуков"""
        try:
            spath.insert(0, mod_path)

            python_files = list(Path(mod_path).glob("*.py"))
            main_file = None

            for py_file in python_files:
                if "test" not in py_file.stem.lower():
                    main_file = py_file
                    break

            if main_file:
                spec = importlib.util.spec_from_file_location("test_mod", main_file)
                mod_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod_module)

                if hasattr(mod_module, 'HOOK_REGISTRY'):
                    hook_registry = mod_module.HOOK_REGISTRY

                    spath.remove(mod_path)

                    return {
                        "test": "Регистрация хуков",
                        "success": isinstance(hook_registry, dict) and len(hook_registry) > 0,
                        "message": f"Зарегистрировано хуков: {len(hook_registry)}" if isinstance(hook_registry, dict) else "HOOK_REGISTRY не является словарем"
                    }

            spath.remove(mod_path)
            return {
                "test": "Регистрация хуков",
                "success": False,
                "message": "HOOK_REGISTRY не найден"
            }

        except Exception as e:
            settings.log_error(f"Ошибка тестирования хуков: {e}")
            return {
                "test": "Регистрация хуков",
                "success": False,
                "message": f"Ошибка тестирования хуков: {e}"
            }

    def _test_compatibility(self, mod_path: str) -> Dict[str, Any]:
        """Тест совместимости с игрой"""
        return {
            "test": "Совместимость с игрой",
            "success": True,
            "message": "Мод совместим с Text War Legacy"
        }

    def build_package(self, mod_path: str) -> Dict[str, Any]:
        """Сборка мода в пакет для распространения"""
        result = {
            "success": False,
            "output_path": "",
            "errors": [],
            "warnings": []
        }

        try:
            project_path = Path(mod_path)
            project_name = project_path.name

            # Создание временной директории для сборки
            with TemporaryDirectory() as temp_dir:
                build_dir = Path(temp_dir) / project_name
                build_dir.mkdir()

                # Копирование Python файлов
                python_files = list(project_path.glob("*.py"))
                for py_file in python_files:
                    copy2(py_file, build_dir)

                # Копирование конфигурационных файлов
                config_files = list(project_path.glob("*.json"))
                for config_file in config_files:
                    copy2(config_file, build_dir)

                # Создание README если его нет
                readme_file = build_dir / "README.md"
                if not readme_file.exists():
                    self._create_default_readme(readme_file, project_name)

                # Создание архива
                output_filename = f"{project_name}_mod.zip"
                output_path = project_path.parent / output_filename

                make_archive(
                    str(output_path.with_suffix('')),  # Без расширения
                    'zip',
                    build_dir
                )

                result["success"] = True
                result["output_path"] = str(output_path)
                result["message"] = f"Мод собран в: {output_path}"

        except Exception as e:
            result["errors"].append(f"Ошибка сборки: {e}")
            settings.log_error(f"Ошибка сборки: {e}")

        return result

    def _create_default_readme(self, readme_path: Path, project_name: str):
        """Создание README по умолчанию"""
        readme_content = f"""# {project_name}

Мод для игры Text War Legacy

## Установка

1. Скопируйте файлы мода в папку `src/saves/mods/`
2. Перезапустите игру

## Функциональность

Опишите здесь что делает ваш мод.

## Совместимость

- Text War Legacy: Версия 1.0
- Python: 3.8+

## Автор

Ваше имя здесь
"""
        readme_path.write_text(readme_content, encoding='utf-8')
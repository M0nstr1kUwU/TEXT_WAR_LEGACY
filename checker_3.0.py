# [file name]: checker_3.0.py
import os
import platform
import sys
import importlib
import json
import ast
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set


class ProjectAnalyzer:
    """Расширенный анализатор проекта"""

    def __init__(self):
        self.project_root = Path('.')
        self.stats = {
            'total_files': 0,
            'total_lines': 0,
            'total_classes': 0,
            'total_functions': 0,
            'total_imports': 0,
            'file_types': {},
            'largest_files': [],
            'complex_files': []
        }
        self.dependencies = set()
        self.issues = []
        self.recommendations = []
        self.unexpected_files = {}  # Новый словарь для неожиданных файлов

    def analyze_project(self):
        """Основной метод анализа"""
        print("🔍 РАСШИРЕННЫЙ АНАЛИЗ ПРОЕКТА TEXT WAR LEGACY")
        print(f"🕐 Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        self.create_file_tree()
        self.analyze_python_files_extended()
        self.analyze_project_structure_extended()
        self.check_imports_extended()
        self.check_config_files_extended()
        self.analyze_code_complexity()
        self.check_performance_issues()
        self.analyze_mod_system()
        self.analyze_ai_system()
        self.analyze_unexpected_files()  # НОВЫЙ МЕТОД
        self.system_info_extended()
        self.potential_issues_extended()
        self.generate_recommendations()
        self.generate_summary_report()

    def create_file_tree(self):
        """Создает расширенное дерево файлов проекта"""
        print("\n" + "=" * 60)
        print("🌳 РАСШИРЕННОЕ ДЕРЕВО ФАЙЛОВ ПРОЕКТА")
        print("=" * 60)

        def generate_tree(startpath, prefix="", level=0):
            if level > 5:  # Ограничиваем глубину рекурсии
                return

            contents = []
            try:
                contents = os.listdir(startpath)
            except Exception as e:
                return print(f"Error: {e}.\n")

            # Расширенный список исключений
            exclude_dirs = ['__pycache__', '.git', '.vscode', '.idea', 'venv', '.env']
            exclude_files = ['checker.py', 'checker_2.0.py', 'checker_3.0.py', 'calculator.py', 'fix_achievements.py']

            contents = [c for c in contents if c not in exclude_dirs + exclude_files]
            contents.sort()

            pointers = ["├── "] * (len(contents) - 1) + ["└── "]

            for pointer, path in zip(pointers, contents):
                full_path = os.path.join(startpath, path)

                # Расширенная информация о файлах
                if os.path.isfile(full_path):
                    size = os.path.getsize(full_path)
                    ext = Path(path).suffix.lower()
                    file_info = f" ({size} bytes, {ext})"

                    # Собираем информацию о неожиданных файлах
                    if self.is_unexpected_file(full_path):
                        file_info += " 🔍"

                elif os.path.isdir(full_path):
                    file_count = count_files_in_dir(full_path)
                    dir_size = self.get_directory_size(full_path)
                    file_info = f" ({file_count} files, {dir_size})"
                else:
                    file_info = ""

                print(prefix + pointer + path + file_info)

                if os.path.isdir(full_path) and path not in exclude_dirs:
                    extension = "    " if pointer == "└── " else "│   "
                    generate_tree(full_path, prefix=prefix + extension, level=level + 1)

        generate_tree('.')

    def is_unexpected_file(self, file_path):
        """Проверяет, является ли файл неожиданным"""
        # Ожидаемые файлы по структуре проекта
        expected_files = [
            'main.py', 'run_mod_editor.py',
            # Сущности
            'src/entities/player.py', 'src/entities/enemy.py',
            # Действия
            'src/actions/actions_battle.py',
            # Настройки
            'src/settings/settings_manager.py', 'src/settings/settings_menu.py', 'src/settings/support_list.py',
            # AI
            'src/ai_resources/ai_enemy/base_ai.py', 'src/ai_resources/ai_enemy/ai_manager.py',
            'src/ai_resources/ai_enemy/aggressive_ai.py', 'src/ai_resources/ai_enemy/defensive_ai.py',
            'src/ai_resources/ai_enemy/balanced_ai.py', 'src/ai_resources/ai_enemy/adaptive_ai.py',
            'src/ai_resources/ai_enemy/boss_ai.py', 'src/ai_resources/ai_enemy/enhanced_ai.py',
            # Моды
            'src/modding/support_mods.py',
            'src/modding/mod_editor/main.py', 'src/modding/mod_editor/project_manager.py',
            'src/modding/mod_editor/settings_manager.py', 'src/modding/mod_editor/mod_compiler.py',
            'src/modding/mod_editor/template_manager.py', 'src/modding/mod_editor/code_completion.py',
            'src/modding/mod_editor/hook_explorer.py', 'src/modding/mod_editor/editor_core.py',
            'src/modding/mod_editor/syntax_highlighter.py',
            'src/modding/mod_editor/ui/main_window.py', 'src/modding/mod_editor/ui/code_editor.py',
            'src/modding/mod_editor/ui/file_tree.py', 'src/modding/mod_editor/ui/hook_browser.py',
            'src/modding/mod_editor/ui/toolbars.py', 'src/modding/mod_editor/ui/status_bar.py',
            # Магазин
            'src/shop_source/shop_core.py', 'src/shop_source/shop_manager.py', 'src/shop_source/shop_menu.py',
            'src/shop_source/hook_integration.py',
            # Достижения
            'src/achievements_source/achievements_core.py', 'src/achievements_source/achievements_manager.py',
            'src/achievements_source/achievements_menu.py',
            # Классы
            'src/classes_entities/classes_core.py', 'src/classes_entities/classes_menu.py',
            'src/classes_entities/skill_tree.py',
            # Элементы
            'src/elemental_source/elemental_core.py', 'src/elemental_source/elemental_integration.py',
            # Инвентарь
            'src/inventory/inventory_manager.py', 'src/inventory/inventory_menu.py',
            # Хуки
            'src/hooks/hook_system.py',
            # Утилиты
            'src/utils/helpers_def.py', 'src/utils/path_manager.py'
        ]

        # Конфигурационные файлы
        expected_configs = [
            'src/saves/configs/settings.json', 'src/saves/configs/hooks.json',
            'src/saves/configs/player_data.json', 'src/saves/configs/editor_settings.json'
        ]

        all_expected = expected_files + expected_configs

        # Нормализуем путь для сравнения
        normalized_path = file_path.replace('\\', '/')

        return normalized_path not in all_expected and not normalized_path.endswith('/__init__.py')

    def get_directory_size(self, directory):
        """Получает размер директории в читаемом формате"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)

        # Конвертируем в читаемый формат
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total_size < 1024.0:
                return f"{total_size:.1f} {unit}"
            total_size /= 1024.0
        return f"{total_size:.1f} TB"

    def analyze_python_files_extended(self):
        """Расширенный анализ Python файлов"""
        print("\n" + "=" * 60)
        print("🐍 РАСШИРЕННЫЙ АНАЛИЗ PYTHON ФАЙЛОВ")
        print("=" * 60)

        python_files = []
        file_analysis = []

        for root, dirs, files in os.walk('.'):
            if any(skip in root for skip in ['__pycache__', '.git', '.vscode', '.idea']):
                continue

            for file in files:
                if file.endswith('.py') and file not in ['checker.py', 'checker_2.0.py', 'checker_3.0.py',
                                                         'calculator.py', 'fix_achievements.py']:
                    full_path = os.path.join(root, file)
                    python_files.append(full_path)

                    analysis = self.analyze_python_file(full_path)
                    file_analysis.append(analysis)

        # Сортировка по сложности
        file_analysis.sort(key=lambda x: x['complexity_score'], reverse=True)

        print("📊 ТОП-10 САМЫХ СЛОЖНЫХ ФАЙЛОВ:")
        for i, analysis in enumerate(file_analysis[:10], 1):
            print(f"{i:2d}. {analysis['path']}")
            print(
                f"    📏 Строк: {analysis['lines']:4d} | 🏛️  Классы: {analysis['classes']:2d} | 🔧 Функции: {analysis['functions']:2d}")
            print(f"    📊 Сложность: {analysis['complexity_score']:.1f} | 📚 Импорты: {analysis['imports']:2d}")

        # Общая статистика
        total_stats = {
            'files': len(python_files),
            'lines': sum(a['lines'] for a in file_analysis),
            'classes': sum(a['classes'] for a in file_analysis),
            'functions': sum(a['functions'] for a in file_analysis),
            'imports': sum(a['imports'] for a in file_analysis),
            'avg_complexity': sum(a['complexity_score'] for a in file_analysis) / len(
                file_analysis) if file_analysis else 0
        }

        print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
        print(f"📁 Всего Python файлов: {total_stats['files']}")
        print(f"📏 Всего строк кода: {total_stats['lines']}")
        print(f"🏛️  Всего классов: {total_stats['classes']}")
        print(f"🔧 Всего функций/методов: {total_stats['functions']}")
        print(f"📚 Всего импортов: {total_stats['imports']}")
        print(f"📊 Средняя сложность: {total_stats['avg_complexity']:.2f}")

        # Сохраняем статистику
        self.stats.update(total_stats)
        self.stats['largest_files'] = sorted(file_analysis, key=lambda x: x['lines'], reverse=True)[:5]
        self.stats['complex_files'] = file_analysis[:5]

    def analyze_python_file(self, file_path):
        """Анализирует отдельный Python файл"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.count('\n') + 1
            classes = content.count('class ')
            functions = content.count('def ')
            imports = content.count('import ') + content.count('from ')

            # Простая метрика сложности
            complexity_score = (classes * 5 + functions * 3 + imports * 1) / max(lines, 1) * 100

            return {
                'path': file_path[2:],  # Убираем './' в начале
                'lines': lines,
                'classes': classes,
                'functions': functions,
                'imports': imports,
                'complexity_score': complexity_score
            }
        except Exception as e:
            return {
                'path': file_path[2:],
                'lines': 0,
                'classes': 0,
                'functions': 0,
                'imports': 0,
                'complexity_score': 0,
                'error': str(e)
            }

    def analyze_project_structure_extended(self):
        """Расширенный анализ структуры проекта"""
        print("\n" + "=" * 60)
        print("🏗️  РАСШИРЕННАЯ СТРУКТУРА ПРОЕКТА")
        print("=" * 60)

        # Обновленная структура с учетом всех модулей
        modules_analysis = {
            '🎮 Игровое ядро': {
                'src/entities': ['player', 'enemy'],
                'src/actions': ['actions_battle'],
                'src/settings': ['settings_manager', 'settings_menu', 'support_list']
            },
            '🤖 AI Система': {
                'src/ai_resources/ai_enemy': [
                    'base_ai', 'ai_manager', 'aggressive_ai', 'defensive_ai',
                    'balanced_ai', 'adaptive_ai', 'boss_ai', 'enhanced_ai'
                ]
            },
            '🔧 Модификации': {
                'src/modding': ['support_mods'],
                'src/modding/mod_editor': [
                    'main', 'project_manager', 'settings_manager', 'mod_compiler',
                    'template_manager', 'code_completion', 'hook_explorer',
                    'editor_core', 'syntax_highlighter'
                ],
                'src/modding/mod_editor/ui': [
                    'main_window', 'code_editor', 'file_tree', 'hook_browser',
                    'toolbars', 'status_bar'
                ]
            },
            '🛒 Магазин': {
                'src/shop_source': ['shop_core', 'shop_manager', 'shop_menu', 'hook_integration']
            },
            '🏆 Достижения': {
                'src/achievements_source': ['achievements_core', 'achievements_manager', 'achievements_menu']
            },
            '🎯 Классы и навыки': {
                'src/classes_entities': ['classes_core', 'classes_menu', 'skill_tree']
            },
            '🌪️ Элементальная система': {
                'src/elemental_source': ['elemental_core', 'elemental_integration']
            },
            '🎒 Инвентарь': {
                'src/inventory': ['inventory_manager', 'inventory_menu']
            },
            '📁 Данные': {
                'src/saves/configs': ['settings.json', 'hooks.json', 'player_data.json', 'editor_settings.json'],
                'src/saves/logs': [],
                'src/saves/mods': ['example_mod.py']
            },
            '🛠️ Утилиты': {
                'src/utils': ['helpers_def', 'path_manager'],
                'src/hooks': ['hook_system']
            }
        }

        total_modules = 0
        total_components = 0
        missing_components = []

        for category, modules in modules_analysis.items():
            print(f"\n{category}:")
            print("-" * 40)

            for directory, expected_items in modules.items():
                exists = os.path.exists(directory)
                status = "✅" if exists else "❌"
                print(f"{status} {directory}/")
                total_modules += 1

                if exists:
                    actual_items = os.listdir(directory)
                    actual_items = [f for f in actual_items if not f.startswith('.') and f != '__pycache__']

                    for expected in expected_items:
                        total_components += 1
                        expected_with_py = expected + '.py'
                        expected_with_json = expected + '.json'

                        if (expected in [f.split('.')[0] for f in actual_items if f.endswith('.py')] or
                                expected in actual_items or
                                expected_with_py in actual_items or
                                expected_with_json in actual_items):
                            print(f"   ✅ {expected}")
                        else:
                            print(f"   ❌ {expected} - ОТСУТСТВУЕТ!")
                            missing_components.append(f"{directory}/{expected}")

                    # Собираем информацию о неожиданных файлах
                    unexpected_items = self.get_unexpected_items(actual_items, expected_items)
                    if unexpected_items:
                        if directory not in self.unexpected_files:
                            self.unexpected_files[directory] = []
                        self.unexpected_files[directory].extend(unexpected_items)

                else:
                    print(f"   📁 Директория не существует!")
                    missing_components.extend([f"{directory}/{item}" for item in expected_items])

        print(f"\n📊 СТАТИСТИКА СТРУКТУРЫ:")
        print(f"📦 Всего модулей: {total_modules}")
        print(f"🔧 Всего компонентов: {total_components}")
        print(f"❌ Отсутствует компонентов: {len(missing_components)}")

        if missing_components:
            print(f"\n📋 Отсутствующие компоненты:")
            for missing in missing_components[:5]:
                print(f"   • {missing}")

    def get_unexpected_items(self, actual_items, expected_items):
        """Получает неожиданные элементы"""
        expected_set = set(expected_items)
        expected_set.update([item + '.py' for item in expected_items])
        expected_set.update([item + '.json' for item in expected_items])

        return [item for item in actual_items
                if item not in expected_set
                and not item.endswith('__init__.py')
                and not item.startswith('__')]

    def analyze_unexpected_files(self):
        """Анализ неожиданных файлов"""
        print("\n" + "=" * 60)
        print("🔍 АНАЛИЗ НЕОЖИДАННЫХ ФАЙЛОВ")
        print("=" * 60)

        if not self.unexpected_files:
            print("✅ Неожиданных файлов не обнаружено!")
            return

        total_unexpected = sum(len(files) for files in self.unexpected_files.values())
        print(f"📊 Всего неожиданных файлов: {total_unexpected}")

        for directory, files in self.unexpected_files.items():
            print(f"\n📁 {directory}/:")
            for file in sorted(files)[:10]:  # Показываем первые 10 файлов каждой директории
                file_path = os.path.join(directory, file)
                file_type = "📄" if file.endswith('.py') else "📊" if file.endswith('.json') else "📝"

                # Получаем дополнительную информацию о файле
                try:
                    size = os.path.getsize(file_path)
                    if file.endswith('.py'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = len(f.readlines())
                        print(f"   {file_type} {file} ({size} bytes, {lines} строк)")
                    else:
                        print(f"   {file_type} {file} ({size} bytes)")
                except Exception as e:
                    print(f"   {file_type} {file} (ошибка: {e})")

        # Группируем по типам
        file_types = {}
        for files in self.unexpected_files.values():
            for file in files:
                ext = Path(file).suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1

        print(f"\n📈 РАСПРЕДЕЛЕНИЕ ПО ТИПАМ:")
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            ext_name = ext if ext else 'без расширения'
            print(f"   {ext_name}: {count} файлов")

    def check_imports_extended(self):
        """Расширенный анализ импортов"""
        print("\n" + "=" * 60)
        print("🔗 РАСШИРЕННЫЙ АНАЛИЗ ИМПОРТОВ")
        print("=" * 60)

        internal_imports = set()
        external_imports = set()
        circular_imports = set()
        unused_imports = set()

        # Стандартные библиотеки Python
        stdlib_modules = set(sys.builtin_module_names)
        stdlib_modules.update(['os', 'sys', 'json', 'random', 'datetime', 'typing', 'pathlib'])

        for root, dirs, files in os.walk('src'):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            for line_num, line in enumerate(f, 1):
                                line = line.strip()
                                if line.startswith('import ') or line.startswith('from '):
                                    # Анализ импортов
                                    if 'src.' in line or line.startswith('from .') or line.startswith('import .'):
                                        internal_imports.add(f"{file}:{line_num} - {line}")
                                    else:
                                        # Проверяем внешние зависимости
                                        module_name = self.extract_module_name(line)
                                        if module_name and module_name not in stdlib_modules:
                                            external_imports.add(module_name)
                    except Exception as e:
                        print(f"❌ Ошибка анализа импортов в {full_path}: {e}")

        print("📦 ВНУТРЕННИЕ ИМПОРТЫ (первые 10):")
        for imp in sorted(internal_imports)[:10]:
            print(f"   📎 {imp}")

        print(f"\n🌐 ВНЕШНИЕ ЗАВИСИМОСТИ ({len(external_imports)}):")
        for imp in sorted(external_imports):
            print(f"   📦 {imp}")

        # Анализ зависимостей
        self.analyze_dependencies(external_imports)

    def extract_module_name(self, import_line):
        """Извлекает имя модуля из строки импорта"""
        if import_line.startswith('import '):
            return import_line.split('import ')[1].split()[0].split('.')[0]
        elif import_line.startswith('from '):
            return import_line.split('from ')[1].split()[0].split('.')[0]
        return None

    def analyze_dependencies(self, external_imports):
        """Анализирует внешние зависимости"""
        print(f"\n📊 АНАЛИЗ ЗАВИСИМОСТЕЙ:")

        # Группируем по типам
        qt_deps = [dep for dep in external_imports if 'qt' in dep.lower() or 'pyqt' in dep.lower()]
        data_deps = [dep for dep in external_imports if dep in ['json', 'dataclasses', 'enum']]
        other_deps = [dep for dep in external_imports if dep not in qt_deps + data_deps]

        print(f"🎨 GUI (Qt): {len(qt_deps)}")
        for dep in qt_deps:
            print(f"   • {dep}")

        print(f"📊 Data: {len(data_deps)}")
        for dep in data_deps:
            print(f"   • {dep}")

        print(f"🔧 Other: {len(other_deps)}")
        for dep in other_deps:
            print(f"   • {dep}")

    def check_config_files_extended(self):
        """Расширенная проверка конфигурационных файлов"""
        print("\n" + "=" * 60)
        print("⚙️  РАСШИРЕННАЯ ПРОВЕРКА КОНФИГУРАЦИЙ")
        print("=" * 60)

        config_files = {
            'src/saves/configs/settings.json': {
                'description': 'Настройки игры',
                'required_keys': ['game', 'ai', 'logging']
            },
            'src/saves/configs/hooks.json': {
                'description': 'Хуки для модов',
                'required_keys': []
            },
            'src/saves/configs/player_data.json': {
                'description': 'Данные игрока',
                'required_keys': ['name', 'health', 'damage', 'coin']
            },
            'src/saves/configs/editor_settings.json': {
                'description': 'Настройки редактора',
                'required_keys': []
            }
        }

        for file_path, info in config_files.items():
            exists = os.path.exists(file_path)
            status = "✅" if exists else "❌"
            print(f"{status} {info['description']}: {file_path}")

            if exists:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if file_path.endswith('.json'):
                            data = json.loads(content)
                            print(f"   📊 Размер: {len(content)} bytes | Записей: {len(data)}")

                            # Проверка обязательных ключей
                            if info['required_keys']:
                                missing_keys = [key for key in info['required_keys'] if key not in data]
                                if missing_keys:
                                    print(f"   ⚠️  Отсутствуют ключи: {', '.join(missing_keys)}")
                                else:
                                    print(f"   ✅ Все обязательные ключи присутствуют")

                except Exception as e:
                    print(f"   ❌ Ошибка чтения: {e}")

    def analyze_code_complexity(self):
        """Анализ сложности кода"""
        print("\n" + "=" * 60)
        print("📊 АНАЛИЗ СЛОЖНОСТИ КОДА")
        print("=" * 60)

        complexity_metrics = {
            'low': 0,
            'medium': 0,
            'high': 0,
            'very_high': 0
        }

        for root, dirs, files in os.walk('src'):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Простая метрика сложности
                        lines = content.count('\n')
                        functions = content.count('def ')
                        classes = content.count('class ')

                        complexity = (functions * 10 + classes * 20) / max(lines, 1)

                        if complexity < 0.1:
                            complexity_metrics['low'] += 1
                        elif complexity < 0.3:
                            complexity_metrics['medium'] += 1
                        elif complexity < 0.5:
                            complexity_metrics['high'] += 1
                        else:
                            complexity_metrics['very_high'] += 1

                    except Exception:
                        continue

        total_files = sum(complexity_metrics.values())
        if total_files > 0:
            print("📈 РАСПРЕДЕЛЕНИЕ СЛОЖНОСТИ:")
            for level, count in complexity_metrics.items():
                percentage = (count / total_files) * 100
                print(f"   {level.upper():<10}: {count:3d} файлов ({percentage:5.1f}%)")

    def check_performance_issues(self):
        """Проверка потенциальных проблем производительности"""
        print("\n" + "=" * 60)
        print("⚡ ПРОВЕРКА ПРОИЗВОДИТЕЛЬНОСТИ")
        print("=" * 60)

        performance_issues = []

        # Проверяем большие файлы
        large_files = [f for f in self.stats.get('largest_files', []) if f['lines'] > 300]
        if large_files:
            performance_issues.append("📏 Слишком большие файлы (более 300 строк):")
            for file in large_files[:3]:
                performance_issues.append(f"   • {file['path']} ({file['lines']} строк)")

        # Проверяем сложные файлы
        complex_files = [f for f in self.stats.get('complex_files', []) if f['complexity_score'] > 50]
        if complex_files:
            performance_issues.append("🧩 Слишком сложные файлы:")
            for file in complex_files[:3]:
                performance_issues.append(f"   • {file['path']} (сложность: {file['complexity_score']:.1f})")

        if performance_issues:
            for issue in performance_issues:
                print(issue)
        else:
            print("✅ Проблем с производительностью не обнаружено")

    def analyze_mod_system(self):
        """Анализ системы модов"""
        print("\n" + "=" * 60)
        print("🔧 АНАЛИЗ СИСТЕМЫ МОДОВ")
        print("=" * 60)

        mods_dir = 'src/saves/mods'
        if os.path.exists(mods_dir):
            mod_files = [f for f in os.listdir(mods_dir) if f.endswith('.py') and f != '__init__.py']
            json_files = [f for f in os.listdir(mods_dir) if f.endswith('.json')]

            print(f"📁 Моды Python: {len(mod_files)}")
            for mod in mod_files[:5]:
                mod_path = os.path.join(mods_dir, mod)
                size = os.path.getsize(mod_path)
                print(f"   • {mod} ({size} bytes)")

            print(f"📊 Моды JSON: {len(json_files)}")
            for mod in json_files[:5]:
                mod_path = os.path.join(mods_dir, mod)
                size = os.path.getsize(mod_path)
                print(f"   • {mod} ({size} bytes)")

            if len(mod_files) > 5:
                print(f"   ... и ещё {len(mod_files) - 5} модов")
        else:
            print("❌ Папка модов не найдена")

    def analyze_ai_system(self):
        """Анализ AI системы"""
        print("\n" + "=" * 60)
        print("🤖 АНАЛИЗ AI СИСТЕМЫ")
        print("=" * 60)

        ai_dir = 'src/ai_resources/ai_enemy'
        if os.path.exists(ai_dir):
            ai_files = [f for f in os.listdir(ai_dir) if f.endswith('.py') and f != '__init__.py']

            print(f"🧠 AI Модули: {len(ai_files)}")
            for ai_file in ai_files:
                file_path = os.path.join(ai_dir, ai_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        classes = content.count('class ')
                        functions = content.count('def ')
                        print(f"   • {ai_file}: {classes} классов, {functions} методов")
                except:
                    print(f"   • {ai_file}: ошибка чтения")
        else:
            print("❌ Папка AI не найдена")

    def system_info_extended(self):
        """Расширенная системная информация"""
        print("\n" + "=" * 60)
        print("💻 РАСШИРЕННАЯ СИСТЕМНАЯ ИНФОРМАЦИЯ")
        print("=" * 60)

        print(f"🐍 Версия Python: {sys.version}")
        print(f"📁 Рабочая директория: {os.getcwd()}")
        print(f"🕐 Время анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💾 ОС: {os.name} - {platform.system()} {platform.release()}")

        # Информация о проекте
        total_size = self.get_directory_size('.')
        print(f"📦 Размер проекта: {total_size}")

        # Количество файлов по типам
        file_types = {}
        for root, dirs, files in os.walk('.'):
            for file in files:
                ext = Path(file).suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1

        print(f"\n📄 ФАЙЛЫ ПО ТИПАМ:")
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {ext or 'no ext'}: {count} файлов")

    def potential_issues_extended(self):
        """Расширенная проверка проблем"""
        print("\n" + "=" * 60)
        print("🔍 РАСШИРЕННАЯ ПРОВЕРКА ПРОБЛЕМ")
        print("=" * 60)

        issues = self.collect_issues()

        if issues:
            for category, category_issues in issues.items():
                if category_issues:
                    print(f"\n{category}:")
                    for issue in category_issues[:5]:  # Показываем первые 5 проблем каждой категории
                        print(f"   {issue}")
        else:
            print("✅ Критических проблем не обнаружено!")

    def collect_issues(self):
        """Собирает все проблемы"""
        issues = {
            '❌ КРИТИЧЕСКИЕ': [],
            '⚠️  ВАЖНЫЕ': [],
            'ℹ️  ИНФОРМАЦИОННЫЕ': []
        }

        # Проверка основных файлов
        essential_files = [
            'main.py', 'run_mod_editor.py',
            'src/entities/player.py', 'src/entities/enemy.py',
            'src/actions/actions_battle.py'
        ]

        for file in essential_files:
            if not os.path.exists(file):
                issues['❌ КРИТИЧЕСКИЕ'].append(f"Отсутствует важный файл: {file}")

        # Проверка конфигурационных файлов
        config_files = [
            'src/saves/configs/settings.json',
            'src/saves/configs/player_data.json'
        ]

        for config in config_files:
            if not os.path.exists(config):
                issues['⚠️  ВАЖНЫЕ'].append(f"Отсутствует конфигурационный файл: {config}")

        # Проверка больших файлов
        large_files = [f for f in self.stats.get('largest_files', []) if f['lines'] > 500]
        for file in large_files:
            issues['ℹ️  ИНФОРМАЦИОННЫЕ'].append(f"Большой файл: {file['path']} ({file['lines']} строк)")

        # Проверка неожиданных файлов
        if self.unexpected_files:
            total_unexpected = sum(len(files) for files in self.unexpected_files.values())
            if total_unexpected > 10:
                issues['ℹ️  ИНФОРМАЦИОННЫЕ'].append(f"Обнаружено {total_unexpected} неожиданных файлов")

        return issues

    def generate_recommendations(self):
        """Генерирует рекомендации на основе анализа"""
        print("\n" + "=" * 60)
        print("💡 РАСШИРЕННЫЕ РЕКОМЕНДАЦИИ")
        print("=" * 60)

        recommendations = [
            "🎯 ОПТИМИЗАЦИЯ КОДА:",
            "   • Разделить большие файлы на модули",
            "   • Уменьшить сложность самых сложных файлов",
            "   • Добавить type hints для лучшей читаемости",
            "",
            "🔧 АРХИТЕКТУРА:",
            "   • Создать единую систему событий (Event Bus)",
            "   • Реализовать dependency injection",
            "   • Добавить систему плагинов для модов",
            "",
            "🧪 ТЕСТИРОВАНИЕ:",
            "   • Написать unit-тесты для основных модулей",
            "   • Добавить интеграционные тесты",
            "   • Реализовать тестирование производительности",
            "",
            "📚 ДОКУМЕНТАЦИЯ:",
            "   • Создать API документацию для модмейкеров",
            "   • Добавить примеры использования",
            "   • Создать руководство по архитектуре",
            "",
            "🎮 ИГРОВОЙ КОНТЕНТ:",
            "   • Добавить систему квестов",
            "   • Реализовать систему крафта",
            "   • Создать разные биомы/локации",
            "   • Добавить мультиплеер (PvP)",
            "",
            "🤖 AI УЛУЧШЕНИЯ:",
            "   • Реализовать машинное обучение для AI",
            "   • Добавить нейросетевые модели",
            "   • Создать систему персонализированного AI",
            "",
            "🔧 MOD-EDITOR 2.0:",
            "   • Визуальный конструктор интерфейсов",
            "   • Отладчик модов в реальном времени",
            "   • Система управления версиями модов",
            "   • Магазин модов в игре",
            "",
            "🔍 УПРАВЛЕНИЕ ФАЙЛАМИ:",
            "   • Проверить назначение неожиданных файлов",
            "   • Организовать дополнительные файлы в структуру",
            "   • Создать документацию для пользовательских файлов"
        ]

        for rec in recommendations:
            print(rec)

    def generate_summary_report(self):
        """Генерирует итоговый отчет"""
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 60)

        # Собираем статистику неожиданных файлов
        total_unexpected = sum(len(files) for files in self.unexpected_files.values()) if self.unexpected_files else 0

        summary = f"""
📈 СТАТИСТИКА ПРОЕКТА:
   • 📁 Python файлов: {self.stats['total_files']}
   • 📏 Строк кода: {self.stats['total_lines']}
   • 🏛️  Классов: {self.stats['total_classes']}
   • 🔧 Функций: {self.stats['total_functions']}
   • 📚 Импортов: {self.stats['total_imports']}
   • 🔍 Неожиданных файлов: {total_unexpected}

🎯 КАЧЕСТВО КОДА:
   • 📊 Средняя сложность: {self.stats.get('avg_complexity', 0):.2f}
   • 📏 Самый большой файл: {self.stats['largest_files'][0]['path'] if self.stats['largest_files'] else 'N/A'} ({self.stats['largest_files'][0]['lines'] if self.stats['largest_files'] else 0} строк)
   • 🧩 Самый сложный файл: {self.stats['complex_files'][0]['path'] if self.stats['complex_files'] else 'N/A'} ({self.stats['complex_files'][0]['complexity_score'] if self.stats['complex_files'] else 0:.1f})

🚀 РЕКОМЕНДАЦИИ:
   • Оптимизировать {len([f for f in self.stats.get('largest_files', []) if f['lines'] > 300])} больших файлов
   • Упростить {len([f for f in self.stats.get('complex_files', []) if f['complexity_score'] > 50])} сложных файлов
   • Проверить {total_unexpected} неожиданных файлов
   • Добавить тесты для основных модулей
   • Улучшить документацию API
        """

        print(summary)
        print("🎉 АНАЛИЗ ЗАВЕРШЕН!")


def count_files_in_dir(directory):
    """Считает количество файлов в директории"""
    count = 0
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git']]
        count += len(files)
    return count


if __name__ == '__main__':
    analyzer = ProjectAnalyzer()
    analyzer.analyze_project()
from os import system, name
from time import sleep
from settings.settings_manager import settings


# Очистка консоли
def clear_console_def(action, second):
    if action == 1:       # Очистка
        system('cls' if name == 'nt' else 'clear')
    elif action == 2:     # Время + очистка
        timeout_def(1, second)
        system('cls' if name == 'nt' else 'clear')
    elif action == 3:     # Enter + Очистка
        timeout_def(2, 0)
        system('cls' if name == 'nt' else 'clear')
    elif action == 4:     # Время + Enter + очистка
        message_warning_def(3, "Hастройте очищение консоли правильно!")


# Ожидание
def timeout_def(action, second):
    if action == 1:  # Ожидание
        sleep(second)
    elif action == 2: # Ожидание + Enter
        sleep(second)
        input("Enter...")
    elif action == 3: # Enter
        input("Enter...")
    else:
        message_warning_def(3, "Hастройте очищение консоли правильно!")


# Уведомление об ошибке и логирование уведомления
def message_warning_def(second, message): # Уведомление об ошибке, если неправильно настроено
    settings.log_warning(message)
    sleep(second)
    system('cls' if name == 'nt' else 'clear')
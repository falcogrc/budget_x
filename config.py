from datetime import datetime
import os

# Цвета
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'

# Категории по умолчанию
DEFAULT_CATEGORIES = {
    'income': ['Зарплата', 'Фриланс', 'Подарки', 'Инвестиционный доход'],
    'expense': ['Еда', 'Транспорт', 'ЖКХ', 'Развлечения', 'Здоровье'],
}

_BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(_BASE, 'data', 'budget.json')
EXPORT_DIR = os.path.join(_BASE, 'exports')

def clear_screen():
    print('\033[2J\033[H', end='')

def today():
    return datetime.now().strftime('%Y-%m-%d')

def current_month():
    return datetime.now().strftime('%Y-%m')

def _cols():
    try:
        return os.get_terminal_size().columns
    except (OSError, ValueError):
        return 80

def bar_width():
    c = _cols()
    if c >= 100:
        return 30
    elif c >= 80:
        return 22
    elif c >= 60:
        return 16
    else:
        return 12

def name_width():
    c = _cols()
    if c >= 100:
        return 20
    elif c >= 80:
        return 18
    elif c >= 60:
        return 14
    else:
        return 12

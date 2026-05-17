from datetime import datetime

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

DATA_FILE = 'data/budget.json'
EXPORT_DIR = 'exports'

def clear_screen():
    print('\033[2J\033[H', end='')

def today():
    return datetime.now().strftime('%Y-%m-%d')

def current_month():
    return datetime.now().strftime('%Y-%m')

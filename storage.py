import json
import os
from config import DATA_FILE, DEFAULT_CATEGORIES

def default_data():
    return {
        'categories': {
            'income': DEFAULT_CATEGORIES['income'][:],
            'expense': DEFAULT_CATEGORIES['expense'][:],
        },
        'transactions': [],
        'next_id': 1,
        'investments': {
            'total_invested': 0.0,
            'current_value': 0.0,
        },
        'safety_pillow': {
            'goal': 0.0,
            'current': 0.0,
        },
        'budgets': {},
    }

def load():
    if not os.path.exists(DATA_FILE):
        data = default_data()
        save(data)
        return data
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if 'next_id' not in data:
        data['next_id'] = 1
    if 'budgets' not in data:
        data['budgets'] = {}
    if 'investments' not in data:
        data['investments'] = {'total_invested': 0.0, 'current_value': 0.0}
    if 'safety_pillow' not in data:
        data['safety_pillow'] = {'goal': 0.0, 'current': 0.0}
    return data

def save(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

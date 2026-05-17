from config import GREEN, RED, YELLOW, CYAN, BOLD, RESET, today
from storage import load, save
from datetime import datetime


def _valid_date(s):
    try:
        datetime.strptime(s, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def _next_id(data):
    nid = data['next_id']
    data['next_id'] = nid + 1
    return nid


def _get_date():
    default = today()
    inp = input(f'Дата [{default}]: ').strip()
    if not inp:
        return default
    if _valid_date(inp):
        return inp
    print(f'{RED}Неверный формат даты, используется {default}{RESET}')
    return default


def add_income():
    data = load()
    cats = data['categories']['income']
    print(f'{BOLD}Категории дохода:{RESET}')
    for i, c in enumerate(cats, 1):
        print(f'  {i}. {c}')
    try:
        choice = int(input('Выберите категорию: '))
        category = cats[choice - 1]
    except (ValueError, IndexError):
        print(f'{RED}Неверный выбор{RESET}')
        return
    try:
        amount = float(input('Сумма: '))
        if amount <= 0:
            print(f'{RED}Сумма должна быть положительной{RESET}')
            return
    except ValueError:
        print(f'{RED}Неверная сумма{RESET}')
        return
    comment = input('Комментарий: ').strip()
    date = _get_date()

    data['transactions'].append({
        'id': _next_id(data),
        'type': 'income',
        'category': category,
        'amount': amount,
        'date': date,
        'comment': comment,
    })
    save(data)
    print(f'{GREEN}Доход {amount:.2f} добавлен!{RESET}')


def add_expense():
    data = load()
    cats = data['categories']['expense']
    print(f'{BOLD}Категории расхода:{RESET}')
    for i, c in enumerate(cats, 1):
        print(f'  {i}. {c}')
    try:
        choice = int(input('Выберите категорию: '))
        category = cats[choice - 1]
    except (ValueError, IndexError):
        print(f'{RED}Неверный выбор{RESET}')
        return
    try:
        amount = float(input('Сумма: '))
        if amount <= 0:
            print(f'{RED}Сумма должна быть положительной{RESET}')
            return
    except ValueError:
        print(f'{RED}Неверная сумма{RESET}')
        return
    comment = input('Комментарий: ').strip()
    date = _get_date()

    data['transactions'].append({
        'id': _next_id(data),
        'type': 'expense',
        'category': category,
        'amount': amount,
        'date': date,
        'comment': comment,
    })
    save(data)
    print(f'{RED}Расход {amount:.2f} добавлен!{RESET}')


def _apply_filter(txns):
    print(f'{BOLD}Фильтр:{RESET} Enter=все, д=доходы, р=расходы, дата(2026-05), диапазон(2026-03-01 2026-03-15), текст')
    filt = input('Фильтр: ').strip().lower()
    if not filt:
        return txns
    if filt == 'д':
        return [t for t in txns if t['type'] == 'income']
    if filt == 'р':
        return [t for t in txns if t['type'] == 'expense']
    parts = filt.split()
    if len(parts) == 2:
        if _valid_date(parts[0]) and _valid_date(parts[1]):
            return [t for t in txns if parts[0] <= t['date'] <= parts[1]]
    if len(filt) == 7 and filt[4] == '-':
        return [t for t in txns if t['date'].startswith(filt)]
    return [t for t in txns if filt in t['category'].lower() or filt in t['comment'].lower()]


def list_transactions():
    data = load()
    txns = data['transactions']
    if not txns:
        print('Нет операций')
        return
    txns = _apply_filter(txns)
    if not txns:
        print(f'{YELLOW}Нет операций по фильтру{RESET}')
        return

    print(f'{BOLD}{"ID":>4} {"Дата":<12} {"Тип":<8} {"Категория":<20} {"Сумма":>10} Комментарий{RESET}')
    print('-' * 80)
    for t in reversed(txns):
        if t['type'] == 'income':
            color, sign = GREEN, '+'
        elif t['type'] == 'expense':
            color, sign = RED, '-'
        else:
            color, sign = CYAN, '▶'
        print(f'{t["id"]:>4} {t["date"]:<12} {color}{t["type"]:<8}{RESET} {t["category"]:<20} {color}{sign}{t["amount"]:>8.2f}{RESET} {t["comment"]}')

    print()
    txn_id = input(f'{BOLD}ID транзакции для редактирования, У+ID для удаления, Enter — назад: {RESET}').strip()
    if not txn_id:
        return
    raw = txn_id.lower().replace('+', '').replace(' ', '')
    if raw[0] in ('у', 'y'):
        try:
            delete_id = int(raw[1:])
            _delete_transaction(data, delete_id)
        except (ValueError, IndexError):
            print(f'{RED}Неверный ID{RESET}')
    else:
        try:
            edit_id = int(raw)
            _edit_transaction(data, edit_id)
        except (ValueError, IndexError):
            print(f'{RED}Неверный ID{RESET}')


def _find_txn(data, txn_id):
    for i, t in enumerate(data['transactions']):
        if t['id'] == txn_id:
            return i, t
    return None, None


def _edit_transaction(data, txn_id):
    idx, txn = _find_txn(data, txn_id)
    if txn is None:
        print(f'{RED}Транзакция с ID {txn_id} не найдена{RESET}')
        return

    cats = data['categories'][txn['type']]
    print(f'\n{BOLD}Редактирование #{txn_id}:{RESET}')
    print(f'  Текущая категория: {txn["category"]}')
    for i, c in enumerate(cats, 1):
        print(f'  {i}. {c}')
    try:
        choice = input('Категория (Enter — оставить): ').strip()
        if choice:
            category = cats[int(choice) - 1]
        else:
            category = txn['category']
    except (ValueError, IndexError):
        print(f'{RED}Неверный выбор, категория не изменена{RESET}')
        category = txn['category']

    try:
        inp = input(f'Сумма [{txn["amount"]:.2f}]: ').strip()
        amount = float(inp) if inp else txn['amount']
    except ValueError:
        print(f'{RED}Неверная сумма, оставлено {txn["amount"]:.2f}{RESET}')
        amount = txn['amount']

    inp = input(f'Дата [{txn["date"]}]: ').strip()
    if inp:
        date = inp if _valid_date(inp) else txn['date']
        if inp != date:
            print(f'{RED}Неверный формат, оставлено {txn["date"]}{RESET}')
    else:
        date = txn['date']

    inp = input(f'Комментарий [{txn["comment"]}]: ').strip()
    comment = inp if inp else txn['comment']

    data['transactions'][idx] = {**txn, 'category': category, 'amount': amount, 'date': date, 'comment': comment}
    save(data)
    print(f'{GREEN}Транзакция #{txn_id} обновлена{RESET}')


def _delete_transaction(data, txn_id):
    idx, txn = _find_txn(data, txn_id)
    if txn is None:
        print(f'{RED}Транзакция с ID {txn_id} не найдена{RESET}')
        return
    if txn['type'] == 'income':
        color, sign = GREEN, '+'
    elif txn['type'] == 'expense':
        color, sign = RED, '-'
    else:
        color, sign = CYAN, '▶'
    print(f'  {txn["date"]} {txn["category"]} {color}{sign}{txn["amount"]:.2f}{RESET}')
    confirm = input(f'{BOLD}Удалить? (д/н): {RESET}').strip().lower()
    if confirm in ('д', 'y', 'да', 'yes'):
        removed = data['transactions'].pop(idx)
        save(data)
        print(f'{RED}Транзакция #{txn_id} удалена{RESET}')
    else:
        print('Отменено')

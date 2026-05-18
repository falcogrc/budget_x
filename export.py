import csv
import os
from config import EXPORT_DIR, GREEN, YELLOW, BOLD, RESET, today
from storage import load
from transactions import _valid_date


def export_csv():
    data = load()
    txns = data['transactions']
    if not txns:
        print(f'{YELLOW}Нет операций для выгрузки{RESET}')
        return

    print(f'{BOLD}Период:{RESET}')
    print(f'  Enter=назад, всё, месяц(2026-05), диапазон(2026-03-01 2026-03-15)')
    inp = input('Период: ').strip()
    if not inp:
        return
    if inp:
        parts = inp.split()
        if len(parts) == 1 and len(parts[0]) == 7:
            txns = [t for t in txns if t['date'].startswith(parts[0])]
        elif len(parts) == 2 and _valid_date(parts[0]) and _valid_date(parts[1]):
            txns = [t for t in txns if parts[0] <= t['date'] <= parts[1]]
        elif len(parts) == 2:
            txns = [t for t in txns if parts[0] <= t['date'][:7] <= parts[1]]

    if not txns:
        print(f'{YELLOW}Нет операций за выбранный период{RESET}')
        return

    os.makedirs(EXPORT_DIR, exist_ok=True)
    filename = f'budget_{today()}.csv'
    filepath = os.path.join(EXPORT_DIR, filename)

    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Дата', 'Тип', 'Категория', 'Сумма', 'Комментарий'])
        for t in txns:
            writer.writerow([t['id'], t['date'], t['type'], t['category'], t['amount'], t['comment']])

    print(f'{GREEN}Экспортировано: {filepath}{RESET}')

    total_income = sum(t['amount'] for t in txns if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in txns if t['type'] == 'expense')
    print(f'{BOLD}Всего доходов: {total_income:,.2f} ₽{RESET}')
    print(f'{BOLD}Всего расходов: {total_expense:,.2f} ₽{RESET}')

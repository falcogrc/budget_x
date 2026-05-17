import csv
import os
from config import EXPORT_DIR, GREEN, RED, BOLD, RESET, today
from storage import load


def export_csv():
    data = load()
    txns = data['transactions']
    if not txns:
        print(f'{RED}Нет операций для выгрузки{RESET}')
        return

    os.makedirs(EXPORT_DIR, exist_ok=True)
    filename = f'budget_{today()}.csv'
    filepath = os.path.join(EXPORT_DIR, filename)

    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Дата', 'Тип', 'Категория', 'Сумма', 'Комментарий'])
        for t in txns:
            writer.writerow([
                t['id'], t['date'], t['type'],
                t['category'], t['amount'], t['comment'],
            ])

    print(f'{GREEN}Экспортировано: {filepath}{RESET}')

    # Доп. сводка
    total_income = sum(t['amount'] for t in txns if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in txns if t['type'] == 'expense')
    print(f'{BOLD}Всего доходов: {total_income:,.2f} ₽{RESET}')
    print(f'{BOLD}Всего расходов: {total_expense:,.2f} ₽{RESET}')

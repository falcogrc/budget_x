#!/usr/bin/env python3
import sys
from config import clear_screen, GREEN, RED, YELLOW, CYAN, BOLD, RESET, current_month, bar_width
from storage import load, save
from transactions import add_income, add_expense, list_transactions
from categories import manage_categories
from analytics import show_statistics, show_investments, _set_balance
from export import export_csv


def _balance(data, month):
    all_txns = data['transactions']
    incomes = [t for t in all_txns if t['type'] == 'income' and t['date'].startswith(month)]
    expenses = [t for t in all_txns if t['type'] == 'expense' and t['date'].startswith(month)]
    total_income = sum(t['amount'] for t in incomes)
    total_expense = sum(t['amount'] for t in expenses)

    all_income = sum(t['amount'] for t in all_txns if t['type'] == 'income')
    all_expense = sum(t['amount'] for t in all_txns if t['type'] == 'expense')
    all_savings = sum(t['amount'] for t in all_txns if t['type'] == 'saving')
    bal = data['initial_balance'] + all_income - all_expense - all_savings
    return bal, total_income, total_expense


def _investment_line(data):
    inv = data['investments']
    if inv['total_invested'] > 0:
        pct = ((inv['current_value'] - inv['total_invested']) / inv['total_invested']) * 100
        color = GREEN if pct >= 0 else RED
        return f'💼 Инвестиции: {inv["current_value"]:,.2f} ₽ {color}({pct:+.1f}%){RESET}'
    return f'💼 Инвестиции: {inv["current_value"]:,.2f} ₽'


def _pillow_line(data):
    p = data['safety_pillow']
    if p['goal'] > 0:
        pct = (p['current'] / p['goal']) * 100
        bw = bar_width()
        filled = min(int(pct / 5), bw // 2)
        bar = '█' * filled + '░' * (bw // 2 - filled)
        return f'🛡️ Подушка: {p["current"]:,.2f} / {p["goal"]:,.2f} ₽ {bar} {pct:.0f}%'
    return f'🛡️ Подушка: {p["current"]:,.2f} ₽'


def show_menu():
    data = load()
    month = current_month()
    bal, inc, exp = _balance(data, month)

    savings = [t for t in data['transactions']
               if t['type'] == 'saving' and t['date'].startswith(month)]
    total_savings = sum(t['amount'] for t in savings)

    clear_screen()
    print('=' * 42)
    print(f'  {BOLD}  BX  •  Budget X{RESET}')
    print('=' * 42)
    print(f'📅 {month.replace("-", " ")}')
    print()
    print(f'💰 Баланс: {GREEN if bal >= 0 else RED}{bal:,.2f} ₽{RESET}')
    print(f'📈 Доходы:  {GREEN}{inc:,.2f} ₽{RESET}')
    print(f'📉 Расходы: {RED}{exp:,.2f} ₽{RESET}')
    if total_savings > 0:
        pct = (total_savings / inc) * 100
        print(f'🏦 Отложено: {CYAN}{total_savings:,.2f} ₽ ({pct:.0f}% от дохода){RESET}')
    elif inc > 0 and total_savings <= 0:
        print('🏦 Отложено: 0.00 ₽')
    print()
    print(_investment_line(data))
    print(_pillow_line(data))
    print()
    print('=' * 42)
    menu_items = [
        ('1', '➕ Доход'),
        ('2', '➖ Расход'),
        ('3', '📋 Список'),
        ('4', '💼 Сбережения'),
        ('5', '📊 Статистика'),
        ('6', '🏷️ Категории'),
        ('7', '💾 Выгрузить'),
        ('8', '⚙️ Баланс'),
        ('0', '🚪 Выход'),
    ]
    for key, label in menu_items:
        print(f'  [{key}] {label}')
    print('=' * 42)
    print(f'{BOLD}Ваш выбор:{RESET} ', end='', flush=True)


def main():
    data = load()
    if data['initial_balance'] == 0.0 and not data['transactions']:
        clear_screen()
        print(f'{BOLD}Добро пожаловать в Budget X!{RESET}')
        print()
        try:
            bal = float(input('Сколько у вас денег на всех счетах? '))
            data['initial_balance'] = bal
            save(data)
            print(f'{GREEN}Начальный баланс установлен: {bal:,.2f} ₽{RESET}')
        except ValueError:
            print(f'{YELLOW}Можно установить позже: меню → 8 ⚙️ Баланс{RESET}')
        input(f'\n{YELLOW}Нажмите Enter...{RESET}')

    while True:
        show_menu()
        while True:
            choice = input().strip()
            if choice:
                break
            print(f'{BOLD}Ваш выбор:{RESET} ', end='', flush=True)
        if choice == '1':
            add_income()
        elif choice == '2':
            add_expense()
        elif choice == '3':
            clear_screen()
            list_transactions()
        elif choice == '4':
            clear_screen()
            show_investments()
            continue
        elif choice == '5':
            clear_screen()
            show_statistics()
        elif choice == '6':
            clear_screen()
            manage_categories()
            continue
        elif choice == '7':
            clear_screen()
            export_csv()
        elif choice == '8':
            clear_screen()
            _set_balance(load())
        elif choice == '0':
            clear_screen()
            print(f'{GREEN}До свидания!{RESET}')
            sys.exit(0)
        else:
            print(f'{RED}Неверный выбор{RESET}')
        input(f'\n{YELLOW}Нажмите Enter...{RESET}')


if __name__ == '__main__':
    main()

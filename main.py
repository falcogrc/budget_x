#!/usr/bin/env python3
import sys
from config import clear_screen, GREEN, RED, YELLOW, BOLD, RESET, current_month
from storage import load
from transactions import add_income, add_expense, list_transactions
from categories import manage_categories
from analytics import show_statistics, show_investments
from export import export_csv


def _balance(data, month):
    incomes = [t for t in data['transactions']
               if t['type'] == 'income' and t['date'].startswith(month)]
    expenses = [t for t in data['transactions']
                if t['type'] == 'expense' and t['date'].startswith(month)]
    total_income = sum(t['amount'] for t in incomes)
    total_expense = sum(t['amount'] for t in expenses)
    return total_income - total_expense, total_income, total_expense


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
        bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
        return f'🛡️ Подушка: {p["current"]:,.2f} / {p["goal"]:,.2f} ₽ {bar} {pct:.0f}%'
    return f'🛡️ Подушка: {p["current"]:,.2f} ₽'


def show_menu():
    data = load()
    month = current_month()
    bal, inc, exp = _balance(data, month)

    clear_screen()
    print('=' * 42)
    print(f'  {BOLD}  BX  •  Budget X{RESET}')
    print('=' * 42)
    print(f'📅 {month.replace("-", " ")}')
    print()
    print(f'💰 Баланс: {GREEN if bal >= 0 else RED}{bal:,.2f} ₽{RESET}')
    print(f'📈 Доходы:  {GREEN}{inc:,.2f} ₽{RESET}')
    print(f'📉 Расходы: {RED}{exp:,.2f} ₽{RESET}')
    print()
    print(_investment_line(data))
    print(_pillow_line(data))
    print()
    print('=' * 42)
    menu_items = [
        ('1', '➕ Доход', '2', '➖ Расход'),
        ('3', '📋 Список', '4', '💼 Инвестиции + Подушка'),
        ('5', '📊 Статистика', '6', '🏷️ Категории'),
        ('7', '💾 Выгрузить', '8', '🚪 Выход'),
    ]
    for left_key, left_label, right_key, right_label in menu_items:
        left = f'[{left_key}] {left_label}' if left_key else ''
        right = f'    [{right_key}] {right_label}' if right_key else ''
        print(f'{left:<25}{right}')
    print('=' * 42)
    print(f'{BOLD}Ваш выбор:{RESET} ', end='', flush=True)


def main():
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
            print(f'{GREEN}До свидания!{RESET}')
            sys.exit(0)
        else:
            print(f'{RED}Неверный выбор{RESET}')
        input(f'\n{YELLOW}Нажмите Enter...{RESET}')


if __name__ == '__main__':
    main()

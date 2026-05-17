from collections import defaultdict
from config import GREEN, RED, YELLOW, CYAN, BOLD, RESET, current_month
from storage import load, save


def _bar(value, max_val, width=30):
    filled = int((value / max_val) * width) if max_val > 0 else 0
    return '█' * filled + '░' * (width - filled)


def show_statistics():
    data = load()
    txns = data['transactions']
    month = current_month()

    incomes = [t for t in txns if t['type'] == 'income' and t['date'].startswith(month)]
    expenses = [t for t in txns if t['type'] == 'expense' and t['date'].startswith(month)]
    total_income = sum(t['amount'] for t in incomes)
    total_expense = sum(t['amount'] for t in expenses)
    balance = total_income - total_expense

    inv = data['investments']
    pillow = data['safety_pillow']

    print(f'{BOLD}📊 Статистика{RESET}\n')
    print(f'💰 Баланс: {GREEN if balance >= 0 else RED}{balance:,.2f} ₽{RESET}')
    print(f'📈 Доходы: {GREEN}{total_income:,.2f} ₽{RESET}')
    print(f'📉 Расходы: {RED}{total_expense:,.2f} ₽{RESET}')

    if inv['total_invested'] > 0:
        pct = ((inv['current_value'] - inv['total_invested']) / inv['total_invested']) * 100
        color = GREEN if pct >= 0 else RED
        print(f'💼 Инвестиции: {inv["current_value"]:,.2f} ₽ {color}({pct:+.1f}%){RESET}')
    else:
        print(f'💼 Инвестиции: {inv["current_value"]:,.2f} ₽')

    if pillow['goal'] > 0:
        pct = (pillow['current'] / pillow['goal']) * 100
        width = 20
        filled = int((pillow['current'] / pillow['goal']) * width)
        bar = '█' * filled + '░' * (width - filled)
        print(f'🛡️ Подушка: {pillow["current"]:,.2f} / {pillow["goal"]:,.2f} ₽ {bar} {pct:.0f}%')
    else:
        print(f'🛡️ Подушка: {pillow["current"]:,.2f} ₽')

    print()

    # График расходов по категориям
    if expenses:
        print(f'{BOLD}Расходы по категориям:{RESET}')
        cat_totals = defaultdict(float)
        for t in expenses:
            cat_totals[t['category']] += t['amount']
        max_cat = max(cat_totals.values())
        for cat, amount in sorted(cat_totals.items(), key=lambda x: -x[1]):
            bar = _bar(amount, max_cat)
            print(f'  {cat:<20} {RED}{amount:>8.2f}{RESET} {bar}')
        print()

    # График динамики по месяцам
    _show_monthly_chart(txns)


def _show_monthly_chart(txns):
    if not txns:
        return
    months_income = defaultdict(float)
    months_expense = defaultdict(float)
    for t in txns:
        m = t['date'][:7]
        if t['type'] == 'income':
            months_income[m] += t['amount']
        else:
            months_expense[m] += t['amount']

    all_months = sorted(set(months_income) | set(months_expense))
    if len(all_months) < 1:
        return

    print(f'{BOLD}Динамика по месяцам:{RESET}')
    max_val = max(max(months_income.values(), default=0),
                  max(months_expense.values(), default=0))

    for m in all_months:
        inc = months_income.get(m, 0)
        exp = months_expense.get(m, 0)
        print(f'  {m}')
        print(f'    {GREEN}█{RESET} {"доход":<7} {inc:>8.2f} {_bar(inc, max_val)}')
        print(f'    {RED}█{RESET} {"расход":<7} {exp:>8.2f} {_bar(exp, max_val)}')
    print()


def show_investments():
    data = load()
    inv = data['investments']
    pillow = data['safety_pillow']

    print(f'{BOLD}💼 Инвестиции и 🛡️ Подушка безопасности{RESET}\n')

    print(f'{CYAN}Инвестиции:{RESET}')
    print(f'  Вложено всего:    {inv["total_invested"]:>10.2f} ₽')
    print(f'  Текущая стоимость: {inv["current_value"]:>10.2f} ₽')
    if inv['total_invested'] > 0:
        pct = ((inv['current_value'] - inv['total_invested']) / inv['total_invested']) * 100
        color = GREEN if pct >= 0 else RED
        print(f'  Доходность:        {color}{pct:+.2f}%{RESET}')
    else:
        print(f'  Доходность:        —')

    print()
    print(f'{CYAN}Подушка безопасности:{RESET}')
    print(f'  Накоплено: {pillow["current"]:>10.2f} ₽')
    print(f'  Цель:      {pillow["goal"]:>10.2f} ₽')
    if pillow['goal'] > 0:
        pct = (pillow['current'] / pillow['goal']) * 100
        width = 30
        filled = int((pillow['current'] / pillow['goal']) * width)
        bar = '█' * filled + '░' * (width - filled)
        print(f'  Прогресс:  {bar} {pct:.0f}%')

    print()
    while True:
        print(f'{BOLD}Действия:{RESET}')
        print(f'  1. Пополнить инвестиции')
        print(f'  2. Обновить текущую стоимость')
        print(f'  3. Обновить подушку')
        print(f'  4. Назад')
        choice = input('Выберите: ').strip()
        if choice == '1':
            _add_to_investments(data)
        elif choice == '2':
            _update_investment_value(data)
        elif choice == '3':
            _edit_pillow(data)
        elif choice == '4':
            break
        else:
            print('Неверный выбор')


def _add_to_investments(data):
    try:
        amount = float(input('Сколько добавить: '))
        if amount <= 0:
            print(f'{RED}Сумма должна быть положительной{RESET}')
            return
        data['investments']['total_invested'] += amount
        data['investments']['current_value'] += amount
        save(data)
        print(f'{GREEN}Добавлено {amount:.2f} ₽ в инвестиции{RESET}')
    except ValueError:
        print(f'{RED}Неверное число{RESET}')


def _update_investment_value(data):
    try:
        value = float(input(f'Текущая стоимость портфеля: '))
        if value < 0:
            print(f'{RED}Сумма не может быть отрицательной{RESET}')
            return
        data['investments']['current_value'] = value
        save(data)
        print(f'{GREEN}Текущая стоимость обновлена{RESET}')
    except ValueError:
        print(f'{RED}Неверное число{RESET}')


def _edit_pillow(data):
    try:
        goal = input(f'Цель подушки [{data["safety_pillow"]["goal"]:.2f}]: ').strip()
        if goal:
            data['safety_pillow']['goal'] = float(goal)
        cur = input(f'Накоплено [{data["safety_pillow"]["current"]:.2f}]: ').strip()
        if cur:
            data['safety_pillow']['current'] = float(cur)
        save(data)
        print(f'{GREEN}Подушка обновлена{RESET}')
    except ValueError:
        print(f'{RED}Неверное число{RESET}')




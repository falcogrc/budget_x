from collections import defaultdict
from config import GREEN, RED, YELLOW, CYAN, BOLD, RESET, clear_screen, current_month, today, bar_width, name_width
from storage import load, save
from transactions import _next_id, _get_date


def _bar(value, max_val, width=30):
    if max_val <= 0:
        return '░' * width
    ratio = min(value / max_val, 1.0)
    filled = int(ratio * width)
    return '█' * filled + '░' * (width - filled)


def _ensure_category(data, ttype, name):
    if name not in data['categories'][ttype]:
        data['categories'][ttype].append(name)
        save(data)


def _make_txn(data, ttype, category, amount, date=None):
    txn = {
        'id': _next_id(data),
        'type': ttype,
        'category': category,
        'amount': amount,
        'date': date or today(),
        'comment': '',
    }
    data['transactions'].append(txn)
    save(data)


def _choose_period():
    print(f'{BOLD}Период:{RESET}')
    print(f'  1. Текущий месяц')
    print(f'  2. Прошлый месяц')
    print(f'  3. Всё время')
    print(f'  4. Свой диапазон')
    choice = input('Выберите: ').strip()
    cur_month = current_month()
    y, m = cur_month.split('-')
    prev_month = f'{y}-{int(m)-1:02d}' if int(m) > 1 else f'{int(y)-1}-12'

    if choice == '1':
        return lambda t: t['date'].startswith(cur_month), cur_month
    elif choice == '2':
        return lambda t: t['date'].startswith(prev_month), prev_month
    elif choice == '4':
        start = input('Начало (ГГГГ-ММ): ').strip()
        end = input('Конец (ГГГГ-ММ, Enter=всё): ').strip()
        if end:
            return lambda t: t['date'] >= start and t['date'] <= end + '-31', f'{start} – {end}'
        return lambda t: t['date'] >= start, f'с {start}'
    else:
        return lambda t: True, 'всё время'


def show_statistics():
    clear_screen()
    data = load()
    period_filter, period_label = _choose_period()
    txns = [t for t in data['transactions'] if period_filter(t)]

    if not txns:
        print(f'{YELLOW}Нет операций за выбранный период{RESET}')
        return

    incomes = [t for t in txns if t['type'] == 'income']
    expenses = [t for t in txns if t['type'] == 'expense']
    savings = [t for t in txns if t['type'] == 'saving']
    total_income = sum(t['amount'] for t in incomes)
    total_expense = sum(t['amount'] for t in expenses)
    total_savings = sum(t['amount'] for t in savings)
    if len(txns) == len(data['transactions']):
        balance = data['initial_balance'] + total_income - total_expense - total_savings
    else:
        balance = total_income - total_expense - total_savings

    inv = data['investments']
    pillow = data['safety_pillow']

    print(f'{BOLD}📊 Статистика • {period_label}{RESET}\n')
    print(f'💰 Баланс: {GREEN if balance >= 0 else RED}{balance:,.2f} ₽{RESET}')
    print(f'📈 Доходы: {GREEN}{total_income:,.2f} ₽{RESET}')
    print(f'📉 Расходы: {RED}{total_expense:,.2f} ₽{RESET}')
    if total_savings > 0:
        print(f'🏦 Сбережения: {CYAN}{total_savings:,.2f} ₽{RESET}')
    if total_income > 0:
        pct = (total_expense / total_income) * 100
        print(f'📊 Норма расходов: {pct:.0f}% от дохода')

    print()
    if inv['total_invested'] > 0:
        pct = ((inv['current_value'] - inv['total_invested']) / inv['total_invested']) * 100
        color = GREEN if pct >= 0 else RED
        print(f'💼 Инвестиции: {inv["current_value"]:,.2f} ₽ (вложено {inv["total_invested"]:,.2f} ₽) {color}{pct:+.1f}%{RESET}')
    elif inv['current_value'] > 0:
        print(f'💼 Инвестиции: {inv["current_value"]:,.2f} ₽')

    if pillow['goal'] > 0:
        pct = (pillow['current'] / pillow['goal']) * 100
        bw = bar_width()
        filled = min(int((pillow['current'] / pillow['goal']) * bw), bw)
        bar = '█' * filled + '░' * (bw - filled)
        print(f'🛡️ Подушка: {pillow["current"]:,.2f} / {pillow["goal"]:,.2f} ₽ {bar} {pct:.0f}%')
    else:
        print(f'🛡️ Подушка: {pillow["current"]:,.2f} ₽')

    print()
    months = len(set(t['date'][:7] for t in expenses)) or 1
    _category_chart(incomes, 'Доходы по категориям', GREEN)
    _category_chart(expenses, 'Расходы по категориям', RED,
                    data.get('budgets', {}), months)
    _show_monthly_chart(txns)
    _show_balance_trend(txns)


def _category_chart(txns, title, color, budgets=None, months=1):
    if not txns:
        return
    print(f'{BOLD}{title}:{RESET}')
    cat_totals = defaultdict(float)
    for t in txns:
        cat_totals[t['category']] += t['amount']
    total = sum(cat_totals.values())
    bw = bar_width()
    nw = name_width()
    for cat, amount in sorted(cat_totals.items(), key=lambda x: -x[1]):
        suffix = ''
        if budgets and cat in budgets and budgets[cat] > 0:
            limit = budgets[cat]
            fact_avg = amount / months
            bar = _bar(fact_avg, limit, width=bw)
            pct = (fact_avg / limit) * 100
            flag = ' ✅' if pct <= 100 else ''
            bar_color = GREEN if pct <= 100 else RED
            suffix = f' {bar_color}{pct:.0f}%{flag} ({limit:,.0f}){RESET}'
        else:
            bar = _bar(amount, total, width=bw)
            pct = (amount / total) * 100
            suffix = f' {pct:.0f}%'
        print(f'  {cat:<{nw}} {color}{amount:>12,.2f}{RESET} {bar}{suffix}')
    print()


def _show_monthly_chart(txns):
    if not txns:
        return
    months_income = defaultdict(float)
    months_expense = defaultdict(float)
    months_savings = defaultdict(float)
    for t in txns:
        m = t['date'][:7]
        if t['type'] == 'income':
            months_income[m] += t['amount']
        elif t['type'] == 'expense':
            months_expense[m] += t['amount']
        else:
            months_savings[m] += t['amount']

    all_months = sorted(set(months_income) | set(months_expense) | set(months_savings))
    if len(all_months) < 1:
        return

    print(f'{BOLD}Динамика по месяцам:{RESET}')
    max_val = max(max(months_income.values(), default=0),
                  max(months_expense.values(), default=0))
    bw = bar_width()

    for m in all_months:
        inc = months_income.get(m, 0)
        exp = months_expense.get(m, 0)
        sav = months_savings.get(m, 0)
        print(f'  {m}')
        print(f'    {GREEN}█{RESET} {"доход":<7} {inc:>12,.2f} {_bar(inc, max_val, bw)}')
        print(f'    {RED}█{RESET} {"расход":<7} {exp:>12,.2f} {_bar(exp, max_val, bw)}')
        if sav > 0:
            print(f'    {CYAN}█{RESET} {"сбереж":<7} {sav:>12,.2f} {_bar(sav, max_val, bw)}')
    print()


def _show_balance_trend(txns):
    months = sorted(set(t['date'][:7] for t in txns))
    if len(months) < 2:
        return

    print(f'{BOLD}Баланс по месяцам (накопленный):{RESET}')
    monthly = defaultdict(float)
    for t in txns:
        m = t['date'][:7]
        if t['type'] == 'income':
            monthly[m] += t['amount']
        else:
            monthly[m] -= t['amount']

    cumulative = 0.0
    max_abs = max(abs(v) for v in monthly.values())
    bw = bar_width()
    for m in sorted(monthly):
        cumulative += monthly[m]
        color = GREEN if cumulative >= 0 else RED
        bar = _bar(abs(cumulative), max_abs, bw)
        print(f'  {m} {color}{cumulative:>12,.2f}{RESET} {bar}')
    print()


def show_investments():
    data = load()
    inv = data['investments']
    pillow = data['safety_pillow']

    print(f'{BOLD}💼 Инвестиции и 🛡️ Подушка безопасности{RESET}\n')

    print(f'{CYAN}Инвестиции:{RESET}')
    print(f'  Вложено всего:     {inv["total_invested"]:>12,.2f} ₽')
    print(f'  Текущая стоимость: {inv["current_value"]:>12,.2f} ₽')
    if inv['total_invested'] > 0:
        pct = ((inv['current_value'] - inv['total_invested']) / inv['total_invested']) * 100
        color = GREEN if pct >= 0 else RED
        print(f'  Доходность:        {color}{pct:+.2f}%{RESET}')
    else:
        print(f'  Доходность:        —')

    print()
    print(f'{CYAN}Подушка безопасности:{RESET}')
    print(f'  Накоплено: {pillow["current"]:>12,.2f} ₽')
    print(f'  Цель:      {pillow["goal"]:>12,.2f} ₽')
    if pillow['goal'] > 0:
        pct = (pillow['current'] / pillow['goal']) * 100
        bw = bar_width()
        filled = min(int((pillow['current'] / pillow['goal']) * bw), bw)
        bar = '█' * filled + '░' * (bw - filled)
        print(f'  Прогресс:  {bar} {pct:.0f}%')

    print()
    while True:
        print(f'{BOLD}Действия:{RESET}')
        print(f'  1. Пополнить инвестиции')
        print(f'  2. Обновить текущую стоимость')
        print(f'  3. Вывести из инвестиций')
        print(f'  4. Пополнить подушку')
        print(f'  5. Вывести из подушки')
        print(f'  6. Установить цель подушки')
        print(f'  7. Назад')
        choice = input('Выберите: ').strip()
        if not choice:
            continue
        if choice == '1':
            _add_to_investments(data)
        elif choice == '2':
            _update_investment_value(data)
        elif choice == '3':
            _withdraw_from_investments(data)
        elif choice == '4':
            _add_to_pillow(data)
        elif choice == '5':
            _withdraw_from_pillow(data)
        elif choice == '6':
            _set_pillow_goal(data)
        elif choice == '7':
            break
        else:
            print('Неверный выбор')


def _add_to_investments(data):
    try:
        amount = float(input('Сколько добавить: '))
        if amount <= 0:
            print(f'{RED}Сумма должна быть положительной{RESET}')
            return
        date = _get_date()
        data['investments']['total_invested'] += amount
        data['investments']['current_value'] += amount
        _make_txn(data, 'saving', 'Инвестиции', amount, date)
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


def _add_to_pillow(data):
    try:
        amount = float(input('Сколько добавить в подушку: '))
        if amount <= 0:
            print(f'{RED}Сумма должна быть положительной{RESET}')
            return
        date = _get_date()
        data['safety_pillow']['current'] += amount
        _make_txn(data, 'saving', 'Подушка', amount, date)
        print(f'{GREEN}Добавлено {amount:.2f} ₽ в подушку{RESET}')
    except ValueError:
        print(f'{RED}Неверное число{RESET}')


def _withdraw_from_investments(data):
    try:
        amount = float(input('Сколько вывести: '))
        if amount <= 0:
            print(f'{RED}Сумма должна быть положительной{RESET}')
            return
        inv = data['investments']
        if amount > inv['current_value']:
            print(f'{RED}Нельзя вывести больше, чем текущая стоимость ({inv["current_value"]:,.2f} ₽){RESET}')
            return
        inv['total_invested'] = max(0, inv['total_invested'] - amount)
        inv['current_value'] -= amount
        save(data)
        print(f'{GREEN}Выведено {amount:.2f} ₽ из инвестиций{RESET}')
    except ValueError:
        print(f'{RED}Неверное число{RESET}')


def _withdraw_from_pillow(data):
    try:
        amount = float(input('Сколько вывести из подушки: '))
        if amount <= 0:
            print(f'{RED}Сумма должна быть положительной{RESET}')
            return
        cur = data['safety_pillow']['current']
        if amount > cur:
            print(f'{RED}В подушке только {cur:,.2f} ₽{RESET}')
            return
        data['safety_pillow']['current'] -= amount
        save(data)
        print(f'{GREEN}Выведено {amount:.2f} ₽ из подушки{RESET}')
    except ValueError:
        print(f'{RED}Неверное число{RESET}')


def _set_pillow_goal(data):
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


def _set_balance(data):
    all_txns = data['transactions']
    all_income = sum(t['amount'] for t in all_txns if t['type'] == 'income')
    all_expense = sum(t['amount'] for t in all_txns if t['type'] == 'expense')
    all_savings = sum(t['amount'] for t in all_txns if t['type'] == 'saving')
    current_calc = data['initial_balance'] + all_income - all_expense - all_savings
    print(f'Текущий рассчитанный баланс: {current_calc:,.2f} ₽')
    try:
        inp = input(f'{BOLD}Введите реальный баланс: {RESET}').strip()
        if not inp:
            return
        real = float(inp)
        data['initial_balance'] = real - (all_income - all_expense - all_savings)
        save(data)
        print(f'{GREEN}Баланс установлен: {real:,.2f} ₽{RESET}')
    except ValueError:
        print(f'{RED}Неверное число{RESET}')

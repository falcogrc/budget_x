from config import GREEN, RED, YELLOW, CYAN, BOLD, RESET
from storage import load, save


def _show_categories(cats, label):
    print(f'{BOLD}{label}:{RESET}')
    for i, c in enumerate(cats, 1):
        print(f'  {YELLOW}{i}.{RESET} {c}')


def manage_categories():
    data = load()
    while True:
        print(f'{BOLD}Управление категориями:{RESET}')
        print(f'  1. Доходы ({len(data["categories"]["income"])})')
        print(f'  2. Расходы ({len(data["categories"]["expense"])})')
        print(f'  3. Назад')
        choice = input('Выберите: ').strip()
        if choice == '1':
            _edit_category_group(data, 'income')
        elif choice == '2':
            _edit_category_group(data, 'expense')
        elif choice == '3':
            break
        else:
            print(f'{RED}Неверный выбор{RESET}')


def _edit_category_group(data, ttype):
    label = 'Доходы' if ttype == 'income' else 'Расходы'
    cats = data['categories'][ttype]
    while True:
        _show_categories(cats, label)
        print(f'  {CYAN}д{RESET} — добавить')
        print(f'  {CYAN}р{RESET} — редактировать')
        print(f'  {CYAN}у{RESET} — удалить')
        print(f'  {CYAN}н{RESET} — назад')
        cmd = input('Команда: ').strip().lower()
        if cmd == 'д':
            name = input('Название категории: ').strip()
            if name:
                cats.append(name)
                save(data)
                print(f'{GREEN}Категория "{name}" добавлена{RESET}')
        elif cmd == 'р':
            try:
                idx = int(input('Номер категории: ')) - 1
                if 0 <= idx < len(cats):
                    new_name = input(f'Новое название [{cats[idx]}]: ').strip()
                    if new_name:
                        cats[idx] = new_name
                        save(data)
                        print(f'{GREEN}Категория обновлена{RESET}')
                else:
                    print(f'{RED}Неверный номер{RESET}')
            except ValueError:
                print(f'{RED}Неверный ввод{RESET}')
        elif cmd == 'у':
            try:
                idx = int(input('Номер категории: ')) - 1
                if 0 <= idx < len(cats):
                    removed = cats.pop(idx)
                    save(data)
                    print(f'{RED}Категория "{removed}" удалена{RESET}')
                else:
                    print(f'{RED}Неверный номер{RESET}')
            except ValueError:
                print(f'{RED}Неверный ввод{RESET}')
        elif cmd == 'н':
            break

# Импортирт необходимых библиотек
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime

#  переменные глобальные
DATA_FILE = "itogi_expenses.json"
DEFAULT_CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Жилье", "Здоровье", "Прочее"]
expenses = []

# Функции для работы с данными
def load_data():
    """Загружает расходы из файла JSON"""
    global expenses
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    expenses = data
    except Exception as e:
        messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить данные: {e}")
        expenses = []


def save_data():
    """Сохраняет расходы в файл JSON."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(expenses, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")

# Функции для интерфейса
def validate_input():
    """Проверяет корректность введенной суммы."""
    amount_str = amount_entry.get().replace(',', '.')
    try:
        amount = float(amount_str)
        if amount <= 0:
            messagebox.showerror("Ошибка", "Сумма должна быть больше нуля.")
            return None
        return amount
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректное число для суммы.")
        return None


def add_expense():
    """Добавляет новый расход в список и обновляет таблицу."""
    amount = validate_input()
    if amount is None:
        return

    category = category_entry.get()
    if not category:
        messagebox.showerror("Ошибка", "Выберите категорию.")
        return

    date_str = date_entry.get_date().strftime('%d.%m.%Y')

    expense_id = len(expenses) + 1

    new_expense = {
        "id": expense_id,
        "date": date_str,
        "category": category,
        "amount": round(amount, 2)
    }

    expenses.append(new_expense)
    save_data()
    update_table()

    # Очистка полей после добавления
    amount_entry.delete(0, tk.END)


def delete_selected():
    """Удаляет выбранные в таблице расходы."""
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning("Предупреждение", "Выберите запись для удаления.")
        return

    if messagebox.askyesno("Удалить?", "Удалить выбранные расходы?"):
        for item_id in selected_items:
            expense_id = int(tree.item(item_id)['values'][0])
            # Находим и удаляем из списка
            for i, exp in enumerate(expenses):
                if exp['id'] == expense_id:
                    del expenses[i]
                    break
        save_data()
        update_table()


def apply_filter():
    """Фильтрует и отображает расходы согласно выбранным критериям."""
    filtered_expenses = []

    start_date = start_date_picker.get_date()
    end_date = end_date_picker.get_date()

    selected_category = category_filter.get()

    for exp in expenses:
        exp_date = datetime.strptime(exp['date'], '%d.%m.%Y')

        in_range = start_date <= exp_date <= end_date
        cat_match = (selected_category == "Все") or (exp['category'] == selected_category)

        if in_range and cat_match:
            filtered_expenses.append(exp)

    display_expenses(filtered_expenses)
    calculate_and_show_sum(filtered_expenses)


def update_table():
    """Обновляет таблицу всеми расходами и сбрасывает фильтры на текущий месяц."""
    display_expenses(expenses)

    # Сброс фильтров на текущий месяц по умолчанию
    today = datetime.now()
    start_of_month = today.replace(day=1)

    start_date_picker.set_date(start_of_month)
    end_date_picker.set_date(today)

    calculate_and_show_sum(expenses)


def display_expenses(data):
    """Отображает переданный список расходов в таблице."""
    for i in tree.get_children():
        tree.delete(i)

    for exp in data:
        values = (exp['id'], exp['date'], exp['category'], f"{exp['amount']:.2f} ₽")
        tree.insert("", tk.END, values=values)


def calculate_and_show_sum(data):
    """Вычисляет сумму расходов и выводит ее на экран."""
    total_sum = sum(exp['amount'] for exp in data)
    sum_label.config(text=f"Сумма за период: {total_sum:.2f} ₽")


# Создание главного окна
window = tk.Tk()
window.title("Трекер расходов")
window.geometry("800x500")

# Загрузка данных при старте
load_data()

# Левая панель: Фильтры и Добавление
left_frame = ttk.Frame(window, padding="10")
left_frame.pack(side=tk.LEFT, fill=tk.Y)

# Фильтр по дате (Период)
ttk.Label(left_frame, text="Период:").pack(anchor='w')
start_date_picker = DateEntry(left_frame, width=12, background='darkblue',
                              foreground='white', borderwidth=2, date_pattern='dd.mm.y')
start_date_picker.pack(pady=5)
end_date_picker = DateEntry(left_frame, width=12, background='darkblue',
                            foreground='white', borderwidth=2, date_pattern='dd.mm.y')
end_date_picker.pack(pady=5)
ttk.Button(left_frame, text="Применить фильтр", command=apply_filter).pack(pady=5)

# Фильтр по категории
ttk.Label(left_frame, text="Категория:").pack(anchor='w')
category_filter = ttk.Combobox(left_frame, values=["Все"] + DEFAULT_CATEGORIES,
                               state="readonly", width=15)
category_filter.current(0)  # Выбрать "Все"
category_filter.pack(pady=5)

# Поля для добавления расхода
ttk.Label(left_frame, text="Добавить расход",
           foreground="darkblue",  # цвет текста — тёмно‑синий
           font=("Arial", 14, "bold")).pack(pady=(15, 0))

add_frame = ttk.Frame(left_frame)
add_frame.pack(fill=tk.X)

ttk.Label(add_frame, text="Сумма:",
           foreground="#2c3e50",  # тёмно‑серый цвет текста
           font=("Arial", 10)).grid(row=0, column=0, padx=5)
amount_entry = ttk.Entry(add_frame, width=15)
amount_entry.grid(row=0, column=1, padx=5)
amount_entry.focus()  # Фокус на поле ввода суммы

ttk.Label(add_frame, text="Категория:",
           foreground="#2c3e50",
           font=("Arial", 10)).grid(row=1, column=0, padx=5)
category_entry = ttk.Combobox(add_frame, values=DEFAULT_CATEGORIES,
                              state="readonly", width=13)
category_entry.grid(row=1, column=1, padx=5)
category_entry.current(0)  # Выбрать первую категорию по умолчанию

ttk.Label(add_frame, text="Дата:",
           foreground="#2c3e50",
           font=("Arial", 10)).grid(row=2, column=0, padx=5)
date_entry = DateEntry(add_frame, width=13,
                       background='darkblue', foreground='white',
                       borderwidth=2, date_pattern='dd.mm.y')
date_entry.grid(row=2, column=1, padx=5)
date_entry.set_date(datetime.now())  # Текущая дата по умолчанию

ttk.Button(left_frame,
           text="Добавить расход",
           command=add_expense).pack(pady=10)

# Правая панель: Таблица и Сумма
right_frame = ttk.Frame(window)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Таблица расходов (Treeview)
cols = ("ID", "Дата", "Категория", "Сумма")
tree = ttk.Treeview(right_frame, columns=cols, show="headings")
for col in cols:
    tree.heading(col, text=col)
tree.column("ID", width=40, anchor="center")
tree.column("Дата", width=120, anchor="center")
tree.column("Категория", width=150, anchor="center")
tree.column("Сумма", width=100, anchor="center")
tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

# Кнопка удаления и сумма
btn_frame = ttk.Frame(right_frame)
btn_frame.pack()
ttk.Button(btn_frame,
           text="Удалить выбранное",
           command=delete_selected).pack(side=tk.LEFT)

sum_label = ttk.Label(right_frame, text="Сумма за период: 0 ₽", font=("Arial", 12))
sum_label.pack(pady=(0, 10))

# Запуск обновления таблицы при старте приложения
update_table()

window.mainloop()

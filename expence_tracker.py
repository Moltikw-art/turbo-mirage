import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "expenses.json"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Трекер расходов")
        self.root.geometry("900x600")

        self.expenses = []
        self.load_data()

        # Рамка для добавления расхода
        input_frame = tk.LabelFrame(root, text="Добавить расход", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        tk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.amount_entry = tk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # Категория
        tk.Label(input_frame, text="Категория:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.category_var = tk.StringVar()
        categories = ["Еда", "Транспорт", "Развлечения", "Покупки", "Счета", "Здоровье", "Другое"]
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, values=categories, width=15)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.current(0)

        # Дата
        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.date_entry = tk.Entry(input_frame, width=12)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Кнопка добавления
        self.add_btn = tk.Button(input_frame, text="Добавить расход", command=self.add_expense, bg="green", fg="white")
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)

        # Рамка фильтрации
        filter_frame = tk.LabelFrame(root, text="Фильтрация расходов", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Категория:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.filter_category_var = tk.StringVar()
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, values=["Все"] + categories, width=15)
        self.filter_category_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_category_combo.current(0)

        tk.Label(filter_frame, text="Дата с (ГГГГ-ММ-ДД):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.from_date_entry = tk.Entry(filter_frame, width=12)
        self.from_date_entry.grid(row=0, column=3, padx=5, pady=5)
        self.from_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(filter_frame, text="Дата по (ГГГГ-ММ-ДД):").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.to_date_entry = tk.Entry(filter_frame, width=12)
        self.to_date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.to_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        self.filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.filter_btn.grid(row=0, column=6, padx=10, pady=5)

        self.reset_filter_btn = tk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        self.reset_filter_btn.grid(row=0, column=7, padx=5, pady=5)

        # Рамка суммы
        sum_frame = tk.Frame(root)
        sum_frame.pack(fill="x", padx=10, pady=5)
        self.sum_label = tk.Label(sum_frame, text="Общая сумма за период: 0.00", font=("Arial", 12, "bold"))
        self.sum_label.pack(side="left")

        # Таблица
        columns = ("ID", "Amount", "Category", "Date")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Amount", text="Сумма (€)")
        self.tree.heading("Category", text="Категория")
        self.tree.heading("Date", text="Дата")
        self.tree.column("ID", width=50)
        self.tree.column("Amount", width=100)
        self.tree.column("Category", width=150)
        self.tree.column("Date", width=120)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Кнопка удаления
        self.delete_btn = tk.Button(root, text="Удалить выбранное", command=self.delete_expense, bg="red", fg="white")
        self.delete_btn.pack(pady=5)

        self.refresh_table()

    def validate_date(self, date_str):
        """Проверка формата даты ГГГГ-ММ-ДД"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_expense(self):
        # Проверка суммы
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Сумма должна быть положительным числом.")
            return

        # Проверка категории
        category = self.category_var.get().strip()
        if not category:
            messagebox.showerror("Ошибка ввода", "Выберите категорию.")
            return

        # Проверка даты
        date_str = self.date_entry.get().strip()
        if not self.validate_date(date_str):
            messagebox.showerror("Ошибка ввода", "Дата должна быть в формате ГГГГ-ММ-ДД\nПример: 2026-04-27")
            return

        # Добавление расхода
        new_id = max([e["id"] for e in self.expenses], default=0) + 1
        self.expenses.append({
            "id": new_id,
            "amount": amount,
            "category": category,
            "date": date_str
        })
        self.save_data()
        self.refresh_table()
        self.amount_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", "Расход успешно добавлен!")

    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ничего не выбрано", "Выберите расход для удаления.")
            return
        item = self.tree.item(selected[0])
        expense_id = item["values"][0]
        self.expenses = [e for e in self.expenses if e["id"] != expense_id]
        self.save_data()
        self.refresh_table()
        self.apply_filter()

    def apply_filter(self):
        category_filter = self.filter_category_var.get()
        from_date = self.from_date_entry.get().strip()
        to_date = self.to_date_entry.get().strip()

        filtered = self.expenses[:]

        # Фильтр по категории
        if category_filter != "Все":
            filtered = [e for e in filtered if e["category"] == category_filter]

        # Фильтр по дате (с проверкой формата)
        if from_date and self.validate_date(from_date):
            filtered = [e for e in filtered if e["date"] >= from_date]
        elif from_date and not self.validate_date(from_date):
            messagebox.showwarning("Ошибка формата", f"Дата 'с' имеет неверный формат: {from_date}\nИспользуйте ГГГГ-ММ-ДД")

        if to_date and self.validate_date(to_date):
            filtered = [e for e in filtered if e["date"] <= to_date]
        elif to_date and not self.validate_date(to_date):
            messagebox.showwarning("Ошибка формата", f"Дата 'по' имеет неверный формат: {to_date}\nИспользуйте ГГГГ-ММ-ДД")

        # Подсчёт суммы
        total = sum(e["amount"] for e in filtered)
        self.sum_label.config(text=f"Общая сумма за период: {total:.2f} €")

        # Обновление таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)
        for exp in filtered:
            self.tree.insert("", tk.END, values=(exp["id"], exp["amount"], exp["category"], exp["date"]))

    def reset_filter(self):
        self.filter_category_var.set("Все")
        today = datetime.now().strftime("%Y-%m-%d")
        self.from_date_entry.delete(0, tk.END)
        self.from_date_entry.insert(0, today)
        self.to_date_entry.delete(0, tk.END)
        self.to_date_entry.insert(0, today)
        self.refresh_table()

    def refresh_table(self):
        # Сброс фильтров
        self.filter_category_var.set("Все")
        today = datetime.now().strftime("%Y-%m-%d")
        self.from_date_entry.delete(0, tk.END)
        self.from_date_entry.insert(0, today)
        self.to_date_entry.delete(0, tk.END)
        self.to_date_entry.insert(0, today)

        # Подсчёт общей суммы
        total_all = sum(e["amount"] for e in self.expenses)
        self.sum_label.config(text=f"Общая сумма за период: {total_all:.2f} €")

        # Обновление таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)
        for exp in self.expenses:
            self.tree.insert("", tk.END, values=(exp["id"], exp["amount"], exp["category"], exp["date"]))

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, indent=4, ensure_ascii=False)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.expenses = []

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()

import tkinter as tk
from tkinter import messagebox, simpledialog
import calendar, datetime, os, json

DATA_FILE = "data/expenses.json"

# ---------------- Data Handling ----------------
def init_data():
    if not os.path.exists("data"):
        os.mkdir("data")
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------- Features ----------------
def set_monthly_budget(year, month):
    data = load_data()
    key = f"{year}-{month}"
    if key not in data:
        data[key] = {"budget": 0, "transactions": {}}

    budget = simpledialog.askfloat("Set Budget", f"Enter budget for {key}:")
    if budget is not None:
        data[key]["budget"] = budget
        save_data(data)
        messagebox.showinfo("Budget Set", f"Monthly budget set to ₹{budget}")

def add_entry(year, month, day, entry_type):
    data = load_data()
    key = f"{year}-{month}"
    date_key = f"{year}-{month:02d}-{day:02d}"

    if key not in data:
        data[key] = {"budget": 0, "transactions": {}}

    category = simpledialog.askstring("Category", "Enter category:")
    amount = simpledialog.askfloat("Amount", "Enter amount:")
    if not category or not amount:
        return

    entry = {"type": entry_type, "category": category, "amount": amount}
    data[key]["transactions"].setdefault(date_key, []).append(entry)
    save_data(data)
    messagebox.showinfo("Saved", f"Added {entry_type}: {category} ₹{amount} on {date_key}")

def view_date_expenses(year, month, day):
    data = load_data()
    key = f"{year}-{month}"
    date_key = f"{year}-{month:02d}-{day:02d}"

    if key not in data or date_key not in data[key]["transactions"] or not data[key]["transactions"][date_key]:
        choice = messagebox.askquestion("No Expenses", f"No entries on {date_key}. Add one?")
        if choice == "yes":
            add_entry(year, month, day, "Expense")
        return

    expenses = data[key]["transactions"][date_key]
    text = "\n".join([f"{e['type']} - {e['category']}: ₹{e['amount']}" for e in expenses])
    choice = messagebox.askquestion("Expenses", f"Entries on {date_key}:\n{text}\n\nAdd more?")
    if choice == "yes":
        add_entry(year, month, day, "Expense")

def monthly_summary(year, month):
    data = load_data()
    key = f"{year}-{month}"
    if key not in data:
        messagebox.showinfo("Summary", "No data for this month.")
        return

    budget = data[key].get("budget", 0)
    transactions = data[key].get("transactions", {})
    income = sum(e["amount"] for day in transactions.values() for e in day if e["type"] == "Income")
    expense = sum(e["amount"] for day in transactions.values() for e in day if e["type"] == "Expense")
    savings = income - expense
    balance = budget - expense

    summary = f"Budget: ₹{budget}\nIncome: ₹{income}\nExpense: ₹{expense}\nSavings: ₹{savings}\nBalance Left: ₹{balance}"
    messagebox.showinfo("Monthly Summary", summary)

# ---------------- Calendar ----------------
def show_calendar():
    for widget in cal_frame.winfo_children():
        widget.destroy()

    year = int(year_entry.get())
    month = int(month_entry.get())
    cal = calendar.monthcalendar(year, month)

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for col, day in enumerate(days):
        tk.Label(cal_frame, text=day, font=("Arial", 10, "bold"), bg="#d3d3f3", width=6).grid(row=0, column=col)

    for row, week in enumerate(cal, start=1):
        for col, day in enumerate(week):
            if day == 0:
                tk.Label(cal_frame, text="", width=6, bg="#f0f0f0").grid(row=row, column=col)
            else:
                btn = tk.Button(cal_frame, text=str(day), width=6, bg="#a8dadc",
                                command=lambda d=day: view_date_expenses(year, month, d))
                btn.grid(row=row, column=col, padx=2, pady=2)

# ---------------- UI ----------------
root = tk.Tk()
root.title("Wallet Watch - Budget Tracker")
root.geometry("500x500")
root.configure(bg="#f0f4f8")

tk.Label(root, text="Wallet Watch", font=("Arial", 16, "bold"), bg="#f0f4f8").pack(pady=10)

tk.Label(root, text="Enter Year:", bg="#f0f4f8").pack()

year_entry = tk.Entry(root)
year_entry.insert(0, str(datetime.datetime.now().year))
year_entry.pack()

tk.Label(root, text="Enter Month (1-12):", bg="#f0f4f8").pack()
month_entry = tk.Entry(root)
month_entry.insert(0, str(datetime.datetime.now().month))
month_entry.pack()

tk.Button(root, text="Show Calendar", command=show_calendar, bg="#1d3557", fg="white").pack(pady=5)
tk.Button(root, text="Set Monthly Budget", command=lambda: set_monthly_budget(int(year_entry.get()), int(month_entry.get())), bg="#e63946", fg="white").pack(pady=5)
tk.Button(root, text="Monthly Summary", command=lambda: monthly_summary(int(year_entry.get()), int(month_entry.get())), bg="#2a9d8f", fg="white").pack(pady=5)

cal_frame = tk.Frame(root, bg="#f0f4f8")
cal_frame.pack() 
init_data()
root.mainloop()


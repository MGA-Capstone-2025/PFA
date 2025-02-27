# FileName: PersonalFinanceApp.py
# Author: Section 2, Team 1 (Zachary Henderson, Nicholas Gray, Brian Tucker, Cristabelle Espada, Taylor Clark)
# Course: 22698 ITEC 4750-02 - Senior Capstone
# Term: Spring 2025
# Instructor: Dr. Neil Rigole
# University: Middle Georgia State University
# Date: 2025-01-28
# Description: A personal finance app to help track income/expenses.

# Dependencies:
#   - Python (https://www.python.org/downloads/)
#   - Matplotlib (pip install matplotlib)

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import hashlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches

# Database setup
DB_NAME = "finance_manager.db"


def initialize_db():
    """Initialize the SQLite database and create required tables."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # Create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)
        # Create transactions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            category TEXT,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
    conn.close()

# Hash a password


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Add a new user to the database


def create_user(username, password):
    try:
        hashed_password = hash_password(password)
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# Verify user credentials


def verify_user(username, password):
    hashed_password = hash_password(password)
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        result = cursor.fetchone()
        if result:
            return result[0]  # Return user ID
    return None

# Add a transaction to the database


def add_transaction(user_id, amount, description, category):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO transactions (user_id, amount, description, category, date)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, amount, description, category, datetime.datetime.now().isoformat()))
        conn.commit()

# Load transactions for a user


def load_transactions(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT amount, description, category, date FROM transactions WHERE user_id = ?
        ORDER BY date DESC
        """, (user_id,))
        return cursor.fetchall()

# Load category breakdown


def load_category_breakdown(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT category, SUM(amount) FROM transactions WHERE user_id = ?
        GROUP BY category
        """, (user_id,))
        return cursor.fetchall()

# Calculate total balance for a user


def calculate_total_balance(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT SUM(amount) FROM transactions WHERE user_id = ?
        """, (user_id,))
        result = cursor.fetchone()
        return result[0] if result[0] else 0


def delete_transaction():
    """
    Deletes the selected transaction from the database.
    """
    selected_item = statement_tree.selection()  # Get selected row
    if not selected_item:
        messagebox.showerror("Error", "No transaction selected.")
        return

    # Retrieve transaction details from the selected row
    values = statement_tree.item(selected_item, "values")
    if not values:
        messagebox.showerror(
            "Error", "Unable to retrieve transaction details.")
        return

    # Extract details
    amount = float(values[0].replace("$", "").replace(",", ""))
    description = values[1]
    category = values[2]
    date = values[3]

    # Delete the transaction from the database
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM transactions
        WHERE user_id = ? AND amount = ? AND description = ? AND category = ? AND date = ?
        """, (logged_in_user_id, amount, description, category, date))
        conn.commit()

    # Update the statement view
    update_statement()
    messagebox.showinfo("Success", "Transaction deleted successfully.")

# Logout function


def logout():
    global logged_in_user_id
    logged_in_user_id = None
    username_var.set("")
    password_var.set("")
    show_login_screen()

# Main screen


def show_main_screen():
    for widget in root.winfo_children():
        widget.destroy()

    # Add a logout button
    logout_button = tk.Button(root, text="Logout", command=logout,
                              bg="darkred", fg="white", font=("Arial", 14), padx=10, pady=5)
    logout_button.pack(anchor="ne", padx=10, pady=10)

    notebook = ttk.Notebook(root, style="CustomNotebook.TNotebook")
    notebook.pack(pady=10, padx=10, expand=True, fill="both")

    # Income Tab
    income_tab = ttk.Frame(notebook)
    notebook.add(income_tab, text="Income")
    tk.Label(income_tab, text="Income Amount:",
             font=custom_font).pack(anchor="w")
    tk.Entry(income_tab, textvariable=income_amount_var,
             width=20, font=custom_font).pack(anchor="w")
    tk.Label(income_tab, text="Description:",
             font=custom_font).pack(anchor="w")
    tk.Entry(income_tab, textvariable=income_description_var,
             width=40, font=custom_font).pack(anchor="w")
    tk.Label(income_tab, text="Category:", font=custom_font).pack(anchor="w")
    for cat, var in income_categories.items():
        tk.Checkbutton(income_tab, text=cat, variable=var,
                       font=custom_font).pack(anchor="w")
    tk.Button(income_tab, text="Add Income", command=add_income, bg="green",
              fg="white", font=custom_font, padx=5, pady=5).pack(pady=10)

    # Expense Tab
    expense_tab = ttk.Frame(notebook)
    notebook.add(expense_tab, text="Expenses")
    tk.Label(expense_tab, text="Amount:", font=custom_font).pack(anchor="w")
    tk.Entry(expense_tab, textvariable=expense_amount_var,
             width=20, font=custom_font).pack(anchor="w")
    tk.Label(expense_tab, text="Description:",
             font=custom_font).pack(anchor="w")
    tk.Entry(expense_tab, textvariable=expense_description_var,
             width=40, font=custom_font).pack(anchor="w")
    tk.Label(expense_tab, text="Category:", font=custom_font).pack(anchor="w")
    for cat, var in expense_categories.items():
        tk.Checkbutton(expense_tab, text=cat, variable=var,
                       font=custom_font).pack(anchor="w")
    tk.Button(expense_tab, text="Add Expense", command=add_expense,
              bg="darkred", fg="white", font=custom_font, padx=5, pady=5).pack(pady=10)

    # Statement Tab
    statement_tab = ttk.Frame(notebook)
    notebook.add(statement_tab, text="Statement")
    tk.Label(statement_tab, textvariable=total_balance_var,
             font=("Arial", 14)).pack(pady=10)
    global statement_tree
    statement_tree = ttk.Treeview(statement_tab, columns=(
        "Amount", "Description", "Category", "Date"), show="headings", style="Custom.Treeview")
    statement_tree.heading("Amount", text="Amount")
    statement_tree.heading("Description", text="Description")
    statement_tree.heading("Category", text="Category")
    statement_tree.heading("Date", text="Date")
    statement_tree.column("Amount", width=100)
    statement_tree.column("Description", width=200)
    statement_tree.column("Category", width=150)
    statement_tree.column("Date", width=150)
    statement_tree.pack(pady=10, fill="both", expand=True)

    # Add Delete Button
    delete_button = tk.Button(statement_tab, text="Delete Selected", command=delete_transaction,
                              bg="darkred", fg="white", font=custom_font, padx=5, pady=5)
    delete_button.pack(pady=10)

    update_statement()

    # Breakdown Tab
    breakdown_tab = ttk.Frame(notebook)
    notebook.add(breakdown_tab, text="Breakdown")

    # Automatically update pie chart when Breakdown tab is clicked
    def on_tab_changed(event):
        selected_tab = event.widget.index("current")
        if notebook.tab(selected_tab, "text") == "Breakdown":
            generate_pie_chart(breakdown_tab)

    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)


def update_statement():
    """
    Updates the statement tree view with transactions.
    """
    for row in statement_tree.get_children():
        statement_tree.delete(row)

    transactions = load_transactions(logged_in_user_id)
    total_balance = calculate_total_balance(logged_in_user_id)
    total_balance_var.set(f"Total Balance: ${total_balance:,.2f}")

    for amount, description, category, date in transactions:
        formatted_amount = f"+${amount:,.2f}" if amount > 0 else f"-${abs(amount):,.2f}"
        color = "green" if amount > 0 else "red"
        statement_tree.insert("", "end", values=(
            formatted_amount, description, category, date), tags=(color,))
    statement_tree.tag_configure("green", foreground="green")
    statement_tree.tag_configure("red", foreground="red")


def generate_pie_chart(parent):
    for widget in parent.winfo_children():
        widget.destroy()  # Clear previous content

    # Load breakdown and split into income and expenses
    breakdown = load_category_breakdown(logged_in_user_id)
    income_categories = [item[0] for item in breakdown if item[1] > 0]
    income_amounts = [item[1] for item in breakdown if item[1] > 0]
    expense_categories = [item[0] for item in breakdown if item[1] < 0]
    expense_amounts = [abs(item[1]) for item in breakdown if item[1] < 0]

    # Check if there's data to display
    if not income_categories and not expense_categories:
        tk.Label(parent, text="No data available for chart.",
                 font=("Arial", 12), fg="darkred").pack()
        return

    fig = Figure(figsize=(10, 5), dpi=100)
    ax1 = fig.add_subplot(121)  # Left pie chart for income
    ax2 = fig.add_subplot(122)  # Right pie chart for expenses

    def on_click(event, labels, ax, chart_type):
        # Determine which pie slice was clicked
        wedges = [w for w in ax.patches if isinstance(
            w, matplotlib.patches.Wedge)]
        for wedge, label in zip(wedges, labels):
            if wedge.contains_point((event.x, event.y)):
                show_details_popup(label, chart_type)
                break

    # Income Pie Chart
    if income_categories:
        wedges1, texts1, autotexts1 = ax1.pie(
            income_amounts, labels=income_categories, autopct="%1.1f%%", startangle=140)
        ax1.set_title("Income Breakdown")

        def income_click(event):
            on_click(event, income_categories, ax1, "Income")

        fig.canvas.mpl_connect("button_press_event", income_click)
    else:
        ax1.text(0.5, 0.5, "No Income Data", ha="center",
                 va="center", fontsize=12, color="gray")

    # Expense Pie Chart
    if expense_categories:
        wedges2, texts2, autotexts2 = ax2.pie(
            expense_amounts, labels=expense_categories, autopct="%1.1f%%", startangle=140)
        ax2.set_title("Expense Breakdown")

        def expense_click(event):
            on_click(event, expense_categories, ax2, "Expense")

        fig.canvas.mpl_connect("button_press_event", expense_click)
    else:
        ax2.text(0.5, 0.5, "No Expense Data", ha="center",
                 va="center", fontsize=12, color="gray")

    # Render the figure in the Tkinter application
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack()


def show_details_popup(category, chart_type):
    """
    Display a popup with details for the selected category in a grid format.
    """
    popup = tk.Toplevel(root)
    popup.title(f"{chart_type} Details - {category}")
    popup.geometry("800x400")

    # Frame for the treeview
    frame = tk.Frame(popup)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Treeview widget
    tree = ttk.Treeview(frame, columns=(
        "Amount", "Description", "Date"), show="headings", style="Custom.Treeview")
    tree.heading("Amount", text="Amount",
                 command=lambda: sort_tree(tree, "Amount", False))
    tree.heading("Description", text="Description",
                 command=lambda: sort_tree(tree, "Description", False))
    tree.heading("Date", text="Date",
                 command=lambda: sort_tree(tree, "Date", False))
    tree.column("Amount", anchor="center", width=100)
    tree.column("Description", anchor="w", width=250)
    tree.column("Date", anchor="center", width=150)
    tree.pack(fill="both", expand=True, side="left")

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Load transactions for the selected category
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT amount, description, date FROM transactions
        WHERE user_id = ? AND category = ?
        """, (logged_in_user_id, category))
        transactions = cursor.fetchall()

    # Populate the treeview
    for amount, description, date in transactions:
        formatted_amount = f"+${amount:,.2f}" if amount > 0 else f"-${abs(amount):,.2f}"
        tree.insert("", "end", values=(formatted_amount, description, date))

    # Close button
    close_button = tk.Button(popup, text="Close", command=popup.destroy,
                             bg="darkred", fg="white", font=custom_font)
    close_button.pack(pady=10)


def sort_tree(tree, column, reverse):
    """
    Sort the treeview by the specified column.
    """
    data = [(tree.set(child, column), child)
            for child in tree.get_children("")]

    # Sort data based on the column type (numbers vs text)
    if column == "Amount":
        data.sort(key=lambda t: float(t[0].replace("$", "").replace(
            ",", "").replace("+", "").replace("-", "")), reverse=reverse)
    else:
        data.sort(key=lambda t: t[0], reverse=reverse)

    # Rearrange items in sorted order
    for index, (value, child) in enumerate(data):
        tree.move(child, "", index)

    # Reverse the sort order for the next click
    tree.heading(column, command=lambda: sort_tree(tree, column, not reverse))


def add_income():
    try:
        amount = float(income_amount_var.get())
        description = income_description_var.get()
        category = ", ".join(
            [cat for cat, var in income_categories.items() if var.get()])
        if amount > 0 and description and category:
            add_transaction(logged_in_user_id, amount, description, category)
            update_statement()
            income_amount_var.set("")
            income_description_var.set("")
            for var in income_categories.values():
                var.set(False)
        else:
            messagebox.showerror("Error", "Please fill in all fields.")
    except ValueError:
        messagebox.showerror("Error", "Invalid amount.")


def add_expense():
    try:
        amount = float(expense_amount_var.get())
        description = expense_description_var.get()
        category = ", ".join(
            [cat for cat, var in expense_categories.items() if var.get()])
        if amount > 0 and description and category:
            add_transaction(logged_in_user_id, -amount, description, category)
            update_statement()
            expense_amount_var.set("")
            expense_description_var.set("")
            for var in expense_categories.values():
                var.set(False)
        else:
            messagebox.showerror("Error", "Please fill in all fields.")
    except ValueError:
        messagebox.showerror("Error", "Invalid amount.")


def show_login_screen():
    for widget in root.winfo_children():
        widget.destroy()

    frame = tk.Frame(root, pady=20)
    frame.pack(expand=True)

    tk.Label(frame, text="Welcome to Personal Finance Manager",
             font=("Arial", 18, "bold")).pack(pady=10)
    tk.Label(frame, text="Username:", font=custom_font).pack(pady=5)
    tk.Entry(frame, textvariable=username_var,
             width=30, font=custom_font).pack()

    tk.Label(frame, text="Password:", font=custom_font).pack(pady=5)
    tk.Entry(frame, textvariable=password_var, show="*",
             width=30, font=custom_font).pack()

    tk.Button(frame, text="Login", command=login, font=custom_font,
              bg="blue", fg="white", width=15).pack(pady=10)
    tk.Button(frame, text="Register", command=register,
              font=custom_font, bg="green", fg="white", width=15).pack()


def login():
    global logged_in_user_id
    username = username_var.get()
    password = password_var.get()
    user_id = verify_user(username, password)
    if user_id:
        logged_in_user_id = user_id
        show_main_screen()
    else:
        messagebox.showerror("Error", "Invalid username or password.")


def register():
    username = username_var.get()
    password = password_var.get()
    if create_user(username, password):
        messagebox.showinfo("Success", "Account created successfully!")
        show_login_screen()
    else:
        messagebox.showerror("Error", "Username already exists.")


def main():
    # Initialize database and GUI
    initialize_db()

    root = tk.Tk()
    root.title("Personal Finance Manager")
    root.geometry("1000x600")

    # Set custom style for notebooks
    style = ttk.Style()
    style.configure("CustomNotebook.TNotebook.Tab",
                    font=("Arial", 12), padding=[10, 5])
    style.configure("Custom.Treeview", font=("Arial", 12))
    style.configure("Custom.Treeview.Heading", font=("Arial", 12, "bold"))
    custom_font = ("Arial", 12)

    username_var = tk.StringVar()
    password_var = tk.StringVar()
    total_balance_var = tk.StringVar(value="Total Balance: $0.00")
    income_amount_var = tk.StringVar()
    income_description_var = tk.StringVar()
    income_categories = {"Pay": tk.BooleanVar(), "Other": tk.BooleanVar(
    ), "Bonus": tk.BooleanVar(), "Investment": tk.BooleanVar()}
    expense_amount_var = tk.StringVar()
    expense_description_var = tk.StringVar()
    expense_categories = {"Bills": tk.BooleanVar(), "Subscriptions": tk.BooleanVar(
    ), "Groceries": tk.BooleanVar(), "Entertainment": tk.BooleanVar(), "Travel": tk.BooleanVar()}

    logged_in_user_id = None

    show_login_screen()
    root.mainloop()


if __name__ == "__main__":
    main()

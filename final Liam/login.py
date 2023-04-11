# login.py
import json
import os
import sqlite3
from tkinter import *
from tkinter import messagebox, ttk

import product_manager

# Use arc theme
from ttkthemes import ThemedTk

# Check if accounts.json exists, if not, create it
if not os.path.isfile("accounts.json"):
    with open("accounts.json", "w") as f:
        json.dump([], f)

# Function to load accounts from the JSON file


def load_accounts():
    with open("accounts.json", "r") as f:
        return json.load(f)

# Function to save accounts to the JSON file


def save_accounts(accounts):
    with open("accounts.json", "w") as f:
        json.dump(accounts, f)

# Function to authenticate a user


def authenticate(username, password):
    accounts = load_accounts()
    for account in accounts:
        if account["username"] == username and account["password"] == password:
            return account
    return None

# Function to create a new account and store it in the JSON file


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x_coordinate = int((screen_width / 2) - (width / 2))
    y_coordinate = int((screen_height / 2) - (height / 2))

    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")


def create_account(username, password):
    accounts = load_accounts()
    for account in accounts:
        if account["username"] == username:
            return False

    new_account = {
        "username": username,
        "password": password,
        "usertype": "customer",
        "balance": 500,
        "inventory": []
    }

    accounts.append(new_account)
    save_accounts(accounts)
    return True

# Function to show the login screen


def show_login_screen():
    login_screen = ThemedTk(theme="arc")
    login_screen.title("Login")
    center_window(login_screen, 600, 600)

    username_label = Label(login_screen, text="Username")
    password_label = Label(login_screen, text="Password")
    username_label.pack(pady=(20, 0))
    username_entry = Entry(login_screen)
    username_entry.pack()
    password_label.pack(pady=(20, 0))
    password_entry = Entry(login_screen, show="*")
    password_entry.pack()

    def login():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        account = authenticate(username, password)
        if account:
            login_screen.destroy()
            if account["usertype"] == "admin":
                import importlib
                login = importlib.import_module("product_manager")
                product_manager.show_product_manager()
            else:
                show_customer_ui(account)
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    login_button = Button(login_screen, text="Login", command=login)
    login_button.pack(pady=(10, 0))

    def show_signup_screen():
        login_screen.destroy()
        show_signup()

    signup_button = Button(login_screen, text="Sign up",
                           command=show_signup_screen)
    signup_button.pack(pady=(10, 0))

    login_screen.mainloop()


def show_signup():
    signup_screen = ThemedTk(theme="arc")
    signup_screen.title("Sign up")
    center_window(signup_screen, 800, 800)

    username_label = Label(signup_screen, text="Username")
    password_label = Label(signup_screen, text="Password")
    username_label.pack(pady=(20, 0))
    username_entry = Entry(signup_screen)
    username_entry.pack()
    password_label.pack(pady=(20, 0))
    password_entry = Entry(signup_screen, show="*")
    password_entry.pack()

    def signup():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        if create_account(username, password):
            messagebox.showinfo("Success", "Account created successfully.")
            signup_screen.destroy()
            show_login_screen()
        else:
            messagebox.showerror("Error", "Username already exists.")

    signup_button = Button(signup_screen, text="Sign up", command=signup)
    signup_button.pack(pady=(10, 0))

    def back_to_login():
        signup_screen.destroy()
        show_login_screen()

    back_button = Button(signup_screen, text="Back", command=back_to_login)
    back_button.pack(pady=(10, 0))

    signup_screen.mainloop()


def show_customer_ui(account):

    def edit_product_quantity(product_name, new_quantity):
        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE products
            SET quantity = ?
            WHERE name = ?
        """, (new_quantity, product_name))

        conn.commit()
        conn.close()

    def buy_item():
        selected_items = items_tree.selection()

        if not selected_items:
            messagebox.showerror("Error", "Please select a product to buy.")
            return

        selected_item = selected_items[0]
        item_data = items_tree.item(selected_item)['values']
        name, price, available_quantity = item_data

        try:
            purchase_quantity = int(quantity_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity value.")
            return

        if purchase_quantity > available_quantity or available_quantity == 0:
            messagebox.showerror("Error", "Not enough items in stock.")
            return

        if int(account["balance"]) < float(price) * purchase_quantity:
            messagebox.showerror("Error", "Insufficient balance.")
            return
        edit_product_quantity(
            name, available_quantity - purchase_quantity)
        account["balance"] -= float(price) * purchase_quantity
        purchased_item = {
            "name": name,
            "quantity": purchase_quantity
        }
        account["inventory"].append(purchased_item)

        # Update the accounts.json file
        accounts = load_accounts()
        for i, acc in enumerate(accounts):
            if acc["username"] == account["username"]:
                accounts[i] = account
                break
        save_accounts(accounts)

        # Refresh the items_tree and bought_items_tree
        populate_items_tree(items_tree)
        populate_bought_items_tree(inventory_tree, account)

        # Update account_balance_label
        balance_label.config(text=(f"Balance: ${account['balance']:.2f}"))

    def fetch_products():
        conn = sqlite3.connect("products.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def populate_items_tree(tree):
        tree.delete(*tree.get_children())
        products = fetch_products()
        for product in products:
            tree.insert("", "end", values=(product[1], product[2], product[3]))

    def populate_bought_items_tree(tree, account):
        tree.delete(*tree.get_children())
        for item in account['inventory']:
            tree.insert('', 'end', values=(item['name'], item['quantity']))

    def on_items_tree_select(event):
        selected_items = items_tree.selection()
        if not selected_items:
            return
        selected_item = selected_items[0]
        item_data = items_tree.item(selected_item)['values']
        quantity_entry.delete(0, 'end')
        quantity_entry.insert(0, str(item_data[2]))

    def create_products_tree(master, show_quantity=False):
        tree = ttk.Treeview(master, columns=(
            "Name", "Price", "Quantity"), show="headings")
        tree.heading("Name", text="Name")
        tree.heading("Price", text="Price")
        tree.heading("Quantity", text="Quantity")
        tree.column("Name", anchor=W, width=200)
        tree.column("Price", anchor=W, width=100)
        tree.column("Quantity", anchor=W, width=100)
        if show_quantity:
            for item in account['inventory']:
                tree.insert("", "end", values=(item['name'], item['quantity']))
        else:
            conn = sqlite3.connect("products.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name, price, quantity FROM products")
            rows = cursor.fetchall()
            for row in rows:
                tree.insert("", "end", values=row)

            conn.close()

        return tree

    def logout():
        customer_screen.destroy()
        show_login_screen()

    customer_screen = ThemedTk(theme="arc")
    customer_screen.title("Customer UI")
    center_window(customer_screen, 1200, 800)

    balance_label = Label(
        customer_screen, text=f"Balance: ${account['balance']}")
    balance_label.grid(row=0, column=0, padx=10, pady=10, sticky=W)

    items_label = Label(customer_screen, text="Available Items")
    items_label.grid(row=1, column=0, padx=10, pady=10, sticky=W)

    items_tree = create_products_tree(customer_screen, show_quantity=False)
    items_tree.bind("<<TreeviewSelect>>", on_items_tree_select)
    items_tree.grid(row=2, column=0, padx=10, pady=10)

    buy_label = Label(customer_screen, text="Buy Item")
    buy_label.grid(row=3, column=0, padx=10, pady=10, sticky=W)

    quantity_label = Label(customer_screen, text="Quantity")
    quantity_label.grid(row=4, column=0, padx=10, pady=10, sticky=W)

    quantity_entry = Entry(customer_screen)
    quantity_entry.grid(row=4, column=1, padx=10, pady=10)

    buy_button = Button(customer_screen, text="Buy", command=buy_item)
    buy_button.grid(row=5, column=1, padx=10, pady=10)

    inventory_label = Label(customer_screen, text="Your Purchase History")
    inventory_label.grid(row=1, column=2, padx=10, pady=10, sticky=W)

    inventory_tree = create_products_tree(customer_screen, show_quantity=True)
    inventory_tree.grid(row=2, column=2, padx=10, pady=10)

    logout_button = Button(customer_screen, text="Logout",
                           command=logout)
    logout_button.grid(row=5, column=2, padx=10, pady=10)

    customer_screen.mainloop()


def setup_database():
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    example_items = [
        (0, "iPhone 13", 999.00, 10),
        (1, "Samsung Galaxy S22", 899.00, 15),
        (2, "MacBook Pro", 2499.00, 5),
        (3, "Dell XPS 13", 1399.00, 8),
        (4, "iPad Pro", 1099.00, 12),
        (5, "Sony WH-1000XM4", 349.00, 25),
        (6, "Apple Watch Series 7", 399.00, 18),
        (7, "Amazon Echo Dot", 49.99, 40),
    ]

    for item in example_items:
        try:
            cursor.execute(
                "INSERT INTO products (id, name, price, quantity) VALUES (?, ?, ?, ?)", item)
        except sqlite3.IntegrityError:
            # Item already exists, skip it
            pass

    conn.commit()
    conn.close()


# Set up the database with example electronic items
setup_database()

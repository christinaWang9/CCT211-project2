import sqlite3
from tkinter import *
from tkinter import messagebox, ttk


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x_coordinate = int((screen_width / 2) - (width / 2))
    y_coordinate = int((screen_height / 2) - (height / 2))

    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")


def show_product_manager():
    def create_table():
        conn = sqlite3.connect("products.db")
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS products (
                            id INTEGER PRIMARY KEY,
                            name TEXT UNIQUE NOT NULL,
                            price REAL,
                            quantity INTEGER
                        )""")
        conn.commit()
        conn.close()

    def add_product(name, price, quantity):
        conn = sqlite3.connect("products.db")
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", (name, price, quantity))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Error", "Product with this name already exists!")
        conn.close()

    def delete_product(item_id):
        conn = sqlite3.connect("products.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()

    def update_product(id, name, price, quantity):
        conn = sqlite3.connect("products.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE products SET name = ?, price = ?, quantity = ? WHERE id = ?", (name, price, quantity, id))
        conn.commit()
        conn.close()

    def fetch_products():
        conn = sqlite3.connect("products.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def refresh_tree():
        for item in tree.get_children():
            tree.delete(item)
        for row in fetch_products():
            tree.insert("", "end", values=row)

    def on_add_click():
        try:
            name = entry_name.get()
            price = float(entry_price.get())
            quantity = int(entry_quantity.get())
            if not name or not price or not quantity:
                messagebox.showerror("Error", "Please fill in all fields.")
                return
            add_product(name, price, quantity)
            refresh_tree()
        except ValueError:
            messagebox.showerror("Error", "Invalid price or quantity value.")
            return

    def on_tree_select(event):
        selected_items = tree.selection()

        if not selected_items:
            return

        selected_item = selected_items[0]
        item_data = tree.item(selected_item)['values']

        entry_id_var.set('')
        entry_id_var.set(item_data[0])
        entry_name.delete(0, END)
        entry_name.insert(0, item_data[1])
        entry_price.delete(0, END)
        entry_price.insert(0, item_data[2])
        entry_quantity.delete(0, END)
        entry_quantity.insert(0, item_data[3])

    def on_update_click():
        name = entry_name.get()
        price = entry_price.get()
        quantity = entry_quantity.get()
        if not name or not price or not quantity:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        if not entry_id_var.get():
            messagebox.showerror(
                "Error", "Please select a product from the table before updating.")
            return

        try:
            id = int(entry_id_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid ID value.")
            return

        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Error", "Invalid price or quantity value.")
            return
        update_product(id, name, price, quantity)
        entry_id_var.set('')
        refresh_tree()

    def logout():
        root.destroy()
        import importlib
        login = importlib.import_module("login")
        login.show_login_screen()

    def on_delete_click():
        selected_items = tree.selection()

        if not selected_items:
            messagebox.showerror(
                "Error", "Please select a product from the table before deleting.")
            return

        selected_item = selected_items[0]
        item_data = tree.item(selected_item)['values']
        item_id = item_data[0]

        delete_product(item_id)

        # Remove the item from the treeview
        tree.delete(selected_item)

        # Clear entry fields
        entry_id_var.set('')
        entry_name.delete(0, END)
        entry_price.delete(0, END)
        entry_quantity.delete(0, END)

    root = Tk()
    root.title("Product Manager")
    center_window(root, 800, 800)

    # Create the products table if it doesn't exist
    create_table()

    # Create input fields and buttons
    entry_id_var = StringVar()
    entry_name = Entry(root)
    entry_price = Entry(root)
    entry_quantity = Entry(root)
    entry_name.grid(row=1, column=1)
    entry_price.grid(row=2, column=1)
    entry_quantity.grid(row=3, column=1)

    name_label = Label(root, text="Name")
    price_label = Label(root, text="Price")
    quantity_label = Label(root, text="Quantity")
    name_label.grid(row=1, column=0)
    price_label.grid(row=2, column=0)
    quantity_label.grid(row=3, column=0)

    add_button = Button(root, text="Add Product", command=on_add_click)
    update_button = Button(root, text="Update Product",
                           command=on_update_click)
    delete_button = Button(root, text="Delete",
                           command=on_delete_click, font=("Arial", 12))
    delete_button.grid(row=4, column=2, padx=10, pady=10)
    add_button.grid(row=4, column=0, pady=10)
    update_button.grid(row=4, column=1, pady=10)
    logout_button = Button(root, text="Logout",
                           command=logout)
    logout_button.grid(row=5, column=2, padx=10, pady=10)
    # Create the tree view
    tree = ttk.Treeview(root, columns=(
        "ID", "Name", "Price", "Quantity"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Price", text="Price")
    tree.heading("Quantity", text="Quantity")
    tree.column("ID", anchor=CENTER, width=100)
    tree.column("Name", anchor=W, width=200)
    tree.column("Price", anchor=E, width=100)
    tree.column("Quantity", anchor=E, width=100)
    tree.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    # Load data into the tree view
    refresh_tree()

    root.mainloop()

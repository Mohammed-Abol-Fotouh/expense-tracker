import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import requests

# API endpoint for currency conversion
conversion_url = "https://api.apilayer.com/fixer/convert?to=USD&from={}&amount={}"


# Update the total sum row in the treeview
def update_total():
    # Remove existing total sum row
    total_row_id = find_total_row()
    if total_row_id:
        tree.delete(total_row_id)

    # Convert and sum all amounts to USD
    total_usd_amount = 0.0

    for item in tree.get_children():
        try:
            amount = float(tree.item(item, "values")[0])
            currency = tree.item(item, "values")[1]
        except (ValueError, IndexError):
            # Handle invalid values
            continue

        # Convert amount to USD using the currency conversion API
        conversion_api_url = conversion_url.format(currency, amount)

        headers = {"apikey": "bct4XFDrMyDX7rTGm3YGcFafLy2qcX4x"}
        response = requests.get(conversion_api_url, headers=headers)

        if response.status_code == 200:
            try:
                converted_amount = float(response.text)
                total_usd_amount += converted_amount
            except ValueError:
                # Handle invalid conversion result
                try:
                    response_data = response.json()
                    converted_amount = float(response_data.get("result", amount))
                    total_usd_amount += converted_amount
                except ValueError:
                    total_usd_amount += amount

        else:
            # Handle error here
            print(f"API request failed for {currency} {amount}")
            total_usd_amount += amount

    # Insert a new total sum row at the end with the total converted amount in USD
    tree.tag_configure("yellow", background="yellow")
    tree.insert(
        "", "end", values=(total_usd_amount, "USD"), tags=("total_row", "yellow")
    )


# Find the ID of the total sum row
def find_total_row():
    for item in tree.get_children():
        if "total_row" in tree.item(item, "tags"):
            return item
    return None


# add expense function
def add_expense():
    amount_value = amount.get()
    currency_value = currency.get()
    category_value = category.get()
    payment_value = payment.get()
    date_value = date_entry.get_date()

    if amount_value and date_value:
        tree.insert(
            "",
            tk.END,
            values=(
                amount_value,
                currency_value,
                category_value,
                payment_value,
                date_value,
            ),
        )

        # Update the total sum row
        update_total()

    amount_entry.delete(0, tk.END)
    currency_combobox.current(0)
    category_combobox.current(0)
    payment_combobox.current(0)
    date_entry.delete(0, tk.END)


# Create the main window
window = tk.Tk()
window.title("Expense Tracker")
window.geometry("1000x500")

# variables
amount = tk.StringVar()
currency = tk.StringVar()
category = tk.StringVar()
payment = tk.StringVar()

# Expense Frame
expense_frame = tk.Frame(window)

amount_label = tk.Label(expense_frame, text="Amount", font={"Helvetica", 16}, width=25)
amount_entry = tk.Entry(expense_frame, textvariable=amount, font={"Helvetica", 16})

currency_label = tk.Label(expense_frame, text="Currency", font={"Helvetica", 16})
currency_combobox = ttk.Combobox(expense_frame, textvariable=currency, width=25)
currency_combobox["values"] = ("EUR", "GBP", "EGP", "USD", "SAR")
currency_combobox.current(0)

category_label = tk.Label(expense_frame, text="Category", font={"Helvetica", 16})
category_combobox = ttk.Combobox(expense_frame, textvariable=category, width=25)
category_combobox["values"] = (
    "life expenses",
    "electricity",
    "gas",
    "rental",
    "grocery",
    "savings",
    "education",
    "charity",
)
category_combobox.current(0)

payment_label = tk.Label(expense_frame, text="Payment Method", font={"Helvetica", 16})
payment_combobox = ttk.Combobox(expense_frame, textvariable=payment, width=25)
payment_combobox["values"] = ("Cash", "Credit Card", "Paypal")
payment_combobox.current(0)

date_label = tk.Label(expense_frame, text="Date", font={"Helvetica", 16})
date_entry = DateEntry(expense_frame, date_pattern="y-mm-dd", year=2024, width=25)

add_btn = tk.Button(expense_frame, text="Add Expense", command=add_expense)

# define columns
columns = ("Amount", "currency", "Category", "payment_method", "date")

tree = ttk.Treeview(window, columns=columns, show="headings")

# define headings
tree.heading("Amount", text="Amount")
tree.heading("currency", text="Currency")
tree.heading("Category", text="Category")
tree.heading("payment_method", text="Paymenet Method")
tree.heading("date", text="Date")

# Placements
# options frame
expense_frame.grid(column=0, row=0, pady=10)

# amount placement
amount_label.grid(column=0, row=0, pady=(0, 0), padx=(0, 200))
amount_entry.grid(column=1, row=0)

# currency placement
currency_label.grid(column=0, row=1, pady=(0, 0), padx=(0, 200))
currency_combobox.grid(column=1, row=1)

# category placement
category_label.grid(column=0, row=2, pady=(0, 0), padx=(0, 200))
category_combobox.grid(column=1, row=2)

# payment placement
payment_label.grid(column=0, row=3, pady=(0, 0), padx=(0, 200))
payment_combobox.grid(column=1, row=3)

# date placement
date_label.grid(column=0, row=4, pady=(0, 0), padx=(0, 200))
date_entry.grid(column=1, row=4)

# button placement
add_btn.grid(column=1, row=5, padx=10, pady=10, sticky="nsew")

# tree placement
tree.grid(column=0, row=6, sticky="nsew")

window.columnconfigure(0, weight=1)
window.columnconfigure(0, weight=1)

# Tag for the total sum row
total_row = "total_row"

# Run the Tkinter main loop
window.mainloop()

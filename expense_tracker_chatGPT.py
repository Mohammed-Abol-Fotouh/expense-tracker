import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import requests

conversion_url = "https://api.apilayer.com/fixer/convert?to=USD&from={}&amount={}"


class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("1000x500")

        # Variables
        self.amount = tk.StringVar()
        self.currency = tk.StringVar()
        self.category = tk.StringVar()
        self.payment = tk.StringVar()

        # Expense Frame
        self.expense_frame = tk.Frame(root)

        # Widgets for expense entry
        self.amount_label = tk.Label(
            self.expense_frame, text="Amount", font={"Helvetica", 16}
        )
        self.amount_entry = tk.Entry(
            self.expense_frame, textvariable=self.amount, font={"Helvetica", 16}
        )

        self.currency_label = tk.Label(
            self.expense_frame, text="Currency", font={"Helvetica", 16}
        )
        self.currency_combobox = ttk.Combobox(
            self.expense_frame, textvariable=self.currency, width=25
        )
        self.currency_combobox["values"] = ("EUR", "GBP", "EGP", "USD", "SAR")
        self.currency_combobox.current(0)

        self.category_label = tk.Label(
            self.expense_frame, text="Category", font={"Helvetica", 16}
        )
        self.category_combobox = ttk.Combobox(
            self.expense_frame, textvariable=self.category, width=25
        )
        self.category_combobox["values"] = (
            "life expenses",
            "electricity",
            "gas",
            "rental",
            "grocery",
            "savings",
            "education",
            "charity",
        )
        self.category_combobox.current(0)

        self.payment_label = tk.Label(
            self.expense_frame, text="Payment Method", font={"Helvetica", 16}
        )
        self.payment_combobox = ttk.Combobox(
            self.expense_frame, textvariable=self.payment, width=25
        )
        self.payment_combobox["values"] = ("Cash", "Credit Card", "Paypal")
        self.payment_combobox.current(0)

        self.date_label = tk.Label(
            self.expense_frame, text="Date", font={"Helvetica", 16}
        )
        self.date_entry = DateEntry(
            self.expense_frame, date_pattern="y-mm-dd", year=2024, width=25
        )

        self.add_btn = tk.Button(
            self.expense_frame, text="Add Expense", command=self.add_expense
        )

        # Define columns for the treeview
        self.columns = ("Amount", "Currency", "Category", "Payment Method", "Date")

        # Create a treeview
        self.tree = ttk.Treeview(root, columns=self.columns, show="headings")

        # Define headings for the treeview
        for col in self.columns:
            self.tree.heading(col, text=col)

        # Placements
        # Options frame
        self.expense_frame.grid(column=0, row=0, pady=10)

        # Amount placement
        self.amount_label.grid(column=0, row=0, pady=(0, 0), padx=(0, 200))
        self.amount_entry.grid(column=1, row=0)

        # Currency placement
        self.currency_label.grid(column=0, row=1, pady=(0, 0), padx=(0, 200))
        self.currency_combobox.grid(column=1, row=1)

        # Category placement
        self.category_label.grid(column=0, row=2, pady=(0, 0), padx=(0, 200))
        self.category_combobox.grid(column=1, row=2)

        # Payment placement
        self.payment_label.grid(column=0, row=3, pady=(0, 0), padx=(0, 200))
        self.payment_combobox.grid(column=1, row=3)

        # Date placement
        self.date_label.grid(column=0, row=4, pady=(0, 0), padx=(0, 200))
        self.date_entry.grid(column=1, row=4)

        # Button placement
        self.add_btn.grid(column=1, row=5, padx=10, pady=10, sticky="nsew")

        # Tree placement
        self.tree.grid(column=0, row=6, sticky="nsew")

        # Configure column weights for resizing
        root.columnconfigure(0, weight=1)

        # Tag for the total sum row
        self.total_row_tag = "total_row"

    def add_expense(self):
        amount_value = self.amount.get()
        date_value = self.date_entry.get_date()

        if amount_value and date_value:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    amount_value,
                    self.currency.get(),
                    self.category.get(),
                    self.payment.get(),
                    date_value,
                ),
            )

            # Update the total sum row
            self.update_total()

        # Clear entry fields
        self.amount_entry.delete(0, tk.END)
        self.currency_combobox.current(0)
        self.category_combobox.current(0)
        self.payment_combobox.current(0)
        self.date_entry.delete(0, tk.END)

    def update_total(self):
        # Remove existing total sum row
        total_row_id = self.find_total_row()
        if total_row_id:
            self.tree.delete(total_row_id)

        # Convert and sum all amounts to USD
        total_usd_amount = 0.0

        for item in self.tree.get_children():
            try:
                amount = float(self.tree.item(item, "values")[0])
                currency = self.tree.item(item, "values")[1]
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
        self.tree.tag_configure("yellow", background="yellow")
        self.tree.insert(
            "",
            "end",
            values=(total_usd_amount, "USD"),
            tags=(self.total_row_tag, "yellow"),
        )

    def find_total_row(self):
        for item in self.tree.get_children():
            if self.total_row_tag in self.tree.item(item, "tags"):
                return item
        return None


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()

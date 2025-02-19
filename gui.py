import tkinter as tk
from tkinter import ttk, Label, PhotoImage
from tkinter import messagebox, filedialog
import pandas as pd
from file_handler import FileHandler
from duckle_parser import BankStatementParser
from database_handler import DatabaseHandler  # Ensure this is imported

# Predefined categories and subcategories for auto-categorization
CATEGORY_RULES = {
    "Grocery": ["Walmart", "Kroger", "Dollar-General"],
    "Entertainment": ["Netflix", "Hulu", "Disney", "Steam", "GameStop"],
    "Entertainment -> Meals": ["McDonalds", "Wendys", "Taco Bell", "Dominos", "Doordash"],
    "Debt -> Credit Card": ["Discover", "Merrick Bank", "Best Egg"],
    "Insurance": ["State Farm", "Geico", "Allstate"],
    "Home -> Home Improvement": ["Home Depot", "Lowes"],
    "Mortgage": ["Us Bank Home Mtg"],
    "Utilities": ["Columbia Gas", "Toledo Edison", "Water"],
    "Gas": ["Speedway", "Shell", "BP"],
    "Snacks": ["Circle K", "Speedway", "Sheetz"],  # Transactions under $30 at gas stations
}

class BankStatementApp:
    def __init__(self, root, file_handler, parser, db_handler):
        self.root = root
        self.parser = parser
        self.db_handler = db_handler
        self.file_handler = file_handler

        self.logo = PhotoImage(file="Duckle256.png")  # Make sure "logo.png" is in the same folder

        self.root.iconphoto(True, PhotoImage(file="Duckle256.png"))




        # Configure the root window
        self.root.title("Duckle")
        self.root.iconbitmap("Duckle256.ico") # Set window icon
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f2f5")  # Light gray background

        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')  # Or 'alt', 'default', 'classic' depending on your OS

        # Configure custom styles
        style.configure("Treeview",
                        background="#ffffff",
                        fieldbackground="#ffffff",
                        foreground="#333333",
                        rowheight=30,
                        font=('Segoe UI', 10))

        style.configure("Treeview.Heading",
                        background="#f8f9fa",
                        foreground="#333333",
                        font=('Segoe UI', 10, 'bold'))

        # Create main frame with padding
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header frame
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Title
        title_label = ttk.Label(header_frame,
                                text="Duckle",
                                font=('Garamond', 24, 'bold'))
        title_label.pack(side=tk.LEFT)

        # Button frame
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)

        # Modern styled buttons
        self.load_pdf_btn = ttk.Button(button_frame,
                                       text="Load PDF",
                                       style="Accent.TButton",
                                       command=self.load_pdf)
        self.load_pdf_btn.pack(side=tk.LEFT, padx=5)

        self.export_btn = ttk.Button(button_frame,
                                     text="Export",
                                     command=self.export_data)
        self.export_btn.pack(side=tk.LEFT, padx=5)

        # Category frame
        category_frame = ttk.Frame(main_frame)
        category_frame.pack(fill=tk.X, pady=(0, 20))

        # Category controls
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(category_frame,
                                              textvariable=self.category_var,
                                              state="readonly",
                                              width=30)
        self.category_dropdown.pack(side=tk.LEFT, padx=5)

        self.set_category_btn = ttk.Button(category_frame,
                                           text="Set Category",
                                           command=self.set_category)
        self.set_category_btn.pack(side=tk.LEFT, padx=5)

        # Add new category frame
        new_category_frame = ttk.Frame(category_frame)
        new_category_frame.pack(side=tk.LEFT, padx=20)

        self.new_category_entry = ttk.Entry(new_category_frame, width=20)
        self.new_category_entry.pack(side=tk.LEFT, padx=5)

        self.add_category_btn = ttk.Button(new_category_frame,
                                           text="Add Category",
                                           command=self.add_new_category)
        self.add_category_btn.pack(side=tk.LEFT, padx=5)

        # Treeview in a frame with scrollbars
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Enhanced Treeview
        columns = ("Date", "Withdrawal/Deposit", "Transaction Type", "Details", "Amount", "Balance", "Category", "Subcategory")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 yscrollcommand=tree_scroll_y.set,
                                 xscrollcommand=tree_scroll_x.set)

        # Configure scrollbars
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, anchor="center", width=150)  # Set minimum column width

        # Make Details column wider to accommodate additional text
        self.tree.column("Details", width=300, anchor="w")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Initialize category dropdown
        self.update_category_dropdown()

    def update_category_dropdown(self):
        """Updates the category dropdown with available categories."""
        self.category_dropdown["values"] = list(CATEGORY_RULES.keys())

    def auto_categorize_transaction(self, details, amount):
        """Automatically assigns a category based on transaction details."""
        for category, keywords in CATEGORY_RULES.items():
            for keyword in keywords:
                if keyword.lower() in details.lower():
                    # Special rule for gas/snacks categorization
                    if category == "Snacks" and float(amount) > 30:
                        return "Gas"
                    return category
        return "Uncategorized"

    def add_new_category(self):
        """Allows the user to add a new category."""
        new_category = self.new_category_entry.get().strip()
        if new_category and new_category not in CATEGORY_RULES:
            CATEGORY_RULES[new_category] = []
            self.update_category_dropdown()
            messagebox.showinfo("Success", f"Category '{new_category}' added!")
        else:
            messagebox.showwarning("Invalid", "Category already exists or is empty.")

    def load_pdf(self):
        """Handles PDF loading and transaction parsing."""
        text = self.file_handler.load_pdf()

        if not isinstance(text, str) or not text.strip():
            print("ERROR: No valid text extracted, skipping parsing.")
            messagebox.showerror("Error", "No valid text was extracted from the PDF.")
            return

        print("Text successfully extracted. Parsing now...")

        transactions = self.parser.parse_bank_statement_with_year(text)

        if not transactions:
            print("WARNING: No transactions were parsed.")
            messagebox.showwarning("Warning", "No transactions were found in the PDF.")
            return

        # Insert transactions into the database
        for transaction in transactions:
            self.db_handler.insert_transaction(transaction)

        print(f"Displaying {len(transactions)} transactions in GUI...")
        self.populate_treeview(transactions)

    def populate_treeview(self, transactions):
        """Displays parsed transactions in the GUI with categorization."""
        self.tree.delete(*self.tree.get_children())  # Clear existing items

        for transaction in transactions:
            # Extract transaction data
            date, withdrawal_or_deposit, transaction_type, details = transaction[0:4]
            amount, balance, category, subcategory = transaction[4:8]

            # Create display values
            display_values = (
                date,
                withdrawal_or_deposit,
                transaction_type,
                details,  # Details now includes any additional information
                f"{amount:.2f}",
                f"{balance:.2f}",
                category,
                subcategory
            )

            item_id = self.tree.insert("", tk.END, values=display_values)

            # Apply color coding based on transaction type
            if withdrawal_or_deposit == "Deposit":
                self.tree.item(item_id, tags=("deposit",))
            else:
                self.tree.item(item_id, tags=("withdrawal",))

        # Configure tag colors
        self.tree.tag_configure("deposit", foreground="#008800")
        self.tree.tag_configure("withdrawal", foreground="#880000")

    def set_category(self):
        """Allows user to manually set a category for a selected transaction."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a transaction.")
            return

        category = self.category_var.get()
        if not category:
            messagebox.showwarning("No Category", "Please select a category.")
            return

        for item in selected_item:
            values = list(self.tree.item(item, "values"))
            values[6] = category  # Update category column

            # For subcategory handling
            if " -> " in category:
                main_category, subcategory = category.split(" -> ")
                values[6] = main_category
                values[7] = subcategory
            else:
                values[7] = category  # Default subcategory to match category

            self.tree.item(item, values=values)

            # Update in database if you want persistent changes
            # Get unique identifier and update database
            # (This would require modifications to your database_handler)

    def clear_treeview(self):
        """Clears all items from the Treeview."""
        self.tree.delete(*self.tree.get_children())

    def refresh_view(self):
        """Refreshes transactions by reloading from the database."""
        self.clear_treeview()
        transactions = self.db_handler.fetch_all_transactions()  # Fetch stored transactions
        self.populate_treeview(transactions)

    def sort_column(self, col, reverse):
        """Sort tree contents when a column header is clicked."""
        data = [
            (self.tree.set(child, col), child)
            for child in self.tree.get_children('')
        ]

        # Convert string values to appropriate types for sorting
        def convert_value(value):
            try:
                # Try to convert to float for amount/balance columns
                if col in ('Amount', 'Balance'):
                    return float(value.replace('$', '').replace(',', ''))
                # Try to convert to date for Date column
                elif col == 'Date':
                    return pd.to_datetime(value)
                # Return string for other columns
                return value
            except:
                return value

        # Sort the data
        data.sort(key=lambda x: convert_value(x[0]), reverse=reverse)

        # Rearrange items in sorted positions
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)

        # Switch the heading so it will sort in the opposite direction next time
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def export_data(self):
        """Exports the data to CSV."""
        if not self.tree.get_children():
            messagebox.showwarning("No Data", "No data to export.")
            return

        try:
            data = []
            columns = self.tree["columns"]

            for child in self.tree.get_children():
                values = self.tree.item(child)["values"]
                # Ensure the number of values matches the number of columns
                while len(values) < len(columns):
                    values = list(values) + [""]
                data.append(values[:len(columns)])  # Only take as many values as there are columns

            df = pd.DataFrame(data, columns=[self.tree.heading(col)["text"] for col in columns])

            export_file = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")]
            )

            if export_file:
                df.to_csv(export_file, index=False)
                messagebox.showinfo("Export Successful", f"Data exported to {export_file}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting data: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    db_handler = DatabaseHandler()
    parser = BankStatementParser()
    file_handler = FileHandler(parser, db_handler)
    app = BankStatementApp(root, file_handler, parser, db_handler)
    root.mainloop()

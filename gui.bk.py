import tkinter as tk
from tkinter import filedialog
from duckle_parser import process_pdf

class BankStatementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bank Statement Parser")
        self.file_handler = None
        self.parser = None

        # Initialize GUI components here
        self.load_button = tk.Button(root, text="Load PDF", command=self.load_pdf)
        self.load_button.pack()

        # Add some feedback for debugging
        self.label = tk.Label(root, text="Welcome! Please load a PDF.")
        self.label.pack()

    def set_file_handler(self, file_handler):
        self.file_handler = file_handler

    def set_parser(self, parser):
        self.parser = parser
        # After setting the parser, you might want to update or initialize certain UI components.
        self.load_button.config(command=self.load_pdf)  # Ensure button works with loaded parser

    def load_pdf(self):
        def load_pdf(self):
            # Debugging: Check if this method is being called
            print("Load PDF function triggered.")
            if self.parser:
                print(f"Parser is set: {self.parser}")
            if self.file_handler:
                print(f"File handler is set: {self.file_handler}")

            # Update the label to show that the PDF is loaded
            self.label.config(text="PDF loaded successfully!")

    def display_transactions(self, transactions):
        self.transaction_listbox.delete(0, tk.END)  # Clear existing items
        for txn in transactions:
            display_text = f"{txn['date']} | {txn['type']} | {txn['description']} | ${txn['amount']} | Bal: ${txn['balance']}"
            self.transaction_listbox.insert(tk.END, display_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = BankStatementApp(root)
    root.mainloop()

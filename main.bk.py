from tkinter import Tk
from gui import BankStatementApp
from duckle_parser import process_pdf
from file_handler import FileHandler

def main():
    root = Tk()

    # Initialize the parser and file handler
    parser = process_pdf()
    file_handler = FileHandler(parser)

    # Create the GUI with the required components
    app = BankStatementApp(root, file_handler, parser)
    app.set_parser(parser)  # Ensure this method is still needed in the updated flow

    root.mainloop()

if __name__ == "__main__":
    main()
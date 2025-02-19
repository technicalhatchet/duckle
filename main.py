from tkinter import Tk
import argparse
import sys
import subprocess
import threading
import webbrowser
from database_handler import DatabaseHandler
from duckle_parser import BankStatementParser
from file_handler import FileHandler

def run_flask_server():
    """Run the Flask server in a separate process."""
    from api import app
    app.run(debug=False, port=5000)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Duckle Bank Statement Parser')
    parser.add_argument('--gui', choices=['tkinter', 'pyqt5', 'react'], default='tkinter',
                        help='Choose GUI: tkinter (default), pyqt5, or react')
    args = parser.parse_args()

    # Initialize the parser, database handler, and file handler
    parser_instance = BankStatementParser()
    db_handler = DatabaseHandler()
    file_handler = FileHandler(parser_instance, db_handler)

    if args.gui == 'react':
        # Start Flask server in a separate thread
        server_thread = threading.Thread(target=run_flask_server, daemon=True)
        server_thread.start()

        # Open web browser
        webbrowser.open('http://localhost:5000')

        print("React GUI started. Press Ctrl+C to exit.")
        try:
            server_thread.join()
        except KeyboardInterrupt:
            print("Shutting down...")
            sys.exit(0)

    elif args.gui == 'pyqt5':
        from pyqt5_gui import main as pyqt5_main
        pyqt5_main()

    else:
        # Start Tkinter GUI
        from gui import BankStatementApp
        root = Tk()
        app = BankStatementApp(root, file_handler, parser_instance, db_handler)
        root.mainloop()

if __name__ == "__main__":
    main()
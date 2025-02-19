from tkinter import Tk, messagebox
import argparse
import sys
import subprocess
import threading
import webbrowser
from gui import BankStatementApp
from duckle_parser import BankStatementParser
from file_handler import FileHandler
from database_handler import DatabaseHandler

def run_flask_server():
    """Run the Flask server in a separate process."""
    from api import app
    app.run(debug=False, port=5000)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Duckle Bank Statement Parser')
    parser.add_argument('--gui', choices=['tkinter', 'react'], default='tkinter',
                        help='Choose GUI: tkinter (default) or react')
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
            # Keep the main thread alive
            server_thread.join()
        except KeyboardInterrupt:
            print("Shutting down...")
            sys.exit(0)
    else:
        # Start Tkinter GUI
        root = Tk()
        app = BankStatementApp(root, file_handler, parser_instance, db_handler)
        root.mainloop()

if __name__ == "__main__":
    main()
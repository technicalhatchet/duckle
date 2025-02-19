@echo off
echo ===== Duckle Bank Statement Parser Build Script =====

echo Creating necessary directories...
if not exist react-build mkdir react-build
if not exist uploads mkdir uploads

echo Creating setup_database.py...
(
echo from database_handler import DatabaseHandler
echo.
echo # Initialize the database
echo db = DatabaseHandler^(^)
echo db.create_tables^(^)
echo print^("Database initialized successfully."^)
) > setup_database.py

echo Creating categories.json file...
(
echo {
echo   "Income": [],
echo   "Housing": [],
echo   "Transportation": [],
echo   "Food": [],
echo   "Utilities": [],
echo   "Medical": [],
echo   "Personal": [],
echo   "Entertainment": [],
echo   "Debt": [],
echo   "Savings": [],
echo   "Other": []
echo }
) > categories.json

echo Creating main.py file...
(
echo from tkinter import Tk, messagebox
echo import argparse
echo import sys
echo import subprocess
echo import threading
echo import webbrowser
echo from gui import BankStatementApp
echo from duckle_parser import BankStatementParser
echo from file_handler import FileHandler
echo from database_handler import DatabaseHandler
echo.
echo def run_flask_server^(^):
echo     """Run the Flask server in a separate process."""
echo     from api import app
echo     app.run^(debug=False, port=5000^)
echo.
echo def main^(^):
echo     # Parse command line arguments
echo     parser = argparse.ArgumentParser^(description='Duckle Bank Statement Parser'^)
echo     parser.add_argument^('--gui', choices=['tkinter', 'react'], default='tkinter',
echo                         help='Choose GUI: tkinter ^(default^) or react'^)
echo     args = parser.parse_args^(^)
echo.    
echo     # Initialize the parser, database handler, and file handler
echo     parser_instance = BankStatementParser^(^)
echo     db_handler = DatabaseHandler^(^)
echo     file_handler = FileHandler^(parser_instance, db_handler^)
echo.    
echo     if args.gui == 'react':
echo         # Start Flask server in a separate thread
echo         server_thread = threading.Thread^(target=run_flask_server, daemon=True^)
echo         server_thread.start^(^)
echo.        
echo         # Open web browser
echo         webbrowser.open^('http://localhost:5000'^)
echo.        
echo         print^("React GUI started. Press Ctrl+C to exit."^)
echo         try:
echo             # Keep the main thread alive
echo             server_thread.join^(^)
echo         except KeyboardInterrupt:
echo             print^("Shutting down..."^)
echo             sys.exit^(0^)
echo     else:
echo         # Start Tkinter GUI
echo         root = Tk^(^)
echo         app = BankStatementApp^(root, file_handler, parser_instance, db_handler^)
echo         root.mainloop^(^)
echo.
echo if __name__ == "__main__":
echo     main^(^)
) > main.py

echo ===== Basic setup complete! =====
echo To run the application with React GUI, use:
echo python main.py --gui react
echo.
echo To run with the Tkinter GUI (default), use:
echo python main.py

pause
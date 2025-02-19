import sqlite3
import threading

class DatabaseHandler:
    _instance = None
    _lock = threading.Lock()
    _local = threading.local()

    def __init__(self):
        self.db_name = 'transactions.db'

    def get_connection(self):
        # Create a new connection if one doesn't exist for this thread
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(self.db_name)
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection

    def get_cursor(self):
        return self.get_connection().cursor()

    def create_tables(self):
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()

                print(f"Creating transactions table in {self.db_name}")

                cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    withdrawal_or_deposit TEXT,
                    transaction_type TEXT,
                    details TEXT,
                    amount REAL,
                    balance REAL,
                    category TEXT,
                    subcategory TEXT
                )
            ''')

                # Verify the table was created
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
                if cursor.fetchone():
                    print("Successfully created transactions table")
                else:
                    print("Failed to create transactions table!")

                conn.commit()
                conn.close()
                print("Database connection closed")

            except Exception as e:
                print(f"Error creating tables: {str(e)}")
                raise

    def insert_transaction(self, transaction):
        cursor = self.get_cursor()
        cursor.execute('''
            INSERT INTO transactions (
                date, withdrawal_or_deposit, transaction_type,
                details, amount, balance, category, subcategory
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', transaction)
        self.get_connection().commit()

    def fetch_all_transactions(self):
        cursor = self.get_cursor()
        cursor.execute('SELECT * FROM transactions')
        return cursor.fetchall()

    def update_transaction_category(self, transaction_id, category, subcategory):
        cursor = self.get_cursor()
        cursor.execute('''
            UPDATE transactions 
            SET category = ?, subcategory = ?
            WHERE id = ?
        ''', (category, subcategory, transaction_id))
        self.get_connection().commit()

    def close(self):
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            del self._local.connection
import sqlite3

class DatabaseHandler:
    def __init__(self):
        self.conn = sqlite3.connect("bank_statements.db")
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            withdrawal_or_deposit TEXT,
            transaction_type TEXT,
            details TEXT,
            amount REAL,
            balance REAL
        )
        """)
        self.conn.commit()

    def insert_transaction(self, transaction):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO transactions (date, withdrawal_or_deposit, transaction_type, details, amount, balance)
        VALUES (?, ?, ?, ?, ?, ?)
        """, transaction)
        self.conn.commit()

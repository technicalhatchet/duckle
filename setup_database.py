from database_handler import DatabaseHandler
import os

print("Starting database setup...")

# Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Check if database file exists
db_name = 'transactions.db'
if os.path.exists(db_name):
    print(f"Found existing database: {db_name}")
else:
    print(f"No existing database found. Will create: {db_name}")

# Initialize the database
db = DatabaseHandler()
print("Created DatabaseHandler instance")

# Create tables
print("Creating tables...")
db.create_tables()
print("Tables created successfully")

# Verify table exists
import sqlite3
conn = sqlite3.connect(db_name)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
if cursor.fetchone():
    print("Verified 'transactions' table exists")
else:
    print("WARNING: 'transactions' table was not created!")
conn.close()

print("Database setup complete!")
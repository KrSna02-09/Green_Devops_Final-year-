import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("expenses.db")
        self.cursor = self.conn.cursor()
        
        # 1. Expenses Table - ADDED 'description' column
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                category TEXT,
                amount REAL,
                description TEXT
            )
        """)
        
        # 2. Budget Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY,
                limit_amount REAL
            )
        """)
        
        # Initialize budget if empty
        self.cursor.execute("SELECT count(*) FROM budget")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("INSERT INTO budget (id, limit_amount) VALUES (1, 0)")
            
        # AUTOMATIC MIGRATION: 
        # If the user already has a database without 'description', add it now.
        try:
            self.cursor.execute("ALTER TABLE expenses ADD COLUMN description TEXT")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass # Column already exists, ignore error

        self.conn.commit()

    def add_expense(self, date, category, amount, description):
        self.cursor.execute("INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)", 
                            (date, category, amount, description))
        self.conn.commit()

    def fetch_all(self):
        # Fetching ID, Date, Category, Amount, AND Description
        self.cursor.execute("SELECT id, date, category, amount, description FROM expenses ORDER BY id DESC")
        return self.cursor.fetchall()

    def delete_expense(self, row_id):
        self.cursor.execute("DELETE FROM expenses WHERE id=?", (row_id,))
        self.conn.commit()

    def update_expense(self, row_id, date, category, amount, description):
        self.cursor.execute("UPDATE expenses SET date=?, category=?, amount=?, description=? WHERE id=?", 
                            (date, category, amount, description, row_id))
        self.conn.commit()

    def fetch_category_sums(self):
        self.cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        return self.cursor.fetchall()
    
    def set_budget(self, amount):
        self.cursor.execute("UPDATE budget SET limit_amount = ? WHERE id = 1", (amount,))
        self.conn.commit()
        
    def get_budget(self):
        self.cursor.execute("SELECT limit_amount FROM budget WHERE id = 1")
        return self.cursor.fetchone()[0]
    
    def get_total_spent(self):
        self.cursor.execute("SELECT SUM(amount) FROM expenses")
        result = self.cursor.fetchone()[0]
        return result if result else 0.0
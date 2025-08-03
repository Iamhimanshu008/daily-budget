# database.py
import sqlite3
import pandas as pd
import hashlib
from typing import Dict, Optional

class ExpenseTrackerDB:
    """Database management class for expense tracker"""

    def __init__(self):
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Budgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, category, month, year)
            )
        ''')

        conn.commit()
        conn.close()

    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username: str, email: str, password: str) -> bool:
        """Create new user account"""
        try:
            conn = sqlite3.connect('expense_tracker.db')
            cursor = conn.cursor()

            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user login"""
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()

        password_hash = self.hash_password(password)
        cursor.execute(
            "SELECT id, username, email FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            return {"id": user[0], "username": user[1], "email": user[2]}
        return None

    def add_expense(self, user_id: int, amount: float, category: str, description: str, date: str) -> bool:
        """Add new expense"""
        try:
            conn = sqlite3.connect('expense_tracker.db')
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
                (user_id, amount, category, description, date)
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def get_expenses(self, user_id: int) -> pd.DataFrame:
        """Get all expenses for a user"""
        conn = sqlite3.connect('expense_tracker.db')
        query = """
            SELECT id, amount, category, description, date, created_at
            FROM expenses 
            WHERE user_id = ? 
            ORDER BY date DESC
        """
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        return df

    def delete_expense(self, expense_id: int, user_id: int) -> bool:
        """Delete an expense"""
        try:
            conn = sqlite3.connect('expense_tracker.db')
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM expenses WHERE id = ? AND user_id = ?",
                (expense_id, user_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def update_expense(self, expense_id: int, user_id: int, amount: float, category: str, description: str, date: str) -> bool:
        """Update an expense"""
        try:
            conn = sqlite3.connect('expense_tracker.db')
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE expenses SET amount = ?, category = ?, description = ?, date = ? WHERE id = ? AND user_id = ?",
                (amount, category, description, date, expense_id, user_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def set_budget(self, user_id: int, category: str, amount: float, month: int, year: int) -> bool:
        """Set budget for a category"""
        try:
            conn = sqlite3.connect('expense_tracker.db')
            cursor = conn.cursor()

            cursor.execute(
                "INSERT OR REPLACE INTO budgets (user_id, category, amount, month, year) VALUES (?, ?, ?, ?, ?)",
                (user_id, category, amount, month, year)
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def get_budgets(self, user_id: int, month: int, year: int) -> pd.DataFrame:
        """Get budgets for a specific month/year"""
        conn = sqlite3.connect('expense_tracker.db')
        query = """
            SELECT category, amount
            FROM budgets 
            WHERE user_id = ? AND month = ? AND year = ?
        """
        df = pd.read_sql_query(query, conn, params=(user_id, month, year))
        conn.close()
        return df

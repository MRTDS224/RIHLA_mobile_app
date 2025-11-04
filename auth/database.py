import sqlite3
import hashlib
from pathlib import Path
import json

# Modifiez database.py pour afficher le chemin absolu
DB_PATH = Path(__file__).parent / "rihla_auth.db"
class AuthDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            preferences TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        self.conn.commit()
    
    def add_user(self, email, password, first_name=None, last_name=None, preferences=None):
        hashed_pw = self._hash_password(password)
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute('''
                INSERT INTO users (email, password, first_name, last_name, preferences)
                VALUES (?, ?, ?, ?, ?)
                ''', (email, hashed_pw, first_name, last_name, json.dumps(preferences) if preferences is not None else None))
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def get_user_by_email(self, email):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        return cursor.fetchone()
    
    def verify_user(self, email, password):
        hashed_pw = self._hash_password(password)
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, first_name, last_name, preferences FROM users 
        WHERE email = ? AND password = ?
        ''', (email, hashed_pw))
        result = cursor.fetchone()
        if result is not None:
            user_id, first_name, last_name, prefs_json = result
            preferences = json.loads(prefs_json) if prefs_json else []
            if len(preferences) != 3:
                preferences += [None] * (3 - len(preferences))
            return (user_id, first_name, last_name, preferences)
        return None

    
    def update_user(self, user_id, first_name=None, last_name=None, email=None, preferences=None):
        updates = []
        params = []
        
        if first_name:
            updates.append("first_name = ?")
            params.append(first_name)
        if last_name:
            updates.append("last_name = ?")
            params.append(last_name)
        if email:
            updates.append("email = ?")
            params.append(email)
        if preferences:
            updates.append("preferences = ?")
            params.append(json.dumps(preferences))
        
        if not updates:
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def update_password(self, user_id, new_password):
        hashed_pw = self._hash_password(new_password)
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE users SET password = ? WHERE id = ?
        ''', (hashed_pw, user_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def close(self):
        self.conn.close()

    def delete_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
# Singleton pour la base de données
db = AuthDatabase()
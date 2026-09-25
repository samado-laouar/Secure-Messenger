# db.py
import sqlite3
import hashlib
import os

DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def hash_password(password: str, salt: str = None):
    if salt is None:
        salt = os.urandom(32).hex()
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode(), 100000)
    return pwd_hash.hex(), salt

def register_user(username, password):
    if len(password) < 4: return False, "Mot de passe trop court (min 4)"
    if len(username) < 3: return False, "Nom d'utilisateur trop court"
    pwd_hash, salt = hash_password(password)
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", (username, pwd_hash, salt))
        conn.commit()
        return True, "Compte créé !"
    except sqlite3.IntegrityError:
        return False, "Nom déjà pris"
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if not row: return False
    stored_hash, salt = row
    pwd_hash, _ = hash_password(password, salt)
    return pwd_hash == stored_hash

def user_exists(username):
    """Check if a username exists in the database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row is not None

def update_password(username, new_password):
    """Update user's password after verification"""
    if len(new_password) < 4:
        return False, "Mot de passe trop court (min 4)"
    
    pwd_hash, salt = hash_password(new_password)
    
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE users SET password_hash = ?, salt = ? WHERE username = ?", 
                  (pwd_hash, salt, username))
        conn.commit()
        return True, "Mot de passe mis à jour !"
    except Exception as e:
        return False, f"Erreur: {str(e)}"
    finally:
        conn.close()

init_db()
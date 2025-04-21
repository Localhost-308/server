import os
import sqlite3
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

KEY_DIR = "user_keys"
SQLITE_DB = "keys.sqlite"

os.makedirs(KEY_DIR, exist_ok=True)

def init_sqlite():
    with sqlite3.connect(SQLITE_DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_keys (
                user_id INTEGER PRIMARY KEY,
                private_key TEXT NOT NULL
            )
        """)

def generate_keys(user_id):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    with open(f"{KEY_DIR}/public_{user_id}.pem", "wb") as pub_file:
        pub_file.write(public_pem)

    with sqlite3.connect(SQLITE_DB) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO user_keys (user_id, private_key) VALUES (?, ?)",
            (user_id, private_pem.decode())
        )

def delete_private_key(user_id):
    with sqlite3.connect(SQLITE_DB) as conn:
        conn.execute("DELETE FROM user_keys WHERE user_id = ?", (user_id,))
    try:
        os.remove(f"{KEY_DIR}/public_{user_id}.pem")
    except FileNotFoundError:
        pass

def get_private_key(user_id):
    with sqlite3.connect(SQLITE_DB) as conn:
        row = conn.execute("SELECT private_key FROM user_keys WHERE user_id = ?", (user_id,)).fetchone()
        if not row:
            return None
        return serialization.load_pem_private_key(row[0].encode(), password=None)

def get_public_key(user_id):
    with open(f"{KEY_DIR}/public_{user_id}.pem", "rb") as f:
        return serialization.load_pem_public_key(f.read())

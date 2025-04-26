# app/database/sqlite.py

import sqlite3
import os

# Define o caminho do arquivo SQLite (pode ser configurado no .env)
SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'user_keys.db')

def get_sqlite_session():
    """
    Retorna uma conexão ativa com o banco SQLite.
    """
    conn = sqlite3.connect(SQLITE_DB_PATH)
    return conn

def init_sqlite_db():
    """
    Inicializa o banco SQLite criando a tabela user_keys se não existir.
    """
    conn = get_sqlite_session()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_keys (
            user_id INTEGER PRIMARY KEY,
            private_key BLOB NOT NULL
        );
    """)

    conn.commit()
    conn.close()

import os
import sqlite3

BASE_DIR = os.getcwd()  # Get the current working directory
DB_PATH = os.path.join(BASE_DIR, "src", "backend", "cards.db")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_db_connection():
    """Returns a new database connection."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Creates the necessary tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Drop existing tables to redefine them correctly
    cursor.execute("DROP TABLE IF EXISTS Card")
    cursor.execute("DROP TABLE IF EXISTS Pokemon")
    cursor.execute("DROP TABLE IF EXISTS TCGPlayer")
    cursor.execute("DROP TABLE IF EXISTS Prices")

    # Create Card table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Card (
        id TEXT PRIMARY KEY,
        name TEXT,
        supertype TEXT,
        subtype TEXT,
        set_name TEXT,
        rarity TEXT,
        image_url TEXT,
        url TEXT UNIQUE,
        count INTEGER DEFAULT 1
    );
    ''')

    # Create Pokemon table with self-referencing evolves_from and evolves_to
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Pokemon (
        id TEXT,
        name TEXT,
        hp INTEGER,
        supertype TEXT,
        type TEXT,
        evolves_from TEXT,
        evolves_to TEXT,
        release_date TEXT,
        set_name TEXT,
        PRIMARY KEY (id, name),
        FOREIGN KEY (evolves_from) REFERENCES Pokemon(id),
        FOREIGN KEY (evolves_to) REFERENCES Pokemon(id),
        FOREIGN KEY (id, name) REFERENCES Card(id, name)
    );
    ''')

    # Create TCGPlayer table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS TCGPlayer (
        url TEXT PRIMARY KEY,
        updated_at TEXT
    );
    ''')

    # Create Prices table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Prices (
        tcgplayer_url TEXT,
        type TEXT,
        low REAL,
        mid REAL,
        high REAL,
        market REAL,
        direct_low REAL,
        PRIMARY KEY (tcgplayer_url, type),
        FOREIGN KEY (tcgplayer_url) REFERENCES TCGPlayer(url)
    );
    ''')

    # Commit changes and close connection
    conn.commit()
    conn.close()


def main():
    init_db()


if __name__ == "__main__":
    main()

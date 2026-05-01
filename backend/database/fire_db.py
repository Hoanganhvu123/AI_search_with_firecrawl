import sqlite3
from pathlib import Path

# Default database path relative to this file
# It points to backend/datadb/fire_search.db
DEFAULT_DB_PATH = Path(__file__).parent.parent / "datadb" / "fire_search.db"
DEFAULT_DB_PATH = DEFAULT_DB_PATH.resolve()

def get_db_connection(db_path=None):
    """Establish a connection to the SQLite database.

    Args:
        db_path (str | Path, optional): Path to the SQLite database file.
                                        Defaults to DEFAULT_DB_PATH.

    Returns:
        sqlite3.Connection: A connection object to the database.
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    else:
        db_path = Path(db_path)

    # Ensure the directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    # Enable row factory to access columns by name
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=None):
    """Initialize the database by creating necessary tables if they don't exist.

    Args:
        db_path (str | Path, optional): Path to the SQLite database file.
                                        Defaults to DEFAULT_DB_PATH.
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH

    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Table to store search queries and their overall status
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending'
    )
    """)

    # Table to store scraped data linked to a specific search
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scraped_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_id INTEGER NOT NULL,
        url TEXT NOT NULL,
        content TEXT,
        markdown TEXT,
        metadata TEXT,
        FOREIGN KEY (search_id) REFERENCES searches (id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # If run directly, initialize the default database
    init_db()
    print(f"Database initialized at: {DEFAULT_DB_PATH}")

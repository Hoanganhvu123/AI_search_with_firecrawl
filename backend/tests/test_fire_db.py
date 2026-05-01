import os
import sqlite3
import pytest
import sys

# Add backend dir to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.fire_db import init_db, get_db_connection

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "datadb", "test_fire_search.db")

@pytest.fixture(autouse=True)
def cleanup():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    yield
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

def test_database_initialization():
    init_db(db_path=TEST_DB_PATH)
    
    assert os.path.exists(TEST_DB_PATH)
    
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    
    # Check searches table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='searches';")
    assert cursor.fetchone() is not None
    
    # Check scraped_data table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scraped_data';")
    assert cursor.fetchone() is not None
    
    # Check columns in searches
    cursor.execute("PRAGMA table_info(searches);")
    columns = [col[1] for col in cursor.fetchall()]
    assert "id" in columns
    assert "query" in columns
    assert "timestamp" in columns
    assert "status" in columns
    
    # Check columns in scraped_data
    cursor.execute("PRAGMA table_info(scraped_data);")
    columns = [col[1] for col in cursor.fetchall()]
    assert "id" in columns
    assert "search_id" in columns
    assert "url" in columns
    assert "content" in columns
    assert "markdown" in columns
    assert "metadata" in columns
    
    conn.close()

def test_get_db_connection():
    init_db(db_path=TEST_DB_PATH)
    conn = get_db_connection(db_path=TEST_DB_PATH)
    assert isinstance(conn, sqlite3.Connection)
    
    # Test if we can execute a query
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    assert cursor.fetchone()[0] == 1
    
    conn.close()

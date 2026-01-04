import sqlite3
from pathlib import Path

DB_PATH = Path("data/blog.db")


def get_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    db = get_db()
    cur = db.cursor()

    # BLOGS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS blogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_name TEXT NOT NULL,
        topic TEXT NOT NULL,
        main_heading TEXT,
        overall_similarity REAL DEFAULT 0,
        status TEXT DEFAULT 'draft',

        is_pinned INTEGER DEFAULT 0,
        is_archived INTEGER DEFAULT 0,
        is_published INTEGER DEFAULT 0,

        image_url TEXT,
        image_position TEXT DEFAULT 'top',

        published_url TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        published_at DATETIME
    )
    """)
    try:
        cur.execute("ALTER TABLE blogs ADD COLUMN image_url TEXT")
    except sqlite3.OperationalError:
        pass  # column already exists

    try:
        cur.execute(
            "ALTER TABLE blogs ADD COLUMN image_position TEXT DEFAULT 'top'"
        )
    except sqlite3.OperationalError:
        pass

    # PARAGRAPHS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS blog_paragraphs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        blog_id INTEGER NOT NULL,
        paragraph_index INTEGER,
        content TEXT,
        similarity_score REAL,
        status TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(blog_id) REFERENCES blogs(id)
    )
    """)

    db.commit()

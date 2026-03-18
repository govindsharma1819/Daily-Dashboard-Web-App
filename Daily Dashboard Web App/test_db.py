import psycopg2
import sqlite3
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create and return a database connection"""
    # Try PostgreSQL first
    try:
        db = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB', 'dashboard_db'),
            port=os.getenv('POSTGRES_PORT', '5432')
        )
        return db, 'postgresql'
    except Exception as e:
        print("❌ PostgreSQL connection failed:", e)
        print("Trying SQLite fallback...")
        
        # Fallback to SQLite
        try:
            db = sqlite3.connect('dashboard.db')
            # Create tables if they don't exist
            cursor = db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Insert default admin user if not exists
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password) 
                VALUES (?, ?)
            ''', ('admin', generate_password_hash('admin123')))
            db.commit()
            cursor.close()
            return db, 'sqlite'
        except Exception as sqlite_error:
            print("❌ SQLite connection failed:", sqlite_error)
            print("Please ensure:")
            print("1. PostgreSQL server is running OR")
            print("2. You have write permissions for the current directory")
            return None, None

# Test the connection
db, db_type = get_db_connection()

if db:
    try:
        if db_type == 'postgresql':
            cursor = db.cursor()
            cursor.execute("SELECT NOW();")
            print("✅ PostgreSQL connected successfully:", cursor.fetchone())
            cursor.close()
        else:  # SQLite
            cursor = db.cursor()
            cursor.execute("SELECT datetime('now');")
            print("✅ SQLite connected successfully:", cursor.fetchone())
            cursor.close()
            
        # Test user query
        if db_type == 'postgresql':
            cursor = db.cursor()
            cursor.execute("SELECT id, username, password FROM users WHERE username = %s", ('admin',))
            user = cursor.fetchone()
            cursor.close()
        else:  # SQLite
            cursor = db.cursor()
            cursor.execute("SELECT id, username, password FROM users WHERE username = ?", ('admin',))
            user = cursor.fetchone()
            cursor.close()
            
        if user:
            print(f"✅ User found: {user}")
        else:
            print("❌ No user found")
    except Exception as e:
        print(f"❌ {db_type} test query failed:", e)
        db = None
else:
    print("⚠️  No database connection available")
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    # Try to connect to PostgreSQL
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB', 'dashboard_db'),
        port=os.getenv('POSTGRES_PORT', '5432')
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print("✅ PostgreSQL connected successfully!")
    print("PostgreSQL version:", version)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print("❌ PostgreSQL connection failed:", e)
    print("Please ensure:")
    print("1. PostgreSQL server is running")
    print("2. Database credentials in .env file are correct")
    print("3. The database 'dashboard_db' exists")
import unittest
import os
import sys
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import psycopg2
import sqlite3

# Load environment variables
load_dotenv()

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestLoginSystem(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Database connection - using the same approach as app.py
        try:
            self.db = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD'),
                dbname=os.getenv('POSTGRES_DB', 'dashboard_db'),
                port=os.getenv('POSTGRES_PORT', '5432')
            )
            self.cursor = self.db.cursor()
            self.db_type = 'postgresql'
        except Exception as e:
            print("PostgreSQL connection failed, using SQLite fallback:", e)
            self.db = sqlite3.connect('dashboard.db')
            self.cursor = self.db.cursor()
            self.db_type = 'sqlite'
        
        # Create a test user
        self.test_username = "testuser123"
        self.test_password = "TestPass123"
        self.hashed_password = generate_password_hash(self.test_password)
        
        # Delete test user if exists
        if self.db_type == 'postgresql':
            self.cursor.execute("DELETE FROM users WHERE username = %s", (self.test_username,))
        else:  # SQLite
            self.cursor.execute("DELETE FROM users WHERE username = ?", (self.test_username,))
        self.db.commit()
        
        # Insert test user
        if self.db_type == 'postgresql':
            self.cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)", 
                (self.test_username, self.hashed_password)
            )
        else:  # SQLite
            self.cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)", 
                (self.test_username, self.hashed_password)
            )
        self.db.commit()
    
    def tearDown(self):
        """Clean up test environment"""
        # Delete test user
        if self.db_type == 'postgresql':
            self.cursor.execute("DELETE FROM users WHERE username = %s", (self.test_username,))
        else:  # SQLite
            self.cursor.execute("DELETE FROM users WHERE username = ?", (self.test_username,))
        self.db.commit()
        self.cursor.close()
        self.db.close()
    
    def test_user_registration(self):
        """Test user registration"""
        # Delete test user if exists
        if self.db_type == 'postgresql':
            self.cursor.execute("DELETE FROM users WHERE username = %s", ("newtestuser",))
        else:  # SQLite
            self.cursor.execute("DELETE FROM users WHERE username = ?", ("newtestuser",))
        self.db.commit()
        
        # Test password validation
        from app import app
        with app.test_client() as client:
            # Test weak password
            response = client.post('/register', data={
                'username': 'newtestuser',
                'password': 'weak'
            })
            self.assertIn(b'Password must be at least 8 characters long', response.data)
            
            # Test strong password
            response = client.post('/register', data={
                'username': 'newtestuser',
                'password': 'StrongPass123'
            })
            # Should redirect to login
            self.assertEqual(response.status_code, 302)
    
    def test_user_login(self):
        """Test user login"""
        from app import app
        with app.test_client() as client:
            # Test correct credentials
            response = client.post('/login', data={
                'username': self.test_username,
                'password': self.test_password
            })
            # Should redirect to dashboard
            self.assertEqual(response.status_code, 302)
            
            # Test incorrect password
            response = client.post('/login', data={
                'username': self.test_username,
                'password': 'wrongpassword'
            })
            self.assertIn(b'Invalid username or password', response.data)
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        if self.db_type == 'postgresql':
            self.cursor.execute(
                "SELECT password FROM users WHERE username = %s", 
                (self.test_username,)
            )
        else:  # SQLite
            self.cursor.execute(
                "SELECT password FROM users WHERE username = ?", 
                (self.test_username,)
            )
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)
        # Check that result is not None before accessing its elements
        self.assertIsNotNone(result)
        if result is not None:
            self.assertNotEqual(result[0], self.test_password)

if __name__ == '__main__':
    unittest.main()
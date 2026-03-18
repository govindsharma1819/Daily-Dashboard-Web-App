from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
import traceback
import os
from dotenv import load_dotenv
from functools import wraps

# Load environment variables
load_dotenv()

print("🔥 Starting app.py...")

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'my-super-secret-key-12345')
app.permanent_session_lifetime = timedelta(minutes=30)

# -------------------------------
# Database Connection (PostgreSQL with SQLite fallback)
# -------------------------------
def get_db_connection():
    """Create and return a database connection"""
    # Try PostgreSQL first
    try:
        db = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD'),  # <-- Using environment variable
            dbname=os.getenv('POSTGRES_DB', 'dashboard_db'),
            port=os.getenv('POSTGRES_PORT', '5432')
        )
        return db, 'postgresql'
    except Exception as e:
        print("❌ PostgreSQL connection failed:", e)
        print("Trying SQLite fallback...")
        
        # Fallback to SQLite
        try:
            # For SQLite, we create a new connection each time to avoid threading issues
            db = sqlite3.connect('dashboard.db', check_same_thread=False)
            db.execute('pragma journal_mode=wal')
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

# Fallback in-memory user storage
users = {
    'admin': generate_password_hash('admin123')
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        # Check if session has expired
        if 'last_activity' in session:
            last_activity = datetime.fromisoformat(session['last_activity'])
            if datetime.now() - last_activity > timedelta(minutes=30):
                session.clear()
                return redirect(url_for('login'))
        
        # Update last activity
        session['last_activity'] = datetime.now().isoformat()
        return f(*args, **kwargs)
    return decorated_function

# Initialize database connection for initial setup only
setup_db, setup_db_type = get_db_connection()

if setup_db:
    try:
        if setup_db_type == 'postgresql':
            cursor = setup_db.cursor()
            cursor.execute("SELECT NOW();")
            print("✅ PostgreSQL connected successfully:", cursor.fetchone())
            cursor.close()
        else:  # SQLite
            cursor = setup_db.cursor()
            cursor.execute("SELECT datetime('now');")
            print("✅ SQLite connected successfully:", cursor.fetchone())
            cursor.close()
        setup_db.close()  # Close the setup connection after initialization
    except Exception as e:
        print(f"❌ {setup_db_type} test query failed:", e)
        if setup_db:
            setup_db.close()
else:
    print("⚠️  Continuing without database connection - some features may not work")

# -------------------------------
# Simple in-memory cache
# -------------------------------
from typing import Dict, Any, Optional

cache: Dict[str, Dict[str, Optional[Any]]] = {
    'stocks': {'data': None, 'timestamp': None},
    'weather': {'data': None, 'timestamp': None},
    'news': {'data': None, 'timestamp': None}
}
CACHE_DURATION = timedelta(minutes=int(os.getenv('CACHE_DURATION_MINUTES', '15')))

# -------------------------------
# API Keys
# -------------------------------
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

def is_cache_valid(cache_type):
    if cache[cache_type]['data'] is None or cache[cache_type]['timestamp'] is None:
        return False
    return datetime.now() - cache[cache_type]['timestamp'] < CACHE_DURATION  # type: ignore

# -------------------------------
# Routes
# -------------------------------
@app.route('/')
def index():
    # Check if session is still valid
    if 'user_id' in session:
        # Check if session has expired
        if 'last_activity' in session:
            last_activity = datetime.fromisoformat(session['last_activity'])
            if datetime.now() - last_activity > timedelta(minutes=30):
                session.clear()
                return redirect(url_for('login'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    global users
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Get fresh database connection for this request
        db, db_type = get_db_connection()
        
        # Check in database first if available, otherwise use in-memory storage
        if db is not None:
            try:
                if db_type == 'postgresql':
                    cursor = db.cursor()
                    cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
                    user = cursor.fetchone()
                    cursor.close()
                    
                    if user and check_password_hash(user[2], password):
                        # Set session permanence based on "Remember Me" checkbox
                        remember = request.form.get('remember')
                        if remember:
                            session.permanent = True
                        else:
                            session.permanent = False
                        session['user_id'] = user[0]
                        session['username'] = user[1]
                        session['last_activity'] = datetime.now().isoformat()
                        db.close()
                        return redirect(url_for('dashboard'))
                    else:
                        db.close()
                        return render_template('login.html', error="Invalid username or password. Please try again.")
                else:  # SQLite
                    cursor = db.cursor()
                    cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
                    user = cursor.fetchone()
                    cursor.close()
                    
                    if user and check_password_hash(user[2], password):
                        # Set session permanence based on "Remember Me" checkbox
                        remember = request.form.get('remember')
                        if remember:
                            session.permanent = True
                        else:
                            session.permanent = False
                        session['user_id'] = user[0]
                        session['username'] = user[1]
                        session['last_activity'] = datetime.now().isoformat()
                        db.close()
                        return redirect(url_for('dashboard'))
                    else:
                        db.close()
                        return render_template('login.html', error="Invalid username or password. Please try again.")
            except Exception as e:
                print("Login DB error:", e)
                traceback.print_exc()
                if db:
                    db.close()
                return "Database query failed", 500
        else:
            # Fallback to in-memory storage
            if username in users and check_password_hash(users[username], password):
                # Set session permanence based on "Remember Me" checkbox
                remember = request.form.get('remember')
                if remember:
                    session.permanent = True
                else:
                    session.permanent = False
                session['user_id'] = 1
                session['username'] = username
                session['last_activity'] = datetime.now().isoformat()
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error="Invalid username or password. Please try again.")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    global users
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Password strength validation
        errors = []
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not any(char.isdigit() for char in password):
            errors.append("Password must contain at least one digit")
            
        if not any(char.isupper() for char in password):
            errors.append("Password must contain at least one uppercase letter")
            
        if not any(char.islower() for char in password):
            errors.append("Password must contain at least one lowercase letter")
            
        if errors:
            return render_template('register.html', error="<br>".join(errors))
        
        # Get fresh database connection for this request
        db, db_type = get_db_connection()
        
        # Register in database if available, otherwise use in-memory storage
        if db is not None:
            try:
                hashed_password = generate_password_hash(password)
                if db_type == 'postgresql':
                    cursor = db.cursor()
                    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
                    db.commit()
                    cursor.close()
                    db.close()
                else:  # SQLite
                    cursor = db.cursor()
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                    db.commit()
                    cursor.close()
                    db.close()
                return redirect(url_for('login'))
            except (psycopg2.IntegrityError, sqlite3.IntegrityError) as e:
                if db:
                    if db_type == 'postgresql':
                        db.rollback()
                    db.close()
                print("Register error:", e)
                traceback.print_exc()
                return render_template('register.html', error="Username already exists. Please choose a different username.")
            except Exception as e:
                if db:
                    if db_type == 'postgresql':
                        db.rollback()
                    db.close()
                print("Register error:", e)
                traceback.print_exc()
                return render_template('register.html', error="An error occurred. Please try again.")
        else:
            # Fallback to in-memory storage
            if username in users:
                return render_template('register.html', error="Username already exists. Please choose a different username.")
            else:
                users[username] = generate_password_hash(password)
                return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get fresh database connection for this request
    db, db_type = get_db_connection()
    
    if db is None:
        print("Database connection failed")
        # Return dashboard without user-specific data
        return render_template('dashboard.html', username=session.get('username', 'User'))
    db.close()
    return render_template('dashboard.html', username=session['username'])

# -------------------------------
# API Endpoints
# -------------------------------
@app.route('/api/stocks')
@login_required
def get_stocks():
    if is_cache_valid('stocks'):
        return jsonify(cache['stocks']['data'])
    stocks_data = {
        'nifty50': {'name': 'NIFTY 50', 'value': '19850.25', 'change': '+125.50', 'change_percent': '+0.64%', 'status': 'up'},
        'sensex': {'name': 'SENSEX', 'value': '66589.93', 'change': '+389.50', 'change_percent': '+0.59%', 'status': 'up'},
        'banknifty': {'name': 'Bank NIFTY', 'value': '44234.15', 'change': '-89.25', 'change_percent': '-0.20%', 'status': 'down'}
    }
    cache['stocks']['data'] = stocks_data
    cache['stocks']['timestamp'] = datetime.now()
    return jsonify(stocks_data)

@app.route('/api/weather')
@login_required
def get_weather():
    location = request.args.get('location', 'Mumbai')
    
    # For testing without API keys, return mock data
    # Remove this section when you have valid API keys
    mock_weather = {
        'location': location,
        'temperature': 32.5,
        'feels_like': 35.2,
        'humidity': 65,
        'description': 'Clear Sky',
        'icon': '01d',
        'wind_speed': 3.5
    }
    return jsonify(mock_weather)
    
    # Uncomment the following code when you have valid API keys:~
    """
    if is_cache_valid('weather'):
        return jsonify(cache['weather']['data'])
    try:
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={location},IN&appid={WEATHER_API_KEY}&units=metric")
        data = response.json()
        if response.status_code != 200:
            return jsonify({'error': 'Location not found'}), 404
        formatted = {
            'location': data['name'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
            'wind_speed': data['wind']['speed']
        }
        cache['weather']['data'] = formatted
        cache['weather']['timestamp'] = datetime.now()
        return jsonify(formatted)
    except Exception as e:
        print("Weather API error:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    """

@app.route('/api/news')
@login_required
def get_news():
    # For testing without API keys, return mock data
    # Remove this section when you have valid API keys
    mock_news = {
        'world_news': [
            {
                'title': 'Global Markets Rally on Positive Economic Data',
                'url': 'https://example.com/news1',
                'source': {'name': 'Financial Times'},
                'publishedAt': '2025-10-28T10:00:00Z',
                'description': 'Stock markets around the world showed strong gains as new economic indicators exceeded expectations.'
            },
            {
                'title': 'Climate Summit Reaches Historic Agreement',
                'url': 'https://example.com/news2',
                'source': {'name': 'BBC News'},
                'publishedAt': '2025-10-28T08:30:00Z',
                'description': 'World leaders have达成 a landmark agreement on carbon emissions reduction targets.'
            }
        ],
        'tech_news': [
            {
                'title': 'New AI Model Breaks Performance Records',
                'url': 'https://example.com/tech1',
                'source': {'name': 'TechCrunch'},
                'publishedAt': '2025-10-28T12:15:00Z',
                'description': 'Researchers have developed an AI model that significantly outperforms existing systems in multiple benchmarks.'
            },
            {
                'title': 'Quantum Computing Milestone Achieved',
                'url': 'https://example.com/tech2',
                'source': {'name': 'Wired'},
                'publishedAt': '2025-10-28T09:45:00Z',
                'description': 'Scientists have successfully demonstrated quantum supremacy in a new computational task.'
            }
        ]
    }
    return jsonify(mock_news)
    
    # Uncomment the following code when you have valid API keys:
    """
    if is_cache_valid('news'):
        return jsonify(cache['news']['data'])
    try:
        world_data = requests.get(f"https://newsapi.org/v2/top-headlines?category=general&pageSize=5&apiKey={NEWS_API_KEY}").json()
        tech_data = requests.get(f"https://newsapi.org/v2/top-headlines?category=technology&pageSize=5&apiKey={NEWS_API_KEY}").json()
        formatted = {'world_news': world_data.get('articles', []), 'tech_news': tech_data.get('articles', [])}
        cache['news']['data'] = formatted
        cache['news']['timestamp'] = datetime.now()
        return jsonify(formatted)
    except Exception as e:
        print("News API error:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    """

# -------------------------------
# Run the app
# -------------------------------
if __name__ == "__main__":
    print("🚀 Flask server starting on http://127.0.0.1:5000 ...")
    app.run(debug=True)

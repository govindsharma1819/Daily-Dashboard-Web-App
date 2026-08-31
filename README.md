



        # Daily Dashboard - Complete Setup Guide

## Project Structure
```
daily-dashboard/
│
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── database_setup.sql          # MySQL database schema
│
├── templates/                  # HTML templates
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   └── dashboard.html         # Main dashboard
│
└── static/                     # Static files
    ├── css/
    │   └── style.css          # Custom CSS styles
    └── js/
        └── dashboard.js       # Dashboard JavaScript
```

## Prerequisites
- Python 3.8 or higher
- MySQL Server 8.0 or higher
- pip (Python package manager)

## Step-by-Step Installation

### 1. Install MySQL
**Windows:**
- Download MySQL Installer from https://dev.mysql.com/downloads/installer/
- Run installer and choose "Developer Default"
- Set root password during installation

**Linux:**
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

**Mac:**
```bash
brew install mysql
brew services start mysql
```

### 2. Create Project Directory
```bash
mkdir daily-dashboard
cd daily-dashboard
```

### 3. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 5. Setup MySQL Database
```bash
# Login to MySQL
mysql -u root -p

# Run the SQL script (from MySQL prompt)
source database_setup.sql;

# Or run directly:
mysql -u root -p < database_setup.sql
```

### 6. Get API Keys

#### OpenWeatherMap API (Weather Data)
1. Go to https://openweathermap.org/api
2. Sign up for free account
3. Navigate to API keys section
4. Copy your API key

#### NewsAPI (News Data)
1. Go to https://newsapi.org/
2. Sign up for free account
3. Copy your API key from dashboard
4. Free tier: 100 requests/day

#### Stock Market API (Optional - for real data)
For Indian stocks, you can use:
- Alpha Vantage: https://www.alphavantage.co/
- Yahoo Finance API (free, no key needed)
- NSE/BSE APIs

### 7. Configure Application
Open `app.py` and update:

```python
# Line 8: Change secret key
app.secret_key = 'your-unique-secret-key-here'

# Lines 11-14: Update MySQL credentials
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
app.config['MYSQL_DB'] = 'dashboard_db'

# Lines 26-27: Add your API keys
WEATHER_API_KEY = 'your_openweathermap_api_key'
NEWS_API_KEY = 'your_newsapi_key'
```

### 8. Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

### 9. Access the Dashboard
1. Open browser and go to `http://localhost:5000`
2. Click "Register" to create an account
3. Login with your credentials
4. Dashboard will load with all data

## Default Login (if using sample data)
- Username: `admin`
- Password: `admin123`

## Features Explanation

### 1. **Authentication System**
- **Technology**: Flask sessions + MySQL
- **Security**: Passwords hashed using Werkzeug's pbkdf2
- **How it works**: User credentials stored in MySQL, sessions managed by Flask

### 2. **Indian Stock Markets**
- **Data Source**: Currently uses mock data (you can integrate real APIs)
- **Updates**: Every 15 minutes (cached)
- **Shows**: NIFTY 50, SENSEX, Bank NIFTY with real-time changes

### 3. **Weather Forecast**
- **API**: OpenWeatherMap
- **Features**: Location-based search, current conditions
- **Data**: Temperature, humidity, wind speed, weather description

### 4. **News Sections**
- **API**: NewsAPI
- **Categories**: World News and Tech News
- **Updates**: Every 15 minutes
- **Shows**: Top 5 headlines from each category

### 5. **Caching System**
- **Purpose**: Reduce API calls, improve performance
- **Duration**: 15 minutes
- **Implementation**: In-memory Python dictionary

## Architecture Overview

### Frontend (HTML + CSS + Bootstrap)
- **Bootstrap 5**: Responsive grid system and components
- **Custom CSS**: Additional styling and animations
- **JavaScript**: AJAX calls to fetch data without page reload

### Backend (Python + Flask)
- **Flask**: Web framework for routing and handling requests
- **Flask-MySQLdb**: MySQL database integration
- **Werkzeug**: Password hashing and security
- **Requests**: HTTP library for API calls

### Database (MySQL)
- **users table**: Stores user credentials
- **user_sessions table**: (Optional) Track login/logout
- **user_preferences table**: (Optional) Store user settings

## API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/` | GET | Redirects to login or dashboard | No |
| `/login` | GET, POST | Login page and authentication | No |
| `/register` | GET, POST | Registration page | No |
| `/logout` | GET | Logout user | Yes |
| `/dashboard` | GET | Main dashboard page | Yes |
| `/api/stocks` | GET | Fetch stock market data | Yes |
| `/api/weather` | GET | Fetch weather data | Yes |
| `/api/news` | GET | Fetch news data | Yes |

## Troubleshooting

### MySQL Connection Error
```
Error: Can't connect to MySQL server
```
**Solution**: Check if MySQL is running, verify credentials in app.py

### API Key Errors
```
Error: 401 Unauthorized
```
**Solution**: Verify API keys are correct and active

### Port Already in Use
```
Error: Address already in use
```
**Solution**: Change port in app.py: `app.run(debug=True, port=5001)`

## Presentation Talking Points

### 1. Project Overview
- "Built a secure daily dashboard for monitoring stocks, weather, and news"
- "Used Flask + MySQL for backend, Bootstrap for responsive frontend"

### 2. Key Features
- **Security**: Password hashing, session management
- **Performance**: API caching to reduce calls and improve speed
- **UX**: Responsive design, real-time updates without page refresh

### 3. Technical Decisions
- **Why Flask?**: Lightweight, easy to learn, perfect for small-medium projects
- **Why MySQL?**: Reliable, widely used, good for structured data
- **Why Bootstrap?**: Rapid development, mobile-first, consistent UI

### 4. Challenges & Solutions
- **Challenge**: API rate limits
  - **Solution**: Implemented 15-minute caching system
- **Challenge**: Security concerns
  - **Solution**: Password hashing, session-based auth

### 5. Future Enhancements
- Add user preferences (save favorite locations)
- Email notifications for stock alerts
- Dark mode toggle
- More data visualizations (charts/graphs)
- Mobile app version

## Production Deployment Tips
1. Use environment variables for sensitive data
2. Enable HTTPS
3. Use production-grade WSGI server (Gunicorn)
4. Set `debug=False` in production
5. Use proper session management (Redis/database)
6. Implement rate limiting
7. Add logging and monitoring

## Need Help?
- Flask Documentation: https://flask.palletsprojects.com/
- Bootstrap Docs: https://getbootstrap.com/docs/
- MySQL Docs: https://dev.mysql.com/doc/

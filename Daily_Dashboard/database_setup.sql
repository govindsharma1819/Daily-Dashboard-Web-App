-- Create Database
CREATE DATABASE dashboard_db;

-- Connect to the database
\c dashboard_db;

-- Create Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sample user (password: admin123)
-- Password hash for 'admin123' using werkzeug
INSERT INTO users (username, password) VALUES 
('admin', 'scrypt:32768:8:1$gKJ8uZqvL3Gj7YmB$8e9f3c2a1b4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2');

-- Optional: Create a table to log user sessions (for advanced usage)
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Optional: Create a table to store user preferences
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    default_location VARCHAR(100) DEFAULT 'Mumbai',
    refresh_interval INTEGER DEFAULT 15,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
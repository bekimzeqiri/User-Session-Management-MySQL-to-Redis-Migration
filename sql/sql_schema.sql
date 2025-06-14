-- Create the database schema for user session management
USE user_session_management;

-- Users table
CREATE TABLE users (
   user_id INT AUTO_INCREMENT PRIMARY KEY,
   username VARCHAR(255) UNIQUE NOT NULL,
   email VARCHAR(255) UNIQUE NOT NULL,
   password_hash VARCHAR(255) NOT NULL,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   last_login_at TIMESTAMP NULL
);

-- User sessions table
CREATE TABLE user_sessions (
   session_id VARCHAR(255) PRIMARY KEY,
   user_id INT NOT NULL,
   ip_address VARCHAR(45),
   user_agent TEXT,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   expires_at TIMESTAMP NOT NULL,
   last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT fk_user
       FOREIGN KEY(user_id)
       REFERENCES users(user_id)
       ON DELETE CASCADE
);

-- Session data table
CREATE TABLE session_data (
   session_data_id INT AUTO_INCREMENT PRIMARY KEY,
   session_id VARCHAR(255) NOT NULL,
   attribute_key VARCHAR(255) NOT NULL,
   attribute_value TEXT,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT fk_session
       FOREIGN KEY(session_id)
       REFERENCES user_sessions(session_id)
       ON DELETE CASCADE,
   CONSTRAINT unique_session_attribute UNIQUE (session_id, attribute_key)
);

-- User preferences table
CREATE TABLE user_preferences (
   preference_id INT AUTO_INCREMENT PRIMARY KEY,
   user_id INT NOT NULL UNIQUE,
   theme VARCHAR(50) DEFAULT 'light',
   language VARCHAR(10) DEFAULT 'en',
   notifications_enabled BOOLEAN DEFAULT TRUE,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   CONSTRAINT fk_user_prefs
       FOREIGN KEY(user_id)
       REFERENCES users(user_id)
       ON DELETE CASCADE
);

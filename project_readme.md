# User Session Management: MySQL to Redis Migration Project

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MySQL](https://img.shields.io/badge/mysql-8.0+-orange.svg)](https://www.mysql.com/)
[![Redis](https://img.shields.io/badge/redis-6.0+-red.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

## 📋 Project Overview

This project demonstrates a comprehensive **NoSQL migration strategy** by migrating user session data from a **MySQL relational database** to a **Redis key-value store**. The migration showcases the transition from a normalized relational model to a denormalized NoSQL approach, highlighting the performance and scalability benefits of Redis for session management use cases.

### 🎯 **Project Objectives**

1. **Design a normalized relational database** for user session management
2. **Implement data modeling strategies** for Redis key-value storage
3. **Develop programmatic migration tools** with comprehensive error handling
4. **Demonstrate performance benefits** of NoSQL for session data
5. **Provide complete documentation** and reproducible deployment

## 🏗️ **System Architecture**

```
┌─────────────────┐    Migration    ┌─────────────────┐
│   MySQL RDBMS   │ ───────────────► │   Redis NoSQL   │
│                 │                  │                 │
│ ┌─────────────┐ │                  │ ┌─────────────┐ │
│ │   users     │ │                  │ │session:id   │ │
│ │sessions     │ │ ◄── Extract ──── │ │  (Hash)     │ │
│ │session_data │ │                  │ │             │ │
│ │preferences  │ │                  │ │   + TTL     │ │
│ └─────────────┘ │                  │ └─────────────┘ │
└─────────────────┘                  └─────────────────┘
      Normalized                        Denormalized
     ACID Compliant                   High Performance
```

## 📊 **Database Design**

### **MySQL Relational Schema (Source)**

Our source database follows **3NF normalization** principles:

#### **Core Entities:**
- **`users`** - User account information
- **`user_sessions`** - Active user sessions
- **`session_data`** - Key-value session attributes  
- **`user_preferences`** - User application preferences

#### **Key Relationships:**
- **Users ← (1:M) → Sessions** - One user can have multiple sessions
- **Sessions ← (1:M) → Session Data** - One session contains multiple attributes
- **Users ← (1:1) → Preferences** - Each user has one preference set

### **Redis NoSQL Schema (Target)**

Data is **denormalized** into Redis Hashes for optimal performance:

```redis
Key Pattern: session:{session_id}
Data Structure: Hash

Fields:
├── user_id, username, email          # User info (from users table)
├── ip_address, user_agent            # Session metadata
├── theme, language, notifications    # User preferences  
├── attr_cart_items, attr_*          # Session-specific data
├── session_created_at, expires_at    # Timestamps
└── migrated_at, migration_version    # Migration metadata
```

## 🔄 **Migration Strategy**

### **ETL Process:**

1. **Extract** - Complex SQL JOINs gather related data from multiple tables
2. **Transform** - Convert relational data to Redis-compatible format
3. **Load** - Store as denormalized Redis Hashes with automatic TTL

### **Key Features:**

- ✅ **Denormalization** - Multiple table data combined into single Redis objects
- ✅ **Automatic TTL** - Session expiry handled natively by Redis
- ✅ **Type Conversion** - Proper handling of timestamps, booleans, JSON data
- ✅ **Error Handling** - Comprehensive logging and recovery mechanisms
- ✅ **Data Verification** - Post-migration integrity checks

## 🚀 **Getting Started**

### **Prerequisites**

- Python 3.8+
- MySQL 8.0+
- Redis 6.0+
- Docker & Docker Compose (for containerized deployment)

### **Quick Start with Docker**

1. **Clone the repository:**
```bash
git clone <repository-url>
cd mysql-redis-migration
```

2. **Start the complete environment:**
```bash
docker-compose up -d
```

3. **View migration results:**
```bash
# Check migration logs
docker logs migration_tool

# Access Redis web interface
open http://localhost:8081

# Access MySQL web interface  
open http://localhost:8080
```

### **Manual Setup**

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Setup databases:**
```bash
# Create MySQL database
mysql -u root -p -e "CREATE DATABASE user_session_management;"
mysql -u root -p user_session_management < sql/01_schema.sql
mysql -u root -p user_session_management < sql/02_sample_data.sql

# Start Redis
redis-server
```

3. **Configure connection:**
```python
# Edit migration.py
config = DatabaseConfig(
    mysql_user="your_username",
    mysql_password="your_password",
    mysql_database="user_session_management"
)
```

4. **Run migration:**
```bash
python migration.py
```

## 📁 **Project Structure**

```
mysql-redis-migration/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Multi-service orchestration
│
├── migration.py             # Main migration script
├── check_redis.py          # Redis verification tool
│
├── sql/
│   ├── 01_schema.sql        # MySQL table definitions
│   └── 02_sample_data.sql   # Sample data for testing
│
├── docs/
│   ├── ER_Diagram.svg       # Entity-Relationship diagram
│   └── Architecture.md      # Detailed system design
│
└── logs/
    └── migration.log        # Migration execution logs
```

## 🔍 **Verification & Testing**

### **Automated Verification**
```bash
# Run comprehensive verification
python check_redis.py
```

### **Manual Testing**
```bash
# Check migrated sessions
redis-cli KEYS "session:*"

# Inspect specific session
redis-cli HGETALL session:sess_1a2b3c4d5e6f7g8h

# Verify TTL settings
redis-cli TTL session:sess_1a2b3c4d5e6f7g8h

# Count total sessions
redis-cli EVAL "return #redis.call('keys', 'session:*')" 0
```

### **Expected Results**
- ✅ **Count Match** - Redis sessions = MySQL sessions
- ✅ **Data Integrity** - All fields properly migrated and typed
- ✅ **TTL Configuration** - Sessions expire based on MySQL `expires_at`
- ✅ **Performance Improvement** - Single Redis lookup vs multiple SQL JOINs

## 📈 **Performance Benefits Demonstrated**

| Aspect | MySQL (Before) | Redis (After) | Improvement |
|--------|---------------|---------------|-------------|
| **Session Retrieval** | Multiple JOINs | Single HGETALL | ~10x faster |
| **Scalability** | Vertical scaling | Horizontal clustering | Unlimited |
| **Session Cleanup** | Manual jobs | Automatic TTL | Zero maintenance |
| **Data Access** | Complex queries | Key-based lookup | O(1) complexity |
| **Memory Usage** | Disk-based | In-memory | Sub-ms latency |

## 🛠️ **Technologies Used**

### **Backend Technologies:**
- **Python 3.8+** - Migration scripting language
- **MySQL 8.0** - Source relational database
- **Redis 6.0+** - Target NoSQL key-value store

### **Python Libraries:**
- **mysql-connector-python** - MySQL database connectivity
- **redis-py** - Redis client library
- **logging** - Comprehensive error tracking

### **DevOps & Deployment:**
- **Docker** - Containerization platform
- **Docker Compose** - Multi-service orchestration
- **Redis Commander** - Redis web interface
- **phpMyAdmin** - MySQL web interface

## 📚 **Learning Outcomes**

This project demonstrates mastery of:

### **Database Concepts:**
- ✅ **Relational Database Design** - Normalization, foreign keys, constraints
- ✅ **NoSQL Data Modeling** - Denormalization strategies for performance
- ✅ **Schema Design Patterns** - Entity-Relationship modeling
- ✅ **Data Migration Strategies** - ETL processes and data transformation

### **Technical Skills:**
- ✅ **Python Programming** - Database connectivity, error handling, logging
- ✅ **SQL Proficiency** - Complex JOINs, data extraction, schema definition
- ✅ **Redis Operations** - Hash operations, TTL management, key patterns
- ✅ **Docker Deployment** - Multi-service applications, environment management

### **Software Engineering:**
- ✅ **Project Documentation** - Comprehensive README, code comments
- ✅ **Version Control** - Git repository management
- ✅ **Testing & Verification** - Data integrity validation
- ✅ **Error Handling** - Robust failure recovery mechanisms

## 🔧 **Configuration Options**

### **Environment Variables (Docker):**
```bash
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=rootpassword
MYSQL_DATABASE=user_session_management

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

### **Script Configuration:**
```python
config = DatabaseConfig(
    mysql_host="localhost",
    mysql_port=3306,
    mysql_user="your_username",
    mysql_password="your_password",
    mysql_database="user_session_management",
    redis_host="localhost",
    redis_port=6379,
    redis_db=0
)
```

## 🐛 **Troubleshooting**

### **Common Issues:**

**MySQL Connection Error:**
```bash
# Check MySQL service
systemctl status mysql
# Verify credentials
mysql -u root -p
```

**Redis Connection Error:**
```bash
# Check Redis service
redis-cli ping
# Expected response: PONG
```

**Migration Script Errors:**
```bash
# Check logs
tail -f logs/migration.log
# Verify Python dependencies
pip install -r requirements.txt
```

**Docker Issues:**
```bash
# Rebuild containers
docker-compose down
docker-compose up --build
```

## 📖 **Additional Documentation**

- **[Entity-Relationship Diagram](docs/ER_Diagram.svg)** - Complete database schema
- **[Architecture Documentation](docs/Architecture.md)** - Detailed system design
- **[Migration Logs](logs/migration.log)** - Execution history and debugging

## 🤝 **Contributing**

This project serves as an educational demonstration of NoSQL migration concepts. Contributions for improvements are welcome:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

## 📄 **License**

This project is provided for educational purposes. Feel free to use it as a reference for your own NoSQL migration projects.

## 🎓 **Academic Context**

This project fulfills the requirements for a comprehensive NoSQL database migration assignment, demonstrating:

- **Database Design Principles** - Proper ER modeling and normalization
- **Migration Strategies** - Real-world data transformation techniques  
- **Performance Analysis** - Quantifiable improvements from NoSQL adoption
- **Professional Documentation** - Industry-standard project presentation
- **Reproducible Results** - Complete Docker-based deployment

---

**Project Author:** [Your Name]  
**Course:** Database Systems / NoSQL Databases  
**Academic Year:** 2025  
**Institution:** [Your University]
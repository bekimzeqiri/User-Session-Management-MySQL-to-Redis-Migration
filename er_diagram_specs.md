# Entity-Relationship Diagram Specifications
## User Session Management System

### **ENTITIES**

#### 1. **USERS** (Strong Entity)
| Attribute | Data Type | Constraints | Description |
|-----------|-----------|-------------|-------------|
| **user_id** | INT | PRIMARY KEY, AUTO_INCREMENT, NOT NULL | Unique identifier for each user |
| username | VARCHAR(255) | UNIQUE, NOT NULL | User's login name |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address |
| password_hash | VARCHAR(255) | NOT NULL | Encrypted password |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |
| last_login_at | TIMESTAMP | NULL | Last successful login time |

**Primary Key:** user_id  
**Unique Constraints:** username, email  
**Business Rules:** Each user must have unique username and email

---

#### 2. **USER_SESSIONS** (Strong Entity)
| Attribute | Data Type | Constraints | Description |
|-----------|-----------|-------------|-------------|
| **session_id** | VARCHAR(255) | PRIMARY KEY, NOT NULL | Unique session identifier |
| user_id | INT | FOREIGN KEY, NOT NULL | References USERS(user_id) |
| ip_address | VARCHAR(45) | NULL | Client IP address (IPv4/IPv6) |
| user_agent | TEXT | NULL | Browser/client information |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Session start time |
| expires_at | TIMESTAMP | NOT NULL | Session expiration time |
| last_activity_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last user activity |

**Primary Key:** session_id  
**Foreign Key:** user_id REFERENCES USERS(user_id) ON DELETE CASCADE  
**Business Rules:** Each session belongs to exactly one user; Sessions must have expiration time

---

#### 3. **SESSION_DATA** (Weak Entity)
| Attribute | Data Type | Constraints | Description |
|-----------|-----------|-------------|-------------|
| **session_data_id** | INT | PRIMARY KEY, AUTO_INCREMENT, NOT NULL | Unique data entry identifier |
| session_id | VARCHAR(255) | FOREIGN KEY, NOT NULL | References USER_SESSIONS(session_id) |
| attribute_key | VARCHAR(255) | NOT NULL | Data attribute name |
| attribute_value | TEXT | NULL | Data attribute value (JSON/string) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Data creation time |

**Primary Key:** session_data_id  
**Foreign Key:** session_id REFERENCES USER_SESSIONS(session_id) ON DELETE CASCADE  
**Unique Constraint:** (session_id, attribute_key) - prevents duplicate keys per session  
**Business Rules:** Weak entity dependent on USER_SESSIONS; Each session can have multiple key-value pairs

---

#### 4. **USER_PREFERENCES** (Strong Entity)
| Attribute | Data Type | Constraints | Description |
|-----------|-----------|-------------|-------------|
| **preference_id** | INT | PRIMARY KEY, AUTO_INCREMENT, NOT NULL | Unique preference record identifier |
| user_id | INT | FOREIGN KEY, UNIQUE, NOT NULL | References USERS(user_id) |
| theme | VARCHAR(50) | DEFAULT 'light' | UI theme preference |
| language | VARCHAR(10) | DEFAULT 'en' | Language preference (ISO code) |
| notifications_enabled | BOOLEAN | DEFAULT TRUE | Notification settings |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Last preference update |

**Primary Key:** preference_id  
**Foreign Key:** user_id REFERENCES USERS(user_id) ON DELETE CASCADE  
**Unique Constraint:** user_id (one preference record per user)  
**Business Rules:** Each user can have at most one preference record

---

### **RELATIONSHIPS**

#### 1. **USERS HAS USER_SESSIONS**
- **Type:** One-to-Many (1:M)
- **Cardinality:** One user can have multiple sessions
- **Participation:** 
  - USERS: Partial (users may not have active sessions)
  - USER_SESSIONS: Total (every session must belong to a user)
- **Referential Integrity:** CASCADE DELETE (deleting user removes all sessions)

#### 2. **USER_SESSIONS CONTAINS SESSION_DATA**
- **Type:** One-to-Many (1:M)
- **Cardinality:** One session can have multiple data attributes
- **Participation:**
  - USER_SESSIONS: Partial (sessions may have no custom data)
  - SESSION_DATA: Total (every data entry belongs to a session)
- **Referential Integrity:** CASCADE DELETE (deleting session removes all data)
- **Note:** This creates a weak entity relationship

#### 3. **USERS HAS USER_PREFERENCES**
- **Type:** One-to-One (1:1)
- **Cardinality:** Each user has at most one preference record
- **Participation:**
  - USERS: Partial (users may not have set preferences)
  - USER_PREFERENCES: Total (every preference record belongs to a user)
- **Referential Integrity:** CASCADE DELETE (deleting user removes preferences)

---

### **FUNCTIONAL DEPENDENCIES**

#### Primary Functional Dependencies:
1. **user_id → {username, email, password_hash, created_at, last_login_at}**
2. **session_id → {user_id, ip_address, user_agent, created_at, expires_at, last_activity_at}**
3. **session_data_id → {session_id, attribute_key, attribute_value, created_at}**
4. **preference_id → {user_id, theme, language, notifications_enabled, updated_at}**

#### Secondary Functional Dependencies:
1. **username → user_id** (due to UNIQUE constraint)
2. **email → user_id** (due to UNIQUE constraint)
3. **(session_id, attribute_key) → attribute_value** (composite key for session data)

---

### **CONSTRAINTS SUMMARY**

#### **Integrity Constraints:**
- **Entity Integrity:** All primary keys are non-null and unique
- **Referential Integrity:** All foreign keys reference valid primary keys
- **Domain Integrity:** All attributes have appropriate data types and constraints

#### **Business Rules Constraints:**
1. **User Uniqueness:** No two users can have the same username or email
2. **Session Expiry:** Every session must have an expiration timestamp
3. **Session Data Uniqueness:** Each session can have only one value per attribute key
4. **User Preferences Uniqueness:** Each user can have at most one preference record
5. **Cascade Deletion Rules:**
   - Deleting a user removes all their sessions, session data, and preferences
   - Deleting a session removes all its associated data

#### **Data Type Constraints:**
- **VARCHAR lengths:** Appropriate for expected data sizes
- **TIMESTAMP handling:** Automatic timestamp management where appropriate
- **Boolean defaults:** Sensible defaults for user preferences
- **NULL handling:** Optional fields properly marked as nullable

---

### **NORMALIZATION ANALYSIS**

#### **First Normal Form (1NF):** ✅
- All attributes contain atomic values
- No repeating groups

#### **Second Normal Form (2NF):** ✅  
- In 1NF and no partial dependencies on composite keys
- SESSION_DATA table properly handles composite key (session_id, attribute_key)

#### **Third Normal Form (3NF):** ✅
- In 2NF and no transitive dependencies
- All non-key attributes depend directly on primary keys

#### **BCNF (Boyce-Codd Normal Form):** ✅
- In 3NF and every determinant is a candidate key
- All functional dependencies have candidate keys on the left side

---

### **MIGRATION TO REDIS STRATEGY**

The normalized relational structure will be **denormalized** for Redis storage:

```
Redis Key Pattern: session:{session_id}
Redis Data Structure: Hash

Denormalized Fields:
- User info: user_id, username, email
- Session info: ip_address, user_agent, timestamps
- Preferences: theme, language, notifications_enabled
- Session data: all attribute_key/attribute_value pairs
- Metadata: migrated_at, migration_version
```

This ER diagram provides the complete specification your professor is looking for, showing not just entity names but all attributes with their data types, constraints, relationships, cardinalities, and business rules.
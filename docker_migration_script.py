#!/usr/bin/env python3
"""
Docker-optimized MySQL to Redis Migration Script
===============================================
This version reads configuration from environment variables
for use in Docker containers.
"""

import mysql.connector
import redis
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import sys
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Configuration for database connections from environment variables"""
    mysql_host: str = os.getenv('MYSQL_HOST', 'localhost')
    mysql_port: int = int(os.getenv('MYSQL_PORT', '3306'))
    mysql_user: str = os.getenv('MYSQL_USER', 'root')
    mysql_password: str = os.getenv('MYSQL_PASSWORD', 'rootpassword')
    mysql_database: str = os.getenv('MYSQL_DATABASE', 'user_session_management')
    
    redis_host: str = os.getenv('REDIS_HOST', 'localhost')
    redis_port: int = int(os.getenv('REDIS_PORT', '6379'))
    redis_db: int = int(os.getenv('REDIS_DB', '0'))
    redis_password: Optional[str] = os.getenv('REDIS_PASSWORD', None)


class SessionMigrator:
    """Main class for migrating session data from MySQL to Redis"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.mysql_conn = None
        self.redis_conn = None
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        # Ensure logs directory exists
        os.makedirs('/app/logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/app/logs/migration.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    def connect_to_mysql(self) -> bool:
        """Establish connection to MySQL database"""
        try:
            self.mysql_conn = mysql.connector.connect(
                host=self.config.mysql_host,
                port=self.config.mysql_port,
                user=self.config.mysql_user,
                password=self.config.mysql_password,
                database=self.config.mysql_database,
                autocommit=True
            )
            self.logger.info(f"Successfully connected to MySQL at {self.config.mysql_host}:{self.config.mysql_port}")
            return True
        except mysql.connector.Error as e:
            self.logger.error(f"Failed to connect to MySQL: {e}")
            return False
    
    def connect_to_redis(self) -> bool:
        """Establish connection to Redis"""
        try:
            self.redis_conn = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password,
                decode_responses=True
            )
            # Test connection
            self.redis_conn.ping()
            self.logger.info(f"Successfully connected to Redis at {self.config.redis_host}:{self.config.redis_port}")
            return True
        except redis.RedisError as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            return False
    
    def extract_session_data(self) -> List[Dict[str, Any]]:
        """Extract all session data from MySQL using joins"""
        try:
            cursor = self.mysql_conn.cursor(dictionary=True)
            
            query = """
            SELECT 
                us.session_id,
                us.user_id,
                us.ip_address,
                us.user_agent,
                us.created_at AS session_created_at,
                us.expires_at,
                us.last_activity_at,
                u.username,
                u.email,
                u.created_at AS user_created_at,
                u.last_login_at,
                COALESCE(up.theme, 'light') AS theme,
                COALESCE(up.language, 'en') AS language,
                COALESCE(up.notifications_enabled, TRUE) AS notifications_enabled,
                up.updated_at AS preferences_updated_at
            FROM user_sessions us
            INNER JOIN users u ON us.user_id = u.user_id
            LEFT JOIN user_preferences up ON us.user_id = up.user_id
            ORDER BY us.session_id
            """
            
            cursor.execute(query)
            sessions_data = cursor.fetchall()
            
            self.logger.info(f"Extracted {len(sessions_data)} session records from MySQL")
            
            # Get session-specific attributes for each session
            for session in sessions_data:
                session_id = session['session_id']
                
                attr_query = """
                SELECT attribute_key, attribute_value, created_at
                FROM session_data 
                WHERE session_id = %s
                """
                cursor.execute(attr_query, (session_id,))
                attributes = cursor.fetchall()
                
                session['session_attributes'] = {
                    attr['attribute_key']: attr['attribute_value'] 
                    for attr in attributes
                }
                session['raw_attributes'] = attributes
            
            cursor.close()
            return sessions_data
            
        except mysql.connector.Error as e:
            self.logger.error(f"Error extracting data from MySQL: {e}")
            return []
    
    def transform_data_for_redis(self, session_data: Dict[str, Any]) -> Dict[str, str]:
        """Transform MySQL data to Redis Hash format"""
        try:
            redis_hash = {}
            
            # Basic session information
            redis_hash['user_id'] = str(session_data['user_id'])
            redis_hash['username'] = session_data['username'] or ''
            redis_hash['email'] = session_data['email'] or ''
            redis_hash['ip_address'] = session_data['ip_address'] or ''
            redis_hash['user_agent'] = session_data['user_agent'] or ''
            
            # Convert timestamps to ISO format strings
            for field in ['session_created_at', 'expires_at', 'last_activity_at', 'user_created_at', 'last_login_at', 'preferences_updated_at']:
                if session_data[field]:
                    redis_hash[field] = session_data[field].isoformat()
            
            # User preferences
            redis_hash['theme'] = session_data['theme'] or 'light'
            redis_hash['language'] = session_data['language'] or 'en'
            redis_hash['notifications_enabled'] = str(session_data['notifications_enabled']).lower()
            
            # Session-specific attributes
            session_attributes = session_data.get('session_attributes', {})
            for key, value in session_attributes.items():
                redis_hash[f"attr_{key}"] = str(value) if value is not None else ''
            
            # Store all session attributes as JSON
            redis_hash['session_attributes_json'] = json.dumps(session_attributes) if session_attributes else '{}'
            
            # Migration metadata
            redis_hash['migrated_at'] = datetime.now(timezone.utc).isoformat()
            redis_hash['migration_version'] = '1.0'
            
            return redis_hash
            
        except Exception as e:
            self.logger.error(f"Error transforming session data: {e}")
            raise
    
    def calculate_ttl(self, expires_at: datetime) -> Optional[int]:
        """Calculate TTL in seconds"""
        if not expires_at:
            return None
        
        now = datetime.now(timezone.utc)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        ttl_seconds = int((expires_at - now).total_seconds())
        return ttl_seconds if ttl_seconds > 0 else None
    
    def load_session_to_redis(self, session_id: str, session_hash: Dict[str, str], expires_at: datetime) -> bool:
        """Load session hash to Redis with TTL"""
        try:
            redis_key = f"session:{session_id}"
            
            # Store the hash
            self.redis_conn.hset(name=redis_key, mapping=session_hash)
            
            # Set TTL
            ttl = self.calculate_ttl(expires_at)
            if ttl and ttl > 0:
                self.redis_conn.expire(name=redis_key, time=ttl)
                self.logger.debug(f"Set TTL of {ttl} seconds for session {session_id}")
            else:
                self.logger.warning(f"Session {session_id} has already expired, but storing anyway")
            
            return True
            
        except redis.RedisError as e:
            self.logger.error(f"Error loading session {session_id} to Redis: {e}")
            return False
    
    def verify_migration(self, original_count: int) -> bool:
        """Verify the migration results"""
        try:
            redis_keys = self.redis_conn.keys("session:*")
            redis_count = len(redis_keys)
            
            self.logger.info(f"Verification: MySQL sessions: {original_count}, Redis sessions: {redis_count}")
            
            if redis_count != original_count:
                self.logger.warning(f"Count mismatch! Expected {original_count}, found {redis_count}")
                return False
            
            # Sample verification
            sample_size = min(3, redis_count)
            if sample_size > 0:
                for redis_key in redis_keys[:sample_size]:
                    session_id = redis_key.split(':', 1)[1]
                    redis_hash = self.redis_conn.hgetall(redis_key)
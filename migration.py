"""
MySQL to Redis Migration Script for User Session Management
===========================================================

This script migrates user session data from a MySQL relational database
to Redis key-value store, following the denormalization strategy outlined
in the migration guide.

"""

import mysql.connector
import redis
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import sys
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Configuration for database connections"""
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "your_username"
    mysql_password: str = "your_password"
    mysql_database: str = "user_session_management"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None  # Set if Redis has password


class SessionMigrator:
    """Main class for migrating session data from MySQL to Redis"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.mysql_conn = None
        self.redis_conn = None
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('migration.log'),
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
            self.logger.info("Successfully connected to MySQL database")
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
                decode_responses=True  # Automatically decode byte responses to strings
            )
            # Test connection
            self.redis_conn.ping()
            self.logger.info("Successfully connected to Redis")
            return True
        except redis.RedisError as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            return False

    def extract_session_data(self) -> List[Dict[str, Any]]:
        """
        Extract all session data from MySQL using joins to gather
        related user and preference information
        """
        try:
            cursor = self.mysql_conn.cursor(dictionary=True)

            # Query to join all related session data
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

            # Now get session-specific attributes for each session
            for session in sessions_data:
                session_id = session['session_id']

                # Get session data attributes
                attr_query = """
                SELECT attribute_key, attribute_value, created_at
                FROM session_data 
                WHERE session_id = %s
                """
                cursor.execute(attr_query, (session_id,))
                attributes = cursor.fetchall()

                # Store attributes as a dictionary within the session data
                session['session_attributes'] = {
                    attr['attribute_key']: attr['attribute_value']
                    for attr in attributes
                }

                # Store the raw attributes for reference
                session['raw_attributes'] = attributes

            cursor.close()
            return sessions_data

        except mysql.connector.Error as e:
            self.logger.error(f"Error extracting data from MySQL: {e}")
            return []

    def transform_data_for_redis(self, session_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Transform a single session record from MySQL format to Redis Hash format.
        All values must be strings as Redis Hash fields store string values.
        """
        try:
            # Creates the Redis hash dictionary
            redis_hash = {}

            # Basic session information
            redis_hash['user_id'] = str(session_data['user_id'])
            redis_hash['username'] = session_data['username'] or ''
            redis_hash['email'] = session_data['email'] or ''
            redis_hash['ip_address'] = session_data['ip_address'] or ''
            redis_hash['user_agent'] = session_data['user_agent'] or ''

            # Convert timestamps to ISO format strings
            if session_data['session_created_at']:
                redis_hash['session_created_at'] = session_data['session_created_at'].isoformat()

            if session_data['expires_at']:
                redis_hash['expires_at'] = session_data['expires_at'].isoformat()

            if session_data['last_activity_at']:
                redis_hash['last_activity_at'] = session_data['last_activity_at'].isoformat()

            if session_data['user_created_at']:
                redis_hash['user_created_at'] = session_data['user_created_at'].isoformat()

            if session_data['last_login_at']:
                redis_hash['last_login_at'] = session_data['last_login_at'].isoformat()

            if session_data['preferences_updated_at']:
                redis_hash['preferences_updated_at'] = session_data['preferences_updated_at'].isoformat()

            # User preferences (denormalized from UserPreferences table)
            redis_hash['theme'] = session_data['theme'] or 'light'
            redis_hash['language'] = session_data['language'] or 'en'
            redis_hash['notifications_enabled'] = str(session_data['notifications_enabled']).lower()

            # Session-specific attributes from SessionData table
            # Store as individual fields in the hash
            session_attributes = session_data.get('session_attributes', {})
            for key, value in session_attributes.items():
                # Prefix session attributes to avoid conflicts
                redis_hash[f"attr_{key}"] = str(value) if value is not None else ''

            # Also store all session attributes as a single JSON field for complex queries
            if session_attributes:
                redis_hash['session_attributes_json'] = json.dumps(session_attributes)
            else:
                redis_hash['session_attributes_json'] = '{}'

            # Add migration metadata
            redis_hash['migrated_at'] = datetime.now(timezone.utc).isoformat()
            redis_hash['migration_version'] = '1.0'

            return redis_hash

        except Exception as e:
            self.logger.error(f"Error transforming session data: {e}")
            raise

    def calculate_ttl(self, expires_at: datetime) -> Optional[int]:
        """
        Calculate TTL in seconds from current time to expiration time.
        Returns None if the session has already expired.
        """
        if not expires_at:
            return None

        now = datetime.now(timezone.utc)
        # Ensure expires_at is timezone aware
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        ttl_seconds = int((expires_at - now).total_seconds())

        # Return None if already expired (negative TTL)
        return ttl_seconds if ttl_seconds > 0 else None

    def load_session_to_redis(self, session_id: str, session_hash: Dict[str, str],
                            expires_at: datetime) -> bool:
        """
        Load a single session hash to Redis and set its TTL
        """
        try:
            redis_key = f"session:{session_id}"

            # Store the hash in Redis
            self.redis_conn.hset(name=redis_key, mapping=session_hash)

            # Set TTL based on expires_at
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
        """
        Verify the migration by checking counts and sampling data
        """
        try:
            # Count Redis keys matching session:* pattern
            redis_keys = self.redis_conn.keys("session:*")
            redis_count = len(redis_keys)

            self.logger.info(f"Verification: MySQL sessions: {original_count}, Redis sessions: {redis_count}")

            if redis_count != original_count:
                self.logger.warning(f"Count mismatch! Expected {original_count}, found {redis_count}")
                return False

            # Sample keys for detailed verification
            sample_size = min(3, redis_count)
            if sample_size > 0:
                sample_keys = redis_keys[:sample_size]

                for redis_key in sample_keys:
                    session_id = redis_key.split(':', 1)[1]  # Remove 'session:' prefix

                    # Get hash from Redis
                    redis_hash = self.redis_conn.hgetall(redis_key)

                    # Check TTL
                    ttl = self.redis_conn.ttl(redis_key)

                    self.logger.info(f"Sample verification for {redis_key}:")
                    self.logger.info(f"  - Hash fields: {len(redis_hash)}")
                    self.logger.info(f"  - TTL: {ttl} seconds")
                    self.logger.info(f"  - User ID: {redis_hash.get('user_id', 'N/A')}")
                    self.logger.info(f"  - Username: {redis_hash.get('username', 'N/A')}")

            return True

        except Exception as e:
            self.logger.error(f"Error during verification: {e}")
            return False

    def main_migration_process(self) -> bool:
        """
        Main migration orchestration method
        """
        self.logger.info("Starting MySQL to Redis migration process")

        # Step 1: Connect to both databases
        if not self.connect_to_mysql():
            return False

        if not self.connect_to_redis():
            return False

        try:
            # Step 2: Extract data from MySQL
            self.logger.info("Extracting session data from MySQL...")
            sessions_data = self.extract_session_data()

            if not sessions_data:
                self.logger.warning("No session data found to migrate")
                return True

            # Step 3: Transform and load data to Redis
            successful_migrations = 0
            failed_migrations = 0

            self.logger.info(f"Starting migration of {len(sessions_data)} sessions...")

            for session_data in sessions_data:
                try:
                    session_id = session_data['session_id']

                    # Transform data
                    redis_hash = self.transform_data_for_redis(session_data)

                    # Load to Redis
                    if self.load_session_to_redis(session_id, redis_hash, session_data['expires_at']):
                        successful_migrations += 1
                        if successful_migrations % 10 == 0:  # Log progress every 10 records
                            self.logger.info(f"Migrated {successful_migrations} sessions...")
                    else:
                        failed_migrations += 1

                except Exception as e:
                    self.logger.error(f"Error migrating session {session_data.get('session_id', 'unknown')}: {e}")
                    failed_migrations += 1

            # Step 4: Verify migration
            self.logger.info(f"Migration completed. Success: {successful_migrations}, Failed: {failed_migrations}")

            if successful_migrations > 0:
                verification_success = self.verify_migration(len(sessions_data))
                if verification_success:
                    self.logger.info("Migration verification passed!")
                else:
                    self.logger.warning("Migration verification failed!")
                    return False

            return failed_migrations == 0

        except Exception as e:
            self.logger.error(f"Unexpected error during migration: {e}")
            return False

        finally:
            # Close connections
            if self.mysql_conn:
                self.mysql_conn.close()
                self.logger.info("MySQL connection closed")

            if self.redis_conn:
                # Redis connection will close automatically
                self.logger.info("Redis connection closed")


def main():
    """
    Main function to run the migration
    """
    print("MySQL to Redis Session Migration Tool")
    print("=====================================")

    # Create configuration
    config = DatabaseConfig(
        mysql_host="localhost",
        mysql_port=3306,
        mysql_user="pycharm_user",
        mysql_password="your_password",
        mysql_database="user_session_management",
        redis_host="localhost",
        redis_port=6379,
        redis_db=0
    )
    
    # Create migrator instance
    migrator = SessionMigrator(config)
    
    # Run migration
    success = migrator.main_migration_process()
    
    if success:
        print("\n Migration completed successfully!")
        print("Check the migration.log file for detailed logs.")
        print("\nTo verify in Redis, try:")
        print("  redis-cli KEYS 'session:*'")
        print("  redis-cli HGETALL session:<some_session_id>")
    else:
        print("\n Migration failed! Check the migration.log file for errors.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
import redis
import json

def connect_to_redis():
    """Connect to Redis"""
    try:
        r = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        r.ping()
        print("Connected to Redis successfully")
        return r
    except redis.RedisError as e:
        print(f"Failed to connect to Redis: {e}")
        return None

def check_migration_results(r: redis.Redis):
    """Check the results of the migration"""

    print("\n" + "="*50)
    print("REDIS MIGRATION VERIFICATION")
    print("="*50)

    # Get all session keys
    session_keys = r.keys("session:*")
    print(f"\nTotal sessions found: {len(session_keys)}")

    if not session_keys:
        print("No session keys found!")
        return

    # Show first few session keys
    print(f"\n First 5 session keys:")
    for i, key in enumerate(session_keys[:5]):
        print(f"  {i+1}. {key}")

    # Detailed inspection of first session
    if session_keys:
        first_key = session_keys[0]
        print(f"\n Detailed inspection of: {first_key}")
        session_data = r.hgetall(first_key)

        print(f"  Total fields: {len(session_data)}")
        print(f"  TTL: {r.ttl(first_key)} seconds")

        # Show important fields
        important_fields = ['user_id', 'username', 'email', 'theme', 'language', 'ip_address']
        print(f"  Key information:")
        for field in important_fields:
            if field in session_data:
                print(f"    {field}: {session_data[field]}")

        # Show session attributes if any
        if 'session_attributes_json' in session_data:
            try:
                attrs = json.loads(session_data['session_attributes_json'])
                if attrs:
                    print(f"  Session attributes: {attrs}")
            except json.JSONDecodeError:
                print(f"  Invalid JSON in session_attributes_json")

    # Check TTL distribution
    print(f"\n TTL Analysis:")
    ttl_counts = {'expired': 0, 'no_ttl': 0, 'active': 0}
    ttl_values = []

    for key in session_keys[:10]:  # Check first 10 for performance
        ttl = r.ttl(key)
        if ttl == -2:
            ttl_counts['expired'] += 1
        elif ttl == -1:
            ttl_counts['no_ttl'] += 1
        else:
            ttl_counts['active'] += 1
            ttl_values.append(ttl)

    print(f"  Active sessions: {ttl_counts['active']}")
    print(f"  No TTL set: {ttl_counts['no_ttl']}")
    print(f"  Expired: {ttl_counts['expired']}")

    if ttl_values:
        print(f"  Average TTL: {sum(ttl_values) / len(ttl_values):.0f} seconds")
        print(f"  Max TTL: {max(ttl_values)} seconds")
        print(f"  Min TTL: {min(ttl_values)} seconds")

def show_sample_sessions(r: redis.Redis, count: int = 3):
    """Show detailed view of sample sessions"""
    session_keys = r.keys("session:*")

    print(f"\n" + "="*50)
    print(f"SAMPLE SESSION DATA ({min(count, len(session_keys))} sessions)")
    print("="*50)

    for i, key in enumerate(session_keys[:count]):
        print(f"\n Session {i+1}: {key}")
        session_data = r.hgetall(key)
        ttl = r.ttl(key)

        print(f"   TTL: {ttl} seconds")
        print(f"   Fields ({len(session_data)}):")

        # Group fields for better display
        basic_fields = {}
        timestamp_fields = {}
        preference_fields = {}
        attr_fields = {}
        other_fields = {}

        for field, value in session_data.items():
            if field in ['user_id', 'username', 'email', 'ip_address', 'user_agent']:
                basic_fields[field] = value
            elif 'created_at' in field or 'updated_at' in field or 'login_at' in field or 'activity_at' in field or 'expires_at' in field:
                timestamp_fields[field] = value
            elif field in ['theme', 'language', 'notifications_enabled']:
                preference_fields[field] = value
            elif field.startswith('attr_'):
                attr_fields[field] = value
            else:
                other_fields[field] = value

        if basic_fields:
            print(f"     Basic Info:")
            for k, v in basic_fields.items():
                print(f"       {k}: {v}")

        if preference_fields:
            print(f"      Preferences:")
            for k, v in preference_fields.items():
                print(f"       {k}: {v}")

        if attr_fields:
            print(f"       Attributes:")
            for k, v in attr_fields.items():
                print(f"       {k}: {v}")

        if timestamp_fields:
            print(f"     Timestamps:")
            for k, v in list(timestamp_fields.items())[:3]:  # Show only first 3
                print(f"       {k}: {v}")

        print(f"     Other fields: {len(other_fields)}")

def check_redis_info(r: redis.Redis):
    """Show Redis server information"""
    print(f"\n" + "="*50)
    print("REDIS SERVER INFO")
    print("="*50)

    info = r.info()

    print(f"Redis Version: {info.get('redis_version', 'Unknown')}")
    print(f"Connected Clients: {info.get('connected_clients', 'Unknown')}")
    print(f"Total Keys: {info.get('db0', {}).get('keys', 0) if 'db0' in info else 0}")
    print(f"Memory Used: {info.get('used_memory_human', 'Unknown')}")
    print(f"Max Memory: {info.get('maxmemory_human', 'Not set')}")

def main():
    """Main function"""
    print("Redis Migration Checker")
    print("======================")

    # Connect to Redis
    r = connect_to_redis()
    if not r:
        return 1

    # Run checks
    check_migration_results(r)
    show_sample_sessions(r, count=2)
    check_redis_info(r)

    print(f"\n" + "="*50)
    print("MANUAL VERIFICATION COMMANDS")
    print("="*50)
    print("To manually check Redis, try these commands:")
    print("  redis-cli KEYS 'session:*'")
    print("  redis-cli HGETALL session:<session_id>")
    print("  redis-cli TTL session:<session_id>")
    print("  redis-cli DBSIZE")
    print("  redis-cli INFO memory")

    return 0

if __name__ == "__main__":
    exit(main())
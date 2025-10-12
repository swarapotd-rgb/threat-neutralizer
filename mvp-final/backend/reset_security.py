import sqlite3
from datetime import datetime
import sys

def log_activity(cursor, username, role, action, details):
    """Log security-related activities to the database"""
    timestamp = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO audit_logs (timestamp, username, role, action, details)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, username, role, action, details))

def reset_user_security(username):
    """Reset security monitoring state for a specific user"""
    try:
        conn = sqlite3.connect("secure.db")
        cursor = conn.cursor()
        
        # Get current user status
        cursor.execute("SELECT account_locked, lock_until FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if not result:
            print(f"❌ Error: User {username} not found")
            return False
        
        # Reset database security flags
        cursor.execute("""
            UPDATE users 
            SET failed_login_attempts = 0,
                account_locked = 0,
                lock_until = NULL
            WHERE username = ?
        """, (username,))
        
        # Log the reset action
        log_activity(
            cursor,
            username=username,
            role="system",
            action="security_reset",
            details="Security monitoring state reset by admin"
        )
        
        conn.commit()
        
        print(f"\n✅ Security monitoring reset for user: {username}")
        print("   • Cleared security flags")
        print("   • Reset login attempt counter")
        print("   • Removed account locks")
        print("   • User can now login normally")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error resetting security monitoring: {e}")
        return False
    finally:
        conn.close()

def reset_all_users():
    """Reset security monitoring for all users"""
    try:
        conn = sqlite3.connect("secure.db")
        cursor = conn.cursor()
        
        # Reset all user security flags
        cursor.execute("""
            UPDATE users 
            SET failed_login_attempts = 0,
                account_locked = 0,
                lock_until = NULL
        """)
        
        # Log the reset action
        log_activity(
            cursor,
            username="system",
            role="system",
            action="security_reset_all",
            details="Complete security monitoring system reset"
        )
        
        conn.commit()
        
        print("\n✅ Security monitoring system reset complete")
        print("   • Cleared all security flags")
        print("   • Reset all login attempt counters")
        print("   • Removed all account locks")
        print("   • System restored to initial state")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error resetting security monitoring system: {e}")
        return False
    finally:
        conn.close()

def main():
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  Reset specific user:  python reset_security.py user <username>")
        print("  Reset all users:      python reset_security.py all")
        return
    
    command = sys.argv[1].lower()
    
    if command == "user" and len(sys.argv) == 3:
        username = sys.argv[2]
        reset_user_security(username)
    elif command == "all":
        reset_all_users()
    else:
        print("\n❌ Invalid command")
        print("\nUsage:")
        print("  Reset specific user:  python reset_security.py user <username>")
        print("  Reset all users:      python reset_security.py all")

if __name__ == "__main__":
    main()
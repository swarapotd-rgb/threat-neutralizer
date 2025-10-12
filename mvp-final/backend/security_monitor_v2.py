import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import requests
import json
import pyotp
import time
from datetime import datetime, timedelta
import sqlite3

# Configuration
API_URL = "http://localhost:8000"
ADMIN_TOKEN = None
CHECK_INTERVAL = 30  # seconds between checks
SESSION_SIZE = 10   # events per session
ANOMALY_THRESHOLD = -0.5

# Database connection
conn = sqlite3.connect("secure.db", check_same_thread=False)
cursor = conn.cursor()

def generate_baseline_sessions():
    """Generate baseline normal behavior patterns"""
    baseline_sessions = []
    
    # Normal admin behavior patterns
    normal_patterns = [
        # Pattern 1: Regular log review
        {
            'actions': ['login_success', 'logs_retrieved', 'logs_retrieved', 'logs_retrieved', 
                       'file_accessed', 'file_accessed', 'agent_accessed', 'location_accessed', 
                       'operation_accessed', 'logout'],
            'durations': [100, 200, 200, 200, 300, 300, 250, 250, 300, 100],
            'hour_range': (9, 17)  # Business hours
        },
        # Pattern 2: Security audit
        {
            'actions': ['login_success', 'logs_retrieved', 'user_checked', 'user_checked',
                       'file_accessed', 'location_accessed', 'agent_accessed', 'operation_accessed',
                       'logs_retrieved', 'logout'],
            'durations': [100, 300, 200, 200, 250, 250, 250, 300, 200, 100],
            'hour_range': (9, 17)
        },
        # Pattern 3: Operation monitoring
        {
            'actions': ['login_success', 'operation_accessed', 'operation_accessed', 'agent_accessed',
                       'location_accessed', 'file_accessed', 'logs_retrieved', 'user_checked',
                       'operation_accessed', 'logout'],
            'durations': [100, 400, 400, 300, 300, 250, 200, 200, 400, 100],
            'hour_range': (9, 17)
        }
    ]
    
    # Generate 100 sessions for each pattern
    for pattern in normal_patterns:
        for _ in range(100):
            hour = np.random.randint(pattern['hour_range'][0], pattern['hour_range'][1])
            base_time = datetime.now().replace(hour=hour, minute=0, second=0)
            
            session = []
            current_time = base_time
            
            for action, duration in zip(pattern['actions'], pattern['durations']):
                # Add some randomness to durations (±20%)
                random_duration = int(duration * np.random.uniform(0.8, 1.2))
                
                session.append({
                    'username': 'admin',
                    'role': 'admin',
                    'timestamp': current_time.isoformat(),
                    'session_duration': random_duration,
                    'stuff_accessed': f"endpoint:/{action.split('_')[0]}",
                    'action': action
                })
                current_time += timedelta(seconds=random_duration)
            
            baseline_sessions.append(session)
    
    return baseline_sessions

def extract_session_features(session):
    """Extract features from a session of events"""
    df = pd.DataFrame(session)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Time-based features
    time_diffs = df['timestamp'].diff().dropna()
    
    # Action-based features
    action_counts = df['action'].value_counts()
    
    # Enhanced login pattern detection
    failed_logins = sum(df['action'] == 'login_failed')
    successful_logins = sum(df['action'] == 'login_success')
    failed_then_success = sum(
        (df['action'] == 'login_failed') & 
        (df['action'].shift(-1) == 'login_success')
    )
    
    # Enhanced file access pattern detection
    file_accesses = df[df['action'].str.contains('file', na=False)]
    file_access_times = pd.to_datetime(file_accesses['timestamp'])
    file_time_diffs = file_access_times.diff().dropna()
    rapid_file_accesses = sum(file_time_diffs.dt.total_seconds() < 5)  # Files accessed within 5 seconds
    
    # Detect file download bursts
    if len(file_time_diffs) > 1:
        file_download_burst = any(td < pd.Timedelta(seconds=10) for td in file_time_diffs)
    else:
        file_download_burst = False
    
    features = {
        'mean_time_between_actions': time_diffs.mean().total_seconds(),
        'std_time_between_actions': time_diffs.std().total_seconds() if len(time_diffs) > 1 else 0,
        'total_duration': df['session_duration'].sum(),
        'mean_duration': df['session_duration'].mean(),
        'std_duration': df['session_duration'].std(),
        'unique_actions': len(action_counts),
        'login_count': successful_logins,
        'failed_login_count': failed_logins,
        'failed_then_success': failed_then_success,
        'file_access_count': sum(df['action'].str.contains('file')),
        'rapid_file_accesses': rapid_file_accesses,
        'file_download_burst': int(file_download_burst),
        'logs_access_count': sum(df['action'].str.contains('logs')),
        'operation_access_count': sum(df['action'].str.contains('operation')),
        'hour_of_day': df['timestamp'].iloc[0].hour,
        'is_business_hours': 1 if 9 <= df['timestamp'].iloc[0].hour <= 17 else 0,
        'rapid_actions': sum(time_diffs.dt.total_seconds() < 1),
        'suspicious_sequences': sum(
            (df['action'] == 'logs_retrieved') & 
            (df['action'].shift(-1) == 'logs_retrieved')
        ),
        'failed_login_ratio': failed_logins / (successful_logins + failed_logins) if (successful_logins + failed_logins) > 0 else 0,
        'file_access_frequency': len(file_accesses) / len(df) if len(df) > 0 else 0
    }
    
    return features

def train_model():
    """Train Isolation Forest on baseline data"""
    baseline_sessions = generate_baseline_sessions()
    
    # Extract features from baseline sessions
    baseline_features = pd.DataFrame([
        extract_session_features(session) 
        for session in baseline_sessions
    ])
    
    # Scale features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(baseline_features)
    
    # Train Isolation Forest
    model = IsolationForest(
        contamination=0.1,
        random_state=42,
        n_estimators=100
    )
    model.fit(scaled_features)
    
    print(f"Model trained on {len(baseline_sessions)} baseline sessions")
    return model, scaler

def admin_login():
    """Login as admin to get token"""
    global ADMIN_TOKEN
    try:
        # Generate TOTP code
        totp = pyotp.TOTP('JBSWY3DPEHPK3PXP')
        current_code = totp.now()
        
        response = requests.post(
            f"{API_URL}/login",
            json={
                "username": "admin",
                "password": "admin123",
                "totp_code": current_code
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            ADMIN_TOKEN = response.json()["token"]
            print("Admin login successful")
            return True
        else:
            print(f"Admin login failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error during admin login: {e}")
        return False

def get_logs():
    """Fetch latest logs"""
    try:
        response = requests.get(
            f"{API_URL}/logs",
            headers={
                "Authorization": f"Bearer {ADMIN_TOKEN}",
                "Content-Type": "application/json"
            }
        )
        if response.status_code == 200:
            return response.json()["logs"]
        elif response.status_code == 401:
            if admin_login():  # Try to login again
                return get_logs()  # Retry the request
        return []
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return []

def reset_user_credentials(username):
    """Reset user's credentials and invalidate their token"""
    try:
        cursor.execute("""
            UPDATE users 
            SET password_hash = 'password',
                current_auth_token = NULL,
                failed_login_attempts = 0,
                account_locked = 0,
                lock_until = NULL
            WHERE username = ?
        """, (username,))
        conn.commit()
        print(f"⚠️ SECURITY ACTION: Reset credentials for user: {username}")
    except Exception as e:
        print(f"Error resetting credentials: {e}")

def reset_security_monitoring(username):
    """Reset security monitoring state for a specific user"""
    try:
        # Reset database security flags
        cursor.execute("""
            UPDATE users 
            SET failed_login_attempts = 0,
                account_locked = 0,
                lock_until = NULL
            WHERE username = ?
        """, (username,))
        conn.commit()
        
        # Clear any active sessions for the user
        if username in current_sessions:
            current_sessions[username] = []
        
        # Log the reset action
        log_activity(
            username=username,
            role="system",
            action="security_reset",
            details="Security monitoring state reset by admin"
        )
        
        print(f"✅ Security monitoring reset for user: {username}")
        print("   • Cleared security flags")
        print("   • Reset login attempt counter")
        print("   • Cleared active session monitoring")
        print("   • Removed account locks")
        print("   • User can now login normally")
        
        return True
    except Exception as e:
        print(f"Error resetting security monitoring: {e}")
        return False

def reset_all():
    """Reset the entire security monitoring system"""
    try:
        # Reset all user security flags
        cursor.execute("""
            UPDATE users 
            SET failed_login_attempts = 0,
                account_locked = 0,
                lock_until = NULL
        """)
        conn.commit()
        
        # Clear all active sessions
        global current_sessions
        current_sessions = {}
        
        # Log the reset action
        log_activity(
            username="system",
            role="system",
            action="security_reset_all",
            details="Complete security monitoring system reset"
        )
        
        print("✅ Security monitoring system reset complete")
        print("   • Cleared all security flags")
        print("   • Reset all login attempt counters")
        print("   • Cleared all active session monitoring")
        print("   • Removed all account locks")
        print("   • System restored to initial state")
        
        return True
    except Exception as e:
        print(f"Error resetting security monitoring system: {e}")
        return False

def check_for_anomalies(model, scaler, current_sessions):
    """Check sessions for anomalous behavior"""
    for username, session in current_sessions.items():
        if len(session) >= SESSION_SIZE:
            # Extract features from the session
            features = extract_session_features(session)
            features_df = pd.DataFrame([features])
            
            # Scale features
            scaled_features = scaler.transform(features_df)
            
            # Get anomaly score
            score = model.decision_function(scaled_features)[0]
            
            print(f"Analyzing session for {username} (score: {score:.3f})")
            
            # Immediate lockout conditions (bypass anomaly score)
            should_lockout = False
            lockout_reason = []

            # 1. Failed login patterns
            if features['failed_login_count'] >= 3:
                should_lockout = True
                lockout_reason.append("Multiple failed login attempts detected")
            
            # 2. Failed then successful login pattern
            if features['failed_then_success'] > 0:
                should_lockout = True
                lockout_reason.append("Successful login after failed attempts - possible credential stuffing")
            
            # 3. Rapid file access patterns
            if features['rapid_file_accesses'] >= 3:
                should_lockout = True
                lockout_reason.append("Suspicious rapid file access pattern")
            
            # 4. File download bursts
            if features['file_download_burst'] == 1:
                should_lockout = True
                lockout_reason.append("Suspicious file download burst detected")

            # 5. High failed login ratio
            if features['failed_login_ratio'] > 0.4:  # More than 40% failed logins
                should_lockout = True
                lockout_reason.append("High ratio of failed logins")

            # 6. Excessive file access frequency
            if features['file_access_frequency'] > 0.5:  # More than 50% of actions are file accesses
                should_lockout = True
                lockout_reason.append("Unusually high file access frequency")
            
            # Check for anomalies or immediate lockout conditions
            if should_lockout or score < ANOMALY_THRESHOLD:
                print(f"🚨 SECURITY ALERT for {username}'s session!")
                
                suspicious_patterns = []
                
                # Add immediate lockout reasons if any
                if lockout_reason:
                    suspicious_patterns.extend(lockout_reason)
                
                # Additional checks for specific suspicious patterns
                # 1. Rapid successive actions
                if features['rapid_actions'] > 3:
                    suspicious_patterns.append("Unusually rapid action sequences")
                
                # 2. Off-hours activity
                if not features['is_business_hours']:
                    suspicious_patterns.append("Activity outside business hours")
                
                # 3. Excessive log retrievals
                if features['logs_access_count'] > 5:
                    suspicious_patterns.append("Excessive log access")
                
                # 4. Unusual action patterns
                if features['suspicious_sequences'] > 2:
                    suspicious_patterns.append("Suspicious action sequences")
                
                if suspicious_patterns:
                    print("Detected suspicious patterns:")
                    for pattern in suspicious_patterns:
                        print(f"- {pattern}")
                    print("\nTaking protective actions...")
                    reset_user_credentials(username)
            
            # Clear the processed session
            current_sessions[username] = []
            
    return current_sessions

def main():
    """Main monitoring loop"""
    print("🔒 Starting security monitoring system...")
    
    # Initial admin login
    if not admin_login():
        print("Failed to perform initial admin login")
        return
    
    # Train the model
    print("Training anomaly detection model...")
    model, scaler = train_model()
    
    # Keep track of sessions per user
    current_sessions = {}
    last_check_time = datetime.now()
    
    print("\n✅ Monitoring system initialized. Watching for suspicious activities...\n")
    
    while True:
        try:
            # Get latest logs
            logs = get_logs()
            current_time = datetime.now()
            
            # Process new logs
            for log in logs:
                username = log['username']
                if username not in current_sessions:
                    current_sessions[username] = []
                
                # Add event to user's current session
                current_sessions[username].append(log)
            
            # Check for anomalies in completed sessions
            current_sessions = check_for_anomalies(model, scaler, current_sessions)
            
            # Sleep until next check
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n👋 Stopping security monitoring...")
            break
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
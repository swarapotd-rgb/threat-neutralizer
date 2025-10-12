import requests
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import json
import time
from datetime import datetime, timedelta
import sqlite3
import pyotp
import warnings
warnings.filterwarnings('ignore')

# Configuration
API_URL = "http://localhost:8000"
ADMIN_TOKEN = None  # Will be set after login
CHECK_INTERVAL = 10  # seconds
ANOMALY_THRESHOLD = -0.5  # Isolation Forest decision function threshold

# Database connection
conn = sqlite3.connect("secure.db", check_same_thread=False)
cursor = conn.cursor()

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
            }
        )
        if response.status_code == 200:
            ADMIN_TOKEN = response.json()["token"]
            print("Admin login successful")
        else:
            print(f"Admin login failed: {response.text}")
    except Exception as e:
        print(f"Error during admin login: {e}")

def get_logs():
    """Fetch latest logs"""
    try:
        response = requests.get(
            f"{API_URL}/logs",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
        )
        if response.status_code == 200:
            return response.json()["logs"]
        else:
            print(f"Error fetching logs: {response.text}")
            if response.status_code == 401:
                admin_login()  # Refresh token
            return []
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return []

def process_logs(logs):
    """Convert logs to features for anomaly detection focusing on admin activities"""
    df = pd.DataFrame(logs)
    
    # Filter only admin logs
    admin_logs = df[df['username'] == 'admin']
    if admin_logs.empty:
        return pd.DataFrame()  # Return empty if no admin logs
    
    # Convert timestamps to datetime
    admin_logs['timestamp'] = pd.to_datetime(admin_logs['timestamp'])
    
    # Time windows for analysis (5 minute windows)
    windows = pd.Grouper(key='timestamp', freq='5T')
    
    # Create features per time window
    features_list = []
    for _, window_logs in admin_logs.groupby(windows):
        if len(window_logs) == 0:
            continue
            
        # Time-based features
        time_diffs = window_logs['timestamp'].diff()
        avg_time_between_actions = time_diffs.mean().total_seconds() if len(time_diffs) > 1 else 0
        
        # Action-based features
        action_counts = window_logs['action'].value_counts()
        sensitive_actions = action_counts.get('logs_retrieved', 0) + \
                          action_counts.get('file_accessed', 0) + \
                          action_counts.get('user_modified', 0)
        
        # Calculate action entropy (diversity of actions)
        action_probs = action_counts / len(window_logs)
        action_entropy = -(action_probs * np.log2(action_probs)).sum()
        
        # Features specific to admin behavior
        features_list.append({
            'timestamp': window_logs['timestamp'].iloc[0],  # Window start
            'actions_per_minute': len(window_logs) / 5.0,  # 5-minute window
            'avg_time_between_actions': avg_time_between_actions,
            'sensitive_actions': sensitive_actions,
            'unique_actions': len(action_counts),
            'action_entropy': action_entropy,
            'failed_operations': len(window_logs[window_logs['action'].str.contains('failed|error', case=False, na=False)]),
            'suspicious_hours': 1 if window_logs['timestamp'].dt.hour.iloc[0] not in range(9, 18) else 0,  # Outside 9 AM to 6 PM
            'rapid_sequences': len(window_logs[window_logs['timestamp'].diff().dt.total_seconds() < 1])  # Actions less than 1 second apart
        })
    
    if not features_list:
        return pd.DataFrame()
        
    features = pd.DataFrame(features_list)
    return features.set_index('timestamp')
    
    return features.set_index('username')

def generate_baseline_data():
    """Generate synthetic baseline data for normal admin behavior"""
    baseline_data = []
    current_time = datetime.now()

    # Generate 24 hours of synthetic normal behavior
    for hour in range(24):
        timestamp = current_time - timedelta(hours=24-hour)
        
        # Business hours (9 AM to 6 PM)
        if 9 <= hour <= 18:
            # Normal working hours - more activity
            num_actions = np.random.randint(5, 15)  # Normal amount of actions per hour
        else:
            # Off hours - less activity
            num_actions = np.random.randint(0, 3)  # Few or no actions

        for _ in range(num_actions):
            action_time = timestamp + timedelta(minutes=np.random.randint(0, 60))
            
            # Generate normal admin activities
            action_types = [
                'login_success',
                'logs_retrieved',
                'file_accessed',
                'user_checked',
                'config_viewed'
            ]
            
            baseline_data.append({
                'username': 'admin',
                'timestamp': action_time.strftime('%Y-%m-%d %H:%M:%S'),
                'action': np.random.choice(action_types),
                'session_duration': np.random.randint(100, 1000),
                'ip_address': '127.0.0.1'
            })
    
    return baseline_data

def load_and_train_model():
    """Load baseline data and train Isolation Forest"""
    try:
        # Generate baseline data for normal behavior
        baseline_data = generate_baseline_data()
        features = process_logs(baseline_data)
        
        if features.empty:
            raise ValueError("No features generated from baseline data")
        
        # Scale features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # Train Isolation Forest
        model = IsolationForest(
            contamination=0.1,  # Expected proportion of anomalies
            random_state=42,
            n_estimators=100
        )
        model.fit(scaled_features)
        
        print("Model trained successfully on baseline data")
        print(f"Number of training samples: {len(features)}")
        print("Feature columns:", features.columns.tolist())
        
        return model, scaler
    except Exception as e:
        print(f"Error training model: {e}")
        return None, None

def reset_user_credentials(username):
    """Reset user's credentials and invalidate their token"""
    try:
        # Set password hash to "password" (an impossible hash)
        cursor.execute("""
            UPDATE users 
            SET password = 'password',
                auth_token = NULL
            WHERE username = ?
        """, (username,))
        conn.commit()
        print(f"Reset credentials for user: {username}")
    except Exception as e:
        print(f"Error resetting credentials: {e}")

def check_for_anomalies(model, scaler):
    """Check latest logs for admin anomalies"""
    if not ADMIN_TOKEN:
        admin_login()
        return
    
    try:
        # Get latest logs
        logs = get_logs()
        if not logs:
            return
        
        # Process logs into features
        features = process_logs(logs)
        if features.empty:
            return
        
        # Scale features
        scaled_features = scaler.transform(features)
        
        # Get anomaly scores
        scores = model.decision_function(scaled_features)
        
        # Check for anomalies in each time window
        for timestamp, score in zip(features.index, scores):
            if score < ANOMALY_THRESHOLD:
                print(f"Anomaly detected in admin activity at {timestamp} (score: {score:.3f})")
                
                # Get logs from this time window
                window_start = timestamp
                window_end = timestamp + timedelta(minutes=5)
                window_logs = pd.DataFrame(logs)
                window_logs['timestamp'] = pd.to_datetime(window_logs['timestamp'])
                window_logs = window_logs[
                    (window_logs['timestamp'] >= window_start) & 
                    (window_logs['timestamp'] < window_end) &
                    (window_logs['username'] == 'admin')
                ]
                
                # Advanced threat detection for admin activities
                threat_indicators = []
                
                # 1. Rapid-fire actions
                if len(window_logs) > 30:  # More than 30 actions in 5 minutes
                    threat_indicators.append("Unusually high action frequency")
                
                # 2. Sensitive operation patterns
                sensitive_ops = window_logs[window_logs['action'].isin([
                    'logs_retrieved', 'file_accessed', 'user_modified', 'config_changed'
                ])]
                if len(sensitive_ops) > 10:
                    threat_indicators.append("High number of sensitive operations")
                
                # 3. Failed operation patterns
                failed_ops = window_logs[window_logs['action'].str.contains('failed|error', case=False, na=False)]
                if len(failed_ops) > 5:
                    threat_indicators.append("Multiple failed operations")
                
                # 4. Time-based anomalies
                hour = timestamp.hour
                if hour < 9 or hour > 18:  # Outside normal business hours
                    threat_indicators.append("Activity outside business hours")
                
                # 5. Rapid sequence detection
                time_diffs = window_logs['timestamp'].diff()
                if len(time_diffs[time_diffs.dt.total_seconds() < 1]) > 5:
                    threat_indicators.append("Suspiciously rapid action sequences")
                
                if threat_indicators:
                    print("Potential admin credential compromise detected!")
                    print("Threat indicators:")
                    for indicator in threat_indicators:
                        print(f"- {indicator}")
                    print("\nTaking protective actions...")
                    reset_user_credentials('admin')
                    
    except Exception as e:
        print(f"Error checking for anomalies: {e}")

def main():
    """Main monitoring loop"""
    print("Starting security monitoring...")
    
    # Initial admin login
    admin_login()
    
    # Load and train model
    model, scaler = load_and_train_model()
    if not model or not scaler:
        print("Failed to initialize model")
        return
    
    print("Model trained, starting monitoring...")
    
    while True:
        try:
            check_for_anomalies(model, scaler)
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\nStopping security monitoring...")
            break
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
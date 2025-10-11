import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# 1. User profiles and organizational structure
users_data = {
    'user_id': ['analyst_1', 'analyst_2', 'analyst_3', 'admin_1', 'admin_2', 
                'operator_1', 'operator_2', 'operator_3', 'contractor_1', 'supervisor_1'],
    'full_name': ['Sarah Chen', 'Michael Rodriguez', 'Emily Johnson', 'David Kim', 'Rachel Thompson',
                  'James Wilson', 'Lisa Garcia', 'Robert Brown', 'Alex Kumar', 'Jennifer Davis'],
    'role': ['analyst', 'analyst', 'analyst', 'admin', 'admin',
             'operator', 'operator', 'operator', 'contractor', 'supervisor'],
    'department': ['Intelligence', 'Intelligence', 'Counter-Intel', 'IT Security', 'IT Security',
                   'Operations', 'Operations', 'Field Ops', 'External', 'Management'],
    'clearance_level': ['SECRET', 'TOP SECRET', 'SECRET', 'TOP SECRET', 'SECRET',
                        'CONFIDENTIAL', 'SECRET', 'TOP SECRET', 'CONFIDENTIAL', 'TOP SECRET'],
    'hire_date': ['2022-03-15', '2021-08-22', '2023-01-10', '2020-11-05', '2022-07-18',
                  '2021-12-03', '2023-04-20', '2020-09-14', '2024-02-01', '2019-06-30'],
    'office_location': ['Building A-3', 'Building A-3', 'Building B-1', 'Building C-2', 'Building C-2',
                        'Building D-4', 'Building D-4', 'Field Office', 'Building E-5', 'Building A-1']
}

users_df = pd.DataFrame(users_data)
print(f"Generated {len(users_df)} user profiles")

# 2. Generate normal behavioral data (30 days)
def generate_comprehensive_normal_data():
    normal_activities = []
    
    for _, user in users_df.iterrows():
        user_id = user['user_id']
        role = user['role']
        
        # Role-specific behavior patterns
        if role == 'analyst':
            daily_actions = (12, 18)  # Range of actions per day
            work_hours = (8, 18)
            action_weights = {
                'login': 0.08, 'file_access': 0.35, 'data_query': 0.25,
                'report_generate': 0.15, 'email_send': 0.10, 'logout': 0.07
            }
        elif role == 'admin':
            daily_actions = (20, 30)
            work_hours = (7, 20)
            action_weights = {
                'login': 0.06, 'system_config': 0.20, 'user_management': 0.15,
                'security_audit': 0.18, 'file_access': 0.25, 'logout': 0.06,
                'patch_install': 0.10
            }
        elif role == 'operator':
            daily_actions = (15, 25)
            work_hours = (6, 22)  # 24/7 operations
            action_weights = {
                'login': 0.08, 'monitor_systems': 0.30, 'incident_response': 0.12,
                'data_query': 0.20, 'file_access': 0.20, 'logout': 0.10
            }
        elif role == 'contractor':
            daily_actions = (8, 15)
            work_hours = (9, 17)
            action_weights = {
                'login': 0.10, 'file_access': 0.40, 'data_query': 0.30,
                'report_generate': 0.15, 'logout': 0.05
            }
        else:  # supervisor
            daily_actions = (10, 20)
            work_hours = (8, 19)
            action_weights = {
                'login': 0.08, 'review_reports': 0.25, 'approve_requests': 0.20,
                'file_access': 0.25, 'meeting_join': 0.15, 'logout': 0.07
            }
        
        # Generate 30 days of activity
        for day in range(30):
            date = datetime.now() - timedelta(days=day)
            
            # Skip weekends for most users (except operators)
            if date.weekday() >= 5 and role != 'operator':
                if random.random() > 0.2:  # 20% chance of weekend work
                    continue
            
            num_actions = np.random.randint(daily_actions[0], daily_actions[1])
            
            for _ in range(num_actions):
                # Generate realistic timestamp
                if role == 'operator' and random.random() < 0.3:  # 30% night shift
                    hour = np.random.uniform(22, 6) % 24
                else:
                    hour = np.random.uniform(work_hours[0], work_hours[1])
                
                timestamp = date.replace(
                    hour=int(hour),
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                )
                
                # Select action based on role weights
                action = np.random.choice(
                    list(action_weights.keys()),
                    p=list(action_weights.values())
                )
                
                # Generate realistic metrics
                session_duration = max(5, np.random.normal(45, 20))
                files_accessed = max(0, np.random.poisson(3))
                data_size_mb = max(0.1, np.random.exponential(15))
                
                # Add some variability based on action type
                if action in ['data_query', 'security_audit']:
                    files_accessed *= 2
                    data_size_mb *= 1.5
                elif action in ['login', 'logout']:
                    files_accessed = 0
                    data_size_mb = 0
                    session_duration = np.random.uniform(1, 5)
                
                normal_activities.append({
                    'timestamp': timestamp,
                    'user_id': user_id,
                    'full_name': user['full_name'],
                    'role': role,
                    'department': user['department'],
                    'clearance_level': user['clearance_level'],
                    'action': action,
                    'session_duration_minutes': round(session_duration, 2),
                    'files_accessed': int(files_accessed),
                    'data_size_mb': round(data_size_mb, 2),
                    'source_ip': f"192.168.{random.randint(1,10)}.{random.randint(100,200)}",
                    'device_type': np.random.choice(['Desktop', 'Laptop', 'Mobile'], p=[0.6, 0.35, 0.05]),
                    'location': user['office_location'],
                    'anomaly_score': round(np.random.uniform(-0.1, 0.2), 3),
                    'is_anomaly': False
                })
    
    return pd.DataFrame(normal_activities)

normal_data = generate_comprehensive_normal_data()
print(f"Generated {len(normal_data)} normal activity records")

# 3. Generate suspicious/anomalous activities
def generate_suspicious_activities():
    suspicious_activities = []
    
    # Scenario 1: After-hours data exfiltration
    user = 'analyst_2'
    base_time = datetime.now().replace(hour=2, minute=30, second=0)
    
    after_hours_sequence = [
        {'action': 'login', 'duration': 8, 'files': 0, 'data_mb': 0, 'offset_min': 0},
        {'action': 'file_access', 'duration': 45, 'files': 25, 'data_mb': 350, 'offset_min': 15},
        {'action': 'data_query', 'duration': 90, 'files': 40, 'data_mb': 800, 'offset_min': 35},
        {'action': 'file_access', 'duration': 60, 'files': 35, 'data_mb': 650, 'offset_min': 55},
        {'action': 'logout', 'duration': 2, 'files': 0, 'data_mb': 0, 'offset_min': 75}
    ]
    
    for activity in after_hours_sequence:
        suspicious_activities.append({
            'timestamp': base_time + timedelta(minutes=activity['offset_min']),
            'user_id': user,
            'full_name': 'Michael Rodriguez',
            'role': 'analyst',
            'department': 'Intelligence',
            'clearance_level': 'TOP SECRET',
            'action': activity['action'],
            'session_duration_minutes': activity['duration'],
            'files_accessed': activity['files'],
            'data_size_mb': activity['data_mb'],
            'source_ip': '192.168.5.150',
            'device_type': 'Laptop',
            'location': 'Building A-3',
            'anomaly_score': round(np.random.uniform(-0.8, -0.3), 3),
            'is_anomaly': True,
            'threat_type': 'After-hours Data Exfiltration'
        })
    
    # Scenario 2: Privilege escalation attempt
    user = 'contractor_1'
    base_time = datetime.now().replace(hour=14, minute=0, second=0)
    
    privilege_escalation = [
        {'action': 'login', 'duration': 5, 'files': 0, 'data_mb': 0, 'offset_min': 0},
        {'action': 'file_access', 'duration': 120, 'files': 50, 'data_mb': 400, 'offset_min': 10},
        {'action': 'system_config', 'duration': 180, 'files': 30, 'data_mb': 200, 'offset_min': 35},
        {'action': 'user_management', 'duration': 90, 'files': 20, 'data_mb': 150, 'offset_min': 60}
    ]
    
    for activity in privilege_escalation:
        suspicious_activities.append({
            'timestamp': base_time + timedelta(minutes=activity['offset_min']),
            'user_id': user,
            'full_name': 'Alex Kumar',
            'role': 'contractor',
            'department': 'External',
            'clearance_level': 'CONFIDENTIAL',
            'action': activity['action'],
            'session_duration_minutes': activity['duration'],
            'files_accessed': activity['files'],
            'data_size_mb': activity['data_mb'],
            'source_ip': '192.168.7.180',
            'device_type': 'Desktop',
            'location': 'Building E-5',
            'anomaly_score': round(np.random.uniform(-0.7, -0.4), 3),
            'is_anomaly': True,
            'threat_type': 'Privilege Escalation'
        })
    
    # Scenario 3: Unusual access patterns
    user = 'operator_2'
    base_time = datetime.now().replace(hour=11, minute=0, second=0)
    
    unusual_patterns = [
        {'action': 'data_query', 'duration': 200, 'files': 80, 'data_mb': 1200, 'offset_min': 0},
        {'action': 'file_access', 'duration': 150, 'files': 60, 'data_mb': 900, 'offset_min': 25},
        {'action': 'data_query', 'duration': 180, 'files': 70, 'data_mb': 1100, 'offset_min': 50}
    ]
    
    for activity in unusual_patterns:
        suspicious_activities.append({
            'timestamp': base_time + timedelta(minutes=activity['offset_min']),
            'user_id': user,
            'full_name': 'Lisa Garcia',
            'role': 'operator',
            'department': 'Operations',
            'clearance_level': 'SECRET',
            'action': activity['action'],
            'session_duration_minutes': activity['duration'],
            'files_accessed': activity['files'],
            'data_size_mb': activity['data_mb'],
            'source_ip': '192.168.4.165',
            'device_type': 'Desktop',
            'location': 'Building D-4',
            'anomaly_score': round(np.random.uniform(-0.6, -0.3), 3),
            'is_anomaly': True,
            'threat_type': 'Unusual Access Pattern'
        })
    
    return pd.DataFrame(suspicious_activities)

suspicious_data = generate_suspicious_activities()
print(f"Generated {len(suspicious_data)} suspicious activity records")

# 4. Generate system logs and alerts
def generate_system_logs():
    log_types = ['Authentication', 'File Access', 'Network', 'System', 'Security']
    severity_levels = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    logs = []
    for i in range(500):
        timestamp = datetime.now() - timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        log_type = random.choice(log_types)
        severity = np.random.choice(severity_levels, p=[0.6, 0.25, 0.1, 0.05])
        
        # Generate realistic log messages
        if log_type == 'Authentication':
            if severity in ['WARNING', 'ERROR']:
                message = f"Failed login attempt from {random.choice(['192.168.1.100', '10.0.0.50', '172.16.0.75'])}"
            else:
                message = f"Successful authentication for user {random.choice(users_df['user_id'])}"
        elif log_type == 'File Access':
            action = random.choice(['READ', 'write', 'delete', 'modify'])
            file_path = f"/classified/intel/{random.choice(['reports', 'data', 'analysis'])}/file_{random.randint(1000,9999)}.pdf"
            message = f"File {action} operation on {file_path}"
        elif log_type == 'Network':
            message = f"Network connection from {random.choice(['VPN', 'LAN', 'WiFi'])} - Bytes transferred: {random.randint(1000, 100000)}"
        elif log_type == 'System':
            message = f"System event: {random.choice(['Service started', 'Service stopped', 'Configuration changed', 'Update installed'])}"
        else:  # Security
            message = f"Security scan completed - {random.randint(0, 5)} threats detected"
        
        logs.append({
            'timestamp': timestamp,
            'log_id': f"LOG-{10000 + i}",
            'log_type': log_type,
            'severity': severity,
            'source_system': random.choice(['DC-01', 'FILE-SRV-02', 'AUTH-SRV-01', 'MON-SRV-03']),
            'user_id': random.choice(users_df['user_id']) if random.random() < 0.7 else None,
            'message': message,
            'source_ip': f"192.168.{random.randint(1,10)}.{random.randint(1,254)}"
        })
    
    return pd.DataFrame(logs)

system_logs = generate_system_logs()
print(f"Generated {len(system_logs)} system log entries")

# 5. Generate file access records
def generate_file_access_records():
    file_types = ['.pdf', '.docx', '.xlsx', '.txt', '.pptx', '.csv']
    classification_levels = ['UNCLASSIFIED', 'CONFIDENTIAL', 'SECRET', 'TOP SECRET']
    access_types = ['read', 'write', 'download', 'print', 'share']
    
    file_accesses = []
    
    for i in range(1000):
        timestamp = datetime.now() - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        user = random.choice(users_df['user_id'])
        user_info = users_df[users_df['user_id'] == user].iloc[0]
        
        file_extension = random.choice(file_types)
        classification = random.choice(classification_levels)
        
        # Generate realistic file paths
        departments = ['intelligence', 'operations', 'security', 'analysis', 'reports']
        department = random.choice(departments)
        file_name = f"{department}_{random.randint(1000, 9999)}{file_extension}"
        file_path = f"/classified/{classification.lower()}/{department}/{file_name}"
        
        access_type = random.choice(access_types)
        
        # Determine if access is authorized based on clearance
        user_clearance = user_info['clearance_level']
        clearance_hierarchy = {'UNCLASSIFIED': 0, 'CONFIDENTIAL': 1, 'SECRET': 2, 'TOP SECRET': 3}
        
        authorized = clearance_hierarchy[user_clearance] >= clearance_hierarchy[classification]
        
        file_accesses.append({
            'timestamp': timestamp,
            'access_id': f"FA-{20000 + i}",
            'user_id': user,
            'file_path': file_path,
            'file_name': file_name,
            'classification': classification,
            'access_type': access_type,
            'file_size_mb': round(random.uniform(0.1, 50.0), 2),
            'authorized': authorized,
            'source_ip': f"192.168.{random.randint(1,10)}.{random.randint(1,254)}",
            'user_clearance': user_clearance,
            'success': authorized and random.random() > 0.05  # 5% failure rate even for authorized
        })
    
    return pd.DataFrame(file_accesses)

file_access_records = generate_file_access_records()
print(f"Generated {len(file_access_records)} file access records")

# 6. Save all datasets
print("\nSaving datasets to CSV files...")

# Save individual datasets
users_df.to_csv('users_profiles.csv', index=False)
normal_data.to_csv('normal_activities.csv', index=False)
suspicious_data.to_csv('suspicious_activities.csv', index=False)
system_logs.to_csv('system_logs.csv', index=False)
file_access_records.to_csv('file_access_records.csv', index=False)

# Combine normal and suspicious for complete activity log
all_activities = pd.concat([normal_data, suspicious_data], ignore_index=True)
all_activities = all_activities.sort_values('timestamp').reset_index(drop=True)
all_activities.to_csv('complete_activity_log.csv', index=False)

print(f"Saved 6 datasets:")
print(f"users_profiles.csv ({len(users_df)} records)")
print(f"normal_activities.csv ({len(normal_data)} records)")
print(f"suspicious_activities.csv ({len(suspicious_data)} records)")
print(f"system_logs.csv ({len(system_logs)} records)")
print(f"file_access_records.csv ({len(file_access_records)} records)")
print(f" omplete_activity_log.csv ({len(all_activities)} records)")

# 7. Generate summary statistics
print(f"\nDataset Summary Statistics:")
print(f"   Total Users: {len(users_df)}")
print(f"   Roles Distribution: {users_df['role'].value_counts().to_dict()}")
print(f"   Clearance Levels: {users_df['clearance_level'].value_counts().to_dict()}")
print(f"   Total Activities: {len(all_activities)}")
print(f"   Anomalies Detected: {len(suspicious_data)} ({len(suspicious_data)/len(all_activities)*100:.1f}%)")
print(f"   Time Range: {all_activities['timestamp'].min()} to {all_activities['timestamp'].max()}")

print(f"\nFake data generation completed successfully!")
print(f"All files saved and ready for Code of Honour 2.0 ML training!")
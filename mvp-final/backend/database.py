import sqlite3, uuid, time, json
from datetime import datetime, timedelta

def calculate_threat_level(priority):
    priority_levels = {
        'High': 'Critical',
        'Medium': 'Elevated',
        'Low': 'Standard'
    }
    return priority_levels.get(priority, 'Unknown')



conn = sqlite3.connect("secure.db", check_same_thread=False)
cursor=conn.cursor()

# Drop existing tables to recreate with new schema
cursor.execute("DROP TABLE IF EXISTS classified_files")
cursor.execute("DROP TABLE IF EXISTS regtokentable")
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("DROP TABLE IF EXISTS audit_logs")

cursor.execute("""
CREATE TABLE regtokentable (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    regtoken TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    totp_secret TEXT NOT NULL,
    current_auth_token TEXT,
    otp TEXT,
    otp_expiry TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked BOOLEAN DEFAULT 0,
    lock_until TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    role TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_duration INTEGER,
    stuff_accessed TEXT,
    action TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS classified_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    file_data BLOB,
    access_level TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_number TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    rank TEXT NOT NULL,
    status TEXT NOT NULL,
    clearance_level TEXT NOT NULL,
    last_mission TEXT,
    photo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    access_level TEXT NOT NULL,
    geolocation TEXT NOT NULL,
    contents TEXT NOT NULL,
    status TEXT NOT NULL,
    last_accessed TIMESTAMP,
    security_level TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id TEXT UNIQUE NOT NULL,
    code_name TEXT NOT NULL,
    status TEXT NOT NULL,
    priority TEXT NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    description TEXT NOT NULL,
    involved_agents TEXT NOT NULL,
    target_location TEXT,
    classified_level TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    action TEXT NOT NULL,
    details TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()



def get_user_by_username(username):
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, username, password_hash, role FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'password_hash': user[2],
                'role': user[3]
            }
        return None
    except Exception as e:
        print(f"Database error: {e}")
        return None

def get_user_by_token(token):
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, username, role FROM users WHERE current_auth_token = ?", (token,))
        user = cur.fetchone()
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'role': user[2]
            }
        return None
    except Exception as e:
        print(f"Database error: {e}")
        return None

def get_classified_files(role):
    try:
        cur = conn.cursor()
        if role == 'admin':
            # Admin can see all files
            cur.execute("SELECT file_id, filename FROM classified_files")
        elif role == 'file_manager':
            # File manager can see files marked for file_manager access and below
            cur.execute("""
                SELECT file_id, filename
                FROM classified_files 
                WHERE access_level = 'file_manager'
            """)
        else:
            # Other roles can't see any files
            return []
            
        files = cur.fetchall()
        return [{'file_id': file[0], 'filename': file[1]} for file in files]
    except Exception as e:
        print(f"Database error: {e}")
        return []

def update_auth_token(username, token):
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET current_auth_token = ? WHERE username = ?", (token, username))
        conn.commit()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False

def verify_auth_token(token, username, role):
    """Verify auth token with additional security checks."""
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT current_auth_token, account_locked, lock_until, last_login 
            FROM users 
            WHERE username = ? AND role = ?
        """, (username, role))
        result = cur.fetchone()
        
        if not result:
            return False
            
        stored_token, account_locked, lock_until, last_login = result
        
        # Check for account lockout
        if account_locked:
            if lock_until and datetime.fromisoformat(lock_until) > datetime.utcnow():
                return False
            else:
                # If lock period has expired, unlock the account
                cur.execute("""
                    UPDATE users 
                    SET account_locked = 0, lock_until = NULL 
                    WHERE username = ?
                """, (username,))
                conn.commit()
        
        # Check if token matches
        if stored_token != token:
            return False
            
        # Check token expiry (if last_login was more than 1 hour ago)
        if last_login:
            login_time = datetime.fromisoformat(last_login)
            if datetime.utcnow() - login_time > timedelta(hours=1):
                return False
                
        # Token is valid, update last activity
        cur.execute("""
            UPDATE users 
            SET last_login = ?
            WHERE username = ?
        """, (datetime.utcnow().isoformat(), username))
        conn.commit()
        
        return True
        
    except Exception as e:
        print(f"Auth token verification error: {e}")
        return False

# Password hashing
from passlib.hash import pbkdf2_sha256

def hash_password(password):
    return pbkdf2_sha256.hash(password)

def verify_password(password, password_hash):
    return pbkdf2_sha256.verify(password, password_hash)

def create_user(username, password, role, totp_secret):
    try:
        cursor = conn.cursor()
        password_hash = hash_password(password)
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, totp_secret)
            VALUES (?, ?, ?, ?)
        """, (username, password_hash, role, totp_secret))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def authenticate_user(username, password):
    """Authenticate a user with enhanced security measures."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, password_hash, role, totp_secret, 
                   failed_login_attempts, account_locked, lock_until
            FROM users 
            WHERE username = ?
        """, (username,))
        user = cursor.fetchone()
        
        if not user:
            # Don't give away that the username doesn't exist
            return None
            
        # Check if account is locked
        if user[6]:  # account_locked
            if user[7] and datetime.fromisoformat(user[7]) > datetime.utcnow():
                return None
            else:
                # If lock period has expired, unlock the account
                cursor.execute("""
                    UPDATE users 
                    SET account_locked = 0, lock_until = NULL, failed_login_attempts = 0 
                    WHERE username = ?
                """, (username,))
                conn.commit()
        
        # Verify password
        if verify_password(password, user[2]):
            # Reset failed attempts on successful login
            cursor.execute("""
                UPDATE users 
                SET failed_login_attempts = 0,
                    last_login = ?,
                    account_locked = 0,
                    lock_until = NULL
                WHERE username = ?
            """, (datetime.utcnow().isoformat(), username))
            conn.commit()
            
            return {
                'id': user[0],
                'username': user[1],
                'role': user[3],
                'totp_secret': user[4]
            }
        else:
            # Increment failed attempts
            new_attempts = user[5] + 1
            lock_account = new_attempts >= 5
            lock_until = (datetime.utcnow() + timedelta(minutes=30)).isoformat() if lock_account else None
            
            cursor.execute("""
                UPDATE users 
                SET failed_login_attempts = ?,
                    account_locked = ?,
                    lock_until = ?
                WHERE username = ?
            """, (new_attempts, lock_account, lock_until, username))
            conn.commit()
            
            return None
            
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

# Initialize some test data
def init_test_data():
    try:
        import pyotp
        # Use fixed TOTP secrets for testing
        admin_totp_secret = "JBSWY3DPEHPK3PXP"  # Fixed test secret
        user_totp_secret = "JBSWY3DPEHPK3PXQ"   # Fixed test secret
        
        # Add test users with proper password hashing
        create_user('admin', 'admin123', 'admin', admin_totp_secret)
        create_user('user', 'user123', 'file_manager', user_totp_secret)
        
        # Print TOTP secrets for initial setup (in production, these would be securely transmitted to users)
        print("\nTOTP Setup Information:")
        print(f"Admin TOTP Secret: {admin_totp_secret}")
        print(f"User TOTP Secret: {user_totp_secret}")
        
        # Add test files one by one with their content
        test_files = [
            ('DOC001', 'Top Secret Report 2025.txt', b"This is a top secret report. For admin eyes only.", 'admin'),
            ('DOC002', 'Security Protocol Delta.txt', b"Security protocol documentation for file managers.", 'file_manager'),
            ('DOC003', 'Operation Nightwatch.txt', b"Operation Nightwatch details and procedures.", 'file_manager'),
            ('DOC004', 'Personnel Records.txt', b"Confidential personnel records and data.", 'file_manager')
        ]
        
        for file_id, filename, file_data, access_level in test_files:
            cursor.execute("""
                INSERT OR IGNORE INTO classified_files 
                (file_id, filename, file_data, access_level)
                VALUES (?, ?, ?, ?)
            """, (file_id, filename, file_data, access_level))
        conn.commit()
    except Exception as e:
        print(f"Error initializing test data: {e}")

def verify_totp(username, totp_code):
    try:
        import pyotp
        cur = conn.cursor()
        cur.execute("SELECT totp_secret FROM users WHERE username = ?", (username,))
        result = cur.fetchone()
        
        if result and result[0]:
            totp = pyotp.TOTP(result[0])
            # Allow a window of 1 interval before and after for time sync issues
            return totp.verify(totp_code, valid_window=1)
        return False
    except Exception as e:
        print(f"TOTP verification error: {e}")
        print(f"Debug - Username: {username}, Code: {totp_code}")
        if result and result[0]:
            print(f"Debug - Current expected code: {pyotp.TOTP(result[0]).now()}")
        return False

def get_agent_by_id(agent_id, requesting_user_role):
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM agents WHERE agent_number = ?", (agent_id,))
        agent = cur.fetchone()
        
        if not agent:
            return None
            
        # Role-based access control
        if requesting_user_role == 'admin':
            # Admin can see all agent details
            pass
        elif requesting_user_role == 'file_manager':
            # File manager can only see agents with file_manager clearance
            if agent[5] != 'file_manager':  # agent[5] is clearance_level
                return None
        else:
            return None
            
        return {
            'agent_number': agent[1],
            'name': agent[2],
            'rank': agent[3],
            'status': agent[4],
            'clearance_level': agent[5],
            'last_mission': agent[6],
            'photo_url': agent[7],
            'personal_info': {
                'contact': '+1 (XXX) XXX-XXXX',  # Masked for security
                'location': 'Classified',
                'specialization': 'Information Security',
                'years_of_service': '5+',
                'certifications': ['Level 3 Clearance', 'Advanced Combat Training'],
                'current_assignment': 'Project DEEPWATCH'
            }
        }
    except Exception as e:
        print(f"Database error: {e}")
        return None

def get_locations(role):
    try:
        cur = conn.cursor()
        if role == 'admin':
            # Admin can see all locations
            cur.execute("SELECT * FROM locations")
        elif role == 'file_manager':
            # File manager can only see standard security level locations
            cur.execute("""
                SELECT * FROM locations 
                WHERE security_level = 'standard'
            """)
        else:
            return []
            
        locations = cur.fetchall()
        return [{
            'location_id': loc[1],
            'name': loc[2],
            'type': loc[3],
            'access_level': loc[4],
            'geolocation': loc[5],
            'contents': loc[6],
            'status': loc[7],
            'last_accessed': loc[8],
            'security_level': loc[9]
        } for loc in locations]
    except Exception as e:
        print(f"Database error: {e}")
        return []

def get_location_by_id(location_id, requesting_user_role):
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM locations WHERE location_id = ?", (location_id,))
        loc = cur.fetchone()
        
        if not loc:
            return None
            
        # Role-based access control
        if requesting_user_role == 'admin':
            # Admin can see all location details
            pass
        elif requesting_user_role == 'file_manager':
            # File manager can only see standard security level locations
            if loc[9] != 'standard':  # loc[9] is security_level
                return None
        else:
            return None
            
        return {
            'location_id': loc[1],
            'name': loc[2],
            'type': loc[3],
            'access_level': loc[4],
            'geolocation': loc[5],
            'contents': loc[6],
            'status': loc[7],
            'last_accessed': loc[8],
            'security_level': loc[9]
        }
    except Exception as e:
        print(f"Database error: {e}")
        return None

def log_audit(user_id, action, details):
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO audit_log (user_id, action, details)
            VALUES (?, ?, ?)
        """, (user_id, action, details))
        conn.commit()
    except Exception as e:
        print(f"Audit logging error: {e}")

def verify_operation_access(user_id, user_role, operation_id=None):
    if user_role == 'admin':
        return True
        
    if operation_id:
        cur = conn.cursor()
        cur.execute("SELECT classified_level FROM operations WHERE operation_id = ?", (operation_id,))
        result = cur.fetchone()
        
        if not result:
            return False
            
        classified_level = result[0]
        if classified_level == 'TOP_SECRET' and user_role != 'senior_agent':
            return False
            
    return user_role in ['file_manager', 'senior_agent']

def get_operations(user_id, user_role):
    try:
        if not verify_operation_access(user_id, user_role):
            log_audit(user_id, "access_denied", f"Unauthorized operations list access attempt with role {user_role}")
            return []
            
        cur = conn.cursor()
        
        if user_role == 'admin':
            cur.execute("SELECT * FROM operations")
        elif user_role == 'senior_agent':
            cur.execute("SELECT * FROM operations")
        else:
            cur.execute("""
                SELECT * FROM operations 
                WHERE classified_level = 'standard'
            """)
        
        operations = cur.fetchall()
        log_audit(user_id, "list_operations", f"Retrieved operations list with role {user_role}")
        
        return [{
            'operation_id': op[1],
            'code_name': op[2],
            'status': op[3],
            'priority': op[4],
            'start_date': op[5],
            'end_date': op[6],
            'description': op[7],
            'involved_agents': json.loads(op[8]),
            'target_location': op[9],
            'classified_level': op[10]
        } for op in operations]
    except Exception as e:
        print(f"Database error: {e}")
        log_audit(user_id, "error", f"Error retrieving operations: {str(e)}")
        return []

def get_operation_by_id(operation_id, user_id, user_role):
    try:
        if not verify_operation_access(user_id, user_role, operation_id):
            log_audit(user_id, "access_denied", f"Unauthorized access attempt to operation {operation_id} with role {user_role}")
            return None
            
        cur = conn.cursor()
        cur.execute("SELECT * FROM operations WHERE operation_id = ?", (operation_id,))
        op = cur.fetchone()
        
        if not op:
            log_audit(user_id, "not_found", f"Attempted to access non-existent operation {operation_id}")
            return None
            
        # Fetch related agent details with access control
        involved_agents = json.loads(op[8])  # List of agent IDs
        agent_details = []
        for agent_id in involved_agents:
            cur.execute("""
                SELECT name, rank, clearance_level 
                FROM agents 
                WHERE agent_number = ?
            """, (agent_id,))
            agent = cur.fetchone()
            if agent:
                # Only include agent details based on user role
                if user_role == 'admin' or agent[2] in ['standard', user_role]:
                    agent_details.append({
                        'id': agent_id,
                        'name': agent[0],
                        'rank': agent[1]
                    })

        # Fetch location details if available with access control
        location_details = None
        if op[9]:  # If target_location exists
            cur.execute("""
                SELECT name, type, security_level 
                FROM locations 
                WHERE location_id = ?
            """, (op[9],))
            loc = cur.fetchone()
            if loc and (user_role == 'admin' or loc[2] in ['standard', user_role]):
                location_details = {
                    'id': op[9],
                    'name': loc[0],
                    'type': loc[1]
                }
            
        operation_data = {
            'operation_id': op[1],
            'code_name': op[2],
            'status': op[3],
            'priority': op[4],
            'start_date': op[5],
            'end_date': op[6],
            'description': op[7],
            'involved_agents': agent_details,
            'target_location': location_details,
            'classified_level': op[10]
        }
        
        # Add additional info based on clearance
        if user_role == 'admin' or (user_role == 'senior_agent' and op[10] != 'TOP_SECRET'):
            operation_data['additional_info'] = {
                'timeline': [
                    {
                        'date': op[5],
                        'event': 'Operation Initiated',
                        'details': 'Initial briefing and team assembly',
                        'location': 'Command Center Alpha',
                        'participants': ['Mission Director', 'Field Team Lead', 'Intelligence Officer']
                    },
                    {
                        'date': datetime.strptime(op[5], '%Y-%m-%d %H:%M:%S') + timedelta(hours=2),
                        'event': 'Phase 1 - Intelligence Gathering',
                        'details': 'Deployment of surveillance assets and initial reconnaissance',
                        'location': 'Field Operation Zone',
                        'participants': ['Surveillance Team', 'Intelligence Analysts']
                    },
                    {
                        'date': datetime.strptime(op[5], '%Y-%m-%d %H:%M:%S') + timedelta(hours=24),
                        'event': 'Phase 2 - Operation Execution',
                        'details': 'Main operation phase with coordinated team actions',
                        'location': 'Target Zone',
                        'participants': ['Strike Team', 'Support Units', 'Medical Team']
                    }
                ],
                'risk_assessment': {
                    'threat_level': calculate_threat_level(op[4]),  # Based on priority
                    'environmental_risks': [
                        'Weather conditions affecting visibility',
                        'Urban environment complications',
                        'Civilian presence in operation zone'
                    ],
                    'countermeasures': [
                        'Advanced surveillance systems',
                        'Secure communication channels',
                        'Emergency extraction protocols',
                        'Medical evacuation routes'
                    ],
                    'contingency_plans': [
                        'Plan B: Alternative approach vectors',
                        'Plan C: Emergency extraction procedures',
                        'Communication failure protocols'
                    ]
                },
                'resources': {
                    'equipment': {
                        'surveillance': ['Thermal imaging', 'Drone units', 'Signal interceptors'],
                        'communication': ['Encrypted radios', 'Satellite uplinks', 'Emergency beacons'],
                        'tactical': ['Standard issue gear', 'Special equipment based on operation type'],
                        'medical': ['Field medical kits', 'Emergency response equipment']
                    },
                    'vehicles': {
                        'ground': ['Tactical vehicles', 'Support vehicles'],
                        'air': ['Surveillance drones', 'Emergency evacuation units'],
                        'special': ['Mission-specific vehicles']
                    },
                    'support_personnel': {
                        'field_teams': ['Primary strike team', 'Secondary support team'],
                        'technical_support': ['Communications experts', 'Surveillance operators'],
                        'medical_support': ['Field medics', 'Emergency response team'],
                        'logistics': ['Supply chain coordinators', 'Equipment managers']
                    }
                },
                'success_metrics': {
                    'primary_objectives': [
                        'Mission completion within timeframe',
                        'Minimal security breaches',
                        'Asset protection maintained'
                    ],
                    'secondary_objectives': [
                        'Intelligence gathering goals',
                        'Resource efficiency targets',
                        'Operational security maintenance'
                    ],
                    'performance_indicators': [
                        'Response time metrics',
                        'Resource utilization efficiency',
                        'Communication effectiveness'
                    ]
                },
                'security_protocols': {
                    'communication': [
                        'Encrypted channels only',
                        'Regular frequency changes',
                        'Emergency silence protocols'
                    ],
                    'information_handling': [
                        'Need-to-know basis',
                        'Compartmentalized information distribution',
                        'Secure data disposal procedures'
                    ],
                    'personnel': [
                        'Regular security clearance verification',
                        'Real-time location tracking',
                        'Emergency extraction procedures'
                    ]
                }
            }
            
        log_audit(user_id, "view_operation", f"Accessed operation {operation_id}")
        return operation_data
            
    except Exception as e:
        print(f"Database error: {e}")
        log_audit(user_id, "error", f"Error accessing operation {operation_id}: {str(e)}")
        return None

def log_activity(username: str, role: str, action: str, stuff_accessed: str = None, session_duration: int = None):
    """
    Log user activity to audit_logs table.
    
    Args:
        username: The username performing the action
        role: User's role (admin, file_manager, etc.)
        action: Description of the action performed
        stuff_accessed: Resources or endpoints accessed (optional)
        session_duration: Duration of the action in milliseconds (optional)
    """
    try:
        cursor.execute("""
            INSERT INTO audit_logs (username, role, timestamp, session_duration, stuff_accessed, action)
            VALUES (?, ?, datetime('now'), ?, ?, ?)
        """, (username, role, session_duration, stuff_accessed, action))
        conn.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")

def get_audit_logs(username: str = None, role: str = None, start_time: str = None, end_time: str = None, limit: int = 100):
    """
    Retrieve audit logs with optional filtering.
    
    Args:
        username: Filter logs by username (optional)
        role: Filter logs by role (optional)
        start_time: Filter logs after this timestamp (optional)
        end_time: Filter logs before this timestamp (optional)
        limit: Maximum number of logs to return
    """
    try:
        query = "SELECT username, role, timestamp, session_duration, stuff_accessed, action FROM audit_logs"
        conditions = []
        params = []
        
        if username:
            conditions.append("username = ?")
            params.append(username)
        if role:
            conditions.append("role = ?")
            params.append(role)
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time)
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        
        return [{
            'username': log[0],
            'role': log[1],
            'timestamp': log[2],
            'session_duration': log[3],
            'stuff_accessed': log[4],
            'action': log[5]
        } for log in logs]
    except Exception as e:
        print(f"Error retrieving logs: {e}")
        return []

def get_agents(role):
    try:
        cur = conn.cursor()
        if role == 'admin':
            # Admin can see all agents
            cur.execute("SELECT * FROM agents")
        elif role == 'file_manager':
            # File manager can only see agents with clearance level file_manager or lower
            cur.execute("""
                SELECT * FROM agents 
                WHERE clearance_level = 'file_manager'
            """)
        else:
            return []
            
        agents = cur.fetchall()
        return [{
            'agent_number': agent[1],
            'name': agent[2],
            'rank': agent[3],
            'status': agent[4],
            'clearance_level': agent[5],
            'last_mission': agent[6],
            'photo_url': agent[7]
        } for agent in agents]
    except Exception as e:
        print(f"Database error: {e}")
        return []

def init_test_data():
    try:
        import pyotp
        # Use fixed TOTP secrets for testing
        admin_totp_secret = "JBSWY3DPEHPK3PXP"  # Fixed test secret
        user_totp_secret = "JBSWY3DPEHPK3PXQ"   # Fixed test secret
        
        # Add test users with properly hashed passwords and TOTP secrets
        # Create admin users
        create_user('admin', 'admin123', 'admin', admin_totp_secret)
        create_user('admin2', 'admin123', 'admin', admin_totp_secret)  # Second admin with same TOTP
        
        # Then create regular user
        create_user('user', 'user123', 'file_manager', user_totp_secret)
        
        # Print TOTP secrets for initial setup (in production, these would be securely transmitted to users)
        print("\nTOTP Setup Information:")
        print(f"Admin TOTP Secret: {admin_totp_secret}")
        print(f"User TOTP Secret: {user_totp_secret}")
        
        # Add test files
        cursor.execute("""
            INSERT OR IGNORE INTO classified_files (file_id, filename, file_data, access_level)
            VALUES 
                ('DOC001', 'Top Secret Report 2025.txt', ?, 'admin'),
                ('DOC002', 'Security Protocol Delta.txt', ?, 'file_manager'),
                ('DOC003', 'Operation Nightwatch.txt', ?, 'file_manager'),
                ('DOC004', 'Personnel Records.txt', ?, 'file_manager')
        """, (
            b"This is a top secret report. For admin eyes only.",
            b"Security protocol documentation for file managers.",
            b"Operation Nightwatch details and procedures.",
            b"Confidential personnel records and data."
        ))

        # Add test agents
        cursor.execute("""
            INSERT OR IGNORE INTO agents 
            (agent_number, name, rank, status, clearance_level, last_mission, photo_url)
            VALUES
                ('A001', 'John Smith', 'Senior Agent', 'Active', 'admin', 'Operation Phoenix', '/agents/a001.jpg'),
                ('A002', 'Sarah Connor', 'Field Agent', 'Active', 'file_manager', 'Operation Delta', '/agents/a002.jpg'),
                ('A003', 'James Wilson', 'Field Agent', 'On Leave', 'file_manager', 'Operation Echo', '/agents/a003.jpg'),
                ('A004', 'Emily Chen', 'Senior Agent', 'Active', 'admin', 'Operation Sierra', '/agents/a004.jpg'),
                ('A005', 'Michael Brown', 'Junior Agent', 'Training', 'file_manager', 'None', '/agents/a005.jpg')
        """)

        # Add test operations
        cursor.execute("""
            INSERT OR IGNORE INTO operations 
            (operation_id, code_name, status, priority, start_date, end_date, description, involved_agents, target_location, classified_level)
            VALUES
                ('OP001', 'Phoenix Rising', 'Active', 'High', 
                 '2025-10-01 08:00:00', NULL,
                 'High-priority operation targeting major security threat. Details classified.',
                 '["A001", "A004"]', 'LOC001', 'admin'),
                
                ('OP002', 'Silent Echo', 'Completed', 'Medium',
                 '2025-09-15 14:30:00', '2025-09-30 18:45:00',
                 'Intelligence gathering operation in urban environment.',
                 '["A002", "A003"]', 'LOC004', 'standard'),
                
                ('OP003', 'Blue Dawn', 'Active', 'High',
                 '2025-10-05 06:00:00', NULL,
                 'Critical asset protection and surveillance operation.',
                 '["A001", "A002", "A004"]', 'LOC003', 'admin'),
                
                ('OP004', 'Desert Storm', 'Suspended', 'Medium',
                 '2025-08-20 10:00:00', NULL,
                 'Resource security operation in remote location.',
                 '["A003", "A005"]', 'LOC002', 'standard'),
                
                ('OP005', 'Crystal Shield', 'Active', 'Low',
                 '2025-10-10 09:00:00', NULL,
                 'Standard security protocol implementation and training.',
                 '["A005"]', 'LOC005', 'standard')
        """)

        # Add test locations
        cursor.execute("""
            INSERT OR IGNORE INTO locations 
            (location_id, name, type, access_level, geolocation, contents, status, security_level)
            VALUES
                ('LOC001', 'Sierra Safehouse', 'Weapon Cache', 'high', '40.7128° N, 74.0060° W', 
                'Heavy weapons, ammunition, tactical gear', 'Active', 'high'),
                ('LOC002', 'Delta Storage', 'Cash Stash', 'medium', '34.0522° N, 118.2437° W', 
                'Emergency funds, cryptocurrency cold storage', 'Active', 'standard'),
                ('LOC003', 'Echo Bunker', 'Safe Room', 'high', '51.5074° N, 0.1278° W', 
                'Emergency supplies, communications equipment', 'Active', 'high'),
                ('LOC004', 'Bravo Cache', 'Intel Stash', 'medium', '48.8566° N, 2.3522° E', 
                'Documents, hard drives, encryption keys', 'Active', 'standard'),
                ('LOC005', 'Alpha Point', 'Medical Cache', 'medium', '35.6762° N, 139.6503° E', 
                'Emergency medical supplies, field surgery equipment', 'Active', 'standard')
        """)
        
        conn.commit()
    except Exception as e:
        print(f"Error initializing test data: {e}")

init_test_data()

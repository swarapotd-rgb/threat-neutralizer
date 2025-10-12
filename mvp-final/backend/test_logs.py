import requests
import json
import pyotp
import os
from getpass import getpass
import configparser
import sys

# Configuration
CONFIG_FILE = "config.ini"
API_URL = "http://localhost:8000"

def load_config():
    """Load configuration from config file or environment"""
    if os.path.exists(CONFIG_FILE):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        return {
            'totp_secret': config.get('auth', 'totp_secret', fallback=os.getenv('TOTP_SECRET')),
            'username': config.get('auth', 'username', fallback=os.getenv('API_USERNAME')),
        }
    return {
        'totp_secret': os.getenv('TOTP_SECRET'),
        'username': os.getenv('API_USERNAME'),
    }

def get_credentials():
    """Get credentials securely"""
    config = load_config()
    
    if not config['totp_secret'] or not config['username']:
        print("Error: TOTP secret and username must be configured in config.ini or environment variables")
        sys.exit(1)
    
    # Get password securely
    password = getpass(f"Enter password for {config['username']}: ")
    
    # Generate current TOTP code
    totp = pyotp.TOTP(config['totp_secret'])
    current_code = totp.now()
    
    print(f"Generated TOTP code for authentication")
    
    return config['username'], password, current_code

try:
    # Get credentials securely
    username, password, totp_code = get_credentials()
    
    # Login request
    login_data = {
        "username": username,
        "password": password,
        "totp_code": totp_code
    }
    
    # Login to get token
    login_response = requests.post(
        f"{API_URL}/login",
        json=login_data,
        headers={"Content-Type": "application/json"},
        verify=True  # Enforce SSL verification
    )
    
    login_response.raise_for_status()  # Raise exception for 4XX/5XX status codes
    
    if login_response.status_code == 200:
        token = login_response.json()["token"]
        print("\nLogin successful!")
        
        # Get logs using the token
        logs_response = requests.get(
            f"{API_URL}/logs",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            verify=True  # Enforce SSL verification
        )
        
        logs_response.raise_for_status()  # Raise exception for 4XX/5XX status codes
        
        if logs_response.status_code == 200:
            logs = logs_response.json()
            print("Logs retrieved successfully:")
            print(json.dumps(logs, indent=2))
    
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    if e.response is not None:
        print(f"Response: {e.response.text}")
except requests.exceptions.ConnectionError:
    print(f"Error: Could not connect to {API_URL}. Is the server running?")
except requests.exceptions.Timeout:
    print("Error: Request timed out")
except requests.exceptions.RequestException as e:
    print(f"Error: An error occurred while making the request: {e}")
except json.JSONDecodeError:
    print("Error: Invalid JSON response from server")
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    # Clear sensitive data from memory
    if 'password' in locals():
        del password
    if 'token' in locals():
        del token

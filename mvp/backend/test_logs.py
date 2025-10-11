import requests
import json
import pyotp

# Generate current TOTP code
totp = pyotp.TOTP('JBSWY3DPEHPK3PXP')
current_code = totp.now()

print(f"Current TOTP code: {current_code}")

# Login request
login_data = {
    "username": "admin",
    "password": "admin123",
    "totp_code": current_code
}

try:
    # Login to get token
    login_response = requests.post(
        "http://localhost:8000/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code == 200:
        token = login_response.json()["token"]
        print(f"\nLogin successful! Token: {token}\n")
        
        # Get logs using the token
        logs_response = requests.get(
            "http://localhost:8000/logs",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if logs_response.status_code == 200:
            logs = logs_response.json()
            print("Logs retrieved successfully:")
            print(json.dumps(logs, indent=2))
        else:
            print(f"Error getting logs: {logs_response.status_code}")
            print(logs_response.text)
    else:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.text)
        
except Exception as e:
    print(f"Error: {str(e)}")
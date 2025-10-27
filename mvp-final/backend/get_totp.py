#!/usr/bin/env python3
"""
Quick TOTP Code Generator for Threat Neutralizer
Run this script anytime you need fresh TOTP codes
"""
import pyotp
import time

# TOTP Secrets from database
ADMIN_SECRET = "JBSWY3DPEHPK3PXP"
USER_SECRET = "JBSWY3DPEHPK3PXQ"

def get_totp_codes():
    admin_totp = pyotp.TOTP(ADMIN_SECRET)
    user_totp = pyotp.TOTP(USER_SECRET)
    
    admin_code = admin_totp.now()
    user_code = user_totp.now()
    
    # Calculate time until next refresh
    current_time = int(time.time())
    time_remaining = 30 - (current_time % 30)
    
    print("\n" + "="*50)
    print("  THREAT NEUTRALIZER - TOTP CODES")
    print("="*50)
    print(f"\n[ADMIN] Account: admin / Password: admin123")
    print(f"        TOTP Code: {admin_code}")
    print(f"\n[USER]  Account: user / Password: user123")
    print(f"        TOTP Code: {user_code}")
    print(f"\n[TIME]  Valid for: {time_remaining} seconds")
    print("="*50)
    print("\nTip: Codes refresh every 30 seconds")
    print("     Run this script again for new codes!\n")

if __name__ == "__main__":
    get_totp_codes()


from database import *
import hashlib

def generate_sha_256(input_string):
    input_bytes = input_string.encode('utf-8')
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_bytes)
    hex_digest = sha256_hash.hexdigest()
    return hex_digest

print(generate_sha_256("test"))
import pyotp
import jwt
import time

JWT_SECRET = "A6R2JRKSCCSNLOFJE4E5C5OHMMLNOVGF"  
JWT_ALGORITHM = "HS256"

def generate_jwt_token(username, role):
    payload = {
        "username": username,
        "role": role,
        "exp": int(time.time()) + 3600
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def loginuser(username, password, totp_code):
    hashed_password = generate_sha_256(password)
    user = get_user_by_username(username)
    if not user or user['password_hash'] != hashed_password:
        return {"msg": "bad creds"}
    from database import conn
    cursor = conn.cursor()
    cursor.execute("SELECT totp_secret FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if not row:
        return {"msg": "bad creds"}
    totp_secret = row[0]

    totp = pyotp.TOTP(totp_secret)
    if not totp.verify(str(totp_code)):
        return {"msg": "bad creds"}

    token = generate_jwt_token(username, user['role'])
    return {
        "msg": "all good",
        "token": token,
        "username": username,
        "role": user['role']
    }

import os
import io
from fastapi import FastAPI, Body, HTTPException, Header, Depends
from fastapi.responses import StreamingResponse
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import jwt
from database import (
    get_classified_files, 
    verify_auth_token, 
    get_user_by_token, 
    update_auth_token,
    verify_totp,
    get_agents,
    get_agent_by_id,
    get_locations,
    get_location_by_id,
    get_operations,
    get_operation_by_id,
    authenticate_user,
    get_audit_logs,
    conn
)

from database import log_activity

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Secret key for JWT - in production, use a secure environment variable
SECRET_KEY = "JBSWY3DPEHPK3PXP"

# Rate limiting settings
from fastapi import Request
from datetime import datetime, timedelta
from collections import defaultdict

# Store IP: [(timestamp, endpoint), ...]
rate_limit_store = defaultdict(list)
RATE_LIMIT_DURATION = timedelta(minutes=15)  # Window duration
MAX_REQUESTS = 100  # Max requests per window
MAX_FAILED_LOGIN = 50  # Max failed login attempts

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = datetime.utcnow()
    
    # Clean up old entries
    rate_limit_store[client_ip] = [
        hit for hit in rate_limit_store[client_ip]
        if now - hit[0] < RATE_LIMIT_DURATION
    ]
    
    # Check rate limit
    if len(rate_limit_store[client_ip]) >= MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many requests")
    
    # Check failed login attempts for /login endpoint
    if request.url.path == "/login":
        failed_attempts = sum(
            1 for hit in rate_limit_store[client_ip]
            if hit[1] == "/login" and now - hit[0] < RATE_LIMIT_DURATION
        )
        if failed_attempts >= MAX_FAILED_LOGIN:
            raise HTTPException(
                status_code=429, 
                detail="Too many failed login attempts. Please try again later."
            )
    
    # Add current request
    rate_limit_store[client_ip].append((now, request.url.path))
    
    response = await call_next(request)
    return response

app.middleware("http")(rate_limit_middleware)

class AuthRequest(BaseModel):
    username: str
    password: str
    totp_code: str

class FileResponse(BaseModel):
    files: List[dict]
    username: str
    role: str

class AgentResponse(BaseModel):
    agents: List[dict]
    username: str
    role: str

class LocationResponse(BaseModel):
    locations: List[dict]
    username: str
    role: str

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    token = authorization.split(" ")[1]
    try:
        # Verify token format and signature
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token format")
        
        # Verify token in database
        user = get_user_by_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Token not found in database")
            
        # Verify user data matches token payload
        if user["username"] != payload["username"] or user["role"] != payload["role"]:
            raise HTTPException(status_code=401, detail="Token data mismatch")
            
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

@app.post("/login")
def login(auth: AuthRequest):
    try:
        # First verify username and password using database
        user = authenticate_user(auth.username, auth.password)
        if not user:
            log_activity(auth.username, "unknown", "login_failed", "Invalid username or password")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Then verify TOTP
        if not verify_totp(auth.username, auth.totp_code):
            log_activity(auth.username, user['role'], "login_failed", "Invalid TOTP code")
            raise HTTPException(status_code=401, detail="Invalid TOTP code")

        # Generate JWT token with user info from database
        token = jwt.encode(
            {
                "username": user['username'],
                "role": user['role'],
                "exp": datetime.utcnow() + timedelta(hours=1)
            },
            SECRET_KEY,
            algorithm="HS256"
        )
        
        # Update the user's current auth token in database
        if update_auth_token(user['username'], token):
            log_activity(user['username'], user['role'], "login_success", "Successfully logged in")
            return {
                "token": token,
                "role": user['role'],
                "username": user['username']
            }
        
        log_activity(auth.username, user['role'], "login_failed", "Failed to update auth token")
        raise HTTPException(status_code=500, detail="Error updating authentication token")
            
    except HTTPException:
        raise
    except Exception as e:
        log_activity(auth.username, "unknown", "login_error", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/files")
async def get_files(current_user: dict = Depends(get_current_user)):
    try:
        files = get_classified_files(current_user["role"])
        log_activity(
            current_user["username"],
            current_user["role"],
            "files_listed",
            f"Retrieved list of {len(files)} files"
        )
        return FileResponse(
            files=files,
            username=current_user["username"],
            role=current_user["role"]
        )
    except Exception as e:
        log_activity(
            current_user["username"],
            current_user["role"],
            "files_error",
            f"Error retrieving files: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Error retrieving files")

@app.get("/files/{file_id}")
@app.get("/get_file/{file_id}")  # Keep old endpoint for backwards compatibility
@app.get("/files/{file_id}")
async def get_file(file_id: str, user=Depends(get_current_user)):
    try:
        cur = conn.cursor()
        
        # First check if the file exists
        cur.execute("""
            SELECT filename, file_data, access_level 
            FROM classified_files 
            WHERE file_id = ?
        """, (file_id,))
        file = cur.fetchone()

        if file is None:
            log_activity(
                user["username"],
                user["role"],
                "file_not_found",
                f"Attempted to access non-existent file: {file_id}"
            )
            raise HTTPException(status_code=404, detail="File not found")

        filename, file_data, access_level = file
        
        # Check user's role against file access level
        if user["role"] == "admin":
            # Admin can access any file
            pass
        elif user["role"] == "file_manager" and access_level == "file_manager":
            # File manager can only access files marked for file_manager access
            pass
        else:
            # Other roles or unauthorized access
            raise HTTPException(
                status_code=403, 
                detail="You don't have permission to access this file"
            )
        
        log_activity(
            user["username"],
            user["role"],
            "file_downloaded",
            f"Downloaded file: {filename} (ID: {file_id})"
        )
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        log_activity(
            user["username"],
            user["role"],
            "file_error",
            f"Error accessing file {file_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_id}")
async def get_agent_details(agent_id: str, current_user: dict = Depends(get_current_user)):
    try:
        agent = get_agent_by_id(agent_id, current_user["role"])
        if not agent:
            log_activity(
                current_user["username"],
                current_user["role"],
                "agent_not_found",
                f"Attempted to access non-existent or unauthorized agent: {agent_id}"
            )
            raise HTTPException(
                status_code=404,
                detail="Agent not found or you don't have permission to view this agent's details"
            )
        log_activity(
            current_user["username"],
            current_user["role"],
            "agent_accessed",
            f"Viewed details of agent: {agent_id}"
        )
        return {
            "agent": agent,
            "username": current_user["username"],
            "role": current_user["role"]
        }
    except Exception as e:
        log_activity(
            current_user["username"],
            current_user["role"],
            "agent_error",
            f"Error accessing agent {agent_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/locations")
async def get_location_list(current_user: dict = Depends(get_current_user)):
    try:
        locations = get_locations(current_user["role"])
        log_activity(
            current_user["username"],
            current_user["role"],
            "locations_listed",
            f"Retrieved list of {len(locations)} locations"
        )
        return LocationResponse(
            locations=locations,
            username=current_user["username"],
            role=current_user["role"]
        )
    except Exception as e:
        log_activity(
            current_user["username"],
            current_user["role"],
            "locations_error",
            f"Error retrieving locations: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Error retrieving locations")

@app.get("/locations/{location_id}")
async def get_location_details(location_id: str, current_user: dict = Depends(get_current_user)):
    try:
        location = get_location_by_id(location_id, current_user["role"])
        if not location:
            log_activity(
                current_user["username"],
                current_user["role"],
                "location_not_found",
                f"Attempted to access non-existent or unauthorized location: {location_id}"
            )
            raise HTTPException(
                status_code=404,
                detail="Location not found or you don't have permission to view this location"
            )
        log_activity(
            current_user["username"],
            current_user["role"],
            "location_accessed",
            f"Viewed details of location: {location_id}"
        )
        return {
            "location": location,
            "username": current_user["username"],
            "role": current_user["role"]
        }
    except Exception as e:
        log_activity(
            current_user["username"],
            current_user["role"],
            "location_error",
            f"Error accessing location {location_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def get_agent_list(current_user: dict = Depends(get_current_user)):
    try:
        agents = get_agents(current_user["role"])
        log_activity(
            current_user["username"],
            current_user["role"],
            "agents_listed",
            f"Retrieved list of {len(agents)} agents"
        )
        return AgentResponse(
            agents=agents,
            username=current_user["username"],
            role=current_user["role"]
        )
    except Exception as e:
        log_activity(
            current_user["username"],
            current_user["role"],
            "agents_error",
            f"Error retrieving agents: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Error retrieving agents")

class OperationResponse(BaseModel):
    operations: List[dict]
    username: str
    role: str

@app.get("/logs")
async def get_logs(
    current_user: dict = Depends(get_current_user),
    username: Optional[str] = None,
    role: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100
):
    # Only admin can view logs
    if current_user["role"] != "admin":
        log_activity(current_user["username"], current_user["role"], "logs_access_denied", "Attempted to access logs without admin role")
        raise HTTPException(
            status_code=403,
            detail="Only admin users can view logs"
        )
    
    try:
        logs = get_audit_logs(
            username=username,
            role=role,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        # Log the successful retrieval of logs
        filters = {
            "username": username,
            "role": role,
            "start_time": start_time,
            "end_time": end_time,
            "limit": limit
        }
        log_activity(
            current_user["username"],
            current_user["role"],
            "logs_retrieved",
            f"Retrieved {len(logs)} logs with filters: {filters}"
        )
        
        return {
            "logs": logs,
            "total": len(logs)
        }
    except Exception as e:
        log_activity(
            current_user["username"],
            current_user["role"],
            "logs_error",
            f"Error retrieving logs: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving logs: {str(e)}"
        )

@app.get("/operations")
async def get_operation_list(
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(None)
):
    try:
        # Verify token and expiry
        token = authorization.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                log_activity(
                    current_user["username"],
                    current_user["role"],
                    "token_expired",
                    "Attempted to access operations with expired token"
                )
                raise HTTPException(status_code=401, detail="Token has expired")
            if payload["username"] != current_user["username"] or payload["role"] != current_user["role"]:
                log_activity(
                    current_user["username"],
                    current_user["role"],
                    "token_mismatch",
                    "Token data mismatch when accessing operations"
                )
                raise HTTPException(status_code=401, detail="Token data mismatch")
        except jwt.InvalidTokenError:
            log_activity(
                current_user["username"],
                current_user["role"],
                "invalid_token",
                "Invalid token when accessing operations"
            )
            raise HTTPException(status_code=401, detail="Invalid token")

        # Get operations from database with username for audit logging
        operations = get_operations(current_user["username"], current_user["role"])
        
        log_activity(
            current_user["username"],
            current_user["role"],
            "operations_listed",
            f"Retrieved list of {len(operations)} operations"
        )
        
        return OperationResponse(
            operations=operations,
            username=current_user["username"],
            role=current_user["role"]
        )
    except HTTPException:
        raise
    except Exception as e:
        log_activity(
            current_user["username"],
            current_user["role"],
            "operations_error",
            f"Error retrieving operations: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Error retrieving operations")

@app.get("/operations/{operation_id}")
async def get_operation_details(
    operation_id: str,
    current_user: dict = Depends(get_current_user),
    authorization: str = Header(None)
):
    try:
        # Verify token and expiry
        token = authorization.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                log_activity(
                    current_user["username"],
                    current_user["role"],
                    "token_expired",
                    f"Attempted to access operation {operation_id} with expired token"
                )
                raise HTTPException(status_code=401, detail="Token has expired")
            if payload["username"] != current_user["username"] or payload["role"] != current_user["role"]:
                log_activity(
                    current_user["username"],
                    current_user["role"],
                    "token_mismatch",
                    f"Token data mismatch when accessing operation {operation_id}"
                )
                raise HTTPException(status_code=401, detail="Token data mismatch")
        except jwt.InvalidTokenError:
            log_activity(
                current_user["username"],
                current_user["role"],
                "invalid_token",
                f"Invalid token when accessing operation {operation_id}"
            )
            raise HTTPException(status_code=401, detail="Invalid token")

        # Get operation with enhanced security and audit logging
        operation = get_operation_by_id(
            operation_id, 
            current_user["username"], 
            current_user["role"]
        )
        
        if not operation:
            log_activity(
                current_user["username"],
                current_user["role"],
                "operation_not_found",
                f"Attempted to access non-existent or unauthorized operation: {operation_id}"
            )
            raise HTTPException(
                status_code=404,
                detail="Operation not found or you don't have permission to view this operation"
            )

        log_activity(
            current_user["username"],
            current_user["role"],
            "operation_accessed",
            f"Viewed details of operation: {operation_id}"
        )

        return {
            "operation": operation,
            "username": current_user["username"],
            "role": current_user["role"]
        }
    except HTTPException:
        raise
    except Exception as e:
        log_activity(
            current_user["username"],
            current_user["role"],
            "operation_error",
            f"Error accessing operation {operation_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import Request
from fastapi.middleware.base import BaseHTTPMiddleware
import time
from database import log_activity, get_user_by_token

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Try to get user info from token
        user = None
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                user = get_user_by_token(token)
        except Exception as e:
            print(f"Error getting user from token: {e}")

        # Call the next middleware/endpoint
        response = await call_next(request)
        
        # Calculate request duration
        duration = int((time.time() - start_time) * 1000)  # Convert to milliseconds
        
        # Log the request if we have a user
        if user and request.url.path != "/log":  # Don't log requests to /log endpoint
            log_activity(
                username=user['username'],
                role=user['role'],
                action=f"{request.method} {request.url.path}",
                stuff_accessed=str(request.url),
                session_duration=duration
            )
        
        return response
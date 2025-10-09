from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import jwt
import asyncio

from ...core.config import settings
from ...core.database.clients import SupabaseClient, MongoDBClient, RedisClient
from ...security.auth_manager import AuthManager
from ...security.rbac import RBAC

logger = logging.getLogger(__name__)
router = APIRouter(tags=["authentication"])
security = HTTPBearer()

# Initialize clients
supabase_client = SupabaseClient()
mongodb_client = MongoDBClient()
redis_client = RedisClient()
auth_manager = AuthManager(user_store_path="data/users.json")
rbac = RBAC()

# Pydantic models
class LoginRequest(BaseModel):
    identifier: str  # Can be email, username, or user_id
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[Dict[str, Any]] = None
    permissions: Optional[list] = None

class UserProfile(BaseModel):
    username: str
    email: str
    full_name: str
    role: str
    department: str
    location: str
    preferences: Dict[str, Any]
    last_login: Optional[datetime] = None
    permissions: list

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Authenticate user with real database integration"""
    try:
        logger.info(f"Login attempt for identifier: {login_data.identifier}")
        
        # Step 1: Try to identify user (by email, username, or user_id)
        user_profile = await get_user_by_identifier(login_data.identifier)
        
        if not user_profile:
            logger.warning(f"User not found: {login_data.identifier}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Step 2: Verify password using auth manager
        username = user_profile['username']
        
        if not auth_manager.authenticate(username, login_data.password):
            logger.warning(f"Invalid password for user: {username}")
            
            # Log failed attempt
            await log_login_attempt(user_profile, success=False, reason="Invalid password")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Step 3: Check if account is active and not locked
        if user_profile.get('account_locked', False):
            logger.warning(f"Account locked: {username}")
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is locked. Contact administrator."
            )
        
        # Step 4: Generate JWT token
        token = generate_jwt_token(user_profile)
        
        # Step 5: Get user permissions
        permissions = list(rbac.get_permissions(user_profile['role']))
        
        # Step 6: Update login statistics
        await update_login_statistics(user_profile)
        
        # Step 7: Log successful login
        await log_login_attempt(user_profile, success=True)
        
        # Step 8: Cache user session in Redis
        if redis_client.enabled:
            await cache_user_session(username, user_profile, token)
        
        logger.info(f"Successful login for user: {username}")
        
        return LoginResponse(
            success=True,
            message="Login successful",
            token=token,
            user={
                "id": user_profile.get('_id'),
                "username": user_profile['username'],
                "email": user_profile['email'],
                "full_name": user_profile['full_name'],
                "role": user_profile['role'],
                "department": user_profile['department'],
                "location": user_profile['location'],
                "preferences": user_profile.get('preferences', {}),
                "last_login": user_profile.get('last_login'),
                "security_clearance": user_profile.get('security_clearance')
            },
            permissions=permissions
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

async def get_user_by_identifier(identifier: str) -> Optional[Dict[str, Any]]:
    """Get user by email, username, or user_id from MongoDB"""
    if not mongodb_client.enabled:
        logger.warning("MongoDB not enabled, using auth manager fallback")
        
        # Create mapping from email/username to actual username for demo users
        demo_user_mapping = {
            # Email mappings
            "admin@kartavya.demo": "security_admin",
            "analyst@kartavya.demo": "security_analyst", 
            "viewer@kartavya.demo": "security_viewer",
            # Username mappings (direct)
            "security_admin": "security_admin",
            "security_analyst": "security_analyst",
            "security_viewer": "security_viewer"
        }
        
        # Try to find the actual username
        actual_username = demo_user_mapping.get(identifier)
        if not actual_username:
            logger.warning(f"No mapping found for identifier: {identifier}")
            return None
            
        # Get role from auth manager using actual username
        role = auth_manager.get_role(actual_username)
        if not role:
            logger.warning(f"No role found for username: {actual_username}")
            return None
            
        # Create user profile from demo data
        demo_profiles = {
            "security_admin": {
                'username': 'security_admin',
                'email': 'admin@kartavya.demo',
                'full_name': 'Security Administrator',
                'role': 'admin',
                'department': 'IT Security',
                'location': 'Mumbai, India',
                'security_clearance': 'Level 5'
            },
            "security_analyst": {
                'username': 'security_analyst',
                'email': 'analyst@kartavya.demo',
                'full_name': 'Security Analyst',
                'role': 'analyst',
                'department': 'SOC Team',
                'location': 'Delhi, India',
                'security_clearance': 'Level 3'
            },
            "security_viewer": {
                'username': 'security_viewer',
                'email': 'viewer@kartavya.demo',
                'full_name': 'Security Viewer',
                'role': 'viewer',
                'department': 'Management',
                'location': 'Bangalore, India',
                'security_clearance': 'Level 2'
            }
        }
        
        profile = demo_profiles.get(actual_username, {
            'username': actual_username,
            'email': f"{actual_username}@kartavya.demo",
            'full_name': actual_username.replace('_', ' ').title(),
            'role': role,
            'department': 'Demo',
            'location': 'Demo Location',
            'security_clearance': 'Level 1'
        })
        
        profile.update({
            'preferences': {},
            'account_locked': False
        })
        
        return profile
    
    try:
        collection = mongodb_client.database["user_profiles"]
        
        # Try multiple fields to find user
        query_conditions = [
            {"email": identifier},
            {"username": identifier},
            {"_id": identifier}
        ]
        
        for condition in query_conditions:
            user = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: collection.find_one(condition)
            )
            if user:
                return user
        
        return None
    
    except Exception as e:
        logger.error(f"Error querying user: {e}")
        return None

def generate_jwt_token(user_profile: Dict[str, Any]) -> str:
    """Generate JWT token for authenticated user"""
    payload = {
        "sub": user_profile['username'],
        "email": user_profile['email'],
        "role": user_profile['role'],
        "full_name": user_profile['full_name'],
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24),  # 24 hour expiry
        "iss": "kartavya-siem"
    }
    
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

async def update_login_statistics(user_profile: Dict[str, Any]):
    """Update user login statistics in database"""
    if not mongodb_client.enabled:
        return
    
    try:
        collection = mongodb_client.database["user_profiles"]
        
        update_data = {
            "$set": {
                "last_login": datetime.utcnow(),
                "last_updated": datetime.utcnow()
            },
            "$inc": {
                "login_count": 1
            }
        }
        
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: collection.update_one(
                {"username": user_profile['username']}, 
                update_data
            )
        )
        
        logger.info(f"Updated login statistics for: {user_profile['username']}")
        
    except Exception as e:
        logger.error(f"Failed to update login statistics: {e}")

async def log_login_attempt(user_profile: Dict[str, Any], success: bool, reason: str = None):
    """Log login attempt to database for audit purposes"""
    if not mongodb_client.enabled:
        return
    
    try:
        collection = mongodb_client.database["login_history"]
        
        log_entry = {
            "username": user_profile['username'],
            "email": user_profile['email'],
            "timestamp": datetime.utcnow(),
            "success": success,
            "ip_address": "127.0.0.1",  # Would get from request in real implementation
            "user_agent": "Kartavya Frontend",
            "reason": reason,
            "session_id": f"session_{user_profile['username']}_{datetime.utcnow().timestamp()}"
        }
        
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: collection.insert_one(log_entry)
        )
        
    except Exception as e:
        logger.error(f"Failed to log login attempt: {e}")

async def cache_user_session(username: str, user_profile: Dict[str, Any], token: str):
    """Cache user session data in Redis"""
    try:
        session_data = {
            "username": username,
            "token": token,
            "role": user_profile['role'],
            "permissions": list(rbac.get_permissions(user_profile['role'])),
            "login_time": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        
        # Set with 24 hour expiry
        await redis_client.set_with_expiry(f"session:{username}", session_data, 86400)
        
    except Exception as e:
        logger.error(f"Failed to cache user session: {e}")

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user profile"""
    try:
        # Decode JWT token
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        username = payload['sub']
        
        # Get fresh user data from database
        user_profile = await get_user_by_identifier(username)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        permissions = list(rbac.get_permissions(user_profile['role']))
        
        return UserProfile(
            username=user_profile['username'],
            email=user_profile['email'],
            full_name=user_profile['full_name'],
            role=user_profile['role'],
            department=user_profile['department'],
            location=user_profile['location'],
            preferences=user_profile.get('preferences', {}),
            last_login=user_profile.get('last_login'),
            permissions=permissions
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Profile fetch error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user and invalidate session"""
    try:
        # Decode token to get username
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        username = payload['sub']
        
        # Remove session from Redis
        if redis_client.enabled:
            await redis_client.delete(f"session:{username}")
        
        # Log logout event
        if mongodb_client.enabled:
            collection = mongodb_client.database["user_activity"]
            logout_entry = {
                "username": username,
                "action": "logout",
                "timestamp": datetime.utcnow(),
                "details": "User logged out",
                "ip_address": "127.0.0.1",
                "success": True
            }
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: collection.insert_one(logout_entry)
            )
        
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"success": False, "message": "Logout failed"}

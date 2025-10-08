#!/usr/bin/env python3
"""
🛡️ ISRO Security & Compliance Module
Enterprise-grade security controls for mission-critical SIEM operations
"""

import hashlib
import secrets
import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt
import bcrypt
import base64
import os

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """ISRO Security Classification Levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


class AuditEventType(Enum):
    """Types of security events to audit"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_VIOLATION = "security_violation"
    SYSTEM_EVENT = "system_event"
    EXPORT_REQUEST = "export_request"
    QUERY_EXECUTION = "query_execution"


@dataclass
class SecurityContext:
    """Security context for user sessions"""
    user_id: str
    username: str
    role: str
    clearance_level: SecurityLevel
    permissions: List[str]
    session_id: str
    ip_address: str
    user_agent: str
    created_at: datetime
    expires_at: datetime
    mfa_verified: bool = False
    last_activity: Optional[datetime] = None


@dataclass
class AuditEvent:
    """Comprehensive audit event logging"""
    event_id: str
    event_type: AuditEventType
    user_id: Optional[str]
    session_id: Optional[str]
    timestamp: datetime
    ip_address: str
    user_agent: str
    action: str
    resource: str
    result: str  # SUCCESS, FAILURE, DENIED
    risk_score: int
    metadata: Dict[str, Any]
    security_classification: SecurityLevel


class ISROSecurityManager:
    """
    Enterprise Security Manager for ISRO compliance
    Implements defense-in-depth security controls
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize security manager with ISRO-grade configurations"""
        self.config = config
        self.is_production = config.get('environment', 'demo') == 'production'
        
        # Encryption components
        self._setup_encryption()
        
        # Security policies
        self.security_policies = self._load_security_policies()
        
        # Audit system
        self.audit_events: List[AuditEvent] = []
        
        # Rate limiting
        self.rate_limits: Dict[str, List[datetime]] = {}
        
        # IP whitelist/blacklist
        self.ip_whitelist = set(config.get('ip_whitelist', []))
        self.ip_blacklist = set(config.get('ip_blacklist', []))
        
        logger.info("🛡️ ISRO Security Manager initialized - Production: %s", self.is_production)
    
    def _setup_encryption(self):
        """Setup enterprise-grade encryption"""
        # Generate or load encryption key
        key_file = self.config.get('encryption_key_file', '.security/master.key')
        
        try:
            if os.path.exists(key_file) and self.is_production:
                with open(key_file, 'rb') as f:
                    self.master_key = f.read()
            else:
                self.master_key = Fernet.generate_key()
                if self.is_production:
                    os.makedirs(os.path.dirname(key_file), exist_ok=True)
                    with open(key_file, 'wb') as f:
                        f.write(self.master_key)
                    os.chmod(key_file, 0o600)  # Secure permissions
            
            self.fernet = Fernet(self.master_key)
            
            # RSA key pair for asymmetric encryption
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096
            )
            self.public_key = self.private_key.public_key()
            
            logger.info("✅ Encryption subsystem initialized")
            
        except Exception as e:
            logger.error("❌ Failed to setup encryption: %s", e)
            raise
    
    def _load_security_policies(self) -> Dict[str, Any]:
        """Load ISRO security policies and compliance rules"""
        return {
            "password_policy": {
                "min_length": 12,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_special": True,
                "forbidden_patterns": [
                    r"password", r"admin", r"root", r"isro", 
                    r"123456", r"qwerty", r"welcome"
                ],
                "max_age_days": 90,
                "history_count": 10
            },
            "session_policy": {
                "max_duration_hours": 8,
                "idle_timeout_minutes": 30,
                "require_mfa": self.is_production,
                "max_concurrent_sessions": 3,
                "ip_binding": True
            },
            "access_control": {
                "require_clearance_verification": True,
                "data_classification_required": True,
                "export_requires_approval": True,
                "query_logging_required": True
            },
            "audit_policy": {
                "log_all_actions": True,
                "retain_days": 2555,  # 7 years for compliance
                "real_time_monitoring": True,
                "alert_on_violations": True
            },
            "network_security": {
                "require_https": True,
                "hsts_enabled": True,
                "csrf_protection": True,
                "rate_limiting": {
                    "requests_per_minute": 60,
                    "burst_limit": 10
                }
            }
        }
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt with high cost factor"""
        # Validate password against policy
        if not self.validate_password_policy(password):
            raise ValueError("Password does not meet ISRO security policy requirements")
        
        # Use high cost factor for production
        cost_factor = 15 if self.is_production else 12
        salt = bcrypt.gensalt(rounds=cost_factor)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error("Password verification failed: %s", e)
            return False
    
    def validate_password_policy(self, password: str) -> Tuple[bool, List[str]]:
        """Validate password against ISRO security policy"""
        policy = self.security_policies['password_policy']
        violations = []
        
        # Length check
        if len(password) < policy['min_length']:
            violations.append(f"Password must be at least {policy['min_length']} characters")
        
        # Character requirements
        if policy['require_uppercase'] and not re.search(r'[A-Z]', password):
            violations.append("Password must contain uppercase letters")
        
        if policy['require_lowercase'] and not re.search(r'[a-z]', password):
            violations.append("Password must contain lowercase letters")
        
        if policy['require_numbers'] and not re.search(r'\d', password):
            violations.append("Password must contain numbers")
        
        if policy['require_special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            violations.append("Password must contain special characters")
        
        # Forbidden patterns
        password_lower = password.lower()
        for pattern in policy['forbidden_patterns']:
            if re.search(pattern, password_lower):
                violations.append(f"Password contains forbidden pattern: {pattern}")
        
        return len(violations) == 0, violations
    
    def create_jwt_token(self, security_context: SecurityContext) -> str:
        """Create secure JWT token with ISRO claims"""
        payload = {
            'sub': security_context.user_id,
            'username': security_context.username,
            'role': security_context.role,
            'clearance': security_context.clearance_level.value,
            'permissions': security_context.permissions,
            'session_id': security_context.session_id,
            'iat': int(security_context.created_at.timestamp()),
            'exp': int(security_context.expires_at.timestamp()),
            'iss': 'KARTAVYA-SIEM',
            'aud': 'ISRO-SOC',
            'mfa_verified': security_context.mfa_verified,
            'ip': security_context.ip_address
        }
        
        # Use RS256 for production, HS256 for demo
        if self.is_production:
            algorithm = 'RS256'
            key = self.private_key.private_key(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            algorithm = 'HS256'
            key = self.config.get('jwt_secret', 'demo-secret-key')
        
        return jwt.encode(payload, key, algorithm=algorithm)
    
    def verify_jwt_token(self, token: str) -> Optional[SecurityContext]:
        """Verify and decode JWT token"""
        try:
            # Choose algorithm and key based on environment
            if self.is_production:
                algorithm = 'RS256'
                key = self.public_key.public_key(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            else:
                algorithm = 'HS256'
                key = self.config.get('jwt_secret', 'demo-secret-key')
            
            payload = jwt.decode(token, key, algorithms=[algorithm])
            
            # Create security context from payload
            return SecurityContext(
                user_id=payload['sub'],
                username=payload['username'],
                role=payload['role'],
                clearance_level=SecurityLevel(payload['clearance']),
                permissions=payload['permissions'],
                session_id=payload['session_id'],
                ip_address=payload['ip'],
                user_agent='',  # Will be updated from request
                created_at=datetime.fromtimestamp(payload['iat']),
                expires_at=datetime.fromtimestamp(payload['exp']),
                mfa_verified=payload.get('mfa_verified', False)
            )
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid JWT token: %s", e)
            return None
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data using Fernet symmetric encryption"""
        try:
            encrypted = self.fernet.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error("Encryption failed: %s", e)
            raise
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error("Decryption failed: %s", e)
            raise
    
    def check_rate_limit(self, identifier: str, limit_per_minute: int = None) -> bool:
        """Check rate limiting for API requests"""
        if limit_per_minute is None:
            limit_per_minute = self.security_policies['network_security']['rate_limiting']['requests_per_minute']
        
        now = datetime.utcnow()
        cutoff_time = now - timedelta(minutes=1)
        
        # Clean old entries
        if identifier in self.rate_limits:
            self.rate_limits[identifier] = [
                timestamp for timestamp in self.rate_limits[identifier]
                if timestamp > cutoff_time
            ]
        else:
            self.rate_limits[identifier] = []
        
        # Check if under limit
        if len(self.rate_limits[identifier]) >= limit_per_minute:
            self.log_security_violation(
                user_id=None,
                action="rate_limit_exceeded",
                resource=f"api:{identifier}",
                ip_address=identifier.split(':')[0] if ':' in identifier else identifier,
                metadata={"limit": limit_per_minute, "attempts": len(self.rate_limits[identifier])}
            )
            return False
        
        # Add current request
        self.rate_limits[identifier].append(now)
        return True
    
    def validate_ip_address(self, ip_address: str) -> bool:
        """Validate IP address against whitelist/blacklist"""
        # Check blacklist first
        if ip_address in self.ip_blacklist:
            return False
        
        # If whitelist is configured, check it
        if self.ip_whitelist and ip_address not in self.ip_whitelist:
            return False
        
        return True
    
    def check_authorization(self, context: SecurityContext, resource: str, action: str) -> bool:
        """Check if user is authorized for specific resource and action"""
        # Admin users have full access
        if context.role == 'admin':
            return True
        
        # Build permission string
        permission = f"{resource}:{action}"
        
        # Check explicit permissions
        if permission in context.permissions:
            return True
        
        # Check wildcard permissions
        resource_wildcard = f"{resource}:*"
        if resource_wildcard in context.permissions:
            return True
        
        # Check role-based access
        role_permissions = self._get_role_permissions(context.role)
        if permission in role_permissions or resource_wildcard in role_permissions:
            return True
        
        # Check clearance-based access
        if self._check_clearance_access(context.clearance_level, resource):
            return True
        
        return False
    
    def _get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for a specific role"""
        role_permissions = {
            'admin': ['*:*'],  # Full access
            'security_analyst': [
                'siem:query', 'siem:search', 'siem:analyze',
                'reports:generate', 'reports:view',
                'dashboard:view', 'alerts:view', 'alerts:acknowledge'
            ],
            'soc_operator': [
                'siem:query', 'siem:search',
                'dashboard:view', 'alerts:view', 'alerts:acknowledge'
            ],
            'auditor': [
                'reports:generate', 'reports:view', 'reports:export',
                'audit:view', 'dashboard:view'
            ],
            'viewer': [
                'dashboard:view', 'reports:view'
            ]
        }
        
        return role_permissions.get(role, [])
    
    def _check_clearance_access(self, user_clearance: SecurityLevel, resource: str) -> bool:
        """Check if user's clearance level allows access to resource"""
        # Define clearance hierarchy
        clearance_levels = {
            SecurityLevel.PUBLIC: 1,
            SecurityLevel.INTERNAL: 2,
            SecurityLevel.CONFIDENTIAL: 3,
            SecurityLevel.SECRET: 4,
            SecurityLevel.TOP_SECRET: 5
        }
        
        # Resource classification requirements
        resource_requirements = {
            'siem:threat_intelligence': SecurityLevel.CONFIDENTIAL,
            'siem:export': SecurityLevel.SECRET,
            'system:config': SecurityLevel.SECRET,
            'admin:users': SecurityLevel.CONFIDENTIAL,
        }
        
        required_clearance = resource_requirements.get(resource, SecurityLevel.INTERNAL)
        user_level = clearance_levels[user_clearance]
        required_level = clearance_levels[required_clearance]
        
        return user_level >= required_level
    
    def log_audit_event(self, 
                       event_type: AuditEventType,
                       user_id: Optional[str],
                       session_id: Optional[str],
                       ip_address: str,
                       user_agent: str,
                       action: str,
                       resource: str,
                       result: str,
                       metadata: Dict[str, Any] = None,
                       classification: SecurityLevel = SecurityLevel.INTERNAL) -> str:
        """Log comprehensive audit event"""
        
        event_id = self._generate_event_id()
        
        audit_event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            action=action,
            resource=resource,
            result=result,
            risk_score=self._calculate_risk_score(event_type, action, result, metadata or {}),
            metadata=metadata or {},
            security_classification=classification
        )
        
        # Store audit event
        self.audit_events.append(audit_event)
        
        # Log to system logger based on risk score
        log_level = logging.WARNING if audit_event.risk_score >= 7 else logging.INFO
        logger.log(log_level, "AUDIT: %s - %s:%s by %s (%s)", 
                  result, resource, action, user_id or 'anonymous', ip_address)
        
        # Real-time alerting for high-risk events
        if audit_event.risk_score >= 8:
            asyncio.create_task(self._send_security_alert(audit_event))
        
        return event_id
    
    def log_security_violation(self,
                             user_id: Optional[str],
                             action: str,
                             resource: str,
                             ip_address: str,
                             metadata: Dict[str, Any] = None):
        """Log security violation with high priority"""
        self.log_audit_event(
            event_type=AuditEventType.SECURITY_VIOLATION,
            user_id=user_id,
            session_id=None,
            ip_address=ip_address,
            user_agent='',
            action=action,
            resource=resource,
            result='VIOLATION',
            metadata=metadata,
            classification=SecurityLevel.CONFIDENTIAL
        )
    
    def _calculate_risk_score(self, event_type: AuditEventType, action: str, 
                            result: str, metadata: Dict[str, Any]) -> int:
        """Calculate risk score for audit events (0-10 scale)"""
        base_score = 1
        
        # Event type risk
        event_type_scores = {
            AuditEventType.AUTHENTICATION: 3,
            AuditEventType.AUTHORIZATION: 4,
            AuditEventType.DATA_ACCESS: 5,
            AuditEventType.CONFIGURATION_CHANGE: 7,
            AuditEventType.SECURITY_VIOLATION: 9,
            AuditEventType.EXPORT_REQUEST: 6,
            AuditEventType.QUERY_EXECUTION: 2
        }
        
        base_score += event_type_scores.get(event_type, 1)
        
        # Result impact
        if result == 'FAILURE':
            base_score += 2
        elif result == 'DENIED':
            base_score += 3
        elif result == 'VIOLATION':
            base_score += 5
        
        # Action-specific risks
        high_risk_actions = ['delete', 'export', 'modify_config', 'privilege_escalation']
        if any(risk_action in action.lower() for risk_action in high_risk_actions):
            base_score += 2
        
        # Metadata-based adjustments
        if metadata.get('multiple_attempts', 0) > 5:
            base_score += 1
        
        if metadata.get('external_ip', False):
            base_score += 1
        
        return min(base_score, 10)  # Cap at 10
    
    async def _send_security_alert(self, event: AuditEvent):
        """Send real-time security alert for high-risk events"""
        # In production, this would integrate with SIEM alerting
        alert_data = {
            'event_id': event.event_id,
            'severity': 'HIGH' if event.risk_score >= 9 else 'MEDIUM',
            'summary': f'Security Event: {event.action} on {event.resource}',
            'details': asdict(event),
            'timestamp': event.timestamp.isoformat()
        }
        
        logger.critical("SECURITY ALERT: %s", json.dumps(alert_data, indent=2))
        
        # Additional alerting mechanisms would go here
        # - Email notifications
        # - SIEM integration
        # - Incident management system
        # - Mobile push notifications
    
    def _generate_event_id(self) -> str:
        """Generate unique audit event ID"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        random_suffix = secrets.token_hex(4)
        return f"ISRO_AUDIT_{timestamp}_{random_suffix}"
    
    def get_audit_events(self, 
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None,
                        user_id: Optional[str] = None,
                        event_types: Optional[List[AuditEventType]] = None,
                        min_risk_score: Optional[int] = None) -> List[AuditEvent]:
        """Query audit events with filters"""
        
        filtered_events = self.audit_events
        
        if start_time:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
        
        if end_time:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
        
        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]
        
        if event_types:
            filtered_events = [e for e in filtered_events if e.event_type in event_types]
        
        if min_risk_score:
            filtered_events = [e for e in filtered_events if e.risk_score >= min_risk_score]
        
        return sorted(filtered_events, key=lambda x: x.timestamp, reverse=True)
    
    def generate_security_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        events = self.get_audit_events(start_time=start_time, end_time=end_time)
        
        # Calculate statistics
        total_events = len(events)
        high_risk_events = len([e for e in events if e.risk_score >= 7])
        violations = len([e for e in events if e.event_type == AuditEventType.SECURITY_VIOLATION])
        
        # Event type breakdown
        event_type_counts = {}
        for event in events:
            event_type_counts[event.event_type.value] = event_type_counts.get(event.event_type.value, 0) + 1
        
        # Top users by activity
        user_activity = {}
        for event in events:
            if event.user_id:
                user_activity[event.user_id] = user_activity.get(event.user_id, 0) + 1
        
        # Risk trends by day
        daily_risk = {}
        for event in events:
            day = event.timestamp.date().isoformat()
            if day not in daily_risk:
                daily_risk[day] = []
            daily_risk[day].append(event.risk_score)
        
        daily_avg_risk = {day: sum(scores)/len(scores) for day, scores in daily_risk.items()}
        
        return {
            'report_period': {
                'start_date': start_time.isoformat(),
                'end_date': end_time.isoformat(),
                'days': days
            },
            'summary': {
                'total_events': total_events,
                'high_risk_events': high_risk_events,
                'security_violations': violations,
                'average_risk_score': sum(e.risk_score for e in events) / len(events) if events else 0
            },
            'event_breakdown': event_type_counts,
            'top_users': dict(sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]),
            'risk_trends': daily_avg_risk,
            'compliance_status': 'COMPLIANT' if violations == 0 else 'NEEDS_ATTENTION',
            'recommendations': self._generate_security_recommendations(events)
        }
    
    def _generate_security_recommendations(self, events: List[AuditEvent]) -> List[str]:
        """Generate security improvement recommendations"""
        recommendations = []
        
        violations = [e for e in events if e.event_type == AuditEventType.SECURITY_VIOLATION]
        if violations:
            recommendations.append(f"Investigate {len(violations)} security violations")
        
        high_risk = [e for e in events if e.risk_score >= 8]
        if high_risk:
            recommendations.append(f"Review {len(high_risk)} high-risk security events")
        
        failed_auths = [e for e in events if e.event_type == AuditEventType.AUTHENTICATION and e.result == 'FAILURE']
        if len(failed_auths) > 10:
            recommendations.append("High number of authentication failures - consider implementing additional controls")
        
        return recommendations


# Security utilities
def generate_secure_session_id() -> str:
    """Generate cryptographically secure session ID"""
    return f"ISRO_SESSION_{secrets.token_urlsafe(32)}"


def sanitize_user_input(input_data: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    # Remove dangerous characters and patterns
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',  # XSS
        r'javascript:',               # JavaScript URLs
        r'on\w+\s*=',                # Event handlers
        r'union\s+select',           # SQL injection
        r'drop\s+table',             # SQL injection
        r'\bexec\b',                 # Command injection
        r'\beval\b',                 # Code evaluation
    ]
    
    sanitized = input_data
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    # Remove non-printable characters
    sanitized = ''.join(char for char in sanitized if char.isprintable())
    
    return sanitized.strip()


def validate_isro_user_format(username: str) -> bool:
    """Validate username follows ISRO format"""
    # ISRO username pattern: letters, numbers, dots, hyphens
    pattern = r'^[a-zA-Z][a-zA-Z0-9._-]{2,31}$'
    return bool(re.match(pattern, username))


# Factory function
def create_security_manager(config: Dict[str, Any]) -> ISROSecurityManager:
    """Factory function to create security manager"""
    return ISROSecurityManager(config)


if __name__ == "__main__":
    # Demo usage
    config = {
        'environment': 'production',
        'jwt_secret': 'demo-secret',
        'encryption_key_file': '.security/test.key'
    }
    
    security_manager = create_security_manager(config)
    
    # Test password validation
    password = "SecureISRO2025!@#"
    is_valid, violations = security_manager.validate_password_policy(password)
    print(f"Password valid: {is_valid}")
    if not is_valid:
        for violation in violations:
            print(f"  - {violation}")
    
    # Test encryption
    sensitive_data = "CLASSIFIED: ISRO Mission Data"
    encrypted = security_manager.encrypt_sensitive_data(sensitive_data)
    decrypted = security_manager.decrypt_sensitive_data(encrypted)
    print(f"Encryption test: {sensitive_data == decrypted}")
    
    print("🛡️ ISRO Security Manager test completed")

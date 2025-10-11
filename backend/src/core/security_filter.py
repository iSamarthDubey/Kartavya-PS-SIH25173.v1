#!/usr/bin/env python3
"""
🔒 Security Logging Filter
Redacts sensitive information from logs to prevent credential leaks
"""

import re
import logging
from typing import Dict, List, Pattern


class SecurityLoggingFilter(logging.Filter):
    """Filter that redacts sensitive information from log messages"""
    
    def __init__(self):
        super().__init__()
        
        # Patterns to redact sensitive information
        self.sensitive_patterns: List[Pattern] = [
            # API Keys - various formats
            re.compile(r'(?i)(api[_-]?key["\s:=]+)[a-zA-Z0-9_\-\.]{20,}', re.IGNORECASE),
            re.compile(r'(?i)(gemini[_-]?api[_-]?key["\s:=]+)[a-zA-Z0-9_\-\.]{20,}', re.IGNORECASE),
            re.compile(r'(?i)(openai[_-]?api[_-]?key["\s:=]+)[a-zA-Z0-9_\-\.]{20,}', re.IGNORECASE),
            re.compile(r'(?i)(sk-[a-zA-Z0-9_\-\.]{40,})', re.IGNORECASE),  # OpenAI keys
            re.compile(r'(?i)(AIzaSy[a-zA-Z0-9_\-\.]{33})', re.IGNORECASE),  # Google API keys
            
            # JWT Tokens
            re.compile(r'(?i)(bearer\s+)?([a-zA-Z0-9_\-\.]{100,})', re.IGNORECASE),
            re.compile(r'(?i)(jwt["\s:=]+)[a-zA-Z0-9_\-\.]{100,}', re.IGNORECASE),
            re.compile(r'(?i)(token["\s:=]+)[a-zA-Z0-9_\-\.]{100,}', re.IGNORECASE),
            
            # Database URIs
            re.compile(r'(?i)(mongodb\+srv://[^:\s]+):([^@\s]+)@', re.IGNORECASE),
            re.compile(r'(?i)(postgresql://[^:\s]+):([^@\s]+)@', re.IGNORECASE),
            re.compile(r'(?i)(redis://[^:\s]*):([^@\s]+)@', re.IGNORECASE),
            
            # Database passwords
            re.compile(r'(?i)(password["\s:=]+)[^"\s,}]{8,}', re.IGNORECASE),
            re.compile(r'(?i)(passwd["\s:=]+)[^"\s,}]{8,}', re.IGNORECASE),
            re.compile(r'(?i)(pwd["\s:=]+)[^"\s,}]{8,}', re.IGNORECASE),
            
            # Supabase keys
            re.compile(r'(?i)(supabase[_-]?[a-z]*[_-]?key["\s:=]+)[a-zA-Z0-9_\-\.]{40,}', re.IGNORECASE),
            re.compile(r'(?i)(eyJ[a-zA-Z0-9_\-\.]{100,})', re.IGNORECASE),  # JWT format
            
            # Redis passwords
            re.compile(r'(?i)(redis[_-]?password["\s:=]+)[^"\s,}]{8,}', re.IGNORECASE),
            
            # Generic secrets
            re.compile(r'(?i)(secret["\s:=]+)[^"\s,}]{10,}', re.IGNORECASE),
            re.compile(r'(?i)(private[_-]?key["\s:=]+)[^"\s,}]{20,}', re.IGNORECASE),
            
            # Email/username in sensitive contexts
            re.compile(r'(?i)(login.*identifier["\s:=]+)[^\s"}{,]+@[^\s"}{,]+', re.IGNORECASE),
        ]
        
        # Replacement strings
        self.replacements: Dict[str, str] = {
            'api_key': '[API_KEY_REDACTED]',
            'token': '[TOKEN_REDACTED]',
            'password': '[PASSWORD_REDACTED]',
            'secret': '[SECRET_REDACTED]',
            'uri_creds': r'\1[CREDENTIALS_REDACTED]@',
            'jwt': '[JWT_REDACTED]',
            'email': '[EMAIL_REDACTED]'
        }

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter and redact sensitive information from log records
        
        Args:
            record: The log record to filter
            
        Returns:
            bool: Always True (we modify the record but don't drop it)
        """
        try:
            # Redact from the main message
            if hasattr(record, 'msg') and record.msg:
                record.msg = self._redact_sensitive_info(str(record.msg))
            
            # Redact from formatted message if it exists
            if hasattr(record, 'getMessage'):
                try:
                    original_get_message = record.getMessage
                    def safe_get_message():
                        msg = original_get_message()
                        return self._redact_sensitive_info(msg)
                    record.getMessage = safe_get_message
                except:
                    pass
                    
            # Redact from args if they exist
            if hasattr(record, 'args') and record.args:
                try:
                    if isinstance(record.args, (list, tuple)):
                        record.args = tuple(
                            self._redact_sensitive_info(str(arg)) if isinstance(arg, str) else arg
                            for arg in record.args
                        )
                    elif isinstance(record.args, dict):
                        record.args = {
                            k: self._redact_sensitive_info(str(v)) if isinstance(v, str) else v
                            for k, v in record.args.items()
                        }
                except:
                    # If we can't process args safely, leave them as is
                    pass
                    
        except Exception:
            # If anything goes wrong with filtering, don't break logging
            pass
            
        return True

    def _redact_sensitive_info(self, text: str) -> str:
        """
        Redact sensitive information from a text string
        
        Args:
            text: The text to redact
            
        Returns:
            str: The text with sensitive information redacted
        """
        if not text or not isinstance(text, str):
            return text
            
        redacted_text = text
        
        try:
            # API Keys and Tokens
            redacted_text = re.sub(
                r'(?i)(api[_-]?key["\s:=]+)[a-zA-Z0-9_\-\.]{20,}',
                r'\1[API_KEY_REDACTED]',
                redacted_text
            )
            
            redacted_text = re.sub(
                r'(?i)(gemini[_-]?api[_-]?key["\s:=]+)[a-zA-Z0-9_\-\.]{20,}',
                r'\1[API_KEY_REDACTED]',
                redacted_text
            )
            
            redacted_text = re.sub(
                r'(?i)(openai[_-]?api[_-]?key["\s:=]+)[a-zA-Z0-9_\-\.]{20,}',
                r'\1[API_KEY_REDACTED]',
                redacted_text
            )
            
            # OpenAI keys (sk-...)
            redacted_text = re.sub(
                r'(?i)(sk-[a-zA-Z0-9_\-\.]{40,})',
                r'[OPENAI_KEY_REDACTED]',
                redacted_text
            )
            
            # Google API keys (AIzaSy...)
            redacted_text = re.sub(
                r'(?i)(AIzaSy[a-zA-Z0-9_\-\.]{33})',
                r'[GOOGLE_API_KEY_REDACTED]',
                redacted_text
            )
            
            # JWT tokens (long base64 strings)
            redacted_text = re.sub(
                r'(?i)(bearer\s+)?([a-zA-Z0-9_\-\.]{100,})',
                r'\1[JWT_TOKEN_REDACTED]',
                redacted_text
            )
            
            # Database connection strings
            redacted_text = re.sub(
                r'(?i)(mongodb\+srv://[^:\s]+):([^@\s]+)@',
                r'\1:[PASSWORD_REDACTED]@',
                redacted_text
            )
            
            redacted_text = re.sub(
                r'(?i)(postgresql://[^:\s]+):([^@\s]+)@',
                r'\1:[PASSWORD_REDACTED]@',
                redacted_text
            )
            
            redacted_text = re.sub(
                r'(?i)(redis://[^:\s]*):([^@\s]+)@',
                r'\1:[PASSWORD_REDACTED]@',
                redacted_text
            )
            
            # Passwords
            redacted_text = re.sub(
                r'(?i)(password["\s:=]+)[^"\s,}]{8,}',
                r'\1[PASSWORD_REDACTED]',
                redacted_text
            )
            
            # Supabase JWT tokens
            redacted_text = re.sub(
                r'(?i)(supabase[_-]?[a-z]*[_-]?key["\s:=]+)[a-zA-Z0-9_\-\.]{40,}',
                r'\1[SUPABASE_KEY_REDACTED]',
                redacted_text
            )
            
            # Generic secrets
            redacted_text = re.sub(
                r'(?i)(secret["\s:=]+)[^"\s,}]{10,}',
                r'\1[SECRET_REDACTED]',
                redacted_text
            )
            
            # Mask long strings that look like credentials in various contexts
            redacted_text = re.sub(
                r'(?i)(token["\s:=]+)[a-zA-Z0-9_\-\.]{50,}',
                r'\1[TOKEN_REDACTED]',
                redacted_text
            )
            
        except Exception:
            # If regex fails for any reason, return original text
            # Better to show unredacted than to break logging completely
            pass
            
        return redacted_text


def setup_secure_logging(log_level: str = "INFO") -> None:
    """
    Setup secure logging with credential redaction
    
    Args:
        log_level: The logging level to use
    """
    # Create security filter
    security_filter = SecurityLoggingFilter()
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with security filter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Add security filter to handler
    console_handler.addFilter(security_filter)
    
    # Set format
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Also add the filter to any existing handlers
    for logger_name in ['uvicorn', 'uvicorn.error', 'uvicorn.access', 'fastapi']:
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers:
            handler.addFilter(security_filter)


def test_security_filter():
    """Test the security filter with sample sensitive data"""
    test_messages = [
        "API key: AIzaSyAT#####6hjt......y-k........LS**TU",
        "OpenAI key: sk-proj-_HS-X8Mit.................Kw1SL",
        "MongoDB URI: mongodb+srv://user:password123@cluster.mongodb.net/db",
        "JWT token: eyJkpXVCJ9.eyJzdWIiO***********ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
        "Login attempt for admin@kartavya.demo with password Admin!2025",
        "Supabase key: eyJhbGcI1NiIdfnegfdndd.bbbbfejrb##dfdny*****..iJzdXBhYmFzZSJ9.test"
    ]
    
    filter_instance = SecurityLoggingFilter()
    
    print("🧪 Testing Security Filter:")
    for msg in test_messages:
        redacted = filter_instance._redact_sensitive_info(msg)
        print(f"Original: {msg}")
        print(f"Redacted: {redacted}")
        print()


if __name__ == "__main__":
    test_security_filter()

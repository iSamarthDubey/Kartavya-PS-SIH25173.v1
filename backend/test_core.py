#!/usr/bin/env python3
"""Test the core modules"""

try:
    from src.core.security_filter import SecurityLoggingFilter
    from src.core.port_manager import setup_port_for_service
    
    # Test security filter
    filter = SecurityLoggingFilter()
    test_msg = 'API key: AIzaSyATdeO9G6hjt9S4VD81y-kVWpq6OLSO2TU and password Admin!2025'
    redacted = filter._redact_sensitive_info(test_msg)
    print('🔒 Security Filter Test:')
    print(f'Original: {test_msg}')
    print(f'Redacted: {redacted}')
    print()
    
    # Test port manager  
    print('🚢 Port Manager Test:')
    success, port, msg = setup_port_for_service(8888, 'Test Service', auto_kill=False)
    print(f'Port check result: success={success}, port={port}, message="{msg}"')
    print()
    print('✅ All core modules loaded successfully!')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
except Exception as e:
    print(f'❌ Error: {e}')

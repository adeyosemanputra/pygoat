"""
Vulnerabilities views package.

This package contains all the vulnerability-related views organized by category.
"""

# Import and expose all vulnerability views
from .xss_views import xss, xss_lab, xss_lab2, xss_lab3
from .sql_views import sql, sql_lab
from .auth_failure_views import auth_failure, auth_failure_lab2, auth_failure_lab3, A7_discussion
from .deserialization_views import insec_des, insec_des_lab, insec_desgine, insec_desgine_lab
from .ssrf_views import ssrf, ssrf_lab, ssrf_discussion, ssrf_target, ssrf_lab2
from .crypto_views import crypto_failure, crypto_failure_lab, crypto_failure_lab2, crypto_failure_lab3
from .a2_views import a2, a2_lab, insecure_password_reset, a2_lab2
from .a3_views import a3, a3_lab, command_injection, a3_lab2, xml_processor
from .a4_views import a4, a4_lab, password_reset, verify_reset_token, a4_lab2, get_balance
from .a5_views import a5, a5_lab, debug_info, a5_lab2
from .a6_views import a6, a6_lab, package_info, a6_lab2
from .a8_views import a8, a8_lab, webhook, a8_lab2
from .a9_views import a9, a9_lab, get_version, A9_discussion
from .a10_views import a10, a10_lab, debug, a10_lab2
from .a11_views import a11, a11_lab, gentckt
from .access_control_views import (
    ba, ba_lab, 
    a1_broken_access, 
    a1_broken_access_lab_1, 
    a1_broken_access_lab_2, 
    a1_broken_access_lab_3, 
    a1_broken_access_lab3_secret
)

# Make all views available when importing from vulnerabilities package
__all__ = [
    # XSS views
    'xss', 'xss_lab', 'xss_lab2', 'xss_lab3',
    
    # SQL Injection views
    'sql', 'sql_lab',
    
    # Authentication Failure views
    'auth_failure', 'auth_failure_lab2', 'auth_failure_lab3', 'A7_discussion',
    
    # Deserialization views
    'insec_des', 'insec_des_lab', 'insec_desgine', 'insec_desgine_lab',
    
    # SSRF views
    'ssrf', 'ssrf_lab', 'ssrf_discussion', 'ssrf_target', 'ssrf_lab2',
    
    # Cryptographic Failure views
    'crypto_failure', 'crypto_failure_lab', 'crypto_failure_lab2', 'crypto_failure_lab3',
    
    # A2: Cryptographic Failures
    'a2', 'a2_lab', 'insecure_password_reset', 'a2_lab2',
    
    # A3: Injection
    'a3', 'a3_lab', 'command_injection', 'a3_lab2', 'xml_processor',
    
    # A4: Insecure Design
    'a4', 'a4_lab', 'password_reset', 'verify_reset_token', 'a4_lab2', 'get_balance',
    
    # A5: Security Misconfiguration
    'a5', 'a5_lab', 'debug_info', 'a5_lab2',
    
    # A6: Vulnerable and Outdated Components
    'a6', 'a6_lab', 'package_info', 'a6_lab2',
    
    # A8: Software and Data Integrity Failures
    'a8', 'a8_lab', 'webhook', 'a8_lab2',
    
    # A9: Security Logging and Monitoring Failures
    'a9', 'a9_lab', 'get_version', 'A9_discussion',
    
    # A10: Server-Side Request Forgery
    'a10', 'a10_lab', 'debug', 'a10_lab2',
    
    # A11: Insecure Design views
    'a11', 'a11_lab', 'gentckt',
    
    # A1: Broken Access Control views
    'ba', 'ba_lab',
    'a1_broken_access', 'a1_broken_access_lab_1', 'a1_broken_access_lab_2',
    'a1_broken_access_lab_3', 'a1_broken_access_lab3_secret'
]

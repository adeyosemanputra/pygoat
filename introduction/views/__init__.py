# Import and expose all views
from .auth.views import (
    register, auth_home, auth_lab, auth_lab_signup, 
    auth_lab_login, auth_lab_logout
)

from .vulnerabilities.xss_views import xss, xss_lab, xss_lab2, xss_lab3
from .vulnerabilities.sql_views import sql, sql_lab
from .vulnerabilities.auth_failure_views import (
    auth_failure, auth_failure_lab2, auth_failure_lab3, A7_discussion
)

# Keep these imports for backward compatibility
__all__ = [
    'register', 'auth_home', 'auth_lab', 'auth_lab_signup',
    'auth_lab_login', 'auth_lab_logout', 'xss', 'xss_lab',
    'xss_lab2', 'xss_lab3', 'sql', 'sql_lab', 'auth_failure',
    'auth_failure_lab2', 'auth_failure_lab3', 'A7_discussion'
]

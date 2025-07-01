"""
Main views module - serves as a router to the modular views.
All views have been moved to their respective modules in the 'vulnerabilities' package.
This file is maintained for backward compatibility.
"""

import warnings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Import models that might be needed by other parts of the application
from .models import (FAANG, AF_admin, AF_session_id, Blogs, CF_user, authLogin,
                     comments, info, login, otp, sql_lab_table, tickits)

# Import utility functions and constants
from .views.utils import (
    customHash, 
    filter_blog, 
    ph, 
    USER_A7_LAB3, 
    TestUser, 
    pickled_user, 
    encoded_user
)

# Show deprecation warning
warnings.warn(
    "Direct imports from introduction.views are deprecated. "
    "Please import from introduction.views.vulnerabilities instead.",
    DeprecationWarning,
    stacklevel=2
)

# Authentication decorator
authentication_decorator = login_required

def home(request):
    """Home view that redirects to login if not authenticated."""
    if request.user.is_authenticated:
        return render(request, 'introduction/home.html')
    return redirect('login')

# Import all views from the vulnerabilities package
from .views.vulnerabilities import *

# Re-export specific views that might be imported directly
from .views.vulnerabilities.a1_views import *
from .views.vulnerabilities.a2_views import *
from .views.vulnerabilities.a3_views import *
from .views.vulnerabilities.a4_views import *
from .views.vulnerabilities.a5_views import *
from .views.vulnerabilities.a6_views import *
from .views.vulnerabilities.a7_views import *
from .views.vulnerabilities.a8_views import *
from .views.vulnerabilities.a9_views import *
from .views.vulnerabilities.a10_views import *
from .views.vulnerabilities.a11_views import *
from .views.vulnerabilities.xss_views import *
from .views.vulnerabilities.sql_views import *
from .views.vulnerabilities.auth_failure_views import *
from .views.vulnerabilities.deserialization_views import *
from .views.vulnerabilities.ssrf_views import *
from .views.vulnerabilities.crypto_views import *
from .views.vulnerabilities.access_control_views import *

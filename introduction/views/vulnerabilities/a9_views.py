import logging
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# Configure logger
logger = logging.getLogger(__name__)

# A9: Security Logging and Monitoring Failures Views

def a9(request):
    """View for A9: Security Logging and Monitoring Failures introduction."""
    return render(request, 'a9.html')

@require_http_methods(['GET', 'POST'])
def a9_lab(request):
    """Lab for demonstrating security logging and monitoring failures."""
    context = {}
    
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        # Insecure: Logging sensitive information
        logger.info(f"Login attempt - Username: {username}, Password: {password}")
        
        # Simulate login (insecure for demonstration)
        if username == 'admin' and password == 'admin123':
            context['message'] = 'Login successful!'
            # Log successful login without sensitive data
            logger.info(f"Successful login for user: {username}")
        else:
            context['error'] = 'Invalid credentials'
            # Log failed login attempt
            logger.warning(f"Failed login attempt for username: {username}")
    
    return render(request, 'a9_lab.html', context)

def get_version(request):
    """Insecure endpoint that exposes version information."""
    # Insecure: Exposing version information that could help attackers
    version_info = {
        'application': 'VulnerableApp',
        'version': '1.0.0',
        'environment': 'production',
        'debug': False,
        'database': {
            'name': 'postgresql',
            'version': '13.2',
            'host': 'db.internal'
        },
        'server': {
            'name': 'gunicorn',
            'version': '20.0.4'
        },
        'dependencies': {
            'django': '3.2.0',
            'python': '3.9.0'
        }
    }
    
    # Log access to version endpoint
    logger.info(f"Version information accessed by {request.META.get('REMOTE_ADDR')}")
    
    return JsonResponse(version_info)

@require_http_methods(['GET', 'POST'])
def a9_lab2(request):
    """Lab 2 for demonstrating security logging and monitoring failures."""
    context = {}
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Insecure: No rate limiting or proper logging of admin actions
        if action == 'delete_user':
            user_id = request.POST.get('user_id')
            # In a real app, this would delete the user
            context['message'] = f'User {user_id} deleted successfully'
            
            # Log the action (but without proper user context or details)
            logger.info(f"User deleted: {user_id}")
        
        elif action == 'update_settings':
            setting = request.POST.get('setting')
            value = request.POST.get('value')
            # In a real app, this would update the setting
            context['message'] = f'Setting {setting} updated to {value}'
            
            # Log the action (but without proper user context or details)
            logger.info(f"Setting updated: {setting} = {value}")
    
    return render(request, 'a9_lab2.html', context)

def A9_discussion(request):
    """View for A9 discussion and mitigation strategies."""
    return render(request, 'A9_discussion.html')

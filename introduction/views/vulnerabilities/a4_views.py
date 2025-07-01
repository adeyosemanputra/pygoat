import logging
import random
import string
import hashlib
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db import transaction

# Configure logger
logger = logging.getLogger(__name__)

# A4: Insecure Design Views

def a4(request):
    """View for A4: Insecure Design introduction."""
    return render(request, 'a4.html')

def generate_weak_token(user_id):
    ""
    Insecure: Generates a weak token based on predictable values.
    This is just for demonstration - do NOT use in production!
    """
    # Insecure: Using predictable values for token generation
    timestamp = int(datetime.now().timestamp())
    return hashlib.md5(f"{user_id}-{timestamp}".encode()).hexdigest()

@require_http_methods(['GET', 'POST'])
def a4_lab(request):
    """Lab for demonstrating insecure design patterns."""
    context = {}
    
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id', '1')
            
            # Insecure: Using weak token generation
            token = generate_weak_token(user_id)
            
            # Insecure: Storing sensitive information in client-side storage
            response = render(request, 'a4_lab.html', {'token': token, 'user_id': user_id})
            response.set_cookie('auth_token', token, max_age=3600*24*30)  # 30 days
            return response
            
        except Exception as e:
            context['error'] = f"Error: {str(e)}"
    
    return render(request, 'a4_lab.html', context)

@require_http_methods(['GET', 'POST'])
def password_reset(request):
    """Insecure password reset implementation."""
    context = {}
    
    if request.method == 'POST':
        try:
            username = request.POST.get('username', '')
            
            # Insecure: Using weak password reset token
            reset_token = ''.join(random.choices(string.digits, k=4))  # 4-digit token
            
            # Insecure: Logging sensitive information
            logger.info(f"Password reset requested for {username}. Token: {reset_token}")
            
            context['message'] = f"A reset token has been sent to the email associated with {username}."
            context['token'] = reset_token  # Insecure: Returning token in response
            
        except Exception as e:
            context['error'] = f"Error processing request: {str(e)}"
    
    return render(request, 'a4_password_reset.html', context)

def verify_reset_token(request):
    """Insecure token verification."""
    if request.method == 'POST':
        token = request.POST.get('token', '')
        new_password = request.POST.get('new_password', '')
        
        # Insecure: No rate limiting or proper token validation
        if token == request.session.get('reset_token'):
            # Insecure: No password strength requirements
            if len(new_password) > 0:
                # In a real app, this would update the user's password
                return JsonResponse({
                    'status': 'success',
                    'message': 'Password has been reset successfully.'
                })
        
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid or expired token.'
        }, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@require_http_methods(['GET', 'POST'])
def a4_lab2(request):
    """Lab 2 for demonstrating more insecure design patterns."""
    context = {}
    
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            
            if action == 'transfer_money':
                # Insecure: No transaction validation or proper business logic
                amount = float(request.POST.get('amount', '0'))
                from_account = request.POST.get('from_account')
                to_account = request.POST.get('to_account')
                
                # Insecure: No proper validation of account ownership or balance
                if amount > 0:
                    # In a real app, this would update account balances
                    context['message'] = f"Successfully transferred ${amount:.2f} from {from_account} to {to_account}"
                else:
                    context['error'] = "Invalid amount"
            
            elif action == 'create_user':
                # Insecure: No input validation or proper role assignment
                username = request.POST.get('username', '').strip()
                role = request.POST.get('role', 'user')
                
                if username:
                    # Insecure: No validation of username or role
                    # In a real app, this would create a user with the specified role
                    context['message'] = f"Created user '{username}' with role '{role}'"
                    
                    # Insecure: Logging sensitive information
                    logger.info(f"Created user: {username}, Role: {role}")
            
        except Exception as e:
            context['error'] = f"Error processing request: {str(e)}"
    
    return render(request, 'a4_lab2.html', context)

def get_balance(request):
    """Insecure balance checking endpoint."""
    account_id = request.GET.get('account_id')
    
    # Insecure: No proper authentication or authorization
    # In a real app, this would check if the user has access to this account
    
    # Mock balance data (in a real app, this would come from a database)
    balances = {
        '1001': 1500.00,
        '1002': 500.00,
        '1003': 2500.00,
        'admin': 1000000.00
    }
    
    balance = balances.get(account_id, 0.00)
    
    return JsonResponse({
        'account_id': account_id,
        'balance': balance,
        'currency': 'USD',
        'last_updated': datetime.now().isoformat()
    })

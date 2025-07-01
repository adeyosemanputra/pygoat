import logging
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from ..models import login

# Authentication Failure Views
def auth_failure(request):
    return render(request, 'auth_failure.html')

@require_http_methods(['GET', 'POST'])
def auth_failure_lab2(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            # Insecure: Direct string comparison with raw password
            user = login.objects.get(username=username, password=password)
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            return redirect('dashboard')
        except login.DoesNotExist:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'auth_failure_lab2.html')

# Hardcoded user table for demonstration purposes only
USER_A7_LAB3 = {
    "User1": {"userid": "1", "username": "User1", 
              "password": "491a2800b80719ea9e3c89ca5472a8bda1bdd1533d4574ea5bd85b70a8e93be0"},
    "User2": {"userid": "2", "username": "User2", 
              "password": "c577e95bf729b94c30a878d01155693a9cdddafbb2fe0d52143027474ecb91bc"},
    "admin": {"userid": "999", "username": "admin", 
             "password": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"}  # password: admin
}

def auth_failure_lab3(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Insecure: Using hardcoded credentials and weak password hashing
        if username in USER_A7_LAB3:
            import hashlib
            hashed_input = hashlib.sha256(password.encode()).hexdigest()
            
            if hashed_input == USER_A7_LAB3[username]['password']:
                request.session['user_id'] = USER_A7_LAB3[username]['userid']
                request.session['username'] = username
                messages.success(request, 'Login successful')
                return redirect('dashboard')
        
        messages.error(request, 'Invalid credentials')
        
    return render(request, 'auth_failure_lab3.html')

def A7_discussion(request):
    return render(request, 'A7_discussion.html')

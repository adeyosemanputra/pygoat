from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm

from ..forms import NewUserForm

# Authentication views
def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = NewUserForm()
    return render(request, 'register.html', {'form': form})

def auth_home(request):
    return render(request, 'auth_home.html')

def auth_lab(request):
    return render(request, 'auth_lab.html')

def auth_lab_signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 == password2:
            if not login.objects.filter(username=username).exists():
                login.objects.create(username=username, email=email, password=password1)
                messages.success(request, 'User created successfully')
                return redirect('auth_lab_login')
            else:
                messages.error(request, 'Username already exists')
        else:
            messages.error(request, 'Passwords do not match')
    return render(request, 'auth_lab_signup.html')

def auth_lab_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = login.objects.get(username=username, password=password)
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            return redirect('auth_lab_dashboard')
        except login.DoesNotExist:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'auth_lab_login.html')

def auth_lab_logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
        del request.session['username']
    return redirect('auth_lab_login')

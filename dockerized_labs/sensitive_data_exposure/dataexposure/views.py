from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib import messages
from .models import UserData
from .forms import UserLoginForm, UserRegisterForm
import random
import string

def index(request):
    # main landing pg
    return render(request, 'index.html')

def about(request):
    # about pg nothing special
    return render(request, 'about.html')

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}! You are now logged in.')
                return redirect('profile')
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = UserLoginForm()
    
    return render(request, 'login.html', {'form': form})

def generate_api_key():
    # generate a random api key
    # I should probably use a better method but this works for now
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=16))  # 16 chars should be enough right?

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = User.objects.create_user(username=username, password=password)
            
            # Creating sensitive data for the user
            # Yeah i know this is dummy data but works for demo
            UserData.objects.create(
                user=user,
                credit_card='4111111111111111',  # test visa card number lol
                ssn='123456789',  # not a real SSN obvs
                api_key=generate_api_key()  # not very secure api key but whatever
            )
            
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'register.html', {'form': form})

@login_required
def profile_view(request):
    # show user profile with some data masked
    try:
        user_data = UserData.objects.get(user=request.user)
        # TODO: add audit logging here someday
    except UserData.DoesNotExist:
        # If no user data exists, create some dummy data for demo
        # This should never happen but just in case
        print(f"Creating missing user data for {request.user.username}")  # debugging stuff
        user_data = UserData.objects.create(
            user=request.user,
            credit_card='4111111111111111',  # test visa card number lol
            ssn='123456789',  # not a real SSN obvs
            api_key=generate_api_key()  # not very secure api key but whatever
        )
    return render(request, 'profile.html', {'user_data': user_data})

@login_required
def api_data_view(request):
    # FIXME: this is insecure AF - just for demo purposes!!
    # sends all user data as json - bad practice!!
    try:
        user_data = UserData.objects.get(user=request.user)
    except UserData.DoesNotExist:
        # If no user data exists, create some dummy data for demo
        user_data = UserData.objects.create(
            user=request.user,
            credit_card='4111111111111111',  # test card number
            ssn='123456789',  # demo SSN
            api_key=generate_api_key()  # simple api key
        )
    
    data = {
        'username': request.user.username,
        'credit_card': user_data.credit_card,
        'ssn': user_data.ssn,
        'api_key': user_data.api_key
    }
    # Intentionally exposing sensitive data through API
    # cuz we're teaching about data exposure, duh!
    return JsonResponse(data)

# Intentionally insecure - for teaching purposes!
def all_users_data_view(request):
    # MAJOR SECURITY FLAW: This endpoint allows ANY user (even unauthenticated ones!)
    # to see ALL users' sensitive data!
    # This demonstrates why proper authentication/authorization is essential.
    
    # Note for students: Notice how there are no checks for who's requesting the data!

    all_users_data = []
    for user_data in UserData.objects.all():
        all_users_data.append({
            'username': user_data.user.username,
            'credit_card': user_data.credit_card,  # Completely exposed! No masking!
            'ssn': user_data.ssn,  # Sending full SSN - terrible practice!
            'api_key': user_data.api_key  # API keys should never be exposed like this
        })
    
    # In a secure application, we would add:
    # if not request.user.is_authenticated or not request.user.is_staff:
    #     return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    return JsonResponse({'users': all_users_data})

def logout_view(request):
    # simple logout nothing fancy
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('index')

def sensitive_data_exposure_lesson(request):
    # lessons page
    return render(request, 'lesson.html')

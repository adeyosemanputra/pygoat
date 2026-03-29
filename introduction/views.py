import logging
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required # New Import
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import NewUserForm
from challenge.models import Challenge, UserChallenge

# --- Registration (Public) ---
def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("/")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request, "registration/register.html", {"register_form": form})

# --- Authenticated Views ---

@login_required
def home(request):
    return render(request, "introduction/home.html")

@login_required
def xss(request):
    return render(request, "Lab/XSS/xss.html")

@login_required
def sql(request):
    return render(request, "Lab/SQL/sql.html")

@login_required
def insec_des(request):
    return render(request, "Lab/insec_des/insec_des.html")

@login_required
def xxe(request):
    return render(request, "Lab/XXE/xxe.html")

@login_required
def cmd(request):
    return render(request, "Lab/CMD/cmd.html")

@login_required
def bau(request):
    return render(request, "Lab/BrokenAuth/bau.html")

@login_required
def sec_mis(request):
    return render(request, "Lab/sec_mis/sec_mis.html")

@login_required
def supply_chain_failures(request):
    return render(request, "Lab_2021/A03_Supply_Chain_Failures/supply_chain_failures.html")

# --- System Views (No Login Required) ---

def healthz(request):
    return HttpResponse("OK", status=200)

@csrf_exempt
def check_auth(request):
    """The central Bouncer view used by Traefik."""
    # 1. Check if user is logged in
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    
    # 2. Get the host they are trying to access
    host = request.headers.get("X-Forwarded-Host", request.headers.get("Host", ""))
    parts = host.split(".")
    
    # 3. If it's the main domain (lvh.me or localhost), let it pass
    if len(parts) < 3:
        return HttpResponse("OK - Main Domain", status=200)
        
    # 4. If it's a subdomain, verify the user owns it
    username_from_host = parts[0] # e.g., 'lab-rishi-xss'
    
    if request.user.username not in username_from_host:
        return HttpResponse("Access Denied - Not your lab!", status=403)
        
    return HttpResponse("OK - Lab Access Granted", status=200)
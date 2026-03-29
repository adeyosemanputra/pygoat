import logging
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import NewUserForm
from challenge.models import Challenge, UserChallenge

# --- Auth & Home ---
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

def home(request):
    return render(request, "introduction/home.html") if request.user.is_authenticated else redirect("login")

# --- THE BOUNCER (Traefik Auth) ---
@csrf_exempt
def check_auth(request):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    host = request.headers.get("X-Forwarded-Host", request.headers.get("Host", ""))
    parts = host.split(".")
    if len(parts) < 3:
        return HttpResponse("Invalid Host", status=403)
    username_from_host = parts[0] 
    if request.user.username not in username_from_host:
        return HttpResponse("Access Denied", status=403)
    return HttpResponse("OK", status=200)

# --- Theory/Description Views (The "Slim" Lab Wrappers) ---
def xss(request):
    return render(request, "Lab/XSS/xss.html") if request.user.is_authenticated else redirect("login")

def sql(request):
    return render(request, "Lab/SQL/sql.html") if request.user.is_authenticated else redirect("login")

def insec_des(request):
    return render(request, "Lab/insec_des/insec_des.html") if request.user.is_authenticated else redirect("login")

def xxe(request):
    return render(request, "Lab/XXE/xxe.html") if request.user.is_authenticated else redirect("login")

def cmd(request):
    return render(request, "Lab/CMD/cmd.html") if request.user.is_authenticated else redirect("login")

def bau(request):
    return render(request, "Lab/BrokenAuth/bau.html") if request.user.is_authenticated else redirect("login")

def sec_mis(request):
    return render(request, "Lab/sec_mis/sec_mis.html") if request.user.is_authenticated else redirect("login")

def healthz(request):
    return HttpResponse("OK", status=200)

def supply_chain_failures(request):
    return render(request, "Lab_2021/A03_Supply_Chain_Failures/supply_chain_failures.html") if request.user.is_authenticated else redirect("login")
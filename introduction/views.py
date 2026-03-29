import base64
import datetime
from datetime import timezone
import hashlib
import json
import logging
import os
import pickle
import random
import re
import string
import subprocess
import uuid
from dataclasses import dataclass
from hashlib import md5
from io import BytesIO
from random import randint
from xml.dom.pulldom import START_ELEMENT, parseString
from xml.sax import make_parser
from xml.sax.handler import feature_external_ges

import jwt
import requests
import yaml
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from PIL import Image, ImageMath

from .forms import NewUserForm
from .models import (
    FAANG,
    AF_admin,
    AF_session_id,
    Blogs,
    CF_user,
    authLogin,
    comments,
    info,
    login as login_model,
    otp,
    sql_lab_table,
    tickits,
)
from .utility import customHash, filter_blog

# *****************************************Login and Registration****************************************************#

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
    return render(
        request=request,
        template_name="registration/register.html",
        context={"register_form": form},
    )

def home(request):
    if request.user.is_authenticated:
        return render(request, "introduction/home.html")
    else:
        return redirect("login")

def authentication_decorator(func):
    def function(*args, **kwargs):
        if args[0].user.is_authenticated:
            return func(*args, **kwargs)
        else:
            return redirect("login")
    return function

# *****************************************XSS****************************************************#

def xss(request):
    if request.user.is_authenticated:
        return render(request, "Lab/XSS/xss.html")
    else:
        return redirect("login")

def xss_lab(request):
    if request.user.is_authenticated:
        q = request.GET.get("q", "")
        f = FAANG.objects.filter(company=q)
        if f:
            args = {
                "company": f[0].company,
                "ceo": f[0].info_set.all()[0].ceo,
                "about": f[0].info_set.all()[0].about,
            }
            return render(request, "Lab/XSS/xss_lab.html", args)
        else:
            return render(request, "Lab/XSS/xss_lab.html", {"query": q})
    else:
        return redirect("login")

def xss_lab2(request):
    if request.user.is_authenticated:
        username = request.POST.get("username", "")
        if username:
            username = username.strip()
            username = username.replace("<script>", "").replace("</script>", "")
        else:
            username = "Guest"
        context = {"username": username}
        return render(request, "Lab/XSS/xss_lab_2.html", context)
    else:
        return redirect("login")

def xss_lab3(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST.get("username", "")
            pattern = r"[a-zA-Z0-9]"
            result = re.sub(pattern, "", username)
            context = {"code": result}
            return render(request, "Lab/XSS/xss_lab_3.html", context)
        else:
            return render(request, "Lab/XSS/xss_lab_3.html")
    else:
        return redirect("login")

# ***********************************SQL****************************************************************#

def sql(request):
    if request.user.is_authenticated:
        return render(request, "Lab/SQL/sql.html")
    else:
        return redirect("login")

def sql_lab(request):
    if request.user.is_authenticated:
        name = request.POST.get("name")
        password = request.POST.get("pass")
        if name:
            if login_model.objects.filter(user=name):
                sql_query = "SELECT * FROM introduction_login WHERE user='"+name+"' AND password='"+password+"'"
                try:
                    val = login_model.objects.raw(sql_query)
                except:
                    return render(
                        request,
                        "Lab/SQL/sql_lab.html",
                        {"wrongpass": password, "sql_error": sql_query},
                    )
                if val:
                    user = val[0].user
                    return render(request, "Lab/SQL/sql_lab.html", {"user1": user})
                else:
                    return render(
                        request,
                        "Lab/SQL/sql_lab.html",
                        {"wrongpass": password, "sql_error": sql_query},
                    )
            else:
                return render(request, "Lab/SQL/sql_lab.html", {"no": "User not found"})
        else:
            return render(request, "Lab/SQL/sql_lab.html")
    else:
        return redirect("login")

# ***************** INSECURE DESERIALIZATION***************************************************************#

def insec_des(request):
    if request.user.is_authenticated:
        return render(request, "Lab/insec_des/insec_des.html")
    else:
        return redirect("login")

# ****************************************************XXE********************************************************#

def xxe(request):
    if request.user.is_authenticated:
        return render(request, "Lab/XXE/xxe.html")
    else:
        return redirect("login")

def xxe_lab(request):
    if request.user.is_authenticated:
        return render(request, "Lab/XXE/xxe_lab.html")
    else:
        return redirect("login")

@csrf_exempt
def xxe_see(request):
    if request.user.is_authenticated:
        comment_obj = comments.objects.first()
        if comment_obj is None:
            comment_obj = comments.objects.create(
                name="System",
                comment="Default comment for XXE lab",
            )
        com = comment_obj.comment
        return render(request, "Lab/XXE/xxe_lab.html", {"com": com})
    else:
        return redirect("login")

# ****************************************************** Command Injection ***********************************************************************#

def cmd(request):
    if request.user.is_authenticated:
        return render(request, "Lab/CMD/cmd.html")
    else:
        return redirect("login")

@csrf_exempt
def cmd_lab(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            domain = request.POST.get("domain")
            domain = re.sub(r"^(?:(https?|ftp)://)?(?:www\.)?", "", domain, flags=re.IGNORECASE)
            os_type = request.POST.get("os")
            if os_type == "win":
                command = "nslookup {}".format(domain)
            else:
                command = "dig {}".format(domain)
            try:
                process = subprocess.Popen(
                    command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                stdout, stderr = process.communicate()
                output = stdout.decode("utf-8") + stderr.decode("utf-8")
            except:
                output = "Something went wrong"
            return render(request, "Lab/CMD/cmd_lab.html", {"output": output})
        else:
            return render(request, "Lab/CMD/cmd_lab.html")
    else:
        return redirect("login")

# ******************************************Broken Authentication**************************************************#

def bau(request):
    if request.user.is_authenticated:
        return render(request, "Lab/BrokenAuth/bau.html")
    else:
        return redirect("login")

@csrf_exempt
def Otp(request):
    if request.method == "GET":
        email = request.GET.get("email")
        otpN = randint(100, 999)
        if email and otpN:
            if email == "admin@pygoat.com":
                otp.objects.filter(id=2).update(otp=otpN)
                html = render(request, "Lab/BrokenAuth/otp.html", {"otp": "Sent To Admin Mail ID"})
                html.set_cookie("email", email)
                return html
            else:
                otp.objects.filter(id=1).update(email=email, otp=otpN)
                html = render(request, "Lab/BrokenAuth/otp.html", {"otp": otpN})
                html.set_cookie("email", email)
                return html
        else:
            return render(request, "Lab/BrokenAuth/otp.html")
    else:
        otpR = request.POST.get("otp")
        email = request.COOKIES.get("email")
        if otp.objects.filter(email=email, otp=otpR) or otp.objects.filter(id=2, otp=otpR):
            return render(request, "Lab/BrokenAuth/otp.html", {"email": email})
        else:
            return render(request, "Lab/BrokenAuth/otp.html", {"otp": "Invalid OTP Please Try Again"})

# *****************************************THE BOUNCER (Traefik Auth)**********************************************#

def check_auth(request):
    """The central view Traefik calls to verify if a user can access a lab."""
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    
    # Extract the requested lab username from the Host header
    host = request.headers.get("X-Forwarded-Host", request.headers.get("Host", ""))
    parts = host.split(".")
    
    if len(parts) < 3:
        return HttpResponse(status=403)
        
    username_from_host = parts[1] # e.g., lab-username-xss
    
    # Ensure user only accesses their own subdomains
    if request.user.username not in username_from_host:
        return HttpResponse(status=403)
        
    response = HttpResponse(status=200)
    response["X-Forwarded-User"] = request.user.username
    return response

# Standard Theory/Description Views
def sec_mis(request):
    return render(request, "Lab/sec_mis/sec_mis.html") if request.user.is_authenticated else redirect("login")

def a9(request):
    return render(request, "Lab/A9/a9.html") if request.user.is_authenticated else redirect("login")

def a10(request):
    return render(request, "Lab/A10/a10.html") if request.user.is_authenticated else redirect("login")

def a1_broken_access(request):
    return render(request, "Lab_2021/A1_BrokenAccessControl/broken_access.html") if request.user.is_authenticated else redirect("login")

def injection(request):
    return render(request, "Lab_2021/A3_Injection/injection.html") if request.user.is_authenticated else redirect("login")

def ssrf(request):
    return render(request, "Lab/ssrf/ssrf.html") if request.user.is_authenticated else redirect("login")

def ssti(request):
    return render(request, "Lab_2021/A3_Injection/ssti.html") if request.user.is_authenticated else redirect("login")

def supply_chain_failures(request):
    return render(request, "Lab_2021/A03_Supply_Chain_Failures/supply_chain_failures.html") if request.user.is_authenticated else redirect("login")

def crypto_failure(request):
    return render(request, "Lab_2021/A2_Crypto_failur/crypto_failure.html") if request.user.is_authenticated else redirect("login")

@authentication_decorator
def auth_failure(request):
    return render(request, "Lab_2021/A7_auth_failure/a7.html")

@authentication_decorator
def software_and_data_integrity_failure(request):
    return render(request, "Lab_2021/A8_software_and_data_integrity_failure/desc.html")
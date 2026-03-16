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
from argon2 import PasswordHasher
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.core import serializers
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from PIL import Image, ImageMath
from requests.structures import CaseInsensitiveDict

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
    login,
    otp,
    sql_lab_table,
    tickits,
)
from .utility import customHash, filter_blog

# *****************************************Lab Requirements****************************************************#

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


# def register(request):
#     if request.method=="POST":
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#         return redirect("login")

#     else:
#         form=UserCreationForm()
#         return render(request,"registration/register.html",{"form":form,})


def home(request):
    if request.user.is_authenticated:
        return render(
            request,
            "introduction/home.html",
        )
    else:
        return redirect("login")


## authentication check decurator function
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


# ***********************************SQL****************************************************************#


def sql(request):
    if request.user.is_authenticated:

        return render(request, "Lab/SQL/sql.html")
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


def auth_home(request):
    return render(request, "Lab/AUTH/auth_home.html")


# ***************************************************************Broken Access Control************************************************************#


@csrf_exempt
def ba(request):
    if request.user.is_authenticated:
        return render(request, "Lab/BrokenAccess/ba.html")
    else:
        return redirect("login")


# ********************************************************Sensitive Data Exposure*****************************************************#


def data_exp(request):
    if request.user.is_authenticated:
        return render(request, "Lab/DataExp/data_exp.html")
    else:
        return redirect("login")


def robots(request):
    if request.user.is_authenticated:
        response = render(request, "Lab/DataExp/robots.txt")
        response["Content-Type"] = "text/plain"
        return response


def error(request):
    return


# ******************************************************  Command Injection  ***********************************************************************#


def cmd(request):
    if request.user.is_authenticated:
        return render(request, "Lab/CMD/cmd.html")
    else:
        return redirect("login")


# ******************************************Broken Authentication**************************************************#


def bau(request):
    if request.user.is_authenticated:

        return render(request, "Lab/BrokenAuth/bau.html")
    else:
        return redirect("login")


# *****************************************Security Misconfiguration**********************************************#


def sec_mis(request):
    if request.user.is_authenticated:
        return render(request, "Lab/sec_mis/sec_mis.html")
    else:
        return redirect("login")


# **********************************************************A9*************************************************#


def a9(request):
    if request.user.is_authenticated:
        return render(request, "Lab/A9/a9.html")
    else:
        return redirect("login")


# *********************************************************A10*************************************************#


def a10(request):
    if request.user.is_authenticated:
        return render(request, "Lab/A10/a10.html")
    else:
        return redirect("login")


# *********************************************************A11*************************************************#


def gentckt():
    return "".join(
        random.choices(string.ascii_uppercase + string.ascii_lowercase, k=10)
    )


def insec_desgine(request):
    if request.user.is_authenticated:
        return render(request, "Lab/A11/a11.html")
    else:
        return redirect("login")


# -------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------

###################################################### 2021 A1: Broken Access


@csrf_exempt
def a1_broken_access(request):
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "Lab_2021/A1_BrokenAccessControl/broken_access.html")


@csrf_exempt
def a1_broken_access_lab_1(request):
    if request.user.is_authenticated:
        pass
    else:
        return redirect("login")

    name = request.POST.get("name")
    password = request.POST.get("pass")
    print(password)
    print(name)
    if name:
        if request.COOKIES.get("admin") == "1":
            return render(
                request,
                "Lab_2021/A1_BrokenAccessControl/broken_access_lab_1.html",
                {"data": "0NLY_F0R_4DM1N5", "username": "admin"},
            )
        elif (
            name == "jack" and password == "jacktheripper"
        ):  # Will implement hashing here
            html = render(
                request,
                "Lab_2021/A1_BrokenAccessControl/broken_access_lab_1.html",
                {"not_admin": "No Secret key for this User", "username": name},
            )
            html.set_cookie("admin", "0", max_age=200)
            return html
        else:
            return render(
                request,
                "Lab_2021/A1_BrokenAccessControl/broken_access_lab_1.html",
                {"data": "User Not Found"},
            )

    else:
        return render(
            request,
            "Lab_2021/A1_BrokenAccessControl/broken_access_lab_1.html",
            {"no_creds": True},
        )


@csrf_exempt
def a1_broken_access_lab_2(request):
    if request.user.is_authenticated:
        pass
    else:
        return redirect("login")

    name = request.POST.get("name")
    password = request.POST.get("pass")
    user_agent = request.META["HTTP_USER_AGENT"]

    # print(name)
    # print(password)
    print(user_agent)
    if name:
        if user_agent == "pygoat_admin":
            return render(
                request,
                "Lab_2021/A1_BrokenAccessControl/broken_access_lab_2.html",
                {"data": "0NLY_F0R_4DM1N5", "username": "admin", "status": "admin"},
            )
        elif (
            name == "jack" and password == "jacktheripper"
        ):  # Will implement hashing here
            html = render(
                request,
                "Lab_2021/A1_BrokenAccessControl/broken_access_lab_2.html",
                {
                    "not_admin": "No Secret key for this User",
                    "username": name,
                    "status": "not admin",
                },
            )
            return html
        else:
            return render(
                request,
                "Lab_2021/A1_BrokenAccessControl/broken_access_lab_2.html",
                {"data": "User Not Found"},
            )

    else:
        return render(
            request,
            "Lab_2021/A1_BrokenAccessControl/broken_access_lab_2.html",
            {"no_creds": True},
        )


def a1_broken_access_lab_3(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "GET":
        return render(
            request,
            "Lab_2021/A1_BrokenAccessControl/broken_access_lab_3.html",
            {"loggedin": False},
        )
    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if username == "John" and password == "reaper":
            return render(
                request,
                "Lab_2021/A1_BrokenAccessControl/broken_access_lab_3.html",
                {"loggedin": True, "admin": False},
            )
        elif username == "admin" and password == "admin_pass":
            return render(
                request,
                "Lab_2021/A1_BrokenAccessControl/broken_access_lab_3.html",
                {"loggedin": True, "admin": True},
            )
        return render(
            request,
            "Lab_2021/A1_BrokenAccessControl/broken_access_lab_3.html",
            {"loggedin": False},
        )


def a1_broken_access_lab3_secret(request):
    if not request.user.is_authenticated:
        return redirect("login")
    # no checking applied here
    return render(request, "Lab_2021/A1_BrokenAccessControl/secret.html")


###################################################### 2021 A3: Injection


@csrf_exempt
def injection(request):
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "Lab_2021/A3_Injection/injection.html")


@csrf_exempt
def injection_sql_lab(request):
    if request.user.is_authenticated:

        name = request.POST.get("name")
        password = request.POST.get("pass")
        print(name)
        print(password)

        if name:
            sql_query = (
                "SELECT * FROM introduction_sql_lab_table WHERE id='"
                + name
                + "'AND password='"
                + password
                + "'"
            )

            sql_instance = sql_lab_table(
                id="admin", password="65079b006e85a7e798abecb99e47c154"
            )
            sql_instance.save()
            sql_instance = sql_lab_table(id="jack", password="jack")
            sql_instance.save()
            sql_instance = sql_lab_table(
                id="slinky", password="b4f945433ea4c369c12741f62a23ccc0"
            )
            sql_instance.save()
            sql_instance = sql_lab_table(
                id="bloke", password="f8d1ce191319ea8f4d1d26e65e130dd5"
            )
            sql_instance.save()

            print(sql_query)

            try:
                user = sql_lab_table.objects.raw(sql_query)
                user = user[0].id
                print(user)

            except:
                return render(
                    request,
                    "Lab_2021/A3_Injection/sql_lab.html",
                    {"wrongpass": password, "sql_error": sql_query},
                )

            if user:
                return render(
                    request, "Lab_2021/A3_Injection/sql_lab.html", {"user1": user}
                )
            else:
                return render(
                    request,
                    "Lab_2021/A3_Injection/sql_lab.html",
                    {"wrongpass": password, "sql_error": sql_query},
                )
        else:
            return render(request, "Lab_2021/A3_Injection/sql_lab.html")
    else:
        return redirect("login")


##----------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------

# *********************************************************SSRF*************************************************#


def ssrf(request):
    if request.user.is_authenticated:
        return render(request, "Lab/ssrf/ssrf.html")
    else:
        return redirect("login")


# --------------------------------------- Server-side template injection --------------------------------------#


def ssti(request):
    if request.user.is_authenticated:
        return render(request, "Lab_2021/A3_Injection/ssti.html")
    else:
        return redirect("login")


def ssti_lab(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            users_blogs = Blogs.objects.filter(author=request.user)
            return render(
                request, "Lab_2021/A3_Injection/ssti_lab.html", {"blogs": users_blogs}
            )
        elif request.method == "POST":
            blog = request.POST["blog"]
            id = str(uuid.uuid4()).split("-")[-1]

            blog = filter_blog(blog)
            prepend_code = "{% extends 'introduction/base.html' %}\
                {% block content %}{% block title %}\
                <title>SSTI-Blogs</title>\
                {% endblock %}"

            blog = prepend_code + blog + "{% endblock %}"
            new_blog = Blogs.objects.create(author=request.user, blog_id=id)
            new_blog.save()
            dirname = os.path.dirname(__file__)
            filename = os.path.join(
                dirname, f"templates/Lab_2021/A3_Injection/Blogs/{id}.html"
            )
            file = open(filename, "w+")
            file.write(blog)
            file.close()
            return redirect(f"blog/{id}")
    else:
        return redirect("login")


def ssti_view_blog(request, blog_id):
    if request.user.is_authenticated:
        if request.method == "GET":
            return render(request, f"Lab_2021/A3_Injection/Blogs/{blog_id}.html")
        elif request.method == "POST":
            return HttpResponseBadRequest()


# -------------------------Cryptographic Failure -----------------------------------#


def dependency_attack_lab_page(request):
    """Embed the dependency attack lab within the PyGoat page using an iframe."""
    if not request.user.is_authenticated:
        return redirect("login")
    return render(
        request, "Lab_2021/A03_Supply_Chain_Failures/dependency_attack_lab.html"
    )


def package_injection_lab_page(request):
    """Embed the package injection/typosquatting lab within the PyGoat page using an iframe."""
    if not request.user.is_authenticated:
        return redirect("login")
    return render(
        request, "Lab_2021/A03_Supply_Chain_Failures/package_injection_lab.html"
    )


def open_source_library_lab_page(request):
    """Embed the open source library attack lab within the PyGoat page using an iframe."""
    if not request.user.is_authenticated:
        return redirect("login")
    return render(
        request,
        "Lab_2021/A03_Supply_Chain_Failures/open_source_library_attack_lab.html",
    )


def supply_chain_failures(request):
    """In-page theory view for A03:2025 - Software Supply Chain Failures"""
    if request.user.is_authenticated:
        return render(
            request, "Lab_2021/A03_Supply_Chain_Failures/supply_chain_failures.html"
        )
    else:
        return redirect("login")


def crypto_failure(request):
    if request.user.is_authenticated:
        return render(
            request,
            "Lab_2021/A2_Crypto_failur/crypto_failure.html",
            {"success": False, "failure": False},
        )
    else:
        redirect("login")


def crypto_failure_lab(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            return render(request, "Lab_2021/A2_Crypto_failur/crypto_failure_lab.html")
        elif request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            try:
                password = md5(password.encode()).hexdigest()
                user = CF_user.objects.filter(
                    username=username, password=password
                ).first()
                return render(
                    request,
                    "Lab_2021/A2_Crypto_failur/crypto_failure_lab.html",
                    {"user": user, "success": True, "failure": False},
                )
            except Exception as e:
                return render(
                    request,
                    "Lab_2021/A2_Crypto_failur/crypto_failure_lab.html",
                    {"success": False, "failure": True},
                )
    else:
        return redirect("login")


def crypto_failure_lab2(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            return render(request, "Lab_2021/A2_Crypto_failur/crypto_failure_lab2.html")
        elif request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            try:
                password = customHash(password)
                user = CF_user.objects.filter(
                    username=username, password2=password
                ).first()
                return render(
                    request,
                    "Lab_2021/A2_Crypto_failur/crypto_failure_lab2.html",
                    {"user": user, "success": True, "failure": False},
                )
            except:
                return render(
                    request,
                    "Lab_2021/A2_Crypto_failur/crypto_failure_lab2.html",
                    {"success": False, "failure": True},
                )


# based on CWE-319
def crypto_failure_lab3(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            try:
                cookie = request.COOKIES["cookie"]
                print(cookie)
                expire = cookie.split("|")[1]
                expire = datetime.datetime.fromisoformat(expire)
                now = datetime.datetime.now()
                if now > expire:
                    return render(
                        request,
                        "Lab_2021/A2_Crypto_failur/crypto_failure_lab3.html",
                        {"success": False, "failure": False},
                    )
                elif cookie.split("|")[0] == "admin":
                    return render(
                        request,
                        "Lab_2021/A2_Crypto_failur/crypto_failure_lab3.html",
                        {"success": True, "failure": False, "admin": True},
                    )
                else:
                    return render(
                        request,
                        "Lab_2021/A2_Crypto_failur/crypto_failure_lab3.html",
                        {"success": True, "failure": False, "admin": False},
                    )
            except Exception as e:
                print(e)
                pass
            return render(request, "Lab_2021/A2_Crypto_failur/crypto_failure_lab3.html")
        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            try:
                if username == "User" and password == "P@$$w0rd":
                    expire = datetime.datetime.now() + datetime.timedelta(minutes=60)
                    cookie = f"{username}|{expire}"
                    response = render(
                        request,
                        "Lab_2021/A2_Crypto_failur/crypto_failure_lab3.html",
                        {"success": True, "failure": False, "admin": False},
                    )
                    response.set_cookie("cookie", cookie)
                    response.status_code = 200
                    return response
                else:
                    response = render(
                        request,
                        "Lab_2021/A2_Crypto_failur/crypto_failure_lab3.html",
                        {"success": False, "failure": True},
                    )
                    response.set_cookie("cookie", None)
                    return response
            except:
                return render(
                    request,
                    "Lab_2021/A2_Crypto_failur/crypto_failure_lab2.html",
                    {"success": False, "failure": True},
                )


# - ------------------------Identification and Authentication Failures--------------------------------
@authentication_decorator
def auth_failure(request):
    if request.method == "GET":
        return render(request, "Lab_2021/A7_auth_failure/a7.html")


## used admin password --> 2022_in_pygoat@pygoat.com
# ## not a easy password to be brute forced
@authentication_decorator
def auth_failure_lab2(request):
    if request.method == "GET":
        return render(request, "Lab_2021/A7_auth_failure/lab2.html")

    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        try:
            user = AF_admin.objects.get(username=username)
            print(type(user.lockout_cooldown))
            if (
                user.is_locked == True
                and user.lockout_cooldown > datetime.datetime.now()
            ):
                return render(
                    request, "Lab_2021/A7_auth_failure/lab2.html", {"is_locked": True}
                )

            try:
                ph = PasswordHasher()
                ph.verify(user.password, password)
                if (
                    user.is_locked == True
                    and user.lockout_cooldown < datetime.datetime.now()
                ):
                    user.is_locked = False
                    user.last_login = datetime.datetime.now()
                    user.failattempt = 0
                    user.save()
                return render(
                    request,
                    "Lab_2021/A7_auth_failure/lab2.html",
                    {"user": user, "success": True, "failure": False},
                )
            except:
                # fail attempt
                print("wrong password")
                fail_attempt = user.failattempt + 1
                if fail_attempt == 5:
                    user.is_active = False
                    user.failattempt = 0
                    user.is_locked = True
                    user.lockout_cooldown = (
                        datetime.datetime.now() + datetime.timedelta(minutes=1440)
                    )
                    user.save()
                    return render(
                        request,
                        "Lab_2021/A7_auth_failure/lab2.html",
                        {
                            "user": user,
                            "success": False,
                            "failure": True,
                            "is_locked": True,
                        },
                    )
                user.failattempt = fail_attempt
                user.save()
                return render(
                    request,
                    "Lab_2021/A7_auth_failure/lab2.html",
                    {"success": False, "failure": True},
                )
        except Exception as e:
            print(e)
            return render(
                request,
                "Lab_2021/A7_auth_failure/lab2.html",
                {"success": False, "failure": True},
            )


## Hardcoed user table for demonstration purpose only
USER_A7_LAB3 = {
    "User1": {
        "userid": "1",
        "username": "User1",
        "password": "491a2800b80719ea9e3c89ca5472a8bda1bdd1533d4574ea5bd85b70a8e93be0",
    },
    "User2": {
        "userid": "2",
        "username": "User2",
        "password": "c577e95bf729b94c30a878d01155693a9cdddafbb2fe0d52143027474ecb91bc",
    },
    "User3": {
        "userid": "3",
        "username": "User3",
        "password": "5a91a66f0c86b5435fe748706b99c17e6e54a17e03c2a3ef8d0dfa918db41cf6",
    },
    "User4": {
        "userid": "4",
        "username": "User4",
        "password": "6046bc3337728a60967a151ee584e4fd7c53740a49485ebdc38cac42a255f266",
    },
}

# USER_A7_LAB3 = {
#     "User1":{"userid":"1", "username":"User1", "password": "Hash1"},
#     "User2":{"userid":"2", "username":"User2", "password": "Hash2"},
#     "User3":{"userid":"3", "username":"User3", "password": "Hash3"},
#     "User4":{"userid":"4", "username":"User4", "password": "Hash4"}
# }


@authentication_decorator
@csrf_exempt
def auth_failure_lab3(request):
    if request.method == "GET":
        try:
            cookie = request.COOKIES["session_id"]
            session = AF_session_id.objects.get(session_id=cookie)
            if session:
                return render(
                    request,
                    "Lab_2021/A7_auth_failure/lab3.html",
                    {"username": session.user, "success": True},
                )
        except:
            pass
        return render(request, "Lab_2021/A7_auth_failure/lab3.html")
    elif request.method == "POST":
        token = str(uuid.uuid4())
        try:
            username = request.POST["username"]
            password = request.POST["password"]
            password = hashlib.sha256(password.encode()).hexdigest()
        except:
            response = render(request, "Lab_2021/A7_auth_failure/lab3.html")
            response.set_cookie("session_id", None)
            return response

        if USER_A7_LAB3[username]["password"] == password:
            session_data = AF_session_id.objects.create(
                session_id=token, user=USER_A7_LAB3[username]["username"]
            )
            session_data.save()
            response = render(
                request,
                "Lab_2021/A7_auth_failure/lab3.html",
                {"success": True, "failure": False, "username": username},
            )
            response.set_cookie("session_id", token)
            return response


# -- coding playground for lab2
@authentication_decorator
def A7_discussion(request):
    return render(request, "playground/A7/index.html")


## ---------------------Software and Data Integrity Failures-------------------------------------------
@authentication_decorator
def software_and_data_integrity_failure(request):
    if request.method == "GET":
        return render(
            request, "Lab_2021/A8_software_and_data_integrity_failure/desc.html"
        )


@authentication_decorator
def software_and_data_integrity_failure_lab2(request):
    if request.method == "GET":
        try:
            username = request.GET["username"]
            return render(
                request,
                "Lab_2021/A8_software_and_data_integrity_failure/lab2.html",
                {"username": username, "success": True},
            )
        except:
            return render(
                request, "Lab_2021/A8_software_and_data_integrity_failure/lab2.html"
            )


@authentication_decorator
def software_and_data_integrity_failure_lab3(request):
    pass


## --------------------------A6_discussion-------------------------------------------------------


@authentication_decorator
def A6_discussion(request):

    return render(request, "playground/A6/index.html")

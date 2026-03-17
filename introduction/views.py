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
            username = request.POST.get("username")
            print(type(username))
            pattern = r"\w"
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

            if login.objects.filter(user=name):

                sql_query = (
                    "SELECT * FROM introduction_login WHERE user='"
                    + name
                    + "'AND password='"
                    + password
                    + "'"
                )
                print(sql_query)
                try:
                    print("\nin try\n")
                    val = login.objects.raw(sql_query)
                except:
                    print("\nin except\n")
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


@dataclass
class TestUser:
    admin: int = 0


pickled_user = pickle.dumps(TestUser())
encoded_user = base64.b64encode(pickled_user)


def insec_des_lab(request):
    if request.user.is_authenticated:
        response = render(
            request,
            "Lab/insec_des/insec_des_lab.html",
            {"message": "Only Admins can see this page"},
        )
        token = request.COOKIES.get("token")
        if token == None:
            token = encoded_user
            response.set_cookie(key="token", value=token.decode("utf-8"))
        else:
            token = base64.b64decode(token)
            admin = pickle.loads(token)
            if admin.admin == 1:
                response = render(
                    request,
                    "Lab/insec_des/insec_des_lab.html",
                    {"message": "Welcome Admin, SECRETKEY:ADMIN123"},
                )
                return response

        return response
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

        data = comments.objects.all()
        com = data[0].comment
        return render(request, "Lab/XXE/xxe_lab.html", {"com": com})
    else:
        return redirect("login")


@csrf_exempt
def xxe_parse(request):

    parser = make_parser()
    parser.setFeature(feature_external_ges, True)
    doc = parseString(request.body.decode("utf-8"), parser=parser)
    for event, node in doc:
        if event == START_ELEMENT and node.tagName == "text":
            doc.expandNode(node)
            text = node.toxml()
    startInd = text.find(">")
    endInd = text.find("<", startInd)
    text = text[startInd + 1 : endInd :]
    p = comments.objects.filter(id=1).update(comment=text)

    return render(request, "Lab/XXE/xxe_lab.html")


def auth_home(request):
    return render(request, "Lab/AUTH/auth_home.html")


def auth_lab(request):
    return render(request, "Lab/AUTH/auth_lab.html")


def auth_lab_signup(request):
    if request.method == "GET":
        return render(request, "Lab/AUTH/auth_lab_signup.html")
    elif request.method == "POST":
        try:
            name = request.POST["name"]
            user_name = request.POST["username"]
            passwd = request.POST["pass"]
            obj = authLogin.objects.create(
                name=name, username=user_name, password=passwd
            )
            try:
                rendered = render_to_string(
                    "Lab/AUTH/auth_success.html",
                    {
                        "username": obj.username,
                        "userid": obj.userid,
                        "name": obj.name,
                        "err_msg": "Cookie Set",
                    },
                )
                response = HttpResponse(rendered)
                response.set_cookie(
                    "userid", obj.userid, max_age=31449600, samesite=None, secure=False
                )
                print("Setting cookie successful")
                return response
            except:
                render(
                    request,
                    "Lab/AUTH/auth_lab_signup.html",
                    {"err_msg": "Cookie cannot be set"},
                )
        except:
            return render(
                request,
                "Lab/AUTH/auth_lab_signup.html",
                {"err_msg": "Username already exists"},
            )


def auth_lab_login(request):
    if request.method == "GET":
        try:
            obj = authLogin.objects.filter(userid=request.COOKIES["userid"])[0]
            rendered = render_to_string(
                "Lab/AUTH/auth_success.html",
                {
                    "username": obj.username,
                    "userid": obj.userid,
                    "name": obj.name,
                    "err_msg": "Login Successful",
                },
            )
            response = HttpResponse(rendered)
            response.set_cookie(
                "userid", obj.userid, max_age=31449600, samesite=None, secure=False
            )
            print("Login successful")
            return response
        except:
            return render(request, "Lab/AUTH/auth_lab_login.html")
    elif request.method == "POST":
        try:
            user_name = request.POST["username"]
            passwd = request.POST["pass"]
            print(user_name, passwd)
            obj = authLogin.objects.filter(username=user_name, password=passwd)[0]
            try:
                rendered = render_to_string(
                    "Lab/AUTH/auth_success.html",
                    {
                        "username": obj.username,
                        "userid": obj.userid,
                        "name": obj.name,
                        "err_msg": "Login Successful",
                    },
                )
                response = HttpResponse(rendered)
                response.set_cookie(
                    "userid", obj.userid, max_age=31449600, samesite=None, secure=False
                )
                print("Login successful")
                return response
            except:
                render(
                    request,
                    "Lab/AUTH/auth_lab_login.html",
                    {"err_msg": "Cookie cannot be set"},
                )
        except:
            return render(
                request,
                "Lab/AUTH/auth_lab_login.html",
                {"err_msg": "Check your credentials"},
            )


def auth_lab_logout(request):
    rendered = render_to_string(
        "Lab/AUTH/auth_lab.html", context={"err_msg": "Logout successful"}
    )
    response = HttpResponse(rendered)
    response.delete_cookie("userid")
    return response


# ***************************************************************Broken Access Control************************************************************#


@csrf_exempt
def ba(request):
    if request.user.is_authenticated:
        return render(request, "Lab/BrokenAccess/ba.html")
    else:
        return redirect("login")


@csrf_exempt
def ba_lab(request):
    if request.user.is_authenticated:
        name = request.POST.get("name")
        password = request.POST.get("pass")
        if name:
            if request.COOKIES.get("admin") == "1":
                return render(
                    request,
                    "Lab/BrokenAccess/ba_lab.html",
                    {"data": "0NLY_F0R_4DM1N5", "username": "admin"},
                )
            elif login.objects.filter(user="admin", password=password):
                html = render(
                    request,
                    "Lab/BrokenAccess/ba_lab.html",
                    {"data": "0NLY_F0R_4DM1N5", "username": "admin"},
                )
                html.set_cookie("admin", "1", max_age=200)
                return html
            elif login.objects.filter(user=name, password=password):
                html = render(
                    request,
                    "Lab/BrokenAccess/ba_lab.html",
                    {"not_admin": "No Secret key for this User", "username": name},
                )
                html.set_cookie("admin", "0", max_age=200)
                return html
            else:
                return render(
                    request, "Lab/BrokenAccess/ba_lab.html", {"data": "User Not Found"}
                )

        else:
            return render(request, "Lab/BrokenAccess/ba_lab.html", {"no_creds": True})
    else:
        return redirect("login")


# ********************************************************Sensitive Data Exposure*****************************************************#


def data_exp(request):
    if request.user.is_authenticated:
        return render(request, "Lab/DataExp/data_exp.html")
    else:
        return redirect("login")


def data_exp_lab(request):
    if request.user.is_authenticated:
        return render(request, "Lab/DataExp/data_exp_lab.html")
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


@csrf_exempt
def cmd_lab(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            domain = request.POST.get("domain")
            domain = domain.replace("https://www.", "")
            os_type = request.POST.get("os")
            print(os_type)
            if os_type == "win":
                command = "nslookup {}".format(domain)
            else:
                command = "dig {}".format(domain)

            try:
                # output=subprocess.check_output(command,shell=True,encoding="UTF-8")
                process = subprocess.Popen(
                    command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                stdout, stderr = process.communicate()
                data = stdout.decode("utf-8")
                stderr = stderr.decode("utf-8")
                # res = json.loads(data)
                # print("Stdout\n" + data)
                output = data + stderr
                print(data + stderr)
            except:
                output = "Something went wrong"
                return render(request, "Lab/CMD/cmd_lab.html", {"output": output})
            print(output)
            return render(request, "Lab/CMD/cmd_lab.html", {"output": output})
        else:
            return render(request, "Lab/CMD/cmd_lab.html")
    else:
        return redirect("login")


@csrf_exempt
def cmd_lab2(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            val = request.POST.get("val")

            print(val)
            try:
                output = eval(val)
            except:
                output = "Something went wrong"
                return render(request, "Lab/CMD/cmd_lab2.html", {"output": output})
            print("Output = ", output)
            return render(request, "Lab/CMD/cmd_lab2.html", {"output": output})
        else:
            return render(request, "Lab/CMD/cmd_lab2.html")
    else:
        return redirect("login")


# ******************************************Broken Authentication**************************************************#


def bau(request):
    if request.user.is_authenticated:

        return render(request, "Lab/BrokenAuth/bau.html")
    else:
        return redirect("login")


def bau_lab(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            return render(request, "Lab/BrokenAuth/bau_lab.html")
        else:
            return render(request, "Lab/BrokenAuth/bau_lab.html", {"wrongpass": "yes"})
    else:
        return redirect("login")


def login_otp(request):
    return render(request, "Lab/BrokenAuth/otp.html")


@csrf_exempt
def Otp(request):
    if request.method == "GET":
        email = request.GET.get("email")
        otpN = randint(100, 999)
        if email and otpN:
            if email == "admin@pygoat.com":
                otp.objects.filter(id=2).update(otp=otpN)
                html = render(
                    request, "Lab/BrokenAuth/otp.html", {"otp": "Sent To Admin Mail ID"}
                )
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
        if otp.objects.filter(email=email, otp=otpR) or otp.objects.filter(
            id=2, otp=otpR
        ):
            # return HttpResponse("<h3>Login Success for email:::"+email+"</h3>")
            return render(request, "Lab/BrokenAuth/otp.html", {"email": email})
        else:
            return render(
                request,
                "Lab/BrokenAuth/otp.html",
                {"otp": "Invalid OTP Please Try Again"},
            )


# *****************************************Security Misconfiguration**********************************************#


def sec_mis(request):
    if request.user.is_authenticated:
        return render(request, "Lab/sec_mis/sec_mis.html")
    else:
        return redirect("login")


def sec_mis_lab(request):
    if request.user.is_authenticated:
        return render(request, "Lab/sec_mis/sec_mis_lab.html")
    else:
        return redirect("login")


def secret(request):
    XHost = request.headers.get("X-Host", "None")
    if XHost == "admin.localhost:8000":
        return render(request, "Lab/sec_mis/sec_mis_lab.html", {"secret": "S3CR37K3Y"})
    else:
        return render(
            request,
            "Lab/sec_mis/sec_mis_lab.html",
            {
                "no_secret": "Only admin.localhost:8000 can access, Your X-Host is "
                + XHost
            },
        )


# **********************************************************A9*************************************************#


def a9(request):
    if request.user.is_authenticated:
        return render(request, "Lab/A9/a9.html")
    else:
        return redirect("login")


@csrf_exempt
def a9_lab(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            return render(request, "Lab/A9/a9_lab.html")
        else:

            try:
                file = request.FILES["file"]
                try:
                    data = yaml.load(file, yaml.Loader)

                    return render(request, "Lab/A9/a9_lab.html", {"data": data})
                except:
                    return render(request, "Lab/A9/a9_lab.html", {"data": "Error"})

            except:
                return render(
                    request,
                    "Lab/A9/a9_lab.html",
                    {"data": "Please Upload a Yaml file."},
                )
    else:
        return redirect("login")


def get_version(request):
    return render(request, "Lab/A9/a9_lab.html", {"version": "pyyaml v5.1"})


@csrf_exempt
def a9_lab2(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "GET":
        return render(request, "Lab/A9/a9_lab2.html")
    elif request.method == "POST":
        try:
            file = request.FILES["file"]
            function_str = request.POST.get("function")
            img = Image.open(file)
            img = img.convert("RGB")
            r, g, b = img.split()
            # function_str = "convert(r+g, '1')"
            output = ImageMath.eval(function_str, img=img, b=b, r=r, g=g)

            # saving the image
            buffered = BytesIO()
            output.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

            bufferd_ref = BytesIO()
            img.save(bufferd_ref, format="JPEG")
            img_str_ref = base64.b64encode(bufferd_ref.getvalue()).decode("utf-8")
            try:
                return render(
                    request,
                    "Lab/A9/a9_lab2.html",
                    {"img_str": img_str, "img_str_ref": img_str_ref, "success": True},
                )
            except Exception as e:
                print(e)
                return render(
                    request, "Lab/A9/a9_lab2.html", {"data": "Error", "error": True}
                )
        except Exception as e:
            print(e)
            return render(
                request,
                "Lab/A9/a9_lab2.html",
                {"data": "Please Upload a file", "error": True},
            )


@authentication_decorator
def A9_discussion(request):
    return render(request, "playground/A9/index.html")


# *********************************************************A10*************************************************#


def a10(request):
    if request.user.is_authenticated:
        return render(request, "Lab/A10/a10.html")
    else:
        return redirect("login")


def a10_lab(request):
    if request.user.is_authenticated:
        if request.method == "GET":

            return render(request, "Lab/A10/a10_lab.html")
        else:

            user = request.POST.get("name")
            password = request.POST.get("pass")
            if login.objects.filter(user=user, password=password):
                return render(request, "Lab/A10/a10_lab.html", {"name": user})
            else:
                return render(
                    request,
                    "Lab/A10/a10_lab.html",
                    {"error": " Wrong username or Password"},
                )

    else:
        return redirect("login")


def debug(request):
    response = render(request, "Lab/A10/debug.log")
    response["Content-Type"] = "text/plain"
    return response


# Logging basic configuration
logging.basicConfig(level=logging.DEBUG, filename="app.log")


@authentication_decorator
def a10_lab2(request):
    now = datetime.datetime.now()
    if request.method == "GET":
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        logging.info(f"{now}:{ip}")
        return render(request, "Lab/A10/a10_lab2.html")
    else:
        user = request.POST.get("name")
        password = request.POST.get("pass")
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        if login.objects.filter(user=user, password=password):
            if ip != "127.0.0.1":
                logging.warning(f"{now}:{ip}:{user}")
            logging.info(f"{now}:{ip}:{user}")
            return render(request, "Lab/A10/a10_lab2.html", {"name": user})
        else:
            logging.error(f"{now}:{ip}:{user}")
            return render(
                request,
                "Lab/A10/a10_lab2.html",
                {"error": " Wrong username or Password"},
            )


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


def insec_desgine_lab(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            tkts = tickits.objects.filter(user=request.user)
            Tickets = []
            for tkt in tkts:
                Tickets.append(tkt.tickit)
            return render(request, "Lab/A11/a11_lab.html", {"tickets": Tickets})
        elif request.method == "POST":
            tkts = tickits.objects.filter(user=request.user)
            Tickets = []
            for tkt in tkts:
                Tickets.append(tkt.tickit)
            try:
                count = request.POST.get("count")
                if (int(count) + len(tkts)) <= 5:
                    for i in range(int(count)):
                        ticket_code = gentckt()
                        Tickets.append(ticket_code)
                        T = tickits(user=request.user, tickit=ticket_code)
                        T.save()

                    return render(request, "Lab/A11/a11_lab.html", {"tickets": Tickets})
                else:
                    return render(
                        request,
                        "Lab/A11/a11_lab.html",
                        {"error": "You can have atmost 5 tickits", "tickets": Tickets},
                    )
            except:
                try:
                    tickit = request.POST.get("ticket")
                    all_tickets = tickits.objects.all()
                    sold_tickets = len(all_tickets)
                    if sold_tickets < 60:
                        return render(
                            request,
                            "Lab/A11/a11_lab.html",
                            {
                                "error": "Invalid tickit",
                                "tickets": Tickets,
                                "error": f"Wait until all tickets are sold ({60-sold_tickets} tickets left)",
                            },
                        )
                    else:
                        if tickit in Tickets:
                            return render(
                                request,
                                "Lab/A11/a11_lab.html",
                                {
                                    "error": "Congratulation,You figured out the flaw in Design.<br> A better authentication should be used in case for checking the uniqueness of a user.",
                                    "tickets": Tickets,
                                },
                            )
                        else:
                            return render(
                                request,
                                "Lab/A11/a11_lab.html",
                                {"tickets": Tickets, "error": "Invalid ticket"},
                            )
                except:
                    return render(request, "Lab/A11/a11_lab.html", {"tickets": Tickets})
        else:
            pass
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


###################################################### 2021 A3: Injection


@csrf_exempt
def injection(request):
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "Lab_2021/A3_Injection/injection.html")


##----------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------

# *********************************************************SSRF*************************************************#


def ssrf(request):
    if request.user.is_authenticated:
        return render(request, "Lab/ssrf/ssrf.html")
    else:
        return redirect("login")


def ssrf_lab(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            return render(
                request, "Lab/ssrf/ssrf_lab.html", {"blog": "Read Blog About SSRF"}
            )
        else:
            file = request.POST["blog"]
            try:
                dirname = os.path.dirname(__file__)
                filename = os.path.join(dirname, file)
                file = open(filename, "r")
                data = file.read()
                return render(request, "Lab/ssrf/ssrf_lab.html", {"blog": data})
            except:
                return render(
                    request, "Lab/ssrf/ssrf_lab.html", {"blog": "No blog found"}
                )
    else:
        return redirect("login")


def ssrf_discussion(request):
    if request.user.is_authenticated:
        return render(request, "Lab/ssrf/ssrf_discussion.html")
    else:
        return redirect("login")


def ssrf_target(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    if ip == "127.0.0.1":
        return render(request, "Lab/ssrf/ssrf_target.html")
    else:
        return render(request, "Lab/ssrf/ssrf_target.html", {"access_denied": True})


@authentication_decorator
def ssrf_lab2(request):
    if request.method == "GET":
        return render(request, "Lab/ssrf/ssrf_lab2.html")

    elif request.method == "POST":
        url = request.POST["url"]
        try:
            response = requests.get(url)
            return render(
                request,
                "Lab/ssrf/ssrf_lab2.html",
                {"response": response.content.decode()},
            )
        except:
            return render(request, "Lab/ssrf/ssrf_lab2.html", {"error": "Invalid URL"})


# --------------------------------------- Server-side template injection --------------------------------------#


def ssti(request):
    if request.user.is_authenticated:
        return render(request, "Lab_2021/A3_Injection/ssti.html")
    else:
        return redirect("login")


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


# -----------------------------------------------SECURITY MISCONFIGURATION -------------------
from pygoat.settings import SECRET_COOKIE_KEY


def sec_misconfig_lab3(request):
    if not request.user.is_authenticated:
        return redirect("login")
    try:
        cookie = request.COOKIES["auth_cookie"]
        payload = jwt.decode(cookie, SECRET_COOKIE_KEY, algorithms=["HS256"])
        if payload["user"] == "admin":
            return render(request, "Lab/sec_mis/sec_mis_lab3.html", {"admin": True})
        else:
            return render(request, "Lab/sec_mis/sec_mis_lab3.html", {"admin": False})
    except:
        payload = {
            "user": "not_admin",
            "exp": datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=60),
            "iat": datetime.datetime.now(timezone.utc),
        }

        cookie = jwt.encode(payload, SECRET_COOKIE_KEY, algorithm="HS256")
        response = render(request, "Lab/sec_mis/sec_mis_lab3.html", {"admin": False})
        response.set_cookie(key="auth_cookie", value=cookie)
        return response


# - ------------------------Identification and Authentication Failures--------------------------------
@authentication_decorator
def auth_failure(request):
    if request.method == "GET":
        return render(request, "Lab_2021/A7_auth_failure/a7.html")


## ---------------------Software and Data Integrity Failures-------------------------------------------
@authentication_decorator
def software_and_data_integrity_failure(request):
    if request.method == "GET":
        return render(
            request, "Lab_2021/A8_software_and_data_integrity_failure/desc.html"
        )



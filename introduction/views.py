import random
import string

from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .forms import NewUserForm

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

        return render(request, "Lab_2021/A3_Injection/injection.html")
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



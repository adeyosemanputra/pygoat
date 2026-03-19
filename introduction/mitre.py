import datetime
from datetime import timezone
import re
import subprocess
from hashlib import md5

import jwt
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .views import authentication_decorator

# import os

## Mitre top1 | CWE:787

# target zone
FLAG = "NOT_SUPPOSED_TO_BE_ACCESSED"

# target zone end


@authentication_decorator
def mitre_top1(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top1.html")


@authentication_decorator
def mitre_top2(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top2.html")


@authentication_decorator
def mitre_top3(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top3.html")


@authentication_decorator
def mitre_top4(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top4.html")


@authentication_decorator
def mitre_top5(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top5.html")


@authentication_decorator
def mitre_top6(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top6.html")


@authentication_decorator
def mitre_top7(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top7.html")


@authentication_decorator
def mitre_top8(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top8.html")


@authentication_decorator
def mitre_top9(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top9.html")


@authentication_decorator
def mitre_top10(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top10.html")


@authentication_decorator
def mitre_top11(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top11.html")


@authentication_decorator
def mitre_top12(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top12.html")


@authentication_decorator
def mitre_top13(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top13.html")


@authentication_decorator
def mitre_top14(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top14.html")


@authentication_decorator
def mitre_top15(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top15.html")


@authentication_decorator
def mitre_top16(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top16.html")


@authentication_decorator
def mitre_top17(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top17.html")


@authentication_decorator
def mitre_top18(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top18.html")


@authentication_decorator
def mitre_top19(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top19.html")


@authentication_decorator
def mitre_top20(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top20.html")


@authentication_decorator
def mitre_top21(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top21.html")


@authentication_decorator
def mitre_top22(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top22.html")


@authentication_decorator
def mitre_top23(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top23.html")


@authentication_decorator
def mitre_top24(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top24.html")


@authentication_decorator
def mitre_top25(request):
    if request.method == "GET":
        return render(request, "mitre/mitre_top25.html")


# @authentication_decorator
@csrf_exempt
def mitre_lab_25_api(request):
    if request.method == "POST":
        expression = request.POST.get("expression")
        result = eval(expression)
        return JsonResponse({"result": result})
    else:
        return redirect("/mitre/25/lab/")


@authentication_decorator
def mitre_lab_25(request):
    return render(request, "mitre/mitre_lab_25.html")


@authentication_decorator
def mitre_lab_17(request):
    return render(request, "mitre/mitre_lab_17.html")


def command_out(command):
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return process.communicate()


@csrf_exempt
def mitre_lab_17_api(request):
    if request.method == "POST":
        ip = request.POST.get("ip")
        command = "nmap " + ip
        res, err = command_out(command)
        res = res.decode()
        err = err.decode()
        pattern = "STATE SERVICE.*\\n\\n"
        ports = re.findall(pattern, res, re.DOTALL)[0][14:-2].split("\n")
        return JsonResponse({"raw_res": str(res), "raw_err": str(err), "ports": ports})

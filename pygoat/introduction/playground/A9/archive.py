from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .main import Log

@csrf_exempt
def log_function_target(request):
    L = Log(request)
    if request.method == "GET":
        L.info("GET request")
        return JsonResponse({"message":"normal get request", "method":"get"},status = 200)
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        L.info(f"POST request with username {username} and password {password}")
        if username == "admin" and password == "admin":
            return JsonResponse({"message":"Loged in successfully", "method":"post"},status = 200)
        return JsonResponse({"message":"Invalid credentials", "method":"post"},status = 401)
    if request.method == "PUT":
        L.info("PUT request")
        return JsonResponse({"message":"success", "method":"put"},status = 200)
    if request.method == "DELETE":
        if request.user.is_authenticated:
            return JsonResponse({"message":"User is authenticated", "method":"delete"},status = 200)
        L.error("DELETE request")
        return JsonResponse({"message":"permission denied", "method":"delete"},status = 200)
    if request.method == "PATCH":
        L.info("PATCH request")
        return JsonResponse({"message":"success", "method":"patch"},status = 200)
    if request.method == "UPDATE":
        return JsonResponse({"message":"success", "method":"update"},status = 200)
    return JsonResponse({"message":"method not allowed"},status = 403)


# ======================================

import datetime
# f = open('test.log', 'a') --> use this file to log
class Log:
    def __init__(self,request):
        self.request = request

    def info(self,msg):
        now = datetime.datetime.now()
        f = open('test.log', 'a')
        f.write(f"INFO:{now}:{msg}\n")
        f.close()

    def warning(self,msg):
        now = datetime.datetime.now()
        f = open('test.log', 'a')
        f.write(f"WARNING:{now}:{msg}\n")
        f.close()

    def error(self,msg):
        now = datetime.datetime.now()
        f = open('test.log', 'a')
        f.write(f"ERROR:{now}:{msg}\n")
        f.close()

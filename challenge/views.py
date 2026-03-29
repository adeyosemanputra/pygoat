from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
import subprocess
import json
from .utility import get_free_port
from .models import Challenge, UserChallenge

@csrf_exempt 
def submit_solve(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            lab_name = data.get("lab_name")
            user_id = data.get("user_id")
            challenge = Challenge.objects.get(name=lab_name)
            
            # We add port=0 as a placeholder to satisfy the database constraint
            user_challenge, created = UserChallenge.objects.get_or_create(
                user_id=user_id, 
                challenge=challenge,
                defaults={'port': 0}
            )
            
            user_challenge.is_solved = True
            user_challenge.save()
            return JsonResponse({"message": "Progress synchronized", "status": "200"})
        except Exception as e:
            return JsonResponse({"message": str(e), "status": "400"})
    return JsonResponse({"message": "Method not allowed", "status": "405"})

def check_traefik_reachable():
    traefik_urls = getattr(settings, 'TRAEFIK_URLS', [])
    for traefik_url in traefik_urls:
        try:
            response = requests.get(traefik_url, timeout=5)
            if response.status_code == 200:
                return True
        except (requests.RequestException, Exception):
            continue
    print(f"Traefik unreachable on all attempted URLs: {traefik_urls}")
    return False

class DoItFast(View):
    def get(self, request, challenge):
        if not request.user.is_authenticated:
            return redirect("login")
        try:
            chal = Challenge.objects.get(name=challenge)
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
            return render(request, "challenge.html", {"chal": chal, "user_chal": user_chal})
        except:
            chal = Challenge.objects.get(name=challenge)
            return render(request, "challenge.html", {"chal": chal, "user_chal": None})

    def put(self, request, challenge):
        if not request.user.is_authenticated:
            return JsonResponse({"message": "unauthorized", "status": "401"})
        data = json.loads(request.body)
        submitted_flag = data.get("flag")
        chal = Challenge.objects.get(name=challenge)
        if submitted_flag == chal.flag: 
            user_chal, _ = UserChallenge.objects.get_or_create(user=request.user, challenge=chal, defaults={'port': 0})
            user_chal.is_solved = True
            user_chal.save()
            return JsonResponse({"message": "Correct Flag!", "status": "200"})
        return JsonResponse({"message": "Wrong Flag", "status": "400"})

    def post(self, request, challenge):
        if not request.user.is_authenticated:
            return redirect("login")
        chal = Challenge.objects.get(name=challenge)
        user_chal, created = UserChallenge.objects.get_or_create(user=request.user, challenge=chal, defaults={'port': 0})
        if user_chal.is_live:
            return JsonResponse({"message": "already running", "status": "200", "endpoint": f"http://localhost:{user_chal.port}"})
        port = get_free_port(8000, 8100)
        command = f"docker run -d -p {port}:{chal.docker_port} {chal.docker_image}"
        process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
        output, error = process.communicate()
        user_chal.container_id = output.decode("utf-8").strip()
        user_chal.port = port
        user_chal.is_live = True
        user_chal.save()
        return JsonResponse({"message": "success", "status": "200", "endpoint": f"http://localhost:{port}"})

    def delete(self, request, challenge):
        chal = Challenge.objects.get(name=challenge)
        user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
        user_chal.is_live = False
        user_chal.save()
        subprocess.Popen(f"docker stop {user_chal.container_id}".split(" "))
        return JsonResponse({"message": "success", "status": "200"})

def bopla_lab(request):
    return redirect("http://localhost:7018") if request.user.is_authenticated else redirect("login")

def business_logic_lab(request):
    return redirect("http://localhost:7019") if request.user.is_authenticated else redirect("login")

def security_headers_lab(request):
    return redirect("http://localhost:7020") if request.user.is_authenticated else redirect("login")

from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Challenge, UserChallenge
import docker
import json
import os
import time

# --- Helpers ---

def get_docker_client():
    try:
        return docker.from_env()
    except Exception:
        return None

def _sanitize(text: str) -> str:
    return "".join(ch for ch in text if ch.isalnum() or ch in "-").lower()

def _get_container_name(username: str, lab_name: str) -> str:
    return f"lab-{_sanitize(username)}-{_sanitize(lab_name)}"

def _get_user_containers(client, username: str):
    prefix = f"lab-{_sanitize(username)}-"
    return [c for c in client.containers.list(all=True) if c.name.startswith(prefix)]

def _get_lab_config(lab_name: str) -> dict:
    """Reads labs.json to find the correct internal port for Traefik."""
    clean_name = lab_name.replace(" ", "_").lower()
    labs_json_path = os.path.join(settings.BASE_DIR, 'labs.json')
    try:
        with open(labs_json_path, 'r') as f:
            data = json.load(f)
        for lab in data.get('labs', []):
            if lab.get('name') == clean_name or lab.get('name') == lab_name:
                return lab
    except Exception:
        pass
    return {"port": 5000} # Fallback default

# --- THE BOUNCER (Traefik ForwardAuth) ---

@csrf_exempt
def check_auth(request):
    """The central Bouncer view used by Traefik to protect subdomains."""
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    
    host = request.headers.get("X-Forwarded-Host", request.headers.get("Host", ""))
    parts = host.split(".")
    
    # Allow access to the main domain (lvh.me)
    if len(parts) < 3:
        return HttpResponse("OK", status=200)
        
    # Verify the logged-in user owns this specific lab subdomain
    username_from_host = parts[0] 
    if request.user.username not in username_from_host:
        return HttpResponse("Access Denied", status=403)
        
    return HttpResponse("OK", status=200)

# --- Lab Management Views ---

def start_lab(request, lab_image_name):
    """Starts a lab for the new Dashboard UI."""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Auth required'}, status=401)
    
    client = get_docker_client()
    if not client:
        return JsonResponse({'status': 'error', 'message': 'Docker unavailable'}, status=503)

    username = request.user.username
    container_name = _get_container_name(username, lab_image_name)
    subdomain = f"{container_name}.{getattr(settings, 'LAB_DOMAIN', 'lvh.me')}"
    
    # Get port from config
    lab_config = _get_lab_config(lab_image_name)
    lab_port = str(lab_config.get('port', '5000'))

    labels = {
        "traefik.enable": "true",
        f"traefik.http.routers.{container_name}.rule": f"Host(`{subdomain}`)",
        f"traefik.http.routers.{container_name}.middlewares": f"{container_name}-auth",
        f"traefik.http.middlewares.{container_name}-auth.forwardauth.address": "http://pygoat-web-1:8000/challenge/auth-check/",
        f"traefik.http.middlewares.{container_name}-auth.forwardauth.trustForwardHeader": "true",
        f"traefik.http.services.{container_name}.loadbalancer.server.port": lab_port,
    }

    try:
        try:
            client.containers.get(container_name).remove(force=True)
        except:
            pass

        client.containers.run(
            image=lab_image_name,
            name=container_name,
            labels=labels,
            network=getattr(settings, "DOCKER_NETWORK", "my_network"),
            detach=True,
            mem_limit="512m"
        )
        return JsonResponse({'status': 'created', 'url': f"http://{subdomain}"})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def stop_lab(request, lab_image_name):
    client = get_docker_client()
    container_name = _get_container_name(request.user.username, lab_image_name)
    try:
        container = client.containers.get(container_name)
        container.remove(force=True)
        return JsonResponse({'status': 'success', 'message': 'Lab stopped'})
    except:
        return JsonResponse({'status': 'error', 'message': 'Lab not found'}, status=404)

def stop_user_labs(request):
    client = get_docker_client()
    containers = _get_user_containers(client, request.user.username)
    for c in containers:
        c.remove(force=True)
    return JsonResponse({'status': 'success', 'message': f'Stopped {len(containers)} labs'})

def list_user_labs(request):
    client = get_docker_client()
    containers = _get_user_containers(client, request.user.username)
    labs = [{'name': c.name, 'status': c.status} for c in containers]
    return JsonResponse({'status': 'success', 'labs': labs})

class DoItFast(View):
    """Handles Start/Stop/Redirect for the 'Do It Fast' challenge UI."""
    def post(self, request, challenge):
        if not request.user.is_authenticated:
            return JsonResponse({'message': 'Login required', 'status': '401'})
        
        try:
            chal = Challenge.objects.get(name=challenge)
            lab_config = _get_lab_config(chal.name)
            lab_port = str(lab_config.get('port', '5000')) 
        except Exception as e:
            return JsonResponse({'message': f'Config Error: {str(e)}', 'status': '404'})

        client = get_docker_client()
        username = request.user.username
        container_name = _get_container_name(username, challenge)
        subdomain = f"{container_name}.lvh.me"
        
        labels = {
            "traefik.enable": "true",
            f"traefik.http.routers.{container_name}.rule": f"Host(`{subdomain}`)",
            f"traefik.http.routers.{container_name}.middlewares": f"{container_name}-auth",
            f"traefik.http.middlewares.{container_name}-auth.forwardauth.address": "http://pygoat-web-1:8000/challenge/auth-check/",
            f"traefik.http.middlewares.{container_name}-auth.forwardauth.trustForwardHeader": "true",
            f"traefik.http.services.{container_name}.loadbalancer.server.port": lab_port,
        }

        try:
            try:
                client.containers.get(container_name).remove(force=True)
            except:
                pass

            client.containers.run(
                image=chal.docker_image,
                name=container_name,
                labels=labels,
                network=getattr(settings, "DOCKER_NETWORK", "my_network"),
                detach=True
            )

            return JsonResponse({
                'message': 'success',
                'status': '200',
                'endpoint': f'http://{subdomain}' 
            })

        except Exception as e:
            return JsonResponse({'message': f'Docker Error: {str(e)}', 'status': '500'})

    def delete(self, request, challenge):
        client = get_docker_client()
        container_name = _get_container_name(request.user.username, challenge)
        try:
            container = client.containers.get(container_name)
            container.remove(force=True)
            return JsonResponse({'message': 'success', 'status': '200'})
        except:
            return JsonResponse({'message': 'Lab not found', 'status': '404'})
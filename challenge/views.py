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

# --- THE BOUNCER (Traefik Auth) ---

@csrf_exempt
def check_auth(request):
    """The central Bouncer view used by Traefik."""
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    
    host = request.headers.get("X-Forwarded-Host", request.headers.get("Host", ""))
    parts = host.split(".")
    
    # Allow main domain access
    if len(parts) < 3:
        return HttpResponse("OK", status=200)
        
    # Example: lab-rishi-xss.lvh.me -> parts[0] is 'lab-rishi-xss'
    username_from_host = parts[0] 
    if request.user.username not in username_from_host:
        return HttpResponse("Access Denied", status=403)
        
    return HttpResponse("OK", status=200)

# --- Lab Management Views ---

def start_lab(request, lab_image_name):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Auth required'}, status=401)
    
    client = get_docker_client()
    if not client:
        return JsonResponse({'status': 'error', 'message': 'Docker unavailable'}, status=503)

    username = request.user.username
    container_name = _get_container_name(username, lab_image_name)
    domain = getattr(settings, 'LAB_DOMAIN', 'lvh.me')
    subdomain = f"{container_name}.{domain}"
    network_name = getattr(settings, 'DOCKER_NETWORK', 'my_network')

    labels = {
        "traefik.enable": "true",
        f"traefik.http.routers.{container_name}.rule": f"Host(`{subdomain}`)",
        # Point to the web container for session validation
        f"traefik.http.middlewares.{container_name}-auth.forwardauth.address": "http://web:8000/challenge/auth-check/",
        f"traefik.http.routers.{container_name}.middlewares": f"{container_name}-auth",
        f"traefik.http.services.{container_name}.loadbalancer.server.port": "5000",
    }

    try:
        # Cleanup old instances
        try:
            client.containers.get(container_name).remove(force=True)
        except:
            pass

        client.containers.run(
            image=lab_image_name,
            name=container_name,
            labels=labels,
            network=network_name,
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

# --- Legacy Placeholder ---
class DoItFast(View):
    def get(self, request, challenge):
        return HttpResponse("Legacy Lab View - Please use the new Dashboard.")

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
import subprocess
from .utility import get_free_port
from .models import Challenge, UserChallenge, Lab
import docker
import json
import os
import re
from django.conf import settings
import time
import requests

# Create your views here.
def get_docker_client():
    try:
        return docker.from_env()
    except Exception as e:
        print(f"Failed to connect to Docker daemon: {e}")
        return None


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
        except Exception as e:
            return render(request, "chal-not-found.html")

        try:
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
            return render(
                request, "challenge.html", {"chal": chal, "user_chal": user_chal}
            )
        except:
            return render(request, "challenge.html", {"chal": chal, "user_chal": None})

    def post(self, request, challenge):
        user_chall_exists = False
        if not request.user.is_authenticated:
            return redirect("login")

        try:  # checking the existence of challenge
            chal = Challenge.objects.get(name=challenge)
        except Exception as e:
            return render(request, "chal-not-found.html")

        try:  # checking if he attempted it before or not, if yes then check if the container is live or not
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
            if user_chal.is_live:
                return JsonResponse(
                    {
                        "message": "already running",
                        "status": "200",
                        "endpoint": f"http://localhost:{user_chal.port}",
                    }
                )
            user_chall_exists = True
        except:
            pass

        port = get_free_port(8000, 8100)
        if port == None:
            return JsonResponse(
                {"message": "failed", "status": "500", "endpoint": "None"}
            )

        command = f"docker run -d -p {port}:{chal.docker_port} {chal.docker_image}"
        process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
        output, error = process.communicate()
        container_id = output.decode("utf-8").strip()

        if user_chall_exists:
            # TODO : reuse the container instead of creating the new one
            user_chal.container_id = container_id
            user_chal.port = port
            user_chal.is_live = True
            user_chal.save()
        else:
            user_chal = UserChallenge(
                user=request.user, challenge=chal, container_id=container_id, port=port
            )
            user_chal.save()
        # save the output in database for stoping the container
        return JsonResponse(
            {
                "message": "success",
                "status": "200",
                "endpoint": f"http://localhost:{port}",
            }
        )

    def delete(self, request, challenge):
        if not request.user.is_authenticated:
            return redirect("login")

        try:
            chal = Challenge.objects.get(name=challenge)
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
        except Exception as e:
            return JsonResponse({"message": "failed", "status": "500"})

        user_chal.is_live = False
        user_chal.save()
        command = f"docker stop {user_chal.container_id}"
        process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
        output, error = process.communicate()
        return JsonResponse({"message": "success", "status": "200"})

    def put(self, request, challange):
        # TODO : implement flag checking
        return "not implemented"

def _sanitize_username(username: str) -> str:
    return "".join(ch for ch in username if ch.isalnum() or ch in "-_")


def _sanitize_image_name(name: str) -> str:
    return "".join(ch for ch in name if ch.isalnum() or ch in "-_")


def _get_container_name(username: str, lab_image_name: str) -> str:
    safe_username = _sanitize_username(username)
    safe_image = _sanitize_image_name(lab_image_name)
    return f"lab-{safe_username}-{safe_image}"


def _get_lab_config(lab_image_name: str) -> dict:
    try:
        lab = Lab.objects.get(name=lab_image_name)
        return {
            'name': lab.name,
            'build_location': lab.build_location,
            'port': lab.port
        }
    except Lab.DoesNotExist:
        raise KeyError(f'Lab config not found: {lab_image_name}')


def _ensure_image_built(client, image: str, build_location: str):
    try:
        client.images.get(image)
    except docker.errors.ImageNotFound:
        build_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), build_location)
        client.images.build(path=build_path, tag=image)


def _container_exists(client, container_name: str) -> bool:
    try:
        client.containers.get(container_name)
        return True
    except docker.errors.NotFound:
        return False


def _get_user_containers(client, username: str):
    safe_username = _sanitize_username(username)
    container_prefix = f"lab-{safe_username}-"
    containers = client.containers.list(all=True)
    return [c for c in containers if c.name.startswith(container_prefix)]

def wait_for_health(container, timeout=60):
    print(f"Waiting for {container.name} to become healthy...")
    start_time = time.time()

    while True:
        container.reload()
        
        health_status = container.attrs.get('State', {}).get('Health', {}).get('Status')
        
        if health_status == 'healthy':
            print("Container is HEALTHY!")
            return True
        
        if health_status == 'unhealthy':
            container.stop()
            raise RuntimeError(f"Container {container.name} is UNHEALTHY and has been stopped. Check logs for details.")


        if time.time() - start_time > timeout:
            raise TimeoutError("Timed out waiting for healthcheck.")

        time.sleep(1)

def start_lab(request, lab_image_name):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    
    if not check_traefik_reachable():
        return JsonResponse({'status': 'error', 'message': 'Traefik reverse proxy is not reachable'}, status=503)
    
    client = get_docker_client()
    if client is None:
        return JsonResponse({'status': 'error', 'message': 'Docker daemon unavailable'}, status=503)

    username = request.user.username
    safe_image = _sanitize_image_name(lab_image_name)
    container_name = _get_container_name(username, lab_image_name)
    domain = getattr(settings, 'LAB_DOMAIN', 'localhost')
    lab_url = f"http://{container_name}.{domain}"

    per_user_limit = getattr(settings, 'LABS_PER_USER_LIMIT', 3)
    

    try:
        if not _container_exists(client, container_name):
            user_containers = _get_user_containers(client, username)
            if len(user_containers) >= per_user_limit:
                try:
                    client.containers.get(container_name)
                except docker.errors.NotFound:
                    return JsonResponse({'status': 'error', 'message': f'Per-user lab limit reached ({per_user_limit})'}, status=429)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Unable to verify user container quota'}, status=503)

    try:
        lab_config = _get_lab_config(safe_image)
        build_location = lab_config['build_location']
        lab_port = str(lab_config['port'])
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        return JsonResponse({'status': 'error', 'message': f'Error loading lab configuration: {str(e)}'}, status=500)

    try:
        try:
            container = client.containers.get(container_name)
            container.reload()
            if container.status != 'running':
                container.start()
            wait_for_health(container)
            return JsonResponse({'status': 'ready', 'url': lab_url})
        except docker.errors.NotFound:
            _ensure_image_built(client, safe_image, build_location)

            labels = {
                "traefik.enable": "true",
                f"traefik.http.routers.{container_name}.rule": f"Host(`{container_name}.{domain}`)",
                f"traefik.http.services.{container_name}.loadbalancer.server.port": lab_port,
            }
            healthcheck = docker.types.Healthcheck(
            test=[
                "CMD",
                "python",
                "-c",
                (
                    "import urllib.request, sys;"
                    "sys.exit(0) if urllib.request.urlopen("
                    f"'http://localhost:{lab_port}/health'"
                    ").status == 200 else sys.exit(1)"
                )
            ],
            interval=5000000000,  # 5s in nanoseconds
            timeout=2000000000,     # 2s in nanoseconds
            retries=3,
            start_period=2000000000  # 2s in nanoseconds
            )
            container = client.containers.run(
                image=safe_image,
                name=container_name,
                detach=True,
                labels=labels,
                network=getattr(settings, "DOCKER_NETWORK", "my_network"),
                mem_limit="512m",
                healthcheck=healthcheck
            )
            container.reload()
            wait_for_health(container)
            return JsonResponse({'status': 'created', 'url': lab_url})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def stop_user_labs(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    
    username = request.user.username
    client = get_docker_client()
    if client is None:
        return JsonResponse({'status': 'error', 'message': 'Docker daemon unavailable'}, status=503)

    try:
        user_containers = _get_user_containers(client, username)
        
        stopped_count = 0
        for container in user_containers:
            try:
                if container.status == 'running':
                    container.stop()
                container.remove()
                stopped_count += 1
            except Exception as e:
                print(f"Error stopping container {container.name}: {e}")
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Stopped and removed {stopped_count} lab container(s)',
            'count': stopped_count
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def list_user_labs(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)

    username = request.user.username
    client = get_docker_client()
    if client is None:
        return JsonResponse({'status': 'error', 'message': 'Docker daemon unavailable'}, status=503)

    try:
        user_containers = _get_user_containers(client, username)
        labs = []
        for c in user_containers:
            labs.append({
                'name': c.name,
                'status': c.status,
            })
        return JsonResponse({'status': 'success', 'labs': labs})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def stop_lab(request, lab_image_name):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)

    username = request.user.username
    container_name = _get_container_name(username, lab_image_name)

    client = get_docker_client()
    if client is None:
        return JsonResponse({'status': 'error', 'message': 'Docker daemon unavailable'}, status=503)

    try:
        user_containers = _get_user_containers(client, username)
        container = next((c for c in user_containers if c.name == container_name), None)
        if container is None:
            return JsonResponse({'status': 'error', 'message': 'Lab container not found'}, status=404)
        if container.status == 'running':
            container.stop()
        container.remove()
        return JsonResponse({'status': 'success', 'message': f'Stopped {lab_image_name}'})
    except docker.errors.NotFound:
        return JsonResponse({'status': 'error', 'message': 'Lab container not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def list_custom_labs(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    if request.method != "GET":
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    labs = Lab.objects.filter(is_custom=True).order_by('name')
    labs_list = [{
        'id': lab.id,
        'name': lab.name,
        'build_location': lab.build_location,
        'port': lab.port
    } for lab in labs]
    return JsonResponse({'status': 'success', 'labs': labs_list})


def create_custom_lab(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        name = data.get('name')
        build_location = data.get('build_location')
        port = data.get('port')
        
        if not name or not build_location or not port:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)
            
        if not re.match(r'^[-a-zA-Z0-9_]+$', name):
            return JsonResponse({'status': 'error', 'message': 'Invalid lab name. Only alphanumeric characters, hyphens, and underscores are allowed.'}, status=400)
            
        try:
            port = int(port)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Port must be an integer'}, status=400)
            
        if Lab.objects.filter(name=name).exists():
            return JsonResponse({'status': 'error', 'message': f'Lab with name {name} already exists'}, status=400)
            
        lab = Lab.objects.create(name=name, build_location=build_location, port=port)
        return JsonResponse({
            'status': 'success',
            'message': f'Lab {name} created successfully',
            'lab': {
                'id': lab.id,
                'name': lab.name,
                'build_location': lab.build_location,
                'port': lab.port
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def update_custom_lab(request, lab_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
        
    try:
        try:
            lab = Lab.objects.get(id=lab_id, is_custom=True)
        except Lab.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Lab not found'}, status=404)
            
        data = json.loads(request.body)
        name = data.get('name')
        build_location = data.get('build_location')
        port = data.get('port')
        
        if not name or not build_location or not port:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)
            
        if not re.match(r'^[-a-zA-Z0-9_]+$', name):
            return JsonResponse({'status': 'error', 'message': 'Invalid lab name. Only alphanumeric characters, hyphens, and underscores are allowed.'}, status=400)
            
        try:
            port = int(port)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Port must be an integer'}, status=400)
            
        if Lab.objects.filter(name=name).exclude(id=lab_id).exists():
            return JsonResponse({'status': 'error', 'message': f'Lab with name {name} already exists'}, status=400)
            
        lab.name = name
        lab.build_location = build_location
        lab.port = port
        lab.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Lab {name} updated successfully',
            'lab': {
                'id': lab.id,
                'name': lab.name,
                'build_location': lab.build_location,
                'port': lab.port
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def delete_custom_lab(request, lab_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
        
    try:
        try:
            lab = Lab.objects.get(id=lab_id, is_custom=True)
        except Lab.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Lab not found'}, status=404)
            
        name = lab.name
        lab.delete()
        return JsonResponse({'status': 'success', 'message': f'Lab {name} deleted successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


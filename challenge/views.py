from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
import subprocess
from .utility import get_free_port
from .models import Challenge, UserChallenge
import docker
import json
import os
from django.conf import settings
import time

# Create your views here.
def get_docker_client():
    try:
        return docker.from_env()
    except Exception as e:
        print(f"Failed to connect to Docker daemon: {e}")
        return None

class DoItFast(View):
    def get(self, request, challenge):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            chal = Challenge.objects.get(name=challenge)
        except Exception as e:
            return render(request, 'chal-not-found.html')

        try:
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
            return render(request, 'challenge.html', {'chal': chal, 'user_chal': user_chal})
        except:
            return render(request, 'challenge.html', {'chal': chal, 'user_chal': None})
    
    def post(self, request, challenge):
        user_chall_exists = False
        if not request.user.is_authenticated:
            return redirect('login')
        
        try: # checking the existance of challenge
            chal = Challenge.objects.get(name=challenge)
        except Exception as e:
            return render(request, 'chal-not-found.html')

        try: # checking if he attempted it before or not, if yes then check if the container is live or not
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
            if user_chal.is_live:
                return JsonResponse({'message':'already running', 'status': '200', 'endpoint': f'http://localhost:{user_chal.port}'})
            user_chall_exists = True
        except:
            pass

        port = get_free_port(8000, 8100)
        if port == None:
            return JsonResponse({'message': 'failed', 'status': '500', 'endpoint': 'None'})
        
        command = f"docker run -d -p {port}:{chal.docker_port} {chal.docker_image}"
        process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
        output, error = process.communicate()
        container_id = output.decode('utf-8').strip()
        
        if user_chall_exists:
            # TODO : reuse the container instead of creaing the new one
            user_chal.container_id = container_id
            user_chal.port = port
            user_chal.is_live = True
            user_chal.save()
        else:
            user_chal = UserChallenge(user=request.user, challenge=chal, container_id=container_id, port=port)
            user_chal.save()
        # save the output in database for stoping the container 
        return JsonResponse({'message': 'success', 'status': '200', 'endpoint': f'http://localhost:{port}'})



    def delete(self, request, challenge):
        if not request.user.is_authenticated:
            return redirect('login')
    
        try:
            chal = Challenge.objects.get(name=challenge)
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
        except Exception as e:
            return JsonResponse({'message': 'failed', 'status': '500'})

        user_chal.is_live = False
        user_chal.save()
        command = f"docker stop {user_chal.container_id}"
        process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
        output, error = process.communicate()
        return JsonResponse({'message': 'success', 'status': '200'})
    
    def put(self, request, challange):
        # TODO : implement flag checking
        return "not implemented"

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
    client = get_docker_client()
    if client is None:
        return JsonResponse({'status': 'error', 'message': 'Docker daemon unavailable'}, status=503)

    def _sanitize_username(u: str) -> str:
        return "".join(ch for ch in u if ch.isalnum())

    def _sanitize_image_name(n: str) -> str:
        return "".join(ch for ch in n if ch.isalnum() or ch in "-_")

    def _load_lab_config(name: str) -> dict:
        labs_json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'labs.json')
        with open(labs_json_path, 'r') as f:
            data = json.load(f)
        for lab in data.get('labs', []):
            if lab.get('name') == name:
                return lab
        raise KeyError(f'Lab config not found: {name}')

    def _ensure_image_built(image: str, build_location: str):
        try:
            client.images.get(image)
        except docker.errors.ImageNotFound:

            build_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), build_location)
            client.images.build(path=build_path, tag=image)
    
    def _check_container_existence(container_name):
        try:
            client.containers.get(container_name)
            container_exists = True
        except docker.errors.NotFound:
            container_exists = False
        return container_exists

        
    username = request.user.username
    safe_username = _sanitize_username(username)
    safe_image = _sanitize_image_name(lab_image_name)
    container_name = f"lab-{safe_username}-{safe_image}"
    domain = getattr(settings, 'LAB_DOMAIN', 'localhost')
    lab_url = f"http://{container_name}.{domain}"

    per_user_limit = getattr(settings, 'LABS_PER_USER_LIMIT', 3)
    

    try:
        if not _check_container_existence(container_name):
            containers_for_user = client.containers.list(all=True)
            user_containers = [c for c in containers_for_user if c.name.startswith(f"lab-{safe_username}-")]
            if len(user_containers) >= per_user_limit:
                try:
                    client.containers.get(container_name)
                except docker.errors.NotFound:
                    return JsonResponse({'status': 'error', 'message': f'Per-user lab limit reached ({per_user_limit})'}, status=429)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Unable to verify user container quota'}, status=503)

    try:
        lab_config = _load_lab_config(safe_image)
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
            _ensure_image_built(safe_image, build_location)

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
    safe_username = "".join(x for x in username if x.isalnum())
    container_prefix = f"lab-{safe_username}-"
    client = get_docker_client()
    if client is None:
        return JsonResponse({'status': 'error', 'message': 'Docker daemon unavailable'}, status=503)

    try:
        containers = client.containers.list(all=True)
        user_containers = [c for c in containers if c.name.startswith(container_prefix)]
        
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

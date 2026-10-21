from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import View
from .models import Challenge, UserChallenge, Lab
from scoring.services import start_tracking, complete_tracking
import docker

try:
    import fcntl
except ImportError:  # Windows
    fcntl = None
import hashlib
import hmac
import io
import json
import os
import tarfile
import tempfile
from contextlib import contextmanager
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
        if not request.user.is_authenticated:
            return redirect("login")

        try:  # checking the existence of challenge
            chal = Challenge.objects.get(name=challenge)
        except Exception:
            return render(request, "chal-not-found.html")

        client = get_docker_client()
        if client is None:
            return JsonResponse(
                {"message": "Docker daemon unavailable", "status": "503", "endpoint": "None"},
                status=503,
            )

        user_chal = UserChallenge.objects.filter(user=request.user, challenge=chal).first()
        if user_chal and user_chal.is_live:
            container = _get_container_or_none(client, user_chal.container_id)
            if container is not None and container.status == "running":
                return JsonResponse(
                    {
                        "message": "already running",
                        "status": "200",
                        "endpoint": f"http://localhost:{user_chal.port}",
                    }
                )
            # Container exited or was removed outside the app: replace it
            if container is not None:
                container.remove(force=True)

        container = None
        try:
            # Let Docker pick a free host port; checking from inside the web
            # container can't see ports in use on the Docker host.
            container = client.containers.run(
                chal.docker_image,
                detach=True,
                ports={f"{chal.docker_port}/tcp": None},
            )
            container.reload()
            port = int(container.ports[f"{chal.docker_port}/tcp"][0]["HostPort"])
        except (docker.errors.DockerException, KeyError, IndexError, TypeError) as e:
            if container is not None:
                container.remove(force=True)
            return JsonResponse(
                {"message": f"Failed to start challenge: {e}", "status": "500", "endpoint": "None"},
                status=500,
            )

        if user_chal is None:
            user_chal = UserChallenge(user=request.user, challenge=chal)
        user_chal.container_id = container.id
        user_chal.port = port
        user_chal.is_live = True
        user_chal.save()
        start_tracking(request.user, "challenge", chal.id)
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
        except Exception:
            return JsonResponse({"message": "failed", "status": "500"})

        client = get_docker_client()
        if client is None:
            return JsonResponse({"message": "Docker daemon unavailable", "status": "503"}, status=503)
        container = _get_container_or_none(client, user_chal.container_id)
        if container is not None:
            try:
                container.remove(force=True)
            except docker.errors.APIError as e:
                return JsonResponse({"message": f"Failed to stop challenge: {e}", "status": "500"}, status=500)

        # Only mark stopped once the container is really gone
        user_chal.is_live = False
        user_chal.save()
        return JsonResponse({"message": "success", "status": "200"})

    def put(self, request, challenge):
        if not request.user.is_authenticated:
            return JsonResponse({"message": "Authentication required", "status": "401"}, status=401)

        try:
            chal = Challenge.objects.get(name=challenge)
        except Challenge.DoesNotExist:
            return JsonResponse({"message": "Challenge not found", "status": "404"}, status=404)

        try:
            submitted = json.loads(request.body).get("flag", "")
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"message": "Invalid request body", "status": "400"}, status=400)
        if not isinstance(submitted, str) or not submitted:
            return JsonResponse({"message": "Flag is required", "status": "400"}, status=400)

        # Challenge.flag is stored as "hashed_<sha256>" (see Challenge.save)
        submitted_hash = "hashed_" + hashlib.sha256(submitted.strip().encode("utf-8")).hexdigest()

        try:
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
        except UserChallenge.DoesNotExist:
            return JsonResponse(
                {"message": "Start the challenge before submitting a flag", "status": "400"},
                status=400,
            )

        user_chal.no_of_attempt += 1
        if not hmac.compare_digest(submitted_hash, chal.flag):
            user_chal.save()
            return JsonResponse({"message": "Incorrect flag", "status": "200", "correct": False})

        user_chal.is_solved = True
        user_chal.save()
        completion, newly_completed = complete_tracking(
            request.user, "challenge", chal.id, content_name=chal.name
        )
        score = getattr(completion, "score", None)
        return JsonResponse(
            {
                "message": "Correct flag!" if newly_completed else "Already solved",
                "status": "200",
                "correct": True,
                "final_score": score.final_score if score else 0,
            }
        )

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


# Lab images may only be built from these directories of the repo
LAB_BUILD_ROOTS = ("dockerized_labs", os.path.join("challenge", "labs"))


def _resolve_build_path(build_location: str) -> str:
    """
    Return the absolute build directory for a lab, or raise ValueError if it
    is outside LAB_BUILD_ROOTS (e.g. an absolute path or one using "..") or
    has no Dockerfile.
    """
    base = os.path.realpath(settings.BASE_DIR)
    build_path = os.path.realpath(os.path.join(base, build_location or ""))
    roots = [os.path.join(base, root) for root in LAB_BUILD_ROOTS]
    if not any(build_path.startswith(root + os.sep) for root in roots):
        raise ValueError(
            "Build location must be a directory under " + " or ".join(LAB_BUILD_ROOTS)
        )
    if not os.path.isfile(os.path.join(build_path, "Dockerfile")):
        raise ValueError("Build location must contain a Dockerfile")
    return build_path


def _ensure_image_built(client, image: str, build_location: str):
    try:
        client.images.get(image)
    except docker.errors.ImageNotFound:
        build_path = _resolve_build_path(build_location)
        client.images.build(path=build_path, tag=image, rm=True, forcerm=True)


def _copy_common_css(container):
    """
    Copy the shared lab stylesheet into a created (not yet started) container.
    A bind mount can't be used: under docker-compose the web container's path
    doesn't exist on the Docker host.
    """
    css_path = os.path.join(settings.BASE_DIR, "introduction", "static", "css", "common_lab.css")
    if not os.path.exists(css_path):
        return
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        tar.add(css_path, arcname="static/common_lab.css")
        tar.add(css_path, arcname="static/css/common_lab.css")
    try:
        container.put_archive("/app", buf.getvalue())
    except docker.errors.APIError as e:
        print(f"Could not copy common_lab.css into {container.name}: {e}")


def _get_container_or_none(client, container_id: str):
    if not container_id:
        return None
    try:
        return client.containers.get(container_id)
    except docker.errors.NotFound:
        return None


@contextmanager
def _user_lab_lock(username: str):
    """
    Serialize the quota check and container creation for one user across
    gunicorn workers/threads, so parallel requests can't exceed the limit.
    No-op where fcntl is unavailable (Windows).
    """
    if fcntl is None:
        yield
        return
    path = os.path.join(tempfile.gettempdir(), f"pygoat-lab-{_sanitize_username(username)}.lock")
    with open(path, "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def _get_user_containers(client, username: str):
    safe_username = _sanitize_username(username)
    container_prefix = f"lab-{safe_username}-"
    containers = client.containers.list(all=True)
    return [c for c in containers if c.name.startswith(container_prefix)]

def _discard_container(container, remove):
    if remove:
        container.remove(force=True)
    else:
        container.stop()


def wait_for_health(container, timeout=60, remove_on_failure=True):
    """
    Wait for the container's healthcheck. On failure the container is removed
    if it was just created, or only stopped if it already existed, so a slow
    restart doesn't destroy the user's lab state.
    """
    print(f"Waiting for {container.name} to become healthy...")
    start_time = time.time()

    while True:
        container.reload()
        
        health_status = container.attrs.get("State", {}).get("Health", {}).get("Status")
        
        # Handle case where no HEALTHCHECK exists
        if health_status is None:
            return True
        
        if health_status == 'healthy':
            print("Container is HEALTHY!")
            return True
        
        if health_status == 'unhealthy':
            _discard_container(container, remove_on_failure)
            raise RuntimeError(f"Container {container.name} is UNHEALTHY and has been stopped. Check its /health endpoint.")

        if time.time() - start_time > timeout:
            _discard_container(container, remove_on_failure)
            raise TimeoutError(f"Timed out waiting for {container.name} to become healthy.")

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
        lab_config = _get_lab_config(safe_image)
        build_location = lab_config['build_location']
        lab_port = str(lab_config['port'])
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        return JsonResponse({'status': 'error', 'message': f'Error loading lab configuration: {str(e)}'}, status=500)

    try:
        container = _get_container_or_none(client, container_name)
        if container is None:
            # Can take minutes; done before taking the per-user lock
            _ensure_image_built(client, safe_image, build_location)

        created = False
        with _user_lab_lock(username):
            # Re-read: a parallel request may have created/started it meanwhile
            container = _get_container_or_none(client, container_name)
            if container is None or container.status != 'running':
                try:
                    running_others = [
                        c for c in _get_user_containers(client, username)
                        if c.name != container_name and c.status == 'running'
                    ]
                except Exception:
                    return JsonResponse({'status': 'error', 'message': 'Unable to verify user container quota'}, status=503)
                if len(running_others) >= per_user_limit:
                    return JsonResponse({'status': 'error', 'message': f'Per-user lab limit reached ({per_user_limit})'}, status=429)

            if container is None:
                container = _create_lab_container(client, safe_image, container_name, domain, lab_port)
                created = True
            elif container.status != 'running':
                container.start()

        container.reload()
        wait_for_health(container, remove_on_failure=created)
        return JsonResponse({'status': 'created' if created else 'ready', 'url': lab_url})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def _create_lab_container(client, image, container_name, domain, lab_port):
    labels = {
        "traefik.enable": "true",
        f"traefik.http.routers.{container_name}.rule": f"Host(`{container_name}.{domain}`)",
        f"traefik.http.services.{container_name}.loadbalancer.server.port": lab_port,
    }
    forward_auth_url = getattr(settings, "LAB_FORWARD_AUTH_URL", "")
    if forward_auth_url:
        # trustForwardHeader stays off so clients can't spoof X-Forwarded-Host
        labels.update({
            "traefik.http.middlewares.django-auth.forwardauth.address": forward_auth_url,
            "traefik.http.middlewares.django-auth.forwardauth.authResponseHeaders": "X-Forwarded-User",
            f"traefik.http.routers.{container_name}.middlewares": "django-auth",
        })
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
    container = client.containers.create(
        image=image,
        name=container_name,
        detach=True,
        labels=labels,
        network=getattr(settings, "DOCKER_NETWORK", "my_network"),
        mem_limit="512m",
        healthcheck=healthcheck,
    )
    _copy_common_css(container)
    container.start()
    return container


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
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Only staff users can manage custom labs'}, status=403)
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        name = data.get('name')
        build_location = data.get('build_location')
        port = data.get('port')
        
        if not name or not build_location or not port:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

        try:
            _resolve_build_path(build_location)
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
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
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Only staff users can manage custom labs'}, status=403)
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

        try:
            _resolve_build_path(build_location)
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
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
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Only staff users can manage custom labs'}, status=403)
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


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
import requests
import hashlib
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
 
from .models import Challenge, UserChallenge, UserProfile, BADGE_CATALOGUE

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
    labs_json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'labs.json')
    with open(labs_json_path, 'r') as f:
        data = json.load(f)
    for lab in data.get('labs', []):
        if lab.get('name') == lab_image_name:
            return lab
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
    
def _award_completion_badges(profile: UserProfile, solved_count: int, total: int) -> None:
    """
    Check and award milestone badges after a successful flag submission.
    Called after every solve — idempotent (award_badge skips duplicates).
    """
    if solved_count == 1:
        profile.award_badge("first_blood")
    if total > 0 and solved_count >= total // 2:
        profile.award_badge("half_way")
    if total > 0 and solved_count >= total:
        profile.award_badge("completionist")
    if profile.xp_points >= 500:
        profile.award_badge("high_scorer")
 
 
# ─── Progress Dashboard (HTML) ────────────────────────────────────────────────
 
@login_required
def progress_dashboard(request):
    """
    Main learner progress page.
 
    Context variables sent to the template:
      challenges_data  – list of dicts, one per Challenge
      stats            – summary dict (totals, XP, level, streak)
      badges           – list of earned badge dicts
      badge_catalogue  – full catalogue for "locked" badge display
    """
    all_challenges = Challenge.objects.all().order_by("name")
    user_challenges_qs = UserChallenge.objects.filter(
        user=request.user
    ).select_related("challenge")
 
    # Build a lookup: challenge_id → UserChallenge row
    uc_map = {uc.challenge_id: uc for uc in user_challenges_qs}
 
    challenges_data = []
    for chal in all_challenges:
        uc = uc_map.get(chal.id)
        challenges_data.append(
            {
                "challenge":  chal,
                "is_solved":  uc.is_solved if uc else False,
                "is_live":    uc.is_live if uc else False,
                "attempts":   uc.no_of_attempt if uc else 0,
                "started":    uc is not None,
            }
        )
 
    solved_list   = [d for d in challenges_data if d["is_solved"]]
    started_list  = [d for d in challenges_data if d["started"] and not d["is_solved"]]
    total_count   = len(challenges_data)
    solved_count  = len(solved_list)
    total_points  = sum(d["challenge"].point for d in solved_list)
 
    completion_pct = (
        round((solved_count / total_count) * 100) if total_count else 0
    )
 
    # Ensure UserProfile exists (guards legacy accounts created before signals)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
 
    # Sync XP with actual earned points so it stays accurate even if
    # points were awarded outside the flag endpoint below.
    if profile.xp_points != total_points:
        profile.xp_points = total_points
        profile.save(update_fields=["xp_points"])
        _award_completion_badges(profile, solved_count, total_count)
 
    stats = {
        "total_count":     total_count,
        "solved_count":    solved_count,
        "started_count":   len(started_list),
        "completion_pct":  completion_pct,
        "total_points":    total_points,
        "xp_points":       profile.xp_points,
        "xp_level":        profile.xp_level,
        "xp_progress_pct": profile.xp_progress_pct,
        "streak_days":     profile.streak_days,
    }
 
    # Full catalogue with earned/locked distinction for the badge wall
    badge_wall = []
    for key, meta in BADGE_CATALOGUE.items():
        badge_wall.append(
            {**meta, "key": key, "earned": key in profile.badges}
        )
 
    context = {
        "challenges_data": challenges_data,
        "stats":           stats,
        "badges":          profile.badge_details(),
        "badge_wall":      badge_wall,
    }
    return render(request, "introduction/progress_dashboard.html", context)
 
 
# ─── Progress API (JSON) – used by the dashboard chart ───────────────────────
 
@login_required
def progress_api(request):
    """
    Returns a JSON summary of the current user's progress.
    Used by Chart.js on the dashboard page for the doughnut chart.
 
    Response shape:
    {
        "solved": 3,
        "in_progress": 1,
        "not_started": 8,
        "total": 12,
        "xp_points": 350,
        "streak_days": 4
    }
    """
    all_challenges = Challenge.objects.all()
    user_challenges_qs = UserChallenge.objects.filter(user=request.user)
    uc_map = {uc.challenge_id: uc for uc in user_challenges_qs}
 
    solved = in_progress = not_started = 0
    for chal in all_challenges:
        uc = uc_map.get(chal.id)
        if uc is None:
            not_started += 1
        elif uc.is_solved:
            solved += 1
        else:
            in_progress += 1
 
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
 
    return JsonResponse(
        {
            "solved":       solved,
            "in_progress":  in_progress,
            "not_started":  not_started,
            "total":        all_challenges.count(),
            "xp_points":    profile.xp_points,
            "streak_days":  profile.streak_days,
        }
    )
 
 
# ─── Flag Submission (POST) ───────────────────────────────────────────────────
 
@login_required
@require_POST
def submit_flag(request):
    """
    Accepts a flag submission from the dashboard flag input on each challenge row.
 
    POST body (form-encoded):
        challenge_id  – integer PK of the Challenge
        flag          – the user's submitted flag string
 
    Returns JSON:
        {"success": true,  "xp_awarded": 100, "message": "..."} on correct flag
        {"success": false, "message": "..."}                     on wrong flag
    """
    challenge_id   = request.POST.get("challenge_id", "").strip()
    submitted_flag = request.POST.get("flag", "").strip()
 
    if not challenge_id or not submitted_flag:
        return JsonResponse(
            {"success": False, "message": "challenge_id and flag are required."},
            status=400,
        )
 
    try:
        chal = Challenge.objects.get(pk=int(challenge_id))
    except (Challenge.DoesNotExist, ValueError):
        return JsonResponse(
            {"success": False, "message": "Challenge not found."},
            status=404,
        )
 
    # Build hashed version of what the user submitted (same scheme as Challenge.save)
    submitted_hashed = (
        "hashed_" + hashlib.sha256(submitted_flag.encode("utf-8")).hexdigest()
    )
 
    # Constant-time comparison to prevent timing attacks
    import hmac as _hmac
    correct = _hmac.compare_digest(submitted_hashed, chal.flag)
 
    if not correct:
        # Increment attempt counter even on wrong answer
        uc, _ = UserChallenge.objects.get_or_create(
            user=request.user,
            challenge=chal,
            defaults={"container_id": "", "port": 0},
        )
        uc.no_of_attempt = uc.no_of_attempt + 1
        uc.save(update_fields=["no_of_attempt"])
        return JsonResponse({"success": False, "message": "Incorrect flag. Try again!"})
 
    # ── Correct flag ──────────────────────────────────────────────────────────
    uc, _ = UserChallenge.objects.get_or_create(
        user=request.user,
        challenge=chal,
        defaults={"container_id": "", "port": 0},
    )
    uc.no_of_attempt = uc.no_of_attempt + 1
    already_solved    = uc.is_solved
 
    if not already_solved:
        uc.is_solved = True
        uc.save(update_fields=["no_of_attempt", "is_solved"])
 
        # Award XP (only on first solve)
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.add_xp(chal.point)
 
        # Check for milestone badges
        total_count  = Challenge.objects.count()
        solved_count = UserChallenge.objects.filter(
            user=request.user, is_solved=True
        ).count()
        _award_completion_badges(profile, solved_count, total_count)
 
        return JsonResponse(
            {
                "success":    True,
                "xp_awarded": chal.point,
                "message":    f"🎉 Correct! +{chal.point} XP awarded.",
            }
        )
    else:
        uc.save(update_fields=["no_of_attempt"])
        return JsonResponse(
            {
                "success":    True,
                "xp_awarded": 0,
                "message":    "Already solved — no additional XP.",
            }
        )
     

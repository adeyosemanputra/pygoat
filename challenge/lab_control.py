import os
import subprocess
import json

from .lab_registry import (
    get_lab_service_name,
    get_lab_internal_port,
    list_all_labs,
)

LAB_PROFILES = {}
LAB_PORTS = {}

for lab in list_all_labs():
    service_name = get_lab_service_name(lab)
    if service_name:
        lab_key = lab.replace("_", "-")
        LAB_PROFILES[lab_key] = service_name
        LAB_PORTS[lab_key] = get_lab_internal_port(lab)

BASE_CMD = "docker compose -f docker-compose.labs.yml"
RUNNING_IN_DOCKER = os.path.exists("/.dockerenv")

USER_CONTAINERS_FILE = "/tmp/user_labs.json" if RUNNING_IN_DOCKER else "user_labs.json"


def _load_user_containers():
    """Load user->container mapping"""
    if os.path.exists(USER_CONTAINERS_FILE):
        try:
            with open(USER_CONTAINERS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}


def _save_user_containers(data):
    """Save user->container mapping"""
    try:
        with open(USER_CONTAINERS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save user containers: {e}")


def _disabled():
    return False, "Lab control is disabled in local development mode. Use docker-compose to manage labs."


def run(cmd):
    """Execute shell command with timeout and error handling"""
    try:
        return subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
            cwd=os.getcwd() if not RUNNING_IN_DOCKER else "/app"
        )
    except subprocess.TimeoutExpired:
        return type('obj', (object,), {
            'returncode': 1,
            'stderr': 'Command timeout after 30 seconds',
            'stdout': ''
        })()
    except Exception as e:
        return type('obj', (object,), {
            'returncode': 1,
            'stderr': str(e),
            'stdout': ''
        })()

def _get_host_shared_path():
    """Get host path for shared/ by inspecting own container mounts"""
    if not RUNNING_IN_DOCKER:
        return os.path.abspath("shared")
    
    try:
        container_id = open("/etc/hostname").read().strip()
        result = run(f"docker inspect {container_id}")
        mounts = json.loads(result.stdout)
        for mount in mounts[0].get("Mounts", []):
            if mount.get("Destination") == "/app":
                host_app_path = mount["Source"]
                # normalize Windows path separators if needed
                return host_app_path.replace("\\", "/") + "/shared"
    except Exception as e:
        print(f"Warning: Could not detect host shared path: {e}")
    
    return "/app/shared"

def start_lab(lab, user_id=None):
    """Start lab container - isolated per user with network alias"""
    if not RUNNING_IN_DOCKER:
        return _disabled()

    if lab not in LAB_PROFILES:
        return False, f"Unknown lab: {lab}"

    if user_id is None:
        r = run(f"{BASE_CMD} --profile {lab} up -d")
        return (True, "Lab started") if r.returncode == 0 else (False, r.stderr[:200])

    service_name = LAB_PROFILES[lab]
    user_containers = _load_user_containers()
    user_key = f"user{user_id}_{lab}"

    if user_key in user_containers:
        container_name = user_containers[user_key]
        check = run(f"docker inspect -f '{{{{.State.Running}}}}' {container_name}")
        if "true" in check.stdout.lower():
            return True, "Lab already running for this user"

        run(f"docker rm -f {container_name}")
        del user_containers[user_key]
        _save_user_containers(user_containers)

    container_name = f"{service_name}-user{user_id}"
    
    build_result = run(f"{BASE_CMD} build {service_name}")
    if build_result.returncode != 0:
        return False, f"Failed to build image: {build_result.stderr[:200]}"
    
    image_inspect = run(f"docker images --format '{{{{.Repository}}}}:{{{{.Tag}}}}' --filter reference='*{service_name}*' | head -n 1")
    image_name = image_inspect.stdout.strip()
    
    if not image_name:
        return False, "Failed to find built image"

    shared_path = _get_host_shared_path()
    cmd = (
        f"docker run -d --rm"
        f" --name {container_name}"
        f" --network pygoat_my_network"
        f" --network-alias {service_name}"
        f" -v \"{shared_path}:/shared\""
        f" -e PYTHONPATH=/shared"
        f" {image_name}"
    )
    result = run(cmd)

    if result.returncode != 0:
        error_msg = result.stderr[:200] if result.stderr else "Unknown error"
        return False, f"Failed to start lab: {error_msg}"

    user_containers[user_key] = container_name
    _save_user_containers(user_containers)

    return True, "Lab started successfully"


def stop_lab(lab, user_id=None):
    """Stop lab container - user-specific"""
    if not RUNNING_IN_DOCKER:
        return _disabled()

    if lab not in LAB_PROFILES:
        return False, f"Unknown lab: {lab}"

    if user_id is None:
        r = run(f"{BASE_CMD} --profile {lab} stop")
        return (True, "Lab stopped") if r.returncode == 0 else (False, r.stderr[:200])

    user_containers = _load_user_containers()
    user_key = f"user{user_id}_{lab}"

    if user_key not in user_containers:
        return False, "No running lab found for this user"

    container_name = user_containers[user_key]

    result = run(f"docker stop {container_name}")

    if result.returncode == 0:
        del user_containers[user_key]
        _save_user_containers(user_containers)
        return True, "Lab stopped successfully"

    return False, f"Failed to stop lab: {result.stderr[:200]}"


def lab_status(lab, user_id=None):
    """Check if lab is running - user-specific"""
    if lab not in LAB_PROFILES:
        return False

    if user_id is None:
        r = run(f"docker inspect -f '{{{{.State.Running}}}}' {LAB_PROFILES[lab]}")
        return "true" in r.stdout.lower()

    user_containers = _load_user_containers()
    user_key = f"user{user_id}_{lab}"

    if user_key not in user_containers:
        return False

    container_name = user_containers[user_key]
    result = run(f"docker inspect -f '{{{{.State.Running}}}}' {container_name}")
    
    is_running = "true" in result.stdout.lower()
    
    # cleanup
    if not is_running and result.returncode != 0:
        del user_containers[user_key]
        _save_user_containers(user_containers)
    
    return is_running


def get_lab_url(lab, user_id=None):
    """Get the URL to access the lab (via nginx proxy)"""
    if lab not in LAB_PROFILES:
        return None
    
    return f"/labs/{lab}/"

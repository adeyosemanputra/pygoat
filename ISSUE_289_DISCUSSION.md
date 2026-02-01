# Issue #289: Hardcoded Ports in Dockerized Labs - Discussion Summary

## Issue Overview

**Problem:** The current PyGoat Docker setup uses hardcoded host ports (7001, 7002, ... 7017+) for each lab container, which creates several issues:

1. **Port Conflicts** - Hardcoded ports can conflict with services already running on developer machines
2. **Scalability Issues** - Manually tracking and assigning ports for each new lab increases error risk
3. **Environment Inflexibility** - Fixed ports prevent parallel deployments or running multiple lab sets
4. **Resource Waste** - All 17+ labs start even when testing only one or two labs

## Two Proposed Solutions

### Solution 1: PR #340 - Nginx Reverse Proxy with Docker Compose Profiles
**Author:** @caffeine-rohit

**Core Approach:**
- Uses **Nginx as a reverse proxy** (nginx:alpine container) as single entry point
- Only **port 8000 exposed** externally (all labs accessible via path routing)
- Labs controlled via **Docker Compose profiles** (start only what you need)
- Manual container management through Python wrapper (`lab_control.py`)
- All labs accessed via URL paths: `http://localhost:8000/labs/{lab-name}/`

**Technical Architecture:**
```
User → Port 8000 (Nginx) → Internal Docker Network
                           ├─ Django (pygoat-web:8000)
                           ├─ xss-lab (internal 5006)
                           ├─ ssrf-lab (internal 5000)
                           └─ ... (all labs, no host ports)
```

**Key Files:**
- `docker-compose.yml` - Core services (Django + Nginx)
- `docker-compose.labs.yml` - All 20 labs with profiles
- `nginx/nginx.conf` - Static routing configuration (manual updates)
- `challenge/lab_registry.py` - Lab metadata registry
- `challenge/lab_control.py` - Docker Compose wrapper for lab lifecycle

**Workflow:**
- Start specific labs: `docker-compose -f docker-compose.yml -f docker-compose.labs.yml --profile xss up -d`
- Start/stop labs via UI buttons in PyGoat dashboard
- Profile-based isolation (each lab runs independently)

**Changes:** 98 files changed, +2821/-884 lines

---

### Solution 2: PR #339 - Traefik with Dynamic Container Startup
**Author:** @samyak003

**Core Approach:**
- Uses **Traefik as reverse proxy** with automatic service discovery
- Labs started **dynamically at runtime** using Docker Python SDK
- Containers created **on-demand** when user accesses a lab
- Automatic routing via **Traefik labels** (no manual config updates)
- Labs accessible through Traefik's dynamic routing

**Technical Architecture:**
```
User → Traefik (dynamic routing) → Docker API
                                   ├─ Dynamically created labs
                                   ├─ Auto-discovery via labels
                                   └─ Runtime provisioning
```

**Key Features:**
- Dynamic container creation/destruction at runtime
- Docker Python SDK integration for container management
- Traefik automatically discovers new containers via labels
- No need to manually update routing configuration

**Workflow:**
- User clicks "Start Lab" → Docker SDK creates container → Traefik discovers it → Lab accessible
- User clicks "Stop Lab" → Docker SDK stops/removes container
- No pre-built compose profiles needed

**Changes:** 32 files changed, +821/-120 lines

---

## Core Architectural Difference

### PR #340 (Nginx + Profiles):
- **Static routing** - Routes defined in nginx.conf (manual updates when adding labs)
- **Pre-configured containers** - Labs defined in docker-compose files with profiles
- **Declarative approach** - Everything specified upfront in YAML files
- **Compose-based control** - Uses docker-compose commands wrapped in Python

### PR #339 (Traefik + Dynamic):
- **Dynamic routing** - Traefik auto-discovers containers via Docker labels
- **Runtime provisioning** - Containers created on-demand via Docker Python SDK
- **Imperative approach** - Labs created programmatically when needed
- **API-based control** - Direct Docker API calls for container lifecycle

---

## Context for Discussion

### Adding a New Lab

**With PR #340 (Nginx):**
1. Add service definition to `docker-compose.labs.yml` (~30 sec)
2. Add route to `nginx/nginx.conf` (~30 sec)
3. Add entry to `challenge/lab_registry.py` (~30 sec)
4. Restart Nginx: `docker restart nginx-proxy` (~5 sec)
**Total: ~3 minutes**

**With PR #339 (Traefik):**
1. Create lab Docker image with Traefik labels
2. Add lab config to Django (image name, build context)
3. Traefik auto-discovers when container starts
**Total: ~2-3 minutes** (no routing config, no proxy restart)

### Container Lifecycle

**PR #340:** 
- Labs pre-built, controlled via docker-compose profiles
- Faster startup (images already built)
- Manual cleanup required

**PR #339:**
- Labs built/pulled on first start
- True on-demand creation
- Automatic cleanup possible

### Maintainability

**PR #340:**
- More explicit configuration (easier to understand)
- Nginx config requires manual updates
- Clear separation between core services and labs

**PR #339:**
- Less explicit configuration (relies on Docker labels)
- Automatic routing (no manual updates)
- More complex runtime behavior

---

## Open Questions for Discussion

1. **Deployment preference:** Should labs be declaratively defined (Compose) or dynamically provisioned (SDK)?

2. **Routing complexity:** Is manual Nginx config maintenance acceptable, or is Traefik's auto-discovery worth the added abstraction?

3. **Resource management:** Should all labs be pre-built (fast startup) or built on-demand (less storage)?

4. **Developer experience:** Which approach is easier for new contributors to understand and extend?

5. **Local development:** How should these solutions work when running `python manage.py runserver` locally (without Docker)?

6. **Container lifecycle:** Should containers persist between uses or be truly ephemeral?

---

## Current Status

- **PR #340:** Has UI/UX implementation with start/stop buttons, sidebar status indicators, working redirect behavior
- **PR #339:** Cleaner initial approach per maintainer feedback, but some labs not opening correctly
- **Both PRs:** Have merge conflicts and need refinement

The maintainer (@RupakBiswas-2304) noted that PR #339's solution "seems cleaner" but both solutions need work to be production-ready.

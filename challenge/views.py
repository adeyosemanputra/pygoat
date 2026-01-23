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

# Create your views here.
client = docker.from_env()

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

def start_lab(request, lab_image_name):
    username = request.user.username
    safe_username = "".join(x for x in username if x.isalnum())
    safe_image = "".join(x for x in lab_image_name if x.isalnum() or x in "-_")  
    container_name = f"lab-{safe_username}-{safe_image}"
    domain = getattr(settings, 'LAB_DOMAIN', 'localhost')
    lab_url = f"http://{container_name}.{domain}"
    print(lab_url)
    
    
    try:
        labs_json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'labs.json')
        with open(labs_json_path, 'r') as f:
            labs_data = json.load(f)
        
        lab_config = None
        for lab in labs_data['labs']:
            if lab['name'] == safe_image:
                lab_config = lab
                break
        
        if not lab_config:
            return JsonResponse({'status': 'error', 'message': f'Lab configuration not found for {safe_image}'}, status=404)
        
        build_location = lab_config['build_location']
        lab_port = str(lab_config['port'])
        
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        return JsonResponse({'status': 'error', 'message': f'Error loading lab configuration: {str(e)}'}, status=500)
    
    try:
        try:
            container = client.containers.get(container_name)
            print(container)
            if container.status != 'running':
                container.start()
            return JsonResponse({'status': 'ready', 'url': lab_url})
        except docker.errors.NotFound:
            try:
                client.images.get(safe_image)
            except docker.errors.ImageNotFound:
                print(f"Building {safe_image}...") 
            try:
                client.images.build(path=f"./{build_location}/", tag=safe_image)
            except Exception as e:
                print(e)
                return JsonResponse({'status': 'error', 'message': f'Error building image: {str(e)}'}, status=500)

        
        labels = {
            "traefik.enable": "true",
            f"traefik.http.routers.{container_name}.rule": f"Host(`{container_name}.{domain}`)",
            f"traefik.http.services.{container_name}.loadbalancer.server.port": lab_port,
        }
        
        client.containers.run(
            image=safe_image,
            name=container_name,
            detach=True,
            labels=labels,
            network="my_network",
            mem_limit="512m",
        )

        return JsonResponse({'status': 'created', 'url': lab_url})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def stop_user_labs(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    
    username = request.user.username
    safe_username = "".join(x for x in username if x.isalnum())
    container_prefix = f"lab-{safe_username}-"
    
    try:
        containers = client.containers.list(all=True)
        user_containers = [c for c in containers if c.name.startswith(container_prefix)]
        print(user_containers)
        
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


def bopla_lab(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return redirect("http://localhost:7018")

def business_logic_lab(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return redirect("http://localhost:7019")

def security_headers_lab(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return redirect("http://localhost:7020")
    
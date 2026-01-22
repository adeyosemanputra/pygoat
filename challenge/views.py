from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
import subprocess
from .utility import get_free_port
from .models import Challenge, UserChallenge
import docker
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
                client.images.build(path=f"./challenge/labs/{safe_image}/", tag=safe_image)
                # client.images.build(path=f"./dockerized_labs/{safe_image}/", tag=safe_image)
            except e:
                print(e)


        
        labels = {
            "traefik.enable": "true",
            f"traefik.http.routers.{container_name}.rule": f"Host(`{container_name}.{domain}`)",
            f"traefik.http.services.{container_name}.loadbalancer.server.port": "5010",
        }
        
        client.containers.run(
            image=safe_image,
            name=container_name,
            detach=True,
            labels=labels,
            network="my_network",
            mem_limit="512m",
            remove=True
        )

        return JsonResponse({'status': 'created', 'url': lab_url})

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
    
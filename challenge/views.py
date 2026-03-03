from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import View
from .models import Challenge, UserChallenge
import docker
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def check_auth(request):
    print(f"Bouncer check for user: {request.user}") 
    if request.user.is_authenticated:
        return HttpResponse("OK", status=200)
    return HttpResponse("Unauthorized", status=401)

class DoItFast(View):
    def get(self, request, challenge):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            chal = Challenge.objects.get(name=challenge)
        except Challenge.DoesNotExist:
            return render(request, 'chal-not-found.html')

        try:
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
            return render(request, 'challenge.html', {'chal': chal, 'user_chal': user_chal})
        except UserChallenge.DoesNotExist:
            return render(request, 'challenge.html', {'chal': chal, 'user_chal': None})
    
    def post(self, request, challenge):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            chal = Challenge.objects.get(name=challenge)
        except Challenge.DoesNotExist:
            return render(request, 'chal-not-found.html')

        client = docker.from_env()
        lab_slug = chal.name.replace(" ", "-").lower()
        container_name = f"pygoat-{request.user.username}-{lab_slug}"

        labels = {
            "traefik.enable": "true",
            "traefik.http.routers." + lab_slug + ".rule": f"Host(`{lab_slug}.lvh.me`)",
            f"traefik.http.middlewares.{lab_slug}-auth.forwardauth.address": "http://pygoat-web-1:8000/challenge/auth-check/",
            f"traefik.http.middlewares.{lab_slug}-auth.forwardauth.trustForwardHeader": "true",
            f"traefik.http.routers.{lab_slug}.middlewares": f"{lab_slug}-auth",
            f"traefik.http.services.{lab_slug}.loadbalancer.server.port": "5050",
        }

        try:
            container = client.containers.get(container_name)
            container.remove(force=True)
        except docker.errors.NotFound:
            pass 

        try:
            container = client.containers.run(
                chal.docker_image,
                detach=True,
                name=container_name,
                network="pygoat_pygoat_net", 
                labels=labels
            )
            container_id = container.id
        except Exception as e:
            return JsonResponse({'message': f'Docker Error: {str(e)}', 'status': '500'})

        UserChallenge.objects.update_or_create(
            user=request.user, 
            challenge=chal,
            defaults={
                'container_id': container_id, 
                'is_live': True, 
                'port': 80  
            }
        )

        return JsonResponse({
            'message': 'success', 
            'status': '200', 
            'endpoint': f'http://{lab_slug}.lvh.me'
        })

    def delete(self, request, challenge):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            chal = Challenge.objects.get(name=challenge)
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
            
            client = docker.from_env()
            try:
                container = client.containers.get(user_chal.container_id)
                container.stop()
                container.remove()
            except docker.errors.NotFound:
                pass
            
            user_chal.is_live = False
            user_chal.save()
            return JsonResponse({'message': 'success', 'status': '200'})
        except Exception as e:
            return JsonResponse({'message': f'Delete failed: {str(e)}', 'status': '500'})
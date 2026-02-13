from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import subprocess
from .utility import get_free_port
from .models import Challenge, UserChallenge
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .lab_control import start_lab, stop_lab, lab_status
# Create your views here.


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
    
    #lab control views
@login_required
def control_lab(request, lab_name, action):
    """Start, stop, or check status of a lab"""
    
    # get user ID from authenticated user
    user_id = request.user.id
    
    if action == 'status':
        is_running = lab_status(lab_name, user_id)
        return JsonResponse({
            'success': True,
            'status': is_running,
            'message': ''
        })

    if settings.LAB_HYBRID_MODE and action in ['start', 'stop']:
        return JsonResponse({
            'success': False,
            'status': lab_status(lab_name, user_id),
            'message': 'Lab control is disabled in local development mode. Use docker-compose to manage labs.'
        })

    if action == 'start':
        success, msg = start_lab(lab_name, user_id)

    elif action == 'stop':
        success, msg = stop_lab(lab_name, user_id)

    else:
        return JsonResponse({'success': False, 'message': 'Invalid action'}, status=400)

    return JsonResponse({
        'success': success,
        'status': lab_status(lab_name, user_id),
        'message': msg
    })
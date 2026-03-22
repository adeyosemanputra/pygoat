from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import View

import subprocess
import hashlib
from .utility import get_free_port
from .models import Challenge, UserChallenge
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
        
        try:
            chal = Challenge.objects.get(name=challenge)
        except Exception as e:
            return render(request, 'chal-not-found.html')

        try:
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
            if user_chal.is_live:
                return JsonResponse({'message':'already running', 'status': '200', 'endpoint': f'http://localhost:{user_chal.port}'})
            user_chall_exists = True
        except:
            pass

        if user_chall_exists:
            restart_command = f"docker start {user_chal.container_id}"
            restart_process = subprocess.Popen(restart_command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            restart_process.communicate()

            if restart_process.returncode == 0:
                user_chal.is_live = True
                user_chal.save()
                return JsonResponse({'message': 'success', 'status': '200', 'endpoint': f'http://localhost:{user_chal.port}'})

        port = get_free_port(8001, 8100)
        if port is None:
            return JsonResponse({'message': 'failed', 'status': '500', 'endpoint': 'None'})

        command = f"docker run -d -p {port}:{chal.docker_port} {chal.docker_image}"
        process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if process.returncode != 0:
            return JsonResponse({'message': 'failed', 'status': '500', 'endpoint': 'None'})
        container_id = output.decode('utf-8').strip()

        if user_chall_exists:
            user_chal.container_id = container_id
            user_chal.port = port
            user_chal.is_live = True
            user_chal.save()
        else:
            user_chal = UserChallenge(user=request.user, challenge=chal, container_id=container_id, port=port)
            user_chal.save()

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
        process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if process.returncode != 0:
            return JsonResponse({'message': 'failed', 'status': '500', 'endpoint': 'None'})
        return JsonResponse({'message': 'success', 'status': '200'})
    
    def put(self, request, challenge):
        if not request.user.is_authenticated:
            return JsonResponse({'message': 'unauthorized', 'status': '401'})
        
        try:
            chal = Challenge.objects.get(name=challenge)
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
        except Exception as e:
            return JsonResponse({'message': 'challenge not found', 'status': '404'})

        try:
            import json
            data = json.loads(request.body)
            submitted_flag = data.get('flag', '')
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'message': 'invalid request body', 'status': '400'})

        if not submitted_flag:
            return JsonResponse({'message': 'no flag provided', 'status': '400'})

        hashed_submitted = "hashed_" + hashlib.sha256(submitted_flag.encode('utf-8')).hexdigest()

        if hashed_submitted == chal.flag:
            user_chal.is_solved = True
            user_chal.save()
            return JsonResponse({'message': 'correct', 'status': '200', 'points': chal.point})
        else:
            user_chal.no_of_attempt += 1
            user_chal.save()
            return JsonResponse({'message': 'incorrect', 'status': '200'})

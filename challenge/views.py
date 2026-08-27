import hashlib
import json
import subprocess
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
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
    
    def put(self, request, challenge):
        if not request.user.is_authenticated:
            return JsonResponse({'message': 'Authentication required', 'status': '401'}, status=401)

        try:
            chal = Challenge.objects.get(name=challenge)
        except Challenge.DoesNotExist:
            return JsonResponse({'message': 'Challenge not found', 'status': '404'}, status=404)

        try:
            data = json.loads(request.body.decode('utf-8'))
            submitted_flag = data.get('flag', '').strip()
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            return JsonResponse({'message': 'Invalid JSON body', 'status': '400'}, status=400)

        if not submitted_flag:
            return JsonResponse({'message': 'Flag is required', 'status': '400'}, status=400)

        user_chal, _ = UserChallenge.objects.get_or_create(
            user=request.user,
            challenge=chal,
            defaults={'container_id': '', 'port': 0}
        )

        user_chal.no_of_attempt += 1

        # Challenge.flag is stored as 'hashed_' + sha256 hex digest
        expected_hashed_flag = "hashed_" + hashlib.sha256(submitted_flag.encode('utf-8')).hexdigest()

        if chal.flag == expected_hashed_flag:
            user_chal.is_solved = True
            user_chal.save()
            return JsonResponse({
                'message': 'Correct flag! Challenge completed.',
                'status': '200',
                'is_solved': True,
                'attempts': user_chal.no_of_attempt
            }, status=200)
        else:
            user_chal.save()
            return JsonResponse({
                'message': 'Incorrect flag. Try again.',
                'status': '400',
                'is_solved': False,
                'attempts': user_chal.no_of_attempt
            }, status=400)
    
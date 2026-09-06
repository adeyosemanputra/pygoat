from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
import subprocess
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

            # Container reuse logic
            if user_chall_exists and user_chal.container_id:
                # Check if the existing container is present on host
                check_cmd = f"docker inspect --format='((.State.Running))' {user_chal.container_id}"
                process = subprocess.Popen(check_cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, error = process.communicate()
                
                # If inspect succeeded, start the stopped container
                if process.returncode == 0:
                    start_cmd = f"docker start {user_chal.container_id}"
                    start_proc = subprocess.Popen(start_cmd.split(" "), stdout=subprocess.PIPE)
                    start_proc.communicate()

                    user_chal.is_live = True
                    user_chal.save()
                    return JsonResponse({'message': 'success', 'status': '200', 'endpoint': f'http://localhost:{user_chal.port}'})

            # Fallback: Create new container if reuse isn't possible
            port = get_free_port(8000, 8100)
            if port is None:
                return JsonResponse({'message': 'failed', 'status': '500', 'endpoint': 'None'})
            
            command = f"docker run -d -p {port}:{chal.docker_port} {chal.docker_image}"
            process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
            output, error = process.communicate()
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
        process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
        output, error = process.communicate()
        return JsonResponse({'message': 'success', 'status': '200'})
    
    def put(self, request, challange):
        # TODO : implement flag checking
        return "not implemented"
    
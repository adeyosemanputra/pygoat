from django.http import JsonResponse
from django.shortcuts import redirect
from introduction.playground.ssrf import main
from django.contrib.auth import login,authenticate
from .utility import *
from django.views.decorators.csrf import csrf_exempt
import time
# steps --> 
# 1. covert input code to corrosponding code and write in file
# 2. extract inputs form 2nd code 
# 3. Run the code 
# 4. get the result
@csrf_exempt
def ssrf_code_checker(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            python_code = request.POST['python_code']
            html_code = request.POST['html_code']
            if not (ssrf_code_converter(python_code)):
                return JsonResponse({"status": "error", "message": "Invalid code"})
            test_bench1 = ssrf_html_input_extractor(html_code)
            
            if (len(test_bench1) >4):
                return JsonResponse({'message':'too many inputs in Html\n Try again'},status = 400)
            test_bench2 = ['secret.txt']
            correct_output1 = [{"blog": "blog1-passed"}, {"blog": "blog2-passed"}, {"blog": "blog3-passed"}, {"blog": "blog4-passed"}]
            outputs = []
            for inputs in test_bench1:
                outputs.append(main.ssrf_lab(inputs))
            if outputs == correct_output1:
                outputs = []
            else:
                return JsonResponse({'message':'Testbench failed, Code is not working\n Try again'},status = 200)

            correct_output2 = [{"blog": "No blog found"}]
            for inputs in test_bench2:
                outputs.append(main.ssrf_lab(inputs))
            if outputs == correct_output2:
                return JsonResponse({'message':'Congratulation, you have written a secure code.', 'passed':1}, status = 200)
            
            return JsonResponse({'message':'Test bench passed but the code is not secure'}, status = 200,safe = False)
        else:
            return JsonResponse({'message':'method not allowed'},status = 405)
    else:
        return JsonResponse({'message':'UnAuthenticated User'},status = 401)
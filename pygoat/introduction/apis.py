from django.http import JsonResponse
from django.shortcuts import redirect
from introduction.playground.ssrf import main
from django.contrib.auth import login,authenticate
from .utility import *
from django.views.decorators.csrf import csrf_exempt




# input = 'templates/Lab/ssrf/blogs/blog1.txt'
# result = ssrf_lab(input)
# print(result == {'blog': '201'})

# steps --> 
# 1. covert input code to corrosponding code and write in file
# 2. extract inputs form 2nd code 
# 3. Run the code 
# 4. get the result

# def ssrf_code_checker(request):
#     if request.user.is_authenticated:
#         if request.method == 'POST':
#             python_code = request.POST['python_code']
#             html_code = request.POST['html_code']
#             ssrf_code_converter(python_code)
#             test_bench = ssrf_html_input_extractor(html_code)
#             test_bench += ['secret.txt']
#             outputs = []
#             for inputs in test_bench:
#                 outputs.append(main.ssrf_lab(inputs))
#             return JsonResponse(outputs, status = 200)
#         else:
#             return JsonResponse({'message':'method not allowed'},status = 405)
#     else:
#         return redirect('login')
@csrf_exempt
def ssrf_code_checker(request):
    if request.method == 'POST':
        python_code = request.POST['python_code']
        html_code = request.POST['html_code']
        ssrf_code_converter(python_code)
        test_bench = ssrf_html_input_extractor(html_code)
        test_bench += ['secret.txt']
        outputs = []
        for inputs in test_bench:
            outputs.append(main.ssrf_lab(inputs))
        correct_output = [{"blog": "blog1-passed"}, {"blog": "blog2-passed"}, {"blog": "blog3-passed"}, {"blog": "blog4-passed"}, {"blog": "No blog found"}]
        response = ''
        if outputs == correct_output:
            response = 'passed'
        else:
            response = 'failed'
        return JsonResponse({'message':response}, status = 200,safe = False)
    else:
        return JsonResponse({'message':'method not allowed'},status = 405)
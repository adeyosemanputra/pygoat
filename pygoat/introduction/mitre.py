from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from .views import authentication_decorator


## Mitre top1 | CWE:787

@authentication_decorator
def mitre_top1(request):
    if request.method == 'GET':
        return render(request, 'mitre/mitre_top1.html')

@authentication_decorator
def mitre_top2(request):
    if request.method == 'GET':
        return render(request, 'mitre/mitre_top2.html')
from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    
    return render(request,'introduction/home.html')
def xss(request):
    return render(request,"Lab/XSS/xss.html")
def xssL(request):
    q=request.GET.get('q','');
    return render(request, 'Lab/XSS/xssL.html',{'query':q})

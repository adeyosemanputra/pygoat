from django.shortcuts import render
from django.template import loader

def home(request):
    
    return render(request,'introduction/home.html')

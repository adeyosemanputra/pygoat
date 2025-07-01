import base64
import pickle
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from ..utils import TestUser, pickled_user, encoded_user

# Insecure Deserialization Views
def insec_des(request):
    return render(request, 'insec_des.html')

@require_http_methods(['GET', 'POST'])
def insec_des_lab(request):
    context = {}
    
    if request.method == 'POST':
        try:
            # Insecure deserialization vulnerability
            data = request.POST.get('data', '')
            if data:
                # Decode the base64 data
                decoded = base64.b64decode(data)
                # Unsafe deserialization
                user = pickle.loads(decoded)
                context['result'] = f"Deserialized user with admin={getattr(user, 'admin', 'N/A')}"
        except Exception as e:
            context['error'] = str(e)
    
    # Provide the encoded user for the form
    context['encoded_user'] = encoded_user.decode()
    return render(request, 'insec_des_lab.html', context)

def insec_desgine(request):
    return render(request, 'insec_desgine.html')

def insec_desgine_lab(request):
    context = {}
    
    if request.method == 'POST':
        try:
            # Another example of insecure deserialization
            data = request.POST.get('data', '')
            if data:
                # Unsafe deserialization without proper validation
                obj = pickle.loads(base64.b64decode(data))
                context['result'] = f"Deserialized object: {str(obj)[:100]}"
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'insec_desgine_lab.html', context)

import requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# SSRF (Server-Side Request Forgery) Views
def ssrf(request):
    return render(request, 'ssrf.html')

@require_http_methods(['GET', 'POST'])
def ssrf_lab(request):
    content = None
    if request.method == 'POST':
        url = request.POST.get('url', '')
        if url:
            try:
                # Vulnerable to SSRF - no validation of user-supplied URL
                response = requests.get(url, timeout=5)
                content = response.text
            except Exception as e:
                content = f"Error: {str(e)}"
    
    return render(request, 'ssrf_lab.html', {'content': content})

def ssrf_discussion(request):
    return render(request, 'ssrf_discussion.html')

def ssrf_target(request):
    # This is a target endpoint for SSRF testing
    return JsonResponse({
        'status': 'success',
        'message': 'You have accessed an internal API endpoint',
        'internal_data': 'Sensitive internal information here'
    })

def ssrf_lab2(request):
    # Another SSRF example with different context
    content = None
    if request.method == 'POST':
        image_url = request.POST.get('image_url', '')
        if image_url:
            try:
                # Vulnerable to SSRF - no URL validation
                response = requests.get(image_url, timeout=5)
                if 'image' in response.headers.get('Content-Type', ''):
                    content = f"Image loaded from {image_url}"
                else:
                    content = f"The URL does not point to a valid image"
            except Exception as e:
                content = f"Error loading image: {str(e)}"
    
    return render(request, 'ssrf_lab2.html', {'content': content})

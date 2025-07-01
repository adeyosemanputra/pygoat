import requests
import logging
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

# Configure logger
logger = logging.getLogger(__name__)

# A10: Server-Side Request Forgery (SSRF) Views

def a10(request):
    """View for A10: Server-Side Request Forgery introduction."""
    return render(request, 'a10.html')

@require_http_methods(['GET', 'POST'])
def a10_lab(request):
    """Lab for demonstrating SSRF vulnerabilities."""
    context = {}
    
    if request.method == 'POST':
        url = request.POST.get('url', '')
        if url:
            try:
                # Insecure: Making requests to user-supplied URLs without validation
                response = requests.get(url, timeout=5, verify=False)
                context['content'] = response.text
                context['status_code'] = response.status_code
                context['headers'] = dict(response.headers)
                
                # Log the request (in a real app, this should be more detailed)
                logger.info(f"SSRF request to {url} - Status: {response.status_code}")
                
            except requests.exceptions.RequestException as e:
                context['error'] = f"Error: {str(e)}"
                logger.error(f"SSRF request failed to {url}: {str(e)}")
    
    return render(request, 'a10_lab.html', context)

def debug(request):
    """Debug endpoint that's vulnerable to SSRF."""
    # Insecure: This endpoint is vulnerable to SSRF and information disclosure
    url = request.GET.get('url', '')
    if url:
        try:
            response = requests.get(url, timeout=5, verify=False)
            return JsonResponse({
                'status': 'success',
                'url': url,
                'status_code': response.status_code,
                'content': response.text[:1000],  # Limit response size
                'headers': dict(response.headers)
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'error': 'No URL provided'
    }, status=400)

@require_http_methods(['GET', 'POST'])
def a10_lab2(request):
    """Lab 2 for demonstrating more advanced SSRF vulnerabilities."""
    context = {}
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'fetch':
            url = request.POST.get('url', '')
            if url:
                try:
                    # Insecure: Making requests to user-supplied URLs without proper validation
                    # and with disabled SSL verification
                    response = requests.get(
                        url, 
                        timeout=5, 
                        verify=False,  # Disabling SSL verification
                        headers={
                            'User-Agent': 'VulnerableApp/1.0',
                            'X-Forwarded-For': request.META.get('REMOTE_ADDR', 'unknown')
                        }
                    )
                    
                    context.update({
                        'url': url,
                        'status_code': response.status_code,
                        'content': response.text[:5000],  # Limit response size
                        'headers': dict(response.headers)
                    })
                    
                    # Log the request (in a real app, this should be more detailed)
                    logger.info(f"SSRF Lab2 request to {url} - Status: {response.status_code}")
                    
                except requests.exceptions.RequestException as e:
                    context['error'] = f"Error: {str(e)}"
                    logger.error(f"SSRF Lab2 request failed to {url}: {str(e)}")
    
    return render(request, 'a10_lab2.html', context)

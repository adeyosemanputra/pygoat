import os
import subprocess
import logging
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse

# Configure logger
logger = logging.getLogger(__name__)

# A6: Vulnerable and Outdated Components Views

def a6(request):
    """View for A6: Vulnerable and Outdated Components introduction."""
    return render(request, 'a6.html')

@require_http_methods(['GET', 'POST'])
def a6_lab(request):
    """Lab for demonstrating vulnerabilities in outdated components."""
    context = {}
    
    if request.method == 'POST':
        try:
            # Insecure: Using outdated/known vulnerable components
            import django
            import requests
            import urllib3
            
            # Get version information for various components
            context['versions'] = {
                'django': django.get_version(),
                'requests': requests.__version__,
                'urllib3': urllib3.__version__,
                'python': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
            }
            
            # Check for known vulnerabilities (simplified example)
            context['vulnerabilities'] = []
            
            # Example: Check for known vulnerable versions
            if django.VERSION < (3, 2, 0):
                context['vulnerabilities'].append({
                    'component': 'Django',
                    'version': django.get_version(),
                    'severity': 'High',
                    'description': 'Outdated Django version with known security vulnerabilities',
                    'cve': 'CVE-2021-33203, CVE-2021-33571, CVE-2021-45452'
                })
                
            if urllib3.__version__ < '1.26.0':
                context['vulnerabilities'].append({
                    'component': 'urllib3',
                    'version': urllib3.__version__,
                    'severity': 'Medium',
                    'description': 'Outdated urllib3 version with potential security issues',
                    'cve': 'CVE-2021-33503, CVE-2021-33502'
                })
                
            # Add more vulnerability checks as needed
            
        except Exception as e:
            context['error'] = f"Error checking components: {str(e)}"
    
    return render(request, 'a6_lab.html', context)

def package_info(request, package_name):
    """Insecure endpoint that provides package information."""
    try:
        # Insecure: Using subprocess with user input
        result = subprocess.run(
            ['pip', 'show', package_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return HttpResponse(
                f"<pre>{result.stdout}</pre>",
                content_type='text/html'
            )
        else:
            return HttpResponse(
                f"<pre>Error: {result.stderr}</pre>",
                content_type='text/html',
                status=400
            )
            
    except Exception as e:
        return HttpResponse(
            f"<pre>Error: {str(e)}</pre>",
            content_type='text/html',
            status=500
        )

@require_http_methods(['GET', 'POST'])
def a6_lab2(request):
    """Lab 2 for demonstrating more component-related vulnerabilities."""
    context = {}
    
    if request.method == 'POST':
        try:
            # Insecure: Loading and using arbitrary modules
            module_name = request.POST.get('module_name', '')
            
            if module_name:
                try:
                    # WARNING: This is intentionally vulnerable code - DO NOT use in production!
                    module = __import__(module_name)
                    context['module_info'] = {
                        'name': module_name,
                        'version': getattr(module, '__version__', 'Not available'),
                        'file': getattr(module, '__file__', 'Not available'),
                        'doc': getattr(module, '__doc__', 'No documentation')
                    }
                except Exception as e:
                    context['error'] = f"Error loading module: {str(e)}"
            
            # Check for outdated packages
            outdated = request.POST.get('check_outdated', '')
            if outdated:
                try:
                    # Insecure: Running pip list --outdated with shell=True
                    result = subprocess.run(
                        'pip list --outdated',
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        context['outdated_packages'] = result.stdout
                    else:
                        context['error'] = f"Error checking outdated packages: {result.stderr}"
                        
                except Exception as e:
                    context['error'] = f"Error checking outdated packages: {str(e)}"
            
        except Exception as e:
            context['error'] = f"Error processing request: {str(e)}"
    
    return render(request, 'a6_lab2.html', context)

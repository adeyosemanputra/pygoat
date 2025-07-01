import os
import json
import logging
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_exempt

# Configure logger
logger = logging.getLogger(__name__)

# A5: Security Misconfiguration Views

def a5(request):
    """View for A5: Security Misconfiguration introduction."""
    return render(request, 'a5.html')

@require_http_methods(['GET', 'POST'])
def a5_lab(request):
    """Lab for demonstrating security misconfigurations."""
    context = {}
    
    if request.method == 'POST':
        try:
            # Insecure: Exposing sensitive configuration information
            config = {
                'debug': settings.DEBUG,
                'secret_key_exposed': settings.SECRET_KEY[:8] + '...' if settings.SECRET_KEY else 'Not set',
                'allowed_hosts': settings.ALLOWED_HOSTS,
                'database': {
                    'engine': settings.DATABASES['default']['ENGINE'],
                    'name': settings.DATABASES['default']['NAME'],
                    'user': settings.DATABASES['default']['USER'],
                    # Insecure: Exposing database password (truncated for demo)
                    'password': settings.DATABASES['default']['PASSWORD'][:2] + '...' if settings.DATABASES['default']['PASSWORD'] else 'Not set',
                },
                'installed_apps': settings.INSTALLED_APPS,
                'middleware': settings.MIDDLEWARE,
                'static_url': settings.STATIC_URL,
                'static_root': settings.STATIC_ROOT,
                'media_url': settings.MEDIA_URL,
                'media_root': settings.MEDIA_ROOT,
            }
            
            context['config'] = json.dumps(config, indent=2)
            
        except Exception as e:
            context['error'] = f"Error retrieving configuration: {str(e)}"
    
    return render(request, 'a5_lab.html', context)

@xframe_options_exempt
def debug_info(request):
    """Insecure debug information endpoint."""
    # Insecure: Exposing sensitive debug information
    import platform
    import sys
    
    info = {
        'system': {
            'platform': platform.platform(),
            'python_version': sys.version,
            'django_version': None,
            'installed_packages': []
        },
        'environment': dict(os.environ),
        'request': {
            'method': request.method,
            'path': request.path,
            'headers': dict(request.headers),
            'GET': dict(request.GET),
            'POST': dict(request.POST) if request.method == 'POST' else {}
        }
    }
    
    # Try to get Django version
    try:
        import django
        info['system']['django_version'] = django.get_version()
    except ImportError:
        pass
    
    # Try to get installed packages (insecure)
    try:
        import pkg_resources
        info['system']['installed_packages'] = [
            f"{pkg.key}=={pkg.version}" 
            for pkg in pkg_resources.working_set
        ]
    except Exception:
        pass
    
    return JsonResponse(info)

@require_http_methods(['GET', 'POST'])
def a5_lab2(request):
    """Lab 2 for demonstrating more security misconfigurations."""
    context = {}
    
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            
            if action == 'list_dir':
                # Insecure: Directory listing without proper access controls
                path = request.POST.get('path', '.')
                abs_path = os.path.abspath(os.path.join(settings.BASE_DIR, path))
                
                # Very basic path traversal check (inadequate in production)
                if not abs_path.startswith(settings.BASE_DIR):
                    context['error'] = "Access denied"
                else:
                    try:
                        context['listing'] = {
                            'path': abs_path,
                            'exists': os.path.exists(abs_path),
                            'is_file': os.path.isfile(abs_path) if os.path.exists(abs_path) else False,
                            'is_dir': os.path.isdir(abs_path) if os.path.exists(abs_path) else False,
                            'contents': []
                        }
                        
                        if os.path.isdir(abs_path):
                            for item in os.listdir(abs_path):
                                item_path = os.path.join(abs_path, item)
                                try:
                                    stat = os.stat(item_path)
                                    context['listing']['contents'].append({
                                        'name': item,
                                        'is_file': os.path.isfile(item_path),
                                        'is_dir': os.path.isdir(item_path),
                                        'size': stat.st_size,
                                        'modified': stat.st_mtime,
                                        'mode': oct(stat.st_mode)[-3:],
                                        'owner': stat.st_uid,
                                        'group': stat.st_gid
                                    })
                                except Exception as e:
                                    context['listing']['contents'].append({
                                        'name': item,
                                        'error': str(e)
                                    })
                                    
                    except Exception as e:
                        context['error'] = f"Error accessing path: {str(e)}"
            
            elif action == 'read_file':
                # Insecure: File reading without proper access controls
                file_path = request.POST.get('file_path')
                if file_path:
                    abs_path = os.path.abspath(os.path.join(settings.BASE_DIR, file_path))
                    
                    # Very basic path traversal check (inadequate in production)
                    if not abs_path.startswith(settings.BASE_DIR):
                        context['error'] = "Access denied"
                    else:
                        try:
                            with open(abs_path, 'r') as f:
                                context['file_content'] = f.read()
                                context['file_path'] = abs_path
                        except Exception as e:
                            context['error'] = f"Error reading file: {str(e)}"
            
        except Exception as e:
            context['error'] = f"Error processing request: {str(e)}"
    
    return render(request, 'a5_lab2.html', context)

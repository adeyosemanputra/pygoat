from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from ...models import Blogs, info, login

# A1: Broken Access Control Views

def ba(request):
    """View for Broken Access Control introduction."""
    return render(request, 'ba.html')

@login_required
def ba_lab(request):
    """Lab for demonstrating broken access control vulnerabilities."""
    if request.method == "POST":
        try:
            blog_id = int(request.POST.get('blog_id'))
            blog = Blogs.objects.get(id=blog_id)
            return render(request, 'ba_lab.html', {'blog': blog})
        except (ValueError, Blogs.DoesNotExist):
            return render(request, 'ba_lab.html', {'error': 'Blog not found'})
    
    return render(request, 'ba_lab.html')

@csrf_exempt
def a1_broken_access(request):
    """View for A1: Broken Access Control introduction (2021 version)."""
    return render(request, 'a1_broken_access.html')

@login_required
def a1_broken_access_lab_1(request):
    """Lab 1 for demonstrating IDOR (Insecure Direct Object Reference)."""
    if request.method == 'POST':
        try:
            user_id = int(request.POST.get('user_id', 0))
            user = login.objects.get(id=user_id)
            return render(request, 'a1_broken_access_lab_1.html', {
                'user': user,
                'user_id': user_id
            })
        except (ValueError, login.DoesNotExist):
            return render(request, 'a1_broken_access_lab_1.html', {
                'error': 'User not found'
            })
    
    return render(request, 'a1_broken_access_lab_1.html')

@login_required
def a1_broken_access_lab_2(request):
    """Lab 2 for demonstrating privilege escalation."""
    if request.method == 'POST':
        try:
            user_id = int(request.POST.get('user_id', 0))
            user = login.objects.get(id=user_id)
            
            # Insecure: No authorization check
            if 'make_admin' in request.POST:
                user.is_admin = True
                user.save()
                return render(request, 'a1_broken_access_lab_2.html', {
                    'message': f'User {user.username} is now an admin!',
                    'user': user
                })
            
            return render(request, 'a1_broken_access_lab_2.html', {
                'user': user
            })
            
        except (ValueError, login.DoesNotExist):
            return render(request, 'a1_broken_access_lab_2.html', {
                'error': 'User not found'
            })
    
    return render(request, 'a1_broken_access_lab_2.html')

@login_required
def a1_broken_access_lab_3(request):
    """Lab 3 for demonstrating path traversal."""
    return render(request, 'a1_broken_access_lab_3.html')

def a1_broken_access_lab3_secret(request):
    """Secret endpoint for A1 Lab 3 (vulnerable to path traversal)."""
    import os
    from django.http import HttpResponse, HttpResponseForbidden
    
    # Insecure: Direct file access without proper validation
    filename = request.GET.get('file', 'public.txt')
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'static', 'secret', filename)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/plain')
    except (IOError, OSError):
        return HttpResponseForbidden('Access denied')

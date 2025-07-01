from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# XSS Vulnerability Views
def xss(request):
    return render(request, 'xss.html')

@require_http_methods(['GET', 'POST'])
def xss_lab(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        return render(request, 'xss_lab.html', {'name': name})
    return render(request, 'xss_lab.html')

def xss_lab2(request):
    if request.method == 'POST':
        comment = request.POST.get('comment', '')
        return render(request, 'xss_lab2.html', {'comment': comment})
    return render(request, 'xss_lab2.html')

def xss_lab3(request):
    if request.method == 'POST':
        search = request.POST.get('search', '')
        # Simulate search results
        results = [f"Result for {search}"] if search else []
        return render(request, 'xss_lab3.html', {'search': search, 'results': results})
    return render(request, 'xss_lab3.html')

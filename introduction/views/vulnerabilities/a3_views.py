import os
import subprocess
import logging
import json
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.db.utils import ProgrammingError

# Configure logger
logger = logging.getLogger(__name__)

# A3: Injection Views

def a3(request):
    """View for A3: Injection introduction."""
    return render(request, 'a3.html')

@require_http_methods(['GET', 'POST'])
def a3_lab(request):
    """Lab for demonstrating injection vulnerabilities."""
    context = {}
    
    if request.method == 'POST':
        try:
            # Get user input
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            
            # Insecure: Direct string concatenation in SQL query
            query = f"SELECT * FROM auth_user WHERE username = '{username}' AND password = '{password}'"
            
            # Execute the query (insecure)
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                results = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
                
                if results:
                    context['message'] = "Login successful!"
                    context['user'] = results[0]
                else:
                    context['error'] = "Invalid username or password"
                    
        except ProgrammingError as e:
            context['error'] = f"Database error: {str(e)}"
        except Exception as e:
            context['error'] = f"Error: {str(e)}"
    
    return render(request, 'a3_lab.html', context)

def command_injection(request):
    """Vulnerable command injection endpoint."""
    if request.method == 'GET':
        host = request.GET.get('host', '127.0.0.1')
        
        try:
            # Insecure: Directly using user input in a shell command
            cmd = f"ping -c 4 {host}"
            
            # Insecure: Using shell=True with user input
            result = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0:
                return HttpResponse(
                    f"<pre>Command: {cmd}\n\n{result.stdout}</pre>",
                    content_type='text/html'
                )
            else:
                return HttpResponse(
                    f"<pre>Error executing command: {cmd}\n\n{result.stderr}</pre>",
                    content_type='text/html',
                    status=400
                )
                
        except Exception as e:
            return HttpResponse(
                f"<pre>Error: {str(e)}</pre>",
                content_type='text/html',
                status=500
            )
    
    return HttpResponse(
        "<pre>Usage: /a3/command?host=example.com</pre>",
        content_type='text/html'
    )

@require_http_methods(['GET', 'POST'])
def a3_lab2(request):
    """Lab 2 for demonstrating more injection vulnerabilities."""
    context = {}
    
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            
            if action == 'search':
                # Insecure: Direct string concatenation in SQL query
                search_term = request.POST.get('search_term', '')
                
                # Insecure: Using raw SQL with string formatting
                query = f"""
                    SELECT id, username, email, is_superuser 
                    FROM auth_user 
                    WHERE username LIKE '%{search_term}%' 
                    OR email LIKE '%{search_term}%'
                """
                
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    columns = [col[0] for col in cursor.description]
                    context['results'] = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]
            
            elif action == 'file_read':
                # Insecure: Path traversal vulnerability
                filename = request.POST.get('filename', '')
                
                if filename:
                    try:
                        # Insecure: No proper path validation
                        with open(filename, 'r') as f:
                            context['file_content'] = f.read()
                            context['filename'] = filename
                    except Exception as e:
                        context['error'] = f"Error reading file: {str(e)}"
            
            elif action == 'eval':
                # Insecure: Direct evaluation of user input
                expression = request.POST.get('expression', '')
                
                if expression:
                    try:
                        # WARNING: This is extremely dangerous!
                        result = eval(expression, {'__builtins__': None}, {})
                        context['eval_result'] = str(result)
                    except Exception as e:
                        context['eval_error'] = str(e)
            
        except Exception as e:
            context['error'] = f"Error processing request: {str(e)}"
    
    return render(request, 'a3_lab2.html', context)

def xml_processor(request):
    """Vulnerable XML processor endpoint."""
    if request.method == 'POST':
        try:
            import xml.etree.ElementTree as ET
            from io import StringIO
            
            # Get XML data from request
            xml_data = request.body.decode('utf-8')
            
            # Insecure: Parsing XML with external entity processing enabled
            # This is vulnerable to XXE (XML External Entity) attacks
            parser = ET.XMLParser()
            tree = ET.parse(StringIO(xml_data), parser=parser)
            root = tree.getroot()
            
            # Process the XML (example: extract data)
            data = {}
            for child in root:
                data[child.tag] = child.text
            
            return JsonResponse({
                'status': 'success',
                'data': data
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST requests are allowed'
    }, status=405)

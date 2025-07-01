import os
import hashlib
import hmac
import json
import logging
from datetime import datetime
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.conf import settings

# Configure logger
logger = logging.getLogger(__name__)

# A8: Software and Data Integrity Failures Views

def a8(request):
    """View for A8: Software and Data Integrity Failures introduction."""
    return render(request, 'a8.html')

@require_http_methods(['GET', 'POST'])
def a8_lab(request):
    """Lab for demonstrating software and data integrity failures."""
    context = {}
    
    if request.method == 'POST':
        try:
            # Insecure: Accepting and processing untrusted data
            data = request.POST.get('data', '')
            
            # Insecure: Using eval to process data (dangerous!)
            if data:
                try:
                    # WARNING: This is intentionally vulnerable code - DO NOT use in production!
                    result = eval(data)
                    context['result'] = str(result)
                except Exception as e:
                    context['error'] = f"Error evaluating data: {str(e)}"
            
            # Insecure: Storing data without validation
            filename = request.POST.get('filename', 'data.txt')
            file_content = request.POST.get('file_content', '')
            
            if file_content:
                try:
                    # Insecure: Writing file without proper path validation
                    with open(f'/tmp/{filename}', 'w') as f:
                        f.write(file_content)
                    context['message'] = f'File {filename} saved successfully!'
                except Exception as e:
                    context['error'] = f"Error saving file: {str(e)}"
            
        except Exception as e:
            context['error'] = f"Error processing request: {str(e)}"
    
    return render(request, 'a8_lab.html', context)

def verify_signature(data, signature):
    """Insecure signature verification (vulnerable to timing attacks)."""
    # Insecure: Using simple string comparison (vulnerable to timing attacks)
    expected_signature = hashlib.sha256(
        (data + settings.SECRET_KEY).encode()
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

@require_http_methods(['POST'])
def webhook(request):
    """Insecure webhook endpoint that processes signed data."""
    try:
        # Get the signature from headers
        signature = request.headers.get('X-Signature', '')
        
        # Get the raw request body
        data = request.body.decode('utf-8')
        
        # Verify the signature (insecure implementation)
        if not verify_signature(data, signature):
            return JsonResponse({'error': 'Invalid signature'}, status=403)
        
        # Process the data (insecurely)
        payload = json.loads(data)
        
        # Insecure: Directly using data from the payload without proper validation
        action = payload.get('action')
        
        if action == 'deploy':
            # Insecure: Directly executing commands from the payload
            command = payload.get('command', '')
            if command:
                # WARNING: This is intentionally vulnerable code - DO NOT use in production!
                os.system(command)
                return JsonResponse({'status': 'success', 'message': 'Command executed'})
            
        elif action == 'update':
            # Insecure: Updating configuration without proper validation
            config = payload.get('config', {})
            # In a real app, this would update the configuration
            return JsonResponse({'status': 'success', 'message': 'Configuration updated'})
            
        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def a8_lab2(request):
    """Lab 2 for demonstrating more software and data integrity failures."""
    context = {}
    
    if request.method == 'POST':
        try:
            # Insecure: Accepting and deserializing untrusted data
            serialized_data = request.POST.get('serialized_data', '')
            
            if serialized_data:
                # Insecure: Using pickle to deserialize untrusted data (dangerous!)
                import pickle
                import base64
                
                try:
                    # WARNING: This is intentionally vulnerable code - DO NOT use in production!
                    decoded_data = base64.b64decode(serialized_data)
                    deserialized = pickle.loads(decoded_data)
                    context['result'] = f"Deserialized data: {str(deserialized)}"
                except Exception as e:
                    context['error'] = f"Error deserializing data: {str(e)}"
            
            # Insecure: Accepting and processing untrusted YAML
            yaml_data = request.POST.get('yaml_data', '')
            if yaml_data:
                try:
                    # WARNING: Using yaml.load() with untrusted data is dangerous!
                    import yaml
                    parsed_yaml = yaml.load(yaml_data, Loader=yaml.Loader)
                    context['yaml_result'] = parsed_yaml
                except Exception as e:
                    context['yaml_error'] = f"Error parsing YAML: {str(e)}"
            
        except Exception as e:
            context['error'] = f"Error processing request: {str(e)}"
    
    return render(request, 'a8_lab2.html', context)

import base64
import hashlib
import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# Cryptographic Failure Views
def crypto_failure(request):
    return render(request, 'crypto_failure.html')

@require_http_methods(['GET', 'POST'])
def crypto_failure_lab(request):
    context = {}
    
    if request.method == 'POST':
        # Insecure: Using MD5 for password hashing (cryptographic weakness)
        password = request.POST.get('password', '')
        if password:
            # Insecure: MD5 is cryptographically broken
            hashed = hashlib.md5(password.encode()).hexdigest()
            context['hashed'] = hashed
    
    return render(request, 'crypto_failure_lab.html', context)

def crypto_failure_lab2(request):
    context = {}
    
    if request.method == 'POST':
        # Insecure: Using SHA-1 for password hashing (deprecated for security)
        password = request.POST.get('password', '')
        if password:
            # Insecure: SHA-1 is no longer considered secure for password hashing
            hashed = hashlib.sha1(password.encode()).hexdigest()
            context['hashed'] = hashed
    
    return render(request, 'crypto_failure_lab2.html', context)

def crypto_failure_lab3(request):
    context = {}
    
    if request.method == 'POST':
        # Insecure: Using a weak encryption key and algorithm
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad, unpad
        import os
        
        plaintext = request.POST.get('data', '')
        if plaintext:
            try:
                # Insecure: Using a static key and IV
                key = b'thisisakey123456'  # Should be randomly generated and securely stored
                iv = b'1234567890123456'   # Should be randomly generated for each encryption
                
                # Insecure: Using ECB mode (deterministic encryption)
                cipher = AES.new(key, AES.MODE_ECB)
                padded_data = pad(plaintext.encode(), AES.block_size)
                encrypted = cipher.encrypt(padded_data)
                
                context['encrypted'] = base64.b64encode(encrypted).decode()
                
            except Exception as e:
                context['error'] = str(e)
    
    return render(request, 'crypto_failure_lab3.html', context)

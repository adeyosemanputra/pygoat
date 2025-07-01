import os
import base64
import hashlib
import logging
import json
import hmac
from datetime import datetime
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Configure logger
logger = logging.getLogger(__name__)

# A2: Cryptographic Failures Views

def a2(request):
    """View for A2: Cryptographic Failures introduction."""
    return render(request, 'a2.html')

def weak_encryption(text):
    """
    Insecure: Uses weak encryption (AES in ECB mode with static IV)
    This is just for demonstration - do NOT use in production!
    """
    # Insecure: Using a static key and IV
    key = b'thisisaveryweakkey'  # Should be 16, 24, or 32 bytes long
    iv = b'staticiv12345678'     # Should be random for CBC mode
    
    # Pad the text to be a multiple of 16 bytes (AES block size)
    padded_text = pad(text.encode(), AES.block_size)
    
    # Insecure: Using ECB mode which is not secure
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted = cipher.encrypt(padded_text)
    
    return base64.b64encode(encrypted).decode('utf-8')

def weak_decryption(encrypted_text):
    """
    Insecure: Decrypts text using weak encryption
    This is just for demonstration - do NOT use in production!
    """
    try:
        # Insecure: Using the same static key and IV as encryption
        key = b'thisisaveryweakkey'
        iv = b'staticiv12345678'
        
        # Decode from base64
        encrypted_bytes = base64.b64decode(encrypted_text)
        
        # Insecure: Using ECB mode which is not secure
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted = cipher.decrypt(encrypted_bytes)
        
        # Unpad the decrypted text
        unpadded = unpad(decrypted, AES.block_size)
        
        return unpadded.decode('utf-8')
    except Exception as e:
        logger.error(f"Decryption error: {str(e)}")
        return None

@require_http_methods(['GET', 'POST'])
def a2_lab(request):
    """Lab for demonstrating cryptographic failures."""
    context = {}
    
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            
            if action == 'encrypt':
                # Insecure: Using weak encryption
                plaintext = request.POST.get('plaintext', '')
                if plaintext:
                    encrypted = weak_encryption(plaintext)
                    context['encrypted'] = encrypted
                    
                    # Insecure: Logging sensitive data
                    logger.info(f"Encrypted '{plaintext}' to '{encrypted}'")
            
            elif action == 'decrypt':
                # Insecure: Using weak decryption
                encrypted_text = request.POST.get('encrypted_text', '')
                if encrypted_text:
                    decrypted = weak_decryption(encrypted_text)
                    if decrypted is not None:
                        context['decrypted'] = decrypted
                        
                        # Insecure: Logging sensitive data
                        logger.info(f"Decrypted '{encrypted_text}' to '{decrypted}'")
                    else:
                        context['error'] = "Decryption failed"
            
        except Exception as e:
            context['error'] = f"Error: {str(e)}"
    
    return render(request, 'a2_lab.html', context)

def insecure_hash(password):
    """
    Insecure: Uses weak hashing algorithm (MD5) without salt
    This is just for demonstration - do NOT use in production!
    """
    # Insecure: Using MD5 which is cryptographically broken
    return hashlib.md5(password.encode()).hexdigest()

def insecure_password_reset(request):
    """Insecure password reset implementation."""
    if request.method == 'POST':
        try:
            # Insecure: No rate limiting or proper token generation
            email = request.POST.get('email', '')
            
            if email:
                # Insecure: Using a predictable reset token
                reset_token = hashlib.md5(email.encode() + str(datetime.now().timestamp()).encode()).hexdigest()
                
                # Insecure: Logging sensitive information
                logger.info(f"Password reset requested for {email}. Token: {reset_token}")
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'If the email exists, a reset link has been sent.',
                    # Insecure: Returning token in response
                    'token': reset_token
                })
            
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred. Please try again later.'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    }, status=405)

@require_http_methods(['GET', 'POST'])
def a2_lab2(request):
    """Lab 2 for demonstrating more cryptographic failures."""
    context = {}
    
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            
            if action == 'hash':
                # Insecure: Using weak hashing
                password = request.POST.get('password', '')
                if password:
                    # Insecure: Using weak hashing algorithm
                    hashed = insecure_hash(password)
                    context['hashed'] = hashed
                    
                    # Insecure: Logging sensitive data
                    logger.info(f"Hashed password: {hashed}")
            
            elif action == 'verify_hash':
                # Insecure: Hash verification
                password = request.POST.get('password', '')
                stored_hash = request.POST.get('stored_hash', '')
                
                if password and stored_hash:
                    # Insecure: Simple hash comparison
                    computed_hash = insecure_hash(password)
                    context['match'] = (computed_hash == stored_hash)
            
            elif action == 'encrypt_file':
                # Insecure: File encryption
                file = request.FILES.get('file')
                if file:
                    # Read file content
                    content = file.read()
                    
                    # Insecure: Using weak encryption with static key
                    key = b'thisisaveryweakkey'  # Should be 16, 24, or 32 bytes long
                    iv = b'staticiv12345678'     # Should be random for CBC mode
                    
                    # Pad the content to be a multiple of 16 bytes (AES block size)
                    padded_content = pad(content, AES.block_size)
                    
                    # Insecure: Using ECB mode which is not secure
                    cipher = AES.new(key, AES.MODE_ECB)
                    encrypted = cipher.encrypt(padded_content)
                    
                    # Create response with encrypted file
                    response = HttpResponse(encrypted, content_type='application/octet-stream')
                    response['Content-Disposition'] = f'attachment; filename="{file.name}.enc"'
                    return response
            
        except Exception as e:
            context['error'] = f"Error: {str(e)}"
    
    return render(request, 'a2_lab2.html', context)

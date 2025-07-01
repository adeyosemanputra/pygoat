import base64
import hashlib
import json
import logging
import pickle
import random
import re
import string
from dataclasses import dataclass
from hashlib import md5
from io import BytesIO

from argon2 import PasswordHasher
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.template.loader import render_to_string

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='app.log')

# Password hasher
ph = PasswordHasher()

# Utility functions
def customHash(input_str):
    """Generate a custom hash for the input string."""
    return hashlib.sha256(input_str.encode()).hexdigest()

def filter_blog(blog_content):
    """Filter blog content for XSS protection (example implementation)."""
    # This is a simple example - in production, use a proper HTML sanitizer
    return blog_content.replace('<script>', '').replace('</script>', '')

# Common constants
USER_A7_LAB3 = {
    "User1": {"userid": "1", "username": "User1", 
              "password": "491a2800b80719ea9e3c89ca5472a8bda1bdd1533d4574ea5bd85b70a8e93be0"},
    "User2": {"userid": "2", "username": "User2", 
              "password": "c577e95bf729b94c30a878d01155693a9cdddafbb2fe0d52143027474ecb91bc"},
    "admin": {"userid": "999", "username": "admin", 
             "password": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"}
}

# Common dataclasses
@dataclass
class TestUser:
    """Test user class for insecure deserialization demo."""
    admin: int = 0

# Common pickled objects
pickled_user = pickle.dumps(TestUser())
encoded_user = base64.b64encode(pickled_user)

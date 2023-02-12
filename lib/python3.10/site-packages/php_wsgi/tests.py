from werkzeug.test import Client
from .php_app import PhpWsgiApp

client = Client(PhpWsgiApp('test'))
client.get('/')

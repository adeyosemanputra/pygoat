# This is a fixed version demonstrating how to prevent SQL injection in Django.

from django.db import connection
from django.http import HttpResponse

def vuln_sql_injection_safe(request):
    query = request.GET.get('search', '')
    # Use parameterized queries to prevent SQL Injection
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM challenge_challenge WHERE name = %s", [query])
        results = cursor.fetchall()
    return HttpResponse(str(results))

# This is an intentionally vulnerable demonstration for educational purposes only.

from django.db import connection
from django.http import HttpResponse

def vuln_sql_injection(request):
    query = request.GET.get('search', '')
    # WARNING: This is intentionally vulnerable to SQL Injection!
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM challenge_challenge WHERE name = '{query}'")
        results = cursor.fetchall()
    return HttpResponse(str(results))

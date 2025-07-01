from django.db import connection
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# SQL Injection Vulnerability Views
def sql(request):
    return render(request, 'sql.html')

@require_http_methods(['GET', 'POST'])
def sql_lab(request):
    results = []
    query = ''
    
    if request.method == 'POST':
        search = request.POST.get('search', '')
        query = f"SELECT * FROM introduction_sql_lab_table WHERE name LIKE '%{search}%'"
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            results = [{'error': str(e)}]
    
    return render(request, 'sql_lab.html', {'results': results, 'query': query})

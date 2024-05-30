from django.core.signals import request_finished
from django.dispatch import receiver
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render

import sqlite3

connection = sqlite3.connect(":memory:")
connection.cursor().execute("CREATE TABLE Users (name, phone)")
connection.cursor().execute("INSERT INTO Users VALUES ('Jenny','867-5309')")

@csrf_exempt
@receiver(request_finished)
def bad_query(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')

        query = "SELECT * FROM Users WHERE name ='" + name + "' AND phone = '" + phone + "'"
        result = connection.cursor().execute(query)
        return render(request, 'result.html', {'result': result})
    else:
        return redirect('/')

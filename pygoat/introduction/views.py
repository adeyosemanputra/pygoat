from django.shortcuts import render
from django.http import HttpResponse
from .models import  FAANG,info,login

def home(request):
    
    return render(request,'introduction/home.html')
def xss(request):
    return render(request,"Lab/XSS/xss.html")
def xss_lab(request):
    q=request.GET.get('q','');
    f=FAANG.objects.filter(company=q)
    if f:
        args={"company":f[0].company,"ceo":f[0].info_set.all()[0].ceo,"about":f[0].info_set.all()[0].about}
        return render(request,'Lab/XSS/xss_lab.html',args)
    else:
        return render(request,'Lab/XSS/xss_lab.html', {'query': q})
def sql(request):
    return  render(request,'Lab/SQL/sql.html')
def sql_lab(request):

    name=request.POST.get('name')

    password=request.POST.get('pass')

    if name:

        if login.objects.filter(user=name):



            val=login.objects.raw("SELECT * FROM introduction_login WHERE user='"+name+"'AND password='"+password+"'")

            if val:
                user=val[0].user;
                return render(request, 'Lab/SQL/sql_lab.html',{"user1":user})
            else:
                return render(request, 'Lab/SQL/sql_lab.html',{"wrongpass":password})
        else:
            return render(request, 'Lab/SQL/sql_lab.html',{"no": "User not found"})
    else:
        return render(request, 'Lab/SQL/sql_lab.html')


from django.shortcuts import render
from django.http import HttpResponse
from .models import  FAANG,info,login,comments
from django.core import serializers
from requests.structures import CaseInsensitiveDict
import requests
from xml.dom.pulldom import parseString, START_ELEMENT
from xml.sax.handler import feature_external_ges
from xml.sax import make_parser
from django.views.decorators.csrf import csrf_exempt

import pickle
import base64
from dataclasses import dataclass

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


#***********************************SQL*******************************SQL*********************************#

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

#***************** INSECURE DESERIALIZATION***************************************************************#
def insec_des(request):
    return  render(request,'Lab/insec_des/insec_des.html')

@dataclass
class TestUser:
    admin: int = 0
pickled_user = pickle.dumps(TestUser())
encoded_user = base64.b64encode(pickled_user)

def insec_des_lab(request):
    response = render(request,'Lab/insec_des/insec_des_lab.html', {"message":"Only Admins can see this page"})
    token = request.COOKIES.get('token')
    if token == None:
        token = encoded_user
        response.set_cookie(key='token',value=token.decode('utf-8'))
    else:
        token = base64.b64decode(token)
        admin = pickle.loads(token)
        if admin.admin == 1:
            response = render(request,'Lab/insec_des/insec_des_lab.html', {"message":"Welcome Admin, SECRETKEY:ADMIN123"})
            return response

    return response

#****************************************************XXE********************************************************#


def xxe(request):
    return render (request,'Lab/XXE/xxe.html')

def xxe_lab(request):
    return render(request,'Lab/XXE/xxe_lab.html')

@csrf_exempt
def xxe_see(request):

    data=comments.objects.all();
    com=data[0].comment
    return render(request,'Lab/XXE/xxe_lab.html',{"com":com})



@csrf_exempt
def xxe_parse(request):
    parser = make_parser()
    parser.setFeature(feature_external_ges, True)
    doc = parseString(request.body.decode('utf-8'), parser=parser)
    for event, node in doc:
        if event == START_ELEMENT and node.tagName == 'text':
            doc.expandNode(node)
            text = node.toxml()
    startInd = text.find('>')
    endInd = text.find('<', startInd)
    text = text[startInd + 1:endInd:]
    p=comments.objects.filter(id=1).update(comment=text);

    return render(request, 'Lab/XXE/xxe_lab.html')



#***************************************************************Broken Access Control************************************************************#
@csrf_exempt
def ba(request):
    return render(request,"Lab/BrokenAccess/ba.html")
@csrf_exempt
def ba_lab(request):
    name = request.POST.get('name')
    password = request.POST.get('pass')
    if name:


        if request.COOKIES.get('admin') == "1":
            return render(request, 'Lab/BrokenAccess/ba_lab.html', {"data":"Here is your Secret Key :3600"})
        elif login.objects.filter(user=name) and login.objects.filter(password=password):
            html = render(request, 'Lab/BrokenAccess/ba_lab.html', {"data":"Here is your Secret Key :3600"})
            html.set_cookie("admin", "1",max_age=2);
            return html
        else:
            html = render(request, 'Lab/BrokenAccess/ba_lab.html',{"data":"Welcome :"+name} )
            html.set_cookie("admin", "0");
            return html
    else:
        return render(request,'Lab/BrokenAccess/ba_lab.html',{"data":"Please Provide Credentials"})










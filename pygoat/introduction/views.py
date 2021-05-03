from django.shortcuts import render
from django.http import HttpResponse
from .models import  FAANG,info,login,comments,otp
from random import randint
from xml.dom.pulldom import parseString, START_ELEMENT
from xml.sax.handler import feature_external_ges
from xml.sax import make_parser
from django.views.decorators.csrf import csrf_exempt
import subprocess
import pickle
import base64
import yaml
import json
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


#***********************************SQL****************************************************************#

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
        elif login.objects.filter(user='admin',password=password):
            html = render(request, 'Lab/BrokenAccess/ba_lab.html', {"data":"Here is your Secret Key :3600"})
            html.set_cookie("admin", "1",max_age=20);
            return html
        elif login.objects.filter(user=name,password=password):
            html = render(request, 'Lab/BrokenAccess/ba_lab.html',{"data":"Welcome Jack"} )
            html.set_cookie("admin", "0",max_age=20);
            return html
        else:
            return render(request, 'Lab/BrokenAccess/ba_lab.html', {"data": "User Not Found"})

    else:
        return render(request,'Lab/BrokenAccess/ba_lab.html',{"data":"Please Provide Credentials"})


#********************************************************Sensitive Data Exposure*****************************************************#


def data_exp(request):
    return  render(request,'Lab/DataExp/data_exp.html')

def data_exp_lab(request):
    return  render(request,'Lab/DataExp/data_exp_lab.html')

def robots(request):
    response = render(request,'Lab/DataExp/robots.txt')
    response['Content-Type'] =  'text/plain'
    return response

def error(request):
    return 


#******************************************************  Command Injection  ***********************************************************************#
def cmd(request):
    return render(request,'Lab/CMD/cmd.html')
@csrf_exempt
def cmd_lab(request):
    if(request.method=="POST"):
        domain=request.POST.get('domain')
        domain=domain.replace("https://www.",'')
        os=request.POST.get('os')
        print(os)
        if(os=='win'):
            command="nslookup {}".format(domain)
        else:
            command = "dig {}".format(domain)

        output=subprocess.check_output(command,shell=True,encoding="UTF-8");
        print(output)
        return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
    else:
        return render(request, 'Lab/CMD/cmd_lab.html')


#******************************************Broken Authentication**************************************************#
def bau(request):
    return render(request,"Lab/BrokenAuth/bau.html")
def bau_lab(request):
    if request.method=="GET":
        return render(request,"Lab/BrokenAuth/bau_lab.html")
    else:
        return render(request, 'Lab/BrokenAuth/bau_lab.html', {"wrongpass":"yes"})



def login_otp(request):
    return render(request,"Lab/BrokenAuth/otp.html")

@csrf_exempt
def Otp(request):
    if request.method=="GET":
        email=request.GET.get('email');
        otpN=randint(100,999)
        if email and otpN:
            if email=="admin@pygoat.com":
                otp.objects.filter(id=2).update(otp=otpN)
                html = render(request, "Lab/BrokenAuth/otp.html", {"otp":"Sent To Admin Mail ID"})
                html.set_cookie("email", email);
                return html

            else:
                otp.objects.filter(id=1).update(email=email, otp=otpN)
                html=render (request,"Lab/BrokenAuth/otp.html",{"otp":otpN})
                html.set_cookie("email",email);
                return html;
        else:
            return render(request,"Lab/BrokenAuth/otp.html")
    else:
        otpR=request.POST.get("otp")
        email=request.COOKIES.get("email")
        if otp.objects.filter(email=email,otp=otpR) or otp.objects.filter(id=2,otp=otpR):
            return HttpResponse("<h3>Login Success for email:::"+email+"</h3>")
        else:
            return render(request,"Lab/BrokenAuth/otp.html",{"otp":"Invalid OTP Please Try Again"})


#*****************************************Security Misconfiguration**********************************************#

def sec_mis(request):
    return render(request,"Lab/sec_mis/sec_mis.html")

def sec_mis_lab(request):
    return render(request,"Lab/sec_mis/sec_mis_lab.html")

def secret(request):
    XHost = request.headers.get('X-Host', 'None')
    if(XHost == 'admin.localhost:8000'):
        return render(request,"Lab/sec_mis/sec_mis_lab.html", {"secret": "SECERTKEY123"})
    else:
        return render(request,"Lab/sec_mis/sec_mis_lab.html", {"secret": "Only admin.localhost:8000 can access, Your X-Host is " + XHost})


#**********************************************************A9*************************************************#

def a9(request):
    return render(request,"Lab/A9/a9.html")
@csrf_exempt
def a9_lab(request):
    if request.method=="GET":
        return render(request,"Lab/A9/a9_lab.html")
    else:

        try :
            file=request.FILES["file"]
            try :
                data = yaml.load(file)
                return render(request,"Lab/A9/a9_lab.html",{"data":data})
            except:
                return render(request, "Lab/A9/a9_lab.html", {"data": "Error"})

        except:
            return render(request, "Lab/A9/a9_lab.html", {"data":"Please Upload a Yaml file."})

def get_version(request):
      return render(request,"Lab/A9/a9_lab.html",{"version":"pyyaml v5.1"})



#*********************************************************A10*************************************************#

def a10(request):
    return render(request,"Lab/A10/a10.html")

def a10_lab(request):
    return render(request,"Lab/A10/a10_lab.html")

def debug(request):
    response = render(request,'Lab/A10/debug.log')
    response['Content-Type'] =  'text/plain'
    return response

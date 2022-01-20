from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import  FAANG,info,login,comments,authLogin
from django.core import serializers
from requests.structures import CaseInsensitiveDict
import requests
from django.contrib.auth import login,authenticate
from django.contrib.auth.forms import UserCreationForm

#*****************************************Lab Requirements****************************************************#

from .models import  FAANG,info,login,comments,otp
from random import randint
from xml.dom.pulldom import parseString, START_ELEMENT
from xml.sax.handler import feature_external_ges
from xml.sax import make_parser
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
import subprocess
import pickle
import base64
import yaml
import json
from dataclasses import dataclass


#*****************************************Login and Registration****************************************************#


def register(request):
    if request.method=="POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect("login")

    else:
        form=UserCreationForm();
        return render(request,"registration/register.html",{"form":form,})

def home(request):
    if request.user.is_authenticated:
        return render(request,'introduction/home.html',)
    else:
        return redirect('login')

#*****************************************XSS****************************************************#


def xss(request):
    if request.user.is_authenticated:
        return render(request,"Lab/XSS/xss.html")
    else:
        return redirect('login')

def xss_lab(request):
    if request.user.is_authenticated:
        q=request.GET.get('q','');
        f=FAANG.objects.filter(company=q)
        if f:
            args={"company":f[0].company,"ceo":f[0].info_set.all()[0].ceo,"about":f[0].info_set.all()[0].about}
            return render(request,'Lab/XSS/xss_lab.html',args)
        else:
            return render(request,'Lab/XSS/xss_lab.html', {'query': q})
    else:
        return redirect('login')

#***********************************SQL****************************************************************#

def sql(request):
    if request.user.is_authenticated:

        return  render(request,'Lab/SQL/sql.html')
    else:
        return redirect('login')

def sql_lab(request):
    if request.user.is_authenticated:

        name=request.POST.get('name')

        password=request.POST.get('pass')

        if name:

            if login.objects.filter(user=name):

                sql_query = "SELECT * FROM introduction_login WHERE user='"+name+"'AND password='"+password+"'"
                print(sql_query)
                try:
                    print("\nin try\n")
                    val=login.objects.raw(sql_query)
                except:
                    print("\nin except\n")
                    return render(
                        request, 
                        'Lab/SQL/sql_lab.html',
                        {
                            "wrongpass":password,
                            "sql_error":sql_query
                        })

                if val:
                    user=val[0].user;
                    return render(request, 'Lab/SQL/sql_lab.html',{"user1":user})
                else:
                    return render(
                        request, 
                        'Lab/SQL/sql_lab.html',
                        {
                            "wrongpass":password,
                            "sql_error":sql_query
                        })
            else:
                return render(request, 'Lab/SQL/sql_lab.html',{"no": "User not found"})
        else:
            return render(request, 'Lab/SQL/sql_lab.html')
    else:
        return redirect('login')

#***************** INSECURE DESERIALIZATION***************************************************************#

def insec_des(request):
    if request.user.is_authenticated:
        return  render(request,'Lab/insec_des/insec_des.html')
    else:
        return redirect('login')

@dataclass
class TestUser:
    admin: int = 0
pickled_user = pickle.dumps(TestUser())
encoded_user = base64.b64encode(pickled_user)

def insec_des_lab(request):
    if request.user.is_authenticated:
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
    else:
        return redirect('login')

#****************************************************XXE********************************************************#


def xxe(request):
    if request.user.is_authenticated:

        return render (request,'Lab/XXE/xxe.html')
    else:
        return redirect('login')

def xxe_lab(request):
    if request.user.is_authenticated:
        return render(request,'Lab/XXE/xxe_lab.html')
    else:
        return redirect('login')

@csrf_exempt
def xxe_see(request):
    if request.user.is_authenticated:

        data=comments.objects.all();
        com=data[0].comment
        return render(request,'Lab/XXE/xxe_lab.html',{"com":com})
    else:
        return redirect('login')


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

def auth_home(request):
    return render(request,'Lab/AUTH/auth_home.html')


def auth_lab(request):
    return render(request,'Lab/AUTH/auth_lab.html')

def auth_lab_signup(request):
    if request.method == 'GET':
        return render(request,'Lab/AUTH/auth_lab_signup.html')
    elif request.method == 'POST':
        try:
            name = request.POST['name']
            user_name = request.POST['username']
            passwd  = request.POST['pass']
            obj = authLogin.objects.create(name=name,username=user_name,password=passwd)
            try:
                rendered = render_to_string('Lab/AUTH/auth_success.html', {'username': obj.username,'userid':obj.userid,'name':obj.name,'err_msg':'Cookie Set'})
                response = HttpResponse(rendered)
                response.set_cookie('userid', obj.userid, max_age=31449600, samesite=None, secure=False)
                print('Setting cookie successful')
                return response
            except:
                render(request,'Lab/AUTH/auth_lab_signup.html',{'err_msg':'Cookie cannot be set'})
        except:
            return render(request,'Lab/AUTH/auth_lab_signup.html',{'err_msg':'Username already exists'})

def auth_lab_login(request):
    if request.method == 'GET':
        try:
            obj = authLogin.objects.filter(userid=request.COOKIES['userid'])[0]
            rendered = render_to_string('Lab/AUTH/auth_success.html', {'username': obj.username,'userid':obj.userid,'name':obj.name, 'err_msg':'Login Successful'})
            response = HttpResponse(rendered)
            response.set_cookie('userid', obj.userid, max_age=31449600, samesite=None, secure=False)
            print('Login successful')
            return response
        except:
            return render(request,'Lab/AUTH/auth_lab_login.html')
    elif request.method == 'POST':
        try:
            user_name = request.POST['username']
            passwd  = request.POST['pass']
            print(user_name,passwd)
            obj = authLogin.objects.filter(username=user_name,password=passwd)[0]
            try:
                rendered = render_to_string('Lab/AUTH/auth_success.html', {'username': obj.username,'userid':obj.userid,'name':obj.name, 'err_msg':'Login Successful'})
                response = HttpResponse(rendered)
                response.set_cookie('userid', obj.userid, max_age=31449600, samesite=None, secure=False)
                print('Login successful')
                return response
            except:
                render(request,'Lab/AUTH/auth_lab_login.html',{'err_msg':'Cookie cannot be set'})
        except:
            return render(request,'Lab/AUTH/auth_lab_login.html',{'err_msg':'Check your credentials'})

def auth_lab_logout(request):
    rendered = render_to_string('Lab/AUTH/auth_lab.html',context={'err_msg':'Logout successful'})
    response = HttpResponse(rendered)    
    response.delete_cookie('userid')
    return response

#***************************************************************Broken Access Control************************************************************#

@csrf_exempt
def ba(request):
    if request.user.is_authenticated:
        return render(request,"Lab/BrokenAccess/ba.html")
    else:
        return redirect('login')
@csrf_exempt
def ba_lab(request):
    if request.user.is_authenticated:
        name = request.POST.get('name')
        password = request.POST.get('pass')
        if name:


            if request.COOKIES.get('admin') == "1":
                return render(request, 'Lab/BrokenAccess/ba_lab.html', {"data":"Here is your Secret Key :3600"})
            elif login.objects.filter(user='admin',password=password):
                html = render(request, 'Lab/BrokenAccess/ba_lab.html', {"data":"Here is your Secret Key :3600"})
                html.set_cookie("admin", "1",max_age=200);
                return html
            elif login.objects.filter(user=name,password=password):
                html = render(request, 'Lab/BrokenAccess/ba_lab.html',{"data":"Welcome Jack"} )
                html.set_cookie("admin", "0",max_age=200);
                return html
            else:
                return render(request, 'Lab/BrokenAccess/ba_lab.html', {"data": "User Not Found"})

        else:
            return render(request,'Lab/BrokenAccess/ba_lab.html',{"data":"Please Provide Credentials"})
    else:
        return redirect('login')

#********************************************************Sensitive Data Exposure*****************************************************#


def data_exp(request):
    if request.user.is_authenticated:
        return  render(request,'Lab/DataExp/data_exp.html')
    else:
        return redirect('login')

def data_exp_lab(request):
    if request.user.is_authenticated:
        return  render(request,'Lab/DataExp/data_exp_lab.html')
    else:
        return redirect('login')
def robots(request):
    if request.user.is_authenticated:
        response = render(request,'Lab/DataExp/robots.txt')
        response['Content-Type'] =  'text/plain'
        return response

def error(request):
    return 


#******************************************************  Command Injection  ***********************************************************************#

def cmd(request):
    if request.user.is_authenticated:
        return render(request,'Lab/CMD/cmd.html')
    else:
        return redirect('login')
@csrf_exempt
def cmd_lab(request):
    if request.user.is_authenticated:
        if(request.method=="POST"):
            domain=request.POST.get('domain')
            domain=domain.replace("https://www.",'')
            os=request.POST.get('os')
            print(os)
            if(os=='win'):
                command="nslookup {}".format(domain)
            else:
                command = "dig {}".format(domain)
            
            try:
                # output=subprocess.check_output(command,shell=True,encoding="UTF-8")
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                data = stdout.decode('utf-8')
                stderr = stderr.decode('utf-8')
                # res = json.loads(data)
                # print("Stdout\n" + data)
                output = data + stderr
                print(data + stderr)
            except:
                output = "Something went wrong"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
            print(output)
            return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
        else:
            return render(request, 'Lab/CMD/cmd_lab.html')
    else:
        return redirect('login')

#******************************************Broken Authentication**************************************************#

def bau(request):
    if request.user.is_authenticated:

        return render(request,"Lab/BrokenAuth/bau.html")
    else:
        return redirect('login')
def bau_lab(request):
    if request.user.is_authenticated:
        if request.method=="GET":
            return render(request,"Lab/BrokenAuth/bau_lab.html")
        else:
            return render(request, 'Lab/BrokenAuth/bau_lab.html', {"wrongpass":"yes"})
    else:
        return redirect('login')


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
    if request.user.is_authenticated:
        return render(request,"Lab/sec_mis/sec_mis.html")
    else:
        return redirect('login')

def sec_mis_lab(request):
    if request.user.is_authenticated:
        return render(request,"Lab/sec_mis/sec_mis_lab.html")
    else:
        return redirect('login')

def secret(request):
    XHost = request.headers.get('X-Host', 'None')
    if(XHost == 'admin.localhost:8000'):
        return render(request,"Lab/sec_mis/sec_mis_lab.html", {"secret": "SECERTKEY123"})
    else:
        return render(request,"Lab/sec_mis/sec_mis_lab.html", {"secret": "Only admin.localhost:8000 can access, Your X-Host is " + XHost})


#**********************************************************A9*************************************************#

def a9(request):
    if request.user.is_authenticated:
        return render(request,"Lab/A9/a9.html")
    else:
        return redirect('login')
@csrf_exempt
def a9_lab(request):
    if request.user.is_authenticated:
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
    else:
        return redirect('login')
def get_version(request):
      return render(request,"Lab/A9/a9_lab.html",{"version":"pyyaml v5.1"})



#*********************************************************A10*************************************************#

def a10(request):
    if request.user.is_authenticated:
        return render(request,"Lab/A10/a10.html")
    else:
        return redirect('login')
def a10_lab(request):
    if request.user.is_authenticated:
        if request.method=="GET":

            return render(request,"Lab/A10/a10_lab.html")
        else:

            user=request.POST.get("name")
            password=request.POST.get("pass")
            if login.objects.filter(user=user,password=password):
                return render(request,"Lab/A10/a10_lab.html",{"name":user})
            else:
                return render(request, "Lab/A10/a10_lab.html", {"error": " Wrong username or Password"})

    else:
        return redirect('login')

def debug(request):
    response = render(request,'Lab/A10/debug.log')
    response['Content-Type'] =  'text/plain'
    return response
